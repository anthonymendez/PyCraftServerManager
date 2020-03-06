import os

class VanillaServerRunner:
    """
    Server runner handles launching of Minecraft Server 
    jar, and configuring the launch parameters.\n
    TODO: Allow optional arguments for launch options (ram, nogui, etc.)
    """
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
        launch_str = ("""java -jar -Xms%s -Xmx%s %s %s""" % (
            self.get_ram_xms(),
            self.get_ram_xmx(),
            self.get_server_jar_filename(),
            "nogui" if self.get_nogui() else ""
        )).strip()
        # Run server with arguments
        os.system(launch_str)
        # Change directory to python project
        os.chdir(self.main_dir)

    def set_server_folder_relative(self, server_folder):
        """
        Set server folder and directory relative to main directory.\n
        Example inputs:\n
        \t\"../server/\" - Back one directory, then into server folder
        """
        self.server_folder = server_folder
        self.server_dir = os.path.join(self.main_dir, server_folder)

    def get_server_folder_directory(self):
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