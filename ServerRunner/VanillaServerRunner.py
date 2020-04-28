import os
import pexpect
import tarfile

# TODO Move to it's own module possibly
def is_windows():
    return os.name == "nt"

from threading import Thread
from time import sleep
from termcolor import colored
from pexpect import popen_spawn
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_LZMA, ZIP_BZIP2
from datetime import datetime
from Configuration.WhitelistHandler import WhitelistHandler
from Configuration.ServerPropertiesHandler import ServerPropertiesHandler
from Configuration.LaunchOptionsHandler import LaunchOptionsHandler
from Utilities.Scheduler import Scheduler

if is_windows():
    import colorama
    colorama.init()

class VanillaServerRunner:
    """
    Vanilla Server Runner handles launching of the Minecraft 
    Server jar, and configuring the launch parameters.
    """

    server_process = None
    input_thread = None
    output_thread = None

    def __init__(self, server_folder, *args, **kwargs):
        """
        Sets server folder location relative to python project.\n
        Example inputs:\n 
        \t\"../server/\" - Back one directory, then into server folder
        """
        # Handle optional arguments
        server_jar_filename = kwargs.get('server_jar_filename', "server.jar")
        # Set main directory of python project
        self.main_dir = os.getcwd()
        # Set server folder and server directory
        self.set_server_folder_relative(server_folder)
        # Set server jar filename
        self.set_server_jar_filename(server_jar_filename)
        # Set up commands array
        self.commands_functions_dict = {
            # Terminal Command: (fn pointer, argument count)
            "start": (self.start, 0), 
            "stop": (self.stop, 0), 
            "restart": (self.restart, 0), 
            "backup": (self.backup, 1),
            "exit": (self.exit, 0),
            "delete_user_cache": (self.delete_user_cache, 0),
            "schedule": (None, 0)
        }
        # Server Properties Handler
        self.ServerPropertiesHandler = ServerPropertiesHandler(self.main_dir, self.server_dir)
        # Whitelist Handler
        self.WhitelistHandler = WhitelistHandler(self.main_dir, self.server_dir)
        # Launch Options Handler
        self.LaunchOptionsHandler = LaunchOptionsHandler(self.main_dir, self.server_dir)
        # Scheduler Class
        self.scheduler = Scheduler(self.main_dir, self.server_dir, self.__input_handler)
        # Start up input thread
        self.stopping_all = False
        self.input_thread = Thread(target=self.__input_loop)
        self.input_thread.start()

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
        if is_windows():
            self.server_process = pexpect.popen_spawn.PopenSpawn(self.launch_str)
        # If OS is not windows, use pexpect.spawn as normal
        else:
            self.server_process = pexpect.spawn(self.launch_str)
        self.output_thread = Thread(target=self.__output_loop)
        sleep(0.1)
        self.output_thread.start()
        # Change directory to python project
        os.chdir(self.main_dir)

    def __stop(self):
        """
        Stop server along with output thread.
        """
        self.server_process.sendline("stop".encode("utf-8"))
        print(colored("Waiting for server process to die.", "green"))
        if is_windows():
            # Similar to below but for Windows since we don't have isalive for Popen_Spawn
            # From pexpect docs: pexpect.EOF is raised when EOF is read from a child. This usually means the child has exited.
            self.server_process.expect(pexpect.EOF)
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
        # Command to be sent to the server.jar
        elif cmd_input[0] == '/':
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
                    if args_required == 0:
                        fn()
                    elif len(cmd_input_args) - 1 == args_required:
                        fn(cmd_input_args[1::])
                    else:
                        print(colored("Argument count not matched. Required %d. Received %d." % (len(cmd_input_args) - 1, args_required), "red"))
            else:
                print(colored("Command not recognized", "red"))

    def __input_loop(self):
        """
        Handles incoming commands from the user.\n
        All commands prepended with "/" will be sent directly to the server.jar\n
        All other commands will be checked to see if they're supported by the program.
        """
        while not self.stopping_all:
            cmd_input = input(">")

            if isinstance(cmd_input, str):
                cmd_input = cmd_input.strip()
                self.__input_handler(cmd_input)
            else:
                self.server_process.sendline("stop".encode("utf-8"))
                self.server_process.terminate(force=True)
                break

    def __output_loop(self):
        while self.server_process is not None:
            try:
                output = self.server_process.readline().decode("utf-8").strip()
                if not len(output) == 0:
                    print("\b" + output + "\n>", end = "")
                elif not self.input_thread.isAlive():
                    self.server_process.sendline("stop".encode("utf-8"))
                    if self.server_process.isalive():
                        self.server_process.terminate(force=True)
                    break
            except pexpect.exceptions.TIMEOUT:
                print(colored("Output loop Timeout exception.", "red"))
                continue
            except Exception as e:
                print(colored("Output loop exception.", "red"))
                print(e)
                # if not self.server_process is None:
                #     self.stop()
                break

    def start(self):
        if self.server_process is None:
            print(colored("Starting server...", "green"))
            self.__run()
        else:
            print(colored("Server already running!", "yellow"))

    def stop(self):
        if self.server_process is None:
            print(colored("Server is not running!", "yellow"))
        else:
            print(colored("Stopping server...", "green"))
            self.__stop()

    def restart(self):
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
            print(colored("Restart process done!", "green"))

    def exit(self):
        self.stopping_all = True
        if not self.server_process is None:
            self.stop()

    def backup(self, cmd_input_args):
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
            print(colored("Invalid Backup Type passed in. Not backing up.", "red"))
            return
        print(colored("Backed up server files.", "green"))

    def delete_user_cache(self):
        if self.server_process is None:
            print(colored("Deleting user cache.", "green"))
            usercache_file = os.path.join(self.server_dir, "usercache.json")
            os.remove(usercache_file)
        else:
            print(colored("Server is running. Cannot delete user cache." % time_now, "red"))

    def set_server_folder_relative(self, server_folder):
        """
        Set server folder and directory relative to main directory.\n
        Example inputs:\n
        \t\"../server/\" - Back one directory, then into server folder
        """
        self.server_folder = server_folder
        self.server_dir = os.path.join(self.main_dir, server_folder)

    def set_server_jar_filename(self, server_jar_filename):
        """
        Set name of the server jar.\n
        Example inputs:\n
        \t\"server.jar\"
        """
        self.server_jar_filename = server_jar_filename

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
