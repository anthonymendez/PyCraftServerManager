import os
import pexpect
import tarfile
import re
import logging
from datetime import datetime

# Set up Logging
time_now = str(datetime.now()).replace(" ", "_").replace("-", "_").replace(":", "_").replace(".", "_")
log_path = os.path.join("log", time_now)
if not os.path.exists("log"):
    os.mkdir("log")
if not os.path.exists(log_path):
    os.mkdir(log_path)
log_path = os.path.join(log_path, "master.log")
logging.basicConfig(format="%(asctime)s - %(filename)s - %(funcName)s - %(name)s - %(levelname)s - %(message)s", 
                    filename=log_path, 
                    level=logging.DEBUG)

from threading import Thread, Lock
from time import sleep
from termcolor import colored
from pexpect import popen_spawn
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_LZMA, ZIP_BZIP2
from shutil import copy
from ..Configuration.WhitelistHandler import WhitelistHandler
from ..Configuration.ServerPropertiesHandler import ServerPropertiesHandler
from ..Configuration.LaunchOptionsHandler import LaunchOptionsHandler
from ..Utilities.Utilities import *
from ..Utilities.Scheduler import Scheduler
from ..Utilities.Backup import *
from ..Utilities.JarManager import *
from ..ServerDownloader.VanillaServerDownloader import VanillaServerDownloader

if is_windows():
    import colorama
    colorama.init()

