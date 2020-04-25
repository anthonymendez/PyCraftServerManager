import os
import pexpect
from threading import Thread
from time import sleep
from termcolor import colored
from Configuration.WhitelistHandler import WhitelistHandler
from Configuration.ServerPropertiesHandler import ServerPropertiesHandler
from Configuration.GameOptionsHandler import GameOptionsHandler
from Configuration.JavaOptionsHandler import JavaOptionsHandler
from Configuration.LaunchOptionsHandler import LaunchOptionsHandler


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
        ram_xms_int = kwargs.get('ram_xms_int', "1")
        ram_xms_prefix_letter = kwargs.get('ram_xms_prefix_letter', "G")
        ram_xmx_int = kwargs.get('ram_xmx_int', "1")
        ram_xmx_prefix_letter = kwargs.get('ram_xmx_prefix_letter', "G")
        nogui_bool = kwargs.get('nogui_bool', True)
        # Set main directory of python project
        self.main_dir = os.getcwd()
        # Set server folder and server directory
        self.set_server_folder_relative(server_folder)
        # Set server jar filename
        self.set_server_jar_filename(server_jar_filename)
        # Set RAM amount
        self.set_ram_xms(ram_xms_int, ram_xms_prefix_letter)
        self.set_ram_xmx(ram_xmx_int, ram_xmx_prefix_letter)
        # Set where Java GUI displays
        self.set_nogui(nogui_bool)
        # Set up commands array
        self.commands_functions_dict = {
            "start": self.start, 
            "stop": self.stop, 
            "restart": self.restart, 
            "backup": None,
            "exit": self.exit
        }
        # Server Properties Handler
        self.ServerPropertiesHandler = ServerPropertiesHandler(self.main_dir, self.server_dir)
        # Whitelist Handler
        self.WhitelistHandler = WhitelistHandler(self.main_dir, self.server_dir)
        # Game Options Handler
        self.GameOptionsHandler = GameOptionsHandler()
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
        # Prepare launch String
        self.launch_str = ("""java -jar -Xms%s -Xmx%s %s %s""" % (
            self.get_ram_xms(),
            self.get_ram_xmx(),
            self.get_server_jar_filename(),
            "nogui" if self.get_nogui() else ""
        )).strip()
        # Spawn & Launch Server Terminal
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
        while True:
            if self.server_process is None or not self.server_process.isalive():
                break
        self.server_process = None
        while True:
            if self.output_thread is None or not self.output_thread.isAlive():
                break
        self.output_thread = None

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

                # Empty Input
                if len(cmd_input) == 0:
                    continue
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
                    if cmd_input in self.commands_dict:
                        print(colored("Command \"%s\" received!" % cmd_input, "green"))
                        fn = self.commands_functions_dict.get(cmd_input)
                        if fn is None:
                            print(colored("Command not programmed yet! Coming soon!", "yellow"))
                        else:
                            fn()
                    else:
                        print(colored("Command not recognized", "red"))
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
            except pexpect.exceptions.TIMEOUT as e_timeout:
                continue
            except Exception as e:
                # print(colored("Exception, stopping server.", "red"))
                # print(e)
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

    def set_server_folder_relative(self, server_folder):
        """
        Set server folder and directory relative to main directory.\n
        Example inputs:\n
        \t\"../server/\" - Back one directory, then into server folder
        """
        self.server_folder = server_folder
        self.server_dir = os.path.join(self.main_dir, server_folder)

    def get_server_directory(self):
        """
        Get server folder directory.
        """
        return self.server_dir

    def set_server_jar_filename(self, server_jar_filename):
        """
        Set name of the server jar.\n
        Example inputs:\n
        \t\"server.jar\"
        """
        self.server_jar_filename = server_jar_filename

    def get_server_jar_filename(self):
        """
        Get name of the server jar.
        """
        return self.server_jar_filename

    def set_ram_xms(self, ram_xms_int, ram_xms_prefix_letter):
        """
        Set amount of XMS RAM to use.\n
        Example inputs:\n 
        \t1024,\"M\" - 1024 Megabytes/1 Gigabyte\n
        \t2,\"G\" - 2 Gigabytes
        """
        self.ram_xms = str(int(ram_xms_int)) + ram_xms_prefix_letter

    def set_ram_xmx(self, ram_xmx_int, ram_xmx_prefix_letter):
        """
        Set amount of XMX RAM to use.\n
        Example inputs:\n 
        \t1024,\"M\" - 1024 Megabytes/1 Gigabyte\n
        \t2,\"G\" - 2 Gigabytes
        """
        self.ram_xmx = str(int(ram_xmx_int)) + ram_xmx_prefix_letter

    def get_ram_xms(self):
        """
        Get amount of XMS RAM server will use/is using.\n
        Example output:\n 
        \t\"1024M\" - 1024 Megabytes/1 Gigabyte\n
        \t\"2G\" - 2 Gigabytes
        """
        return self.ram_xms

    def get_ram_xmx(self):
        """
        Get amount of XMX RAM server will use/is using.\n
        Example output:\n 
        \t\"1024M\" - 1024 Megabytes/1 Gigabyte\n
        \t\"2G\" - 2 Gigabytes
        """
        return self.ram_xmx

    def set_nogui(self, nogui_bool):
        """
        Set whether server will launch with Java GUI.
        """
        self.nogui = nogui_bool

    def get_nogui(self):
        """
        Returns bool whether server will launch with Java GUI.
        """
        return self.nogui