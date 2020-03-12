import os
import pexpect
from threading import Thread
from time import sleep


class VanillaServerRunner:
    """
    Vanilla Server Runner handles launching of the Minecraft 
    Server jar, and configuring the launch parameters.
    """

    commands = ["restart", "backup"]

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

    def run(self):
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
        # Run server with arguments
        # os.system(launch_str)
        # self.server_process = subprocess.Popen(
        #     self.launch_str.split(" "),
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE,
        #     stdin=subprocess.PIPE,
        #     universal_newlines=True
        # )
        self.server_process = pexpect.spawn(self.launch_str)
        sleep(0.1)
        self.output_thread = Thread(target=self.output_loop)
        self.input_thread = Thread(target=self.input_loop)
        self.input_thread.start()
        sleep(0.1)
        self.output_thread.start()
        # Change directory to python project
        os.chdir(self.main_dir)

    def input_loop(self):
        while self.server_process is not None:
            cmd_input = input(">")

            if isinstance(cmd_input, str):
                cmd_input = cmd_input.strip()
                if len(cmd_input) == 0:
                    continue
                elif cmd_input[0] == '/':
                    if cmd_input[1::] in VanillaServerRunner.commands:
                        print("Command %s received!" % cmd_input[1::])
                    else:
                        print("Command not recognized")
                elif cmd_input == "stop":
                    self.server_process.sendline(cmd_input.encode("utf-8"))
                    break
                else:
                    self.server_process.sendline(cmd_input.encode("utf-8"))
            else:
                self.server_process.sendline("stop".encode("utf-8"))
                self.server_process.terminate(force=True)
                break

    def output_loop(self):
        while self.server_process is not None:
            try:
                output = self.server_process.readline().decode("utf-8").strip()
                if not len(output) == 0:
                    print(output)
                elif not self.input_thread.isAlive():
                    self.server_process.sendline("stop".encode("utf-8"))
                    self.server_process.terminate(force=True)
                    break
            except pexpect.exceptions.TIMEOUT as e_timeout:
                continue
            except Exception as e:
                print("Exception, stopping server.")
                print(e)
                self.server_process.sendline("stop".encode("utf-8"))
                self.server_process.terminate(force=True)
                break


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