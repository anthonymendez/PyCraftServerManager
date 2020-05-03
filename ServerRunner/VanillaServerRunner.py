import os
import pexpect
import tarfile
import re
import logging

# TODO Move to it's own module possibly
def is_windows():
    return os.name == "nt"

from threading import Thread, Lock
from time import sleep
from termcolor import colored
from pexpect import popen_spawn
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_LZMA, ZIP_BZIP2
from datetime import datetime
from shutil import copy
from Configuration.WhitelistHandler import WhitelistHandler
from Configuration.ServerPropertiesHandler import ServerPropertiesHandler
from Configuration.LaunchOptionsHandler import LaunchOptionsHandler
from Utilities.Scheduler import Scheduler
from ServerDownloader.VanillaServerDownloader import VanillaServerDownloader

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
        # Set up Logging
        time_now = str(datetime.now()).replace(" ", ".")
        time_now = time_now.replace("-", ".")
        time_now = time_now.replace(":", ".")
        logging.basicConfig(format="%(asctime)s - %(filename)s - %(name)s - %(levelname)s - %(message)s", 
                            filename=("pycraft_%s.log" % time_now), 
                            level=logging.DEBUG)
        logging.info("VanillaServerRunner Entry")
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
        self.VanillaServerDownloader = VanillaServerDownloader(self.main_directory, self.server_dir, self.server_jars)
        # Server Properties Handler
        self.ServerPropertiesHandler = ServerPropertiesHandler(self.main_directory, self.server_dir)
        # Whitelist Handler
        self.WhitelistHandler = WhitelistHandler(self.main_directory, self.server_dir)
        # Launch Options Handler
        self.LaunchOptionsHandler = LaunchOptionsHandler(self.main_directory, self.server_dir)
        # Scheduler Class
        self.Scheduler = Scheduler(self.main_directory, self.server_dir, self.__input_handler)
        # Enable Eula
        self.__enable_eula()
        # Start up input thread
        self.input_handler_lock = Lock()
        self.stopping_all = False
        self.input_thread = Thread(target=self.__input_loop)
        self.input_thread.start()
        self.server_process_eof = True

    def __run(self):
        """
        Start server with options set in ServerRunner.
        """
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
        # Spawn & Launch Server Terminal
        # Check if OS is windows. If so, use pexpect.popen_spawn.PopenSpawn
        self.server_process_eof = False
        if is_windows():
            self.server_process = pexpect.popen_spawn.PopenSpawn(self.launch_str)
        # If OS is not windows, use pexpect.spawn as normal
        else:
            self.server_process = pexpect.spawn(self.launch_str)
        self.output_thread = Thread(target=self.__output_loop)
        sleep(0.1)
        self.output_thread.start()
        # Watching server process
        self.server_process_watch = Thread(target=self.__server_process_wait)
        self.server_process_watch.start()
        # Change directory to python project
        os.chdir(self.main_directory)

    def __stop(self):
        """
        Stop server along with output thread.
        """
        try:
            self.server_process.sendline("stop".encode("utf-8"))
        except Exception as e:
            pass
        print(colored("Waiting for server process to die.", "green"))
        if is_windows():
            # Similar to below but for Windows since we don't have isalive for Popen_Spawn
            # From pexpect docs: pexpect.EOF is raised when EOF is read from a child. This usually means the child has exited.
            self.server_process.wait()
        else:
            # Check if pexpect.spawn is still alive
            while True:
                if self.server_process is None and not self.server_process.isalive():
                    break
        self.server_process = None
        print(colored("Server process dead (hopefully). Waiting for output thread to die.", "green"))
        while True:
            if self.output_thread is None or not self.output_thread.isAlive():
                break
        self.output_thread = None
        print(colored("Output thread dead. Server officially stopped.", "green"))

    def __input_handler(self, cmd_input):
        """
        Handles input given by input thread/command line or a scheduled command
        """
        # TODO: Setup mutex for this function
        # Empty Input
        if len(cmd_input) == 0:
            return

        # Lock function
        # https://stackoverflow.com/a/10525433/12464369
        with self.input_handler_lock:
            # Command to be sent to the server.jar
            if cmd_input[0] == '/':
                if not self.server_process is None:
                    cmd_input_after_slash = cmd_input[1::]
                    print(cmd_input_after_slash)
                    print(colored("Sending command to %s server... " % cmd_input_after_slash, "green"))
                    self.server_process.sendline(cmd_input_after_slash.encode("utf-8"))
                else:
                    print(colored("Server has not started! Start server with \"start\" to start the server!", "red"))
            # Command to be handled by ServerRunner
            else:
                cmd_input_args = cmd_input.split(" ")
                command = cmd_input_args[0]
                if command in self.commands_functions_dict:
                    print(colored("Command \"%s\" received!" % cmd_input, "green"))
                    fn = self.commands_functions_dict.get(command)[0]
                    if fn is None:
                        print(colored("Command not programmed yet! Coming soon!", "yellow"))
                    else:
                        args_required = self.commands_functions_dict.get(command)[1]
                        if args_required == -1:
                            fn_return = fn(cmd_input)
                        elif args_required == 0:
                            fn_return = fn()
                        elif len(cmd_input_args) - 1 == args_required:
                            fn_return = fn(cmd_input_args[1::])
                        else:
                            print(colored("Argument count not matched. Required %d. Received %d." % (len(cmd_input_args) - 1, args_required), "red"))

                        # Check what function returned if it did return anything
                        if isinstance(fn_return, bool):
                            if not fn_return:
                                print(colored("Command \"%s\" did not run successfully." % cmd_input, "red"))
                else:
                    print(colored("Command not recognized", "red"))

    def __input_loop(self):
        """
        Handles incoming commands from the user.\n
        All commands prepended with "/" will be sent directly to the server.jar\n
        All other commands will be checked to see if they're supported by the program.
        """
        while not self.stopping_all:
            # TODO: Figure out how to put input on bottom of terminal always
            cmd_input = input()

            if isinstance(cmd_input, str):
                cmd_input = cmd_input.strip()
                self.__input_handler(cmd_input)
            else:
                self.server_process.sendline("stop".encode("utf-8"))
                self.server_process.terminate(force=True)
                break

    def __output_loop(self):
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
        print(colored("Server Process stopped", "yellow"))

    def __server_process_wait(self):
        # TODO: Possible Windows Compatibility thing?
        self.server_process.wait()
        self.server_process_eof = True

    def start(self):
        """
        Starts the server. If it is already started, does nothing.
        """
        if self.server_process is None:
            print(colored("Starting server...", "green"))
            self.__run()
        else:
            print(colored("Server already running!", "yellow"))

    def stop(self):
        """
        Stops the server. If it is already stopped, does nothing.
        """
        if self.server_process is None:
            print(colored("Server is not running!", "yellow"))
        else:
            print(colored("Stopping server...", "green"))
            self.__stop()

    def restart(self):
        """
        Restarts the server if it is running. Does nothing if server isn't running.
        """
        if self.server_process is None:
            print(colored("Server is not running!", "yellow"))
        else:
            self.stop()
            print(colored("Waiting for server to stop...", "yellow"))
            while(1):
                sleep(1)
                if (self.server_process is None):
                    break
            self.start()
            print(colored("Restart process done! Wait for server to start!", "green"))

    def exit(self):
        """
        Stops server if it's running and quits program.
        """
        self.stopping_all = True
        if not self.server_process is None:
            self.stop()

    def backup(self, cmd_input_args):
        """
        Backs up server folder into a tar or zip archive.\n
        Places archive folder into backups folder.\n
        Terminal calls command like so"\n
        `backup tar` or `backup zip`\n
        """
        # Check if it's just a string. Hacky bug fix for Scheduler calling.
        if isinstance(cmd_input_args, str):
            cmd_input_args = [cmd_input_args]
        # Extract type of Backup from input args and create enum
        backup_type = cmd_input_args[0].lower()
        
        # Create name for archive based on time space
        time_now = str(datetime.now()).replace(" ", ".")
        time_now = time_now.replace("-", ".")
        time_now = time_now.replace(":", ".")
        print(colored("Compressed archive file name: %s" % time_now, "green"))

        # Create folder to store backups
        backup_path = os.path.abspath("backups")
        if not os.path.exists(backup_path):
            os.mkdir(backup_path)
        # Archive Path to store compressed server folder
        archive_path = os.path.join(backup_path, time_now)
        if backup_type == "zip":
            self.__backup_as_zip(archive_path + ".zip")
        elif backup_type == "tar":
            self.__backup_as_tar(archive_path + ".tar.gz")
        else:
            print(colored("Invalid Backup Type of \"%s\" passed in. Not backing up." % backup_type, "red"))
            return
        print(colored("Backed up server files.", "green"))

    def delete_user_cache(self):
        """
        Deletes usercache.json in server folder if server is not running.\n
        Does nothing if server is not running.
        """
        if self.server_process is None:
            print(colored("Deleting user cache.", "green"))
            usercache_file = os.path.join(self.server_dir, "usercache.json")
            os.remove(usercache_file)
        else:
            print(colored("Server is running. Cannot delete user cache." % time_now, "red"))

    def schedule(self, cmd_input_args):
        # Check what type of schedule command it is
        schedule_command_type = cmd_input_args.split(" ")[1]
        # Add new scheduled command
        if (schedule_command_type == "add"):
            # Extract command and cron string
            # https://stackoverflow.com/a/2076356/12464369
            cmd_inputs_args_quoted = re.findall('"([^"]*)"', cmd_input_args)
            command = cmd_inputs_args_quoted[0]
            cron = cmd_inputs_args_quoted[1]
            print(cmd_inputs_args_quoted)
            # Create scheduled command
            if (self.Scheduler.add_scheduled_command(command, cron)):
                print(colored("Command successfully scheduled!", "green"))
            else:
                print(colored("Command not scheduled!", "red"))
        # List all scheduled commands
        elif (schedule_command_type == "list"):
            if (not self.Scheduler.list_scheduled_commands()):
                print(colored("Something went wrong listing scheduled jobs!", "red"))
        # Delete command
        elif (schedule_command_type == "delete"):
            job_id = cmd_input_args.split(" ")[2]
            if (not self.Scheduler.delete_scheduled_command(job_id)):
                print(colored("Something went wrong deleting a scheduled job!", "red"))
        # Not a valid command
        else:
            print(colored("%s is not a valid schedule command type." % (schedule_command_type), "red"))

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
        # Turn into list for easier processing
        if isinstance(cmd_input_args, str):
            cmd_input_args = cmd_input_args.split(" ")
            if len(cmd_input_args) < 2:
                print(cmd_input_args)
                return False
            cmd_input_args = cmd_input_args[1::]
        # Check if passed in list is valid
        elif isinstance(cmd_input_args, list):
            if len(cmd_input_args) < 2:
                return False
        # Didn't pass in valid object
        else:
            return False

        # Check first argument if it's a valid command type
        valid_commands = ["set", "download", "update"]
        if not cmd_input_args[0] in valid_commands:
            return False
        
        # Check command type, pass off to function
        if cmd_input_args[0] == "set":
            return self.__jar_set(cmd_input_args[1])
        elif cmd_input_args[0] == "download":
            return self.__jar_download(cmd_input_args[1])
        elif cmd_input_args[0] == "update":
            return self.__jar_update()
        else:
            return False

    def launch_options(self, cmd_input_args):
        """
        Handles running Launch Option functions and commands from terminal.
        """
        # Turn into list for easier processing
        if isinstance(cmd_input_args, str):
            cmd_input_args = cmd_input_args.split(" ")
            if len(cmd_input_args) < 2:
                print(cmd_input_args)
                return False
            cmd_input_args = cmd_input_args[1::]
        # Check if passed in list is valid
        elif isinstance(cmd_input_args, list):
            if len(cmd_input_args) < 4:
                return False
        # Didn't pass in valid object
        else:
            return False

        # Check first argument if it's a valid command type
        valid_commands = ["list", "add", "delete"]
        if not cmd_input_args[0] in valid_commands:
            return False
        
        # Check if argument count matches each one
        if cmd_input_args[0] == "list" and len(cmd_input_args) == 1:
            self.LaunchOptionsHandler.read_options()
            print("""%s\n%s\n%s\n%s""" % 
                    (   self.LaunchOptionsHandler.java_section,
                        self.LaunchOptionsHandler.java_options,
                        self.LaunchOptionsHandler.game_section,
                        self.LaunchOptionsHandler.game_options
                    )
                )
        elif cmd_input_args[0] == "add" and len(cmd_input_args) == 3:
            option = cmd_input_args[1]
            is_java_option = bool(cmd_input_args[2])
            self.LaunchOptionsHandler.add_option(option, is_java_option)
        elif cmd_input_args[0] == "delete" and len(cmd_input_args) == 2:
            option = cmd_input_args[1]
            self.LaunchOptionsHandler.delete_option(option)
        else:
            return False

        return True

    def server_properties(self, cmd_input_args):
        """
        Handles running Server Properties functions and commands from terminal.
        """
        # Turn into list for easier processing
        if isinstance(cmd_input_args, str):
            cmd_input_args = cmd_input_args.split(" ")
            if len(cmd_input_args) < 2:
                print(cmd_input_args)
                return False
            cmd_input_args = cmd_input_args[1::]
        # Check if passed in list is valid
        elif isinstance(cmd_input_args, list):
            if len(cmd_input_args) < 4:
                return False
        # Didn't pass in valid object
        else:
            return False

        # Check first argument if it's a valid command type
        valid_commands = ["list", "set", "get"]
        if not cmd_input_args[0] in valid_commands:
            return False

        # Run each command
        if cmd_input_args[0] == "list" and len(cmd_input_args) < 2:
            print(self.ServerPropertiesHandler.read_server_properties_lines())
        elif cmd_input_args[0] == "set" and len(cmd_input_args) < 4:
            self.ServerPropertiesHandler.set_property(cmd_input_args[1], cmd_input_args[2])
        elif cmd_input_args[0] == "get" and len(cmd_input_args) < 3:
            print(self.ServerPropertiesHandler.get_property(cmd_input_args[1]))
        else:
            return False
        return True

    def whitelist(self, cmd_input_args):
        """
        Handles running Whitelist functions and commands from terminal.
        """
        # Turn into list for easier processing
        if isinstance(cmd_input_args, str):
            cmd_input_args = cmd_input_args.split(" ")
            if len(cmd_input_args) < 2:
                print(cmd_input_args)
                return False
            cmd_input_args = cmd_input_args[1::]
        # Check if passed in list is valid
        elif isinstance(cmd_input_args, list):
            if len(cmd_input_args) < 4:
                return False
        # Didn't pass in valid object
        else:
            return False

        # Check first argument if it's a valid command type
        valid_commands = ["get", "add", "delete"]
        if not cmd_input_args[0] in valid_commands:
            return False

        # Run commands
        if cmd_input_args[0] == "get" and len(cmd_input_args) == 2:
            if cmd_input_args[1] == "players":
                print(self.WhitelistHandler.get_players())
            elif cmd_input_args[1] == "ids":
                print(self.WhitelistHandler.get_players_uuids())
            else:
                return False
        elif cmd_input_args[0] == "add" and len(cmd_input_args) == 2:
            self.WhitelistHandler.add_player(cmd_input_args[1])
        elif cmd_input_args[0] == "remove" and len(cmd_input_args) == 2:
            self.WhitelistHandler.remove_player(cmd_input_args[1])
        else:
            return False
        
        return True

    def __backup_as_zip(self, archive_path):
        """
        Backs up Server folder into a ZIP archive using LZMA compression.
        """
        server_zip = ZipFile(archive_path, "w", ZIP_LZMA)
        print(colored("Zip file created. Backing up server files.", "green"))
        os.chdir(self.server_dir)
        for folder_name, subfolders, file_names in os.walk(self.server_dir):
            for file_name in file_names:
                # Create complete filepath of file in directory
                file_path = os.path.join(folder_name, file_name)
                # Add file to zip
                server_zip.write(file_path)

    def __backup_as_tar(self, archive_path):
        """
        Backs up Server folder into a compressed tar file.
        """
        print(colored("Creating and compressing tar file.", "green"))
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(".", arcname=os.path.basename(self.server_dir))

    def __jar_set(self, jar):
        """
        Sets specified jar to use in server folder.\n
        Checks if jar exists in server_jars folder.\n
        If so, copies to server folder and sets jar.\n
        Otherwise, returns False.\n
        Removes any other jar files in th server folder.\n
        Run in terminal like so:\n
        `jar set 1.15.2`\n
        Returns boolean if it was successful.
        """
        # Check if file exists
        jar_path = os.path.join(self.server_jars, jar + ".jar")
        if not os.path.isfile(jar_path):
            return False

        # Remove all .jar files in server directory
        server_dir_files = os.listdir(self.server_dir)
        for s_d_file in server_dir_files:
            if s_d_file.endswith(".jar"):
                os.remove(os.path.join(self.server_dir, s_d_file))

        # Copy file to server directory
        to_copy_path = os.path.join(self.server_dir, jar + ".jar")
        try:
            copy(jar_path, to_copy_path)
        except Exception as e:
            print(e)
            return False
       
        # Set server jar 
        self.server_jar_filename = to_copy_path
        return True        

    def __jar_download(self, version):
        """
        Downloads specified server jar in server backups folder.\n
        Run in terminal like so:\n
        `jar download 1.15.2`\n
        Returns boolean if it was successful.
        """
        success = self.VanillaServerDownloader.download_server_jar(version)
        return success

    def __jar_update(self):
        """
        Updates the local download link database of server jars.\n
        Run in terminal like so:\n
        `jar update`\n
        Returns boolean if it was successful.
        """
        success = self.VanillaServerDownloader.parse_mojang_download_links()
        return success

    def __enable_eula(self):
        """
        Enables eula in eula.txt.
        """
        # Check if it exists
        eula_path = os.path.join(self.server_dir, "eula.txt")
        if not os.path.isfile(eula_path):
            # Create eula.txt
            try:
                open(eula_path, "w").write("eula=true")
                return True
            except Exception as e:
                return False

        # If it does exist, just write eula=true
        try:
            open(eula_path, "w").write("eula=true")
            return True
        except Exception as e:
            return False