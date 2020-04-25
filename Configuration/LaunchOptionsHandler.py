import os

class LaunchOptionsHandler:
    """
    Handles creating Java Option and Game Options string when launching the server jar.
    """

    launch_properties = "launch.properties"
    java_section = "[JAVA]"
    game_section = "[GAME]"

    def __init__(self, main_directory, server_directory):
        """
        Initializes Launch Properties Handler by tying it to a server directory.\n
        Also creates an empty string for Java and Game options.
        """
        self.main_directory = main_directory
        self.server_directory = server_directory
        self.java_options = []
        self.game_options = []

    def read_options(self):
        """
        Goes through and reads the options for the game set java_options and game_options strings.
        """
        launch_properties_path = os.path.join(self.server_directory, LaunchOptionsHandler.launch_properties)
        launch_properties_file = open(launch_properties_path, "r")
        launch_properties_lines = launch_properties_file.readlines()
        launch_properties_file.close()
        # If i = 0, haven't hit a section header
        # If i = 1, hit JAVA section header
        # If i = 2, hit GAME section header
        i = 0
        for line in launch_properties_lines:
            if line == LaunchOptionsHandler.java_section or line == LaunchOptionsHandler.game_section:
                i += 1
                continue

            # Trim and check if it's empty
            line = line.strip()
            if line == "":
                continue

            # Check if it's prepended with dashes
            # If not, prepend with dashes
            if i == 1:
                if not line[0] == '-':
                    line = '-' + line
            elif i == 2:
                while not line[0:2] == '--':
                    line = '-' + line
            
            # Add to the appropriate option string
            if i == 1:
                self.java_options.append(line)
            elif i == 2:
                self.game_options.append(line)