class VanillaServerRunner:
    """
    Vanilla Server Runner handles launching of the Minecraft 
    Server jar, and configuring the launch parameters.
    """

    def __init__(self, server_folder, *args, **kwargs):
        """
        Sets server folder location relative to python project.\n
        Example inputs:\n 
        \t\"../server/\" - Back one directory, then into server folder
        """
        logging.info("Entry")
        # Server running variables
        self.server_process = None
        self.input_thread = None
        self.output_thread = None
        # Handle optional arguments
        self.server_jar_filename = kwargs.get('server_jar_filename', "server.jar")
        # Set main directory of python project
        self.main_directory = os.getcwd()
        # Set server folder and server directory
        self.server_folder = server_folder
        self.server_dir = os.path.join(self.main_directory, server_folder)
        # Set server jar folder
        self.server_jars = "server_jars"
        # Set up commands array
        self.commands_functions_dict = {
            # Terminal Command: (fn pointer, argument count)
            "start": (self.start, 0), 
            "stop": (self.stop, 0), 
            "restart": (self.restart, 0), 
            "backup": (self.backup, 1),
            "exit": (self.exit, 0),
            "delete_user_cache": (self.delete_user_cache, 0),
            "schedule": (self.schedule, -1),
            "jar": (self.jar, -1),
            "launch_options": (self.launch_options, -1),
            "server_properties": (self.server_properties, -1),
            "whitelist": (self.whitelist, -1)
        }
        # Vanilla Server Downloader
        self.ServerDownloader = VanillaServerDownloader(self.main_directory, self.server_dir, self.server_jars)
        # Server Properties Handler
        self.ServerPropertiesHandler = ServerPropertiesHandler(self.main_directory, self.server_dir)
        # Whitelist Handler
        self.WhitelistHandler = WhitelistHandler(self.main_directory, self.server_dir)
        # Launch Options Handler
        self.LaunchOptionsHandler = LaunchOptionsHandler(self.main_directory, self.server_dir)
        # Scheduler Class
        self.Scheduler = Scheduler(self.main_directory, self.server_dir, self.__input_handler, self)
        # Enable Eula
        enable_eula(self.server_dir)
        # Start up input thread
        self.minecraft_input_handler_lock = Lock()
        self.pycraft_input_handler_lock = Lock()
        self.stopping_all = False
        self.input_thread = Thread(target=self.__input_loop_thread)
        self.input_thread.start()
        self.server_process_eof = True
        logging.debug("server_jar_filename: %s", self.server_jar_filename)
        logging.debug("server_jar folder: %s", self.server_jars)
        logging.debug("command_functions_dict: %s", self.commands_functions_dict)
        logging.info("Exit")

    def __minecraft_input_handler(self, cmd_input):
        """
        Handles sending input to the Minecraft Server Process.
        """
        with self.minecraft_input_handler_lock:
            logging.info("Command is a Minecraft Server command.")
            if not self.server_process is None:
                cmd_input_after_slash = cmd_input[1::]
                logging.debug("Command after slash: %s", cmd_input_after_slash)
                logging.info("Sending command to %s server... ", cmd_input_after_slash)
                print(colored("Sending command to %s server... " % cmd_input_after_slash, "green"))
                self.server_process.sendline(cmd_input_after_slash.encode("utf-8"))
            else:
                logging.warning("Server has not been started! Start server with \"start\" to start the server!")
                print(colored("Server has not been started! Start server with \"start\" to start the server!", "red"))

    def __pycraft_input_handler(self, cmd_input):
        """
        Handles input for launching PyCraftServerManager commands.
        """
        with self.pycraft_input_handler_lock:
            logging.info("Command is a PyCraftServerManager command.")
            cmd_input_args = cmd_input.split(" ")
            command = cmd_input_args[0]
            if command in self.commands_functions_dict:
                print(colored("Command \"%s\" received!" % cmd_input, "green"))
                fn = self.commands_functions_dict.get(command)[0]
                if fn is None:
                    logging.warning("Command not programmed yet! Coming soon!")
                    print(colored("Command not programmed yet! Coming soon!", "yellow"))
                else:
                    logging.debug("Given valid command.")
                    args_required = self.commands_functions_dict.get(command)[1]
                    if args_required == -1:
                        fn_return = fn(cmd_input)
                    elif args_required == 0:
                        fn_return = fn()
                    elif len(cmd_input_args) - 1 == args_required:
                        fn_return = fn(cmd_input_args[1::])
                    else:
                        logging.warning("Argument count not matched. Required %d. Received %d." % (len(cmd_input_args) - 1, args_required))
                        print(colored("Argument count not matched. Required %d. Received %d." % (len(cmd_input_args) - 1, args_required), "red"))

                    # Check what function returned if it did return anything
                    if isinstance(fn_return, bool):
                        if not fn_return:
                            logging.warning("Command \"%s\" did not run successfully." % cmd_input)
                            print(colored("Command \"%s\" did not run successfully." % cmd_input, "red"))
                        else:
                            logging.debug("Command \"%s\" ran successfully." % cmd_input)

            else:
                logging.warning("Command not recognized.")
                print(colored("Command not recognized.", "red"))

    @staticmethod
    def __input_handler(self, cmd_input):
        """
        Handles input given by input thread/command line or a scheduled command
        """
        logging.info("Entry")
        logging.info("cmd_input: %s", str(cmd_input))
        if self.input_thread.isAlive():
            # Empty Input
            if len(cmd_input) == 0:
                logging.error("__input_handler given empty input. Not valid.")
                logging.info("Exit")
                return

            # Command to be sent to the server.jar
            if cmd_input[0] == '/':
                self.__minecraft_input_handler(cmd_input)
            # Command to be handled by ServerRunner
            else:
                self.__pycraft_input_handler(cmd_input)

        logging.info("Exit")

    def __input_loop_thread(self):
        """
        Handles incoming commands from the user.\n
        All commands prepended with "/" will be sent directly to the server.jar\n
        All other commands will be checked to see if they're supported by the program.
        """
        logging.info("Entry")
        while not self.stopping_all:
            # TODO: Figure out how to put input on bottom of terminal always
            logging.info("Waiting on user input.")
            cmd_input = input()
            logging.info("User input: %s", str(cmd_input))

            if isinstance(cmd_input, str):
                logging.info("Passing user input to input handler")
                cmd_input = cmd_input.strip()
                self.__input_handler(self, cmd_input)
            else:
                logging.error("User input is not string. Stopping server process and terminating.")
                self.server_process.sendline("stop".encode("utf-8"))
                self.server_process.terminate(force=True)
                break
        logging.info("Exit")

    def __output_loop_thread(self):
        logging.info("Entry")
        while self.server_process is not None and not self.server_process_eof:
            try:
                output = self.server_process.readline().decode("utf-8").strip()
                if not len(output) == 0:
                    print(output + "\n", end = "")
                elif not self.input_thread.isAlive():
                    self.server_process.sendline("stop".encode("utf-8"))
                    if self.server_process.isalive():
                        self.server_process.terminate(force=True)
                    break
            except pexpect.exceptions.TIMEOUT:
                # print(colored("Output loop Timeout exception.", "red"))
                continue
            except Exception as e:
                print(colored("Output loop exception.", "red"))
                print(e)
                # if not self.server_process is None:
                #     self.stop()
                break
        self.server_process = None
        logging.info("Server Process stopped.")
        print(colored("Server Process stopped.", "yellow"))
        logging.info("Exit")

    def __server_process_watch_thread(self):
        # TODO: Possible Windows Compatibility thing?
        logging.info("Entry")
        self.server_process.wait()
        self.server_process_eof = True
        logging.info("Exit")

    def start(self):
        """
        Starts the server. If it is already started, does nothing.
        """
        logging.info("Entry")
        if self.server_process is None:
            logging.info("Starting server...")
            print(colored("Starting server...", "green"))
            # Change directory to server location
            os.chdir(self.server_dir)
            # Update Launch Options Handler
            self.LaunchOptionsHandler.read_options()
            # Prepare launch String
            self.launch_str = """java %s -jar %s %s""" % (
                " ".join(self.LaunchOptionsHandler.java_options),
                self.server_jar_filename,
                " ".join(self.LaunchOptionsHandler.game_options)
            )
            logging.debug("Launch Parameters: %s", self.launch_str)
            # Spawn & Launch Server Terminal
            # Check if OS is windows. If so, use pexpect.popen_spawn.PopenSpawn
            self.server_process_eof = False
            if is_windows():
                self.server_process = pexpect.popen_spawn.PopenSpawn(self.launch_str)
                logging.debug("Launched Windows server-process subroutine.")
            # If OS is not windows, use pexpect.spawn as normal
            else:
                self.server_process = pexpect.spawn(self.launch_str)
                logging.debug("Launched normal server-process subroutine.")
            self.output_thread = Thread(target=self.__output_loop_thread)
            sleep(0.1)
            self.output_thread.start()
            logging.debug("Launched output subroutine")
            # Watching server process
            self.server_process_watch = Thread(target=self.__server_process_watch_thread)
            self.server_process_watch.start()
            logging.debug("Launched server-process watcher subroutine.")
            # Change directory to python project
            os.chdir(self.main_directory)
        else:
            logging.warning("Server already running!")
            print(colored("Server already running!", "yellow"))
        logging.info("Exit")

    def stop(self):
        """
        Stops the server. If it is already stopped, does nothing.
        """
        logging.info("Entry")
        if self.server_process is None:
            logging.warning("Server is not running!")
            print(colored("Server is not running!", "yellow"))
        else:
            logging.info("Stopping server...")
            print(colored("Stopping server...", "green"))
            try:
                self.server_process.sendline("stop".encode("utf-8"))
                logging.debug("Sent stop to server process.")
            except Exception as e:
                logging.error("Could not send \"stop\" to server process. Reason:\n\t%s", str(e))
            logging.info("Waiting for server-process to die.")
            print(colored("Waiting for server-process to die.", "green"))
            if is_windows():
                # Similar to below but for Windows since we don't have isalive for Popen_Spawn
                # From pexpect docs: pexpect.EOF is raised when EOF is read from a child. This usually means the child has exited.
                self.server_process.wait()
                logging.debug("Finished waiting for Windows server-process to die.")
            else:
                # Check if pexpect.spawn is still alive
                while True:
                    if self.server_process is None and not self.server_process.isalive():
                        break
                logging.debug("Finished waiting for normal server-process to die.")
            self.server_process = None
            logging.info("Server process dead (hopefully). Waiting for output thread to die.")
            print(colored("Server process dead (hopefully). Waiting for output thread to die.", "green"))
            while True:
                if self.output_thread is None or not self.output_thread.isAlive():
                    break
            self.output_thread = None
            logging.info("Output thread dead. Server officially stopped.")
            print(colored("Output thread dead. Server officially stopped.", "green"))
        logging.info("Exit")

    def restart(self):
        """
        Restarts the server if it is running. Does nothing if server isn't running.
        """
        logging.info("Entry")
        if self.server_process is None:
            logging.warning("Server is not running!")
            print(colored("Server is not running!", "yellow"))
        else:
            self.stop()
            logging.info("Waiting for server to stop...")
            print(colored("Waiting for server to stop...", "yellow"))
            while(1):
                sleep(1)
                if (self.server_process is None):
                    break
            self.start()
            logging.info("Restart process done! Wait for server to start!")            
            print(colored("Restart process done! Wait for server to start!", "green"))
        logging.info("Exit")

    def exit(self):
        """
        Stops server if it's running and quits program.
        """
        logging.info("Entry")
        self.stopping_all = True
        if not self.server_process is None:
            self.stop()
        logging.info("Exit")

    def backup(self, cmd_input_args):
        """
        Backs up server folder into a tar or zip archive.\n
        Places archive folder into backups folder.\n
        Terminal calls command like so"\n
        `backup tar` or `backup zip`\n
        """
        logging.info("Entry")
        # Check if it's just a string. Hacky bug fix for Scheduler calling.
        if isinstance(cmd_input_args, str):
            cmd_input_args = [cmd_input_args]
        # Extract type of Backup from input args and create enum
        backup_type = cmd_input_args[0].lower()
        
        # Create name for archive based on time space
        time_now = str(datetime.now()).replace(" ", ".").replace("-", ".").replace(":", ".")
        logging.info("Compressed archive file name: %s.%s" % (time_now, backup_type))
        print(colored("Compressed archive file name: %s" % time_now, "green"))

        # Create folder to store backups
        backup_path = os.path.abspath("backups")
        if not os.path.exists(backup_path):
            os.mkdir(backup_path)
        # Archive Path to store compressed server folder
        archive_path = os.path.join(backup_path, time_now)
        if backup_type == "zip":
            backup_as_zip(self.server_dir, archive_path)
        elif backup_type == "tar":
            backup_as_tar(self.server_dir, archive_path)
        else:
            logging.warning("Invalid Backup Type of \"%s\" passed in. Not backing up." % backup_type)
            print(colored("Invalid Backup Type of \"%s\" passed in. Not backing up." % backup_type, "red"))
            logging.info("Exit")
            return
        print(colored("Backed up server files.", "green"))
        logging.info("Exit")

    def delete_user_cache(self):
        """
        Deletes usercache.json in server folder if server is not running.\n
        Does nothing if server is not running.
        """
        logging.info("Entry")
        if self.server_process is None:
            logging.info("Deleting user cache.")
            print(colored("Deleting user cache.", "green"))
            usercache_file = os.path.join(self.server_dir, "usercache.json")
            os.remove(usercache_file)
            logging.info("Deleted user cache.")
        else:
            logging.warning("Server is running. Cannot delete user cache.")
            print(colored("Server is running. Cannot delete user cache.", "red"))
        logging.info("Exit")

    def schedule(self, cmd_input_args):
        logging.info("Entry")
        # Check what type of schedule command it is
        schedule_command_type = cmd_input_args.split(" ")[1]
        # Add new scheduled command
        if (schedule_command_type == "add"):
            # Extract command and cron string
            # https://stackoverflow.com/a/2076356/12464369
            cmd_inputs_args_quoted = re.findall('"([^"]*)"', cmd_input_args)
            command = cmd_inputs_args_quoted[0]
            cron = cmd_inputs_args_quoted[1]
            logging.debug("Command: %s", command)
            logging.debug("Cron: %s", cron)
            print(cmd_inputs_args_quoted)
            # Create scheduled command
            if (self.Scheduler.add_scheduled_command(command, cron)):
                logging.info("Command successfully scheduled!")
                print(colored("Command successfully scheduled!", "green"))
            else:
                logging.warning("Command not scheduled!")
                print(colored("Command not scheduled!", "red"))
        # List all scheduled commands
        elif (schedule_command_type == "list"):
            logging.info("Listing scheduled commands.")
            if (not self.Scheduler.list_scheduled_commands()):
                logging.error("Something went wrong listing scheduled jobs!")
                print(colored("Something went wrong listing scheduled jobs!", "red"))
        # Delete command
        elif (schedule_command_type == "delete"):
            logging.info("Deleting scheduled command.")
            job_id = cmd_input_args.split(" ")[2]
            logging.debug("job_id: %s", str(job_id))
            if (not self.Scheduler.delete_scheduled_command(job_id)):
                logging.error("Something went wrong deleting a scheduled job!")
                print(colored("Something went wrong deleting a scheduled job!", "red"))
        # Not a valid command
        else:
            logging.warning("%s is not a valid schedule command type.", schedule_command_type)
            print(colored("%s is not a valid schedule command type." % (schedule_command_type), "red"))
        logging.info("Exit")

    def jar(self, cmd_input_args):
        """
        Performs any of the server jar related functions.\n
        To call in terminal:\n
        `jar copy 1.15.2`, `jar download 1.15.2`, etc.\n
        To call function in Python:\n
        `VanillaServerRunnerObject.jar("copy 1.15.2")`\n
        or\n
        `VanillaServerRunnerObject.jar(["copy", "1.15.2"])`\n
        Returns boolean if it was successful.
        """
        logging.info("Entry")
        # Turn into list for easier processing
        if isinstance(cmd_input_args, str):
            logging.info("Turning input from string into list.")
            cmd_input_args = cmd_input_args.split(" ")
            if len(cmd_input_args) < 2:
                print(cmd_input_args)
                logging.info("Exit")
                return False
            cmd_input_args = cmd_input_args[1::]
        # Check if passed in list is valid
        elif isinstance(cmd_input_args, list):
            if len(cmd_input_args) < 2:
                logging.info("Exit")
                return False
        # Didn't pass in valid object
        else:
            logging.error("Didn't pass in valid object.")
            logging.info("Exit")
            return False

        logging.debug("cmd_input_args: %s", cmd_input_args)

        # Check first argument if it's a valid command type
        valid_commands = ["set", "download", "update"]
        if not cmd_input_args[0] in valid_commands:
            logging.warning("Valid command type not passed in.")
            logging.info("Exit")
            return False
        
        # Check command type, pass off to function
        if cmd_input_args[0] == "set":
            return jar_set(self.server_dir, self.server_jars, cmd_input_args[1])
        elif cmd_input_args[0] == "download":
            succeded = jar_download(self.ServerDownloader, cmd_input_args[1])
            if succeded:
                self.server_jar_filename = os.path.join(self.server_dir, cmd_input_args[1] + ".jar")
            return succeded
        elif cmd_input_args[0] == "update":
            return jar_update(self.ServerDownloader)
        else:
            logging.warning("Valid command type not passed in.")
            logging.info("Exit")
            return False
        logging.info("Exit")

    def launch_options(self, cmd_input_args):
        """
        Handles running Launch Option functions and commands from terminal.
        """
        logging.info("Entry")
        # Turn into list for easier processing
        if isinstance(cmd_input_args, str):
            logging.info("Turning input from string into list.")
            cmd_input_args = cmd_input_args.split(" ")
            if len(cmd_input_args) < 2:
                logging.info("Exit")
                return False
            cmd_input_args = cmd_input_args[1::]
        # Check if passed in list is valid
        elif isinstance(cmd_input_args, list):
            if len(cmd_input_args) < 4:
                logging.info("Exit")
                return False
        # Didn't pass in valid object
        else:
            logging.error("Didn't pass in valid object.")
            logging.info("Exit")
            return False

        logging.debug("cmd_input_args: %s", cmd_input_args)

        # Check first argument if it's a valid command type
        valid_commands = ["list", "add", "delete"]
        if not cmd_input_args[0] in valid_commands:
            logging.warning("Valid command type not passed in.")
            logging.info("Exit")
            return False
        
        # Check if argument count matches each one
        if cmd_input_args[0] == "list" and len(cmd_input_args) == 1:
            self.LaunchOptionsHandler.read_options()
            loh_str = "%s\n%s\n%s\n%s" %    (  self.LaunchOptionsHandler.java_section, 
                                                self.LaunchOptionsHandler.java_options, 
                                                self.LaunchOptionsHandler.game_section, 
                                                self.LaunchOptionsHandler.game_options
                                            )
            logging.debug("Launch Options Handler String: %s", loh_str)
            print(loh_str)
        elif cmd_input_args[0] == "add" and len(cmd_input_args) == 3:
            option = cmd_input_args[1]
            is_java_option = bool(cmd_input_args[2])
            self.LaunchOptionsHandler.add_option(option, is_java_option)
        elif cmd_input_args[0] == "delete" and len(cmd_input_args) == 2:
            option = cmd_input_args[1]
            self.LaunchOptionsHandler.delete_option(option)
        else:
            logging.warning("Valid command type not passed in.")
            logging.info("Exit")
            return False

        logging.info("Exit")
        return True

    def server_properties(self, cmd_input_args):
        """
        Handles running Server Properties functions and commands from terminal.
        """
        logging.info("Entry")
        # Turn into list for easier processing
        if isinstance(cmd_input_args, str):
            logging.info("Turning input from string into list.")
            cmd_input_args = cmd_input_args.split(" ")
            if len(cmd_input_args) < 2:
                logging.info("Exit")
                return False
            cmd_input_args = cmd_input_args[1::]
        # Check if passed in list is valid
        elif isinstance(cmd_input_args, list):
            if len(cmd_input_args) < 4:
                logging.info("Exit")
                return False
        # Didn't pass in valid object
        else:
            logging.error("Didn't pass in valid object.")
            logging.info("Exit")
            return False

        logging.debug("cmd_input_args: %s", cmd_input_args)

        # Check first argument if it's a valid command type
        valid_commands = ["list", "set", "get"]
        if not cmd_input_args[0] in valid_commands:
            logging.warning("Valid command type not passed in.")
            logging.info("Exit")
            return False

        # Run each command
        if cmd_input_args[0] == "list" and len(cmd_input_args) < 2:
            print(self.ServerPropertiesHandler.read_server_properties_lines())
        elif cmd_input_args[0] == "set" and len(cmd_input_args) < 4:
            self.ServerPropertiesHandler.set_property(cmd_input_args[1], cmd_input_args[2])
        elif cmd_input_args[0] == "get" and len(cmd_input_args) < 3:
            print(self.ServerPropertiesHandler.get_property(cmd_input_args[1]))
        else:
            logging.warning("Valid command type not passed in.")
            logging.info("Exit")
            return False
        logging.info("Exit")
        return True

    def whitelist(self, cmd_input_args):
        """
        Handles running Whitelist functions and commands from terminal.
        """
        logging.info("Entry")
        # Turn into list for easier processing
        if isinstance(cmd_input_args, str):
            logging.info("Turning input from string into list.")
            cmd_input_args = cmd_input_args.split(" ")
            if len(cmd_input_args) < 2:
                logging.info("Exit")
                return False
            cmd_input_args = cmd_input_args[1::]
        # Check if passed in list is valid
        elif isinstance(cmd_input_args, list):
            if len(cmd_input_args) < 4:
                logging.info("Exit")
                return False
        # Didn't pass in valid object
        else:
            logging.error("Didn't pass in valid object.")
            logging.info("Exit")
            return False

        logging.debug("cmd_input_args: %s", cmd_input_args)

        # Check first argument if it's a valid command type
        valid_commands = ["get", "add", "delete"]
        if not cmd_input_args[0] in valid_commands:
            logging.info("Exit")
            return False

        # Run commands
        if cmd_input_args[0] == "get" and len(cmd_input_args) == 2:
            if cmd_input_args[1] == "players":
                print(self.WhitelistHandler.get_players())
            elif cmd_input_args[1] == "ids":
                print(self.WhitelistHandler.get_players_uuids())
            else:
                logging.error("Didn't pass in valid command type for get.")
                logging.info("Exit")
                return False
        elif cmd_input_args[0] == "add" and len(cmd_input_args) == 2:
            self.WhitelistHandler.add_player(cmd_input_args[1])
        elif cmd_input_args[0] == "delete" and len(cmd_input_args) == 2:
            self.WhitelistHandler.remove_player(cmd_input_args[1])
        else:
            logging.warning("Valid command type not passed in.")
            logging.info("Exit")
            return False
        
        logging.info("Exit")
        return True
