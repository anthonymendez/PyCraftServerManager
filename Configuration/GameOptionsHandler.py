import os
import configparser

class GameOptionsHandler:
    """
    Game Option Handler handles modifiyng jar launch options.\n
    These are specific to the Minecraft Server Jar and not just any Java Jar.\n
    Loads and stores launch options from java_options.ini.
    """

    def __init__(self):
        """
        Initializes Java Options Handler
        """
        self.config = configparser.ConfigParser()
        self.config_file = "game_options.ini"
        self.config.read(self.config_file)
        self.category = "OPTIONS"

    def get_options(self):
        """
        Returns array of all vanilla options in config file.
        """
        return self.config[self.category]

    def get_option(self, option):
        """
        Returns value of vanilla option
        """
        return self.get_options()[option]

    # TODO: Implement
    def get_formatted_options(self):
        """
        Returns string of formatted options for use when launching server jar.
        """
        return ""