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
        self.section_boolean = "BOOLEAN_OPTIONS"
        self.section_string = "STRING_OPTIONS"
        # Initialize Typical Game Options value
        if not self.config.has_section(self.section_boolean):
            self.enable_boolean_option("nogui")

    def __write(self):
        """
        Saves changes into config_file.
        """
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def __set_section_option(self, section, option, value):
        """
        Sets option with given value.
        """
        self.config[section][option] = value
        self.__write()

    def get_boolean_option_value(self, option):
        """
        Gets boolean option value.
        """
        return self.config[self.section_boolean][option]

    def get_string_option_value(self, option):
        """
        Gets string option value.
        """
        return self.config[self.section_string][option]

    def get_boolean_options(self):
        """
        Gets boolean options.
        """
        return self.config.options(self.section_boolean)

    def get_string_options(self):
        """
        Gets string options.
        """
        return self.config.options(self.section_string)

    def enable_boolean_option(self, option):
        """
        Enable boolean option.
        """
        self.__set_section_option(self.section_boolean, option, str(True))

    def disable_boolean_option(self, option):
        """
        Disable boolean option.
        """
        self.__set_section_option(self.section_boolean, option, str(False))

    def set_string_option(self, option, value):
        """
        Set string option.
        """
        self.__set_section_option(self.section_string, option, value)

    def disable_string_option(self, option):
        """
        Disables a string option.
        """
        self.__set_section_option(self.section_string, option, "")

    def get_formatted_game_options(self):
        """
        Returns string of formatted options for use when launching server jar.\n
        NOTE: Goes after server.jar in launch argument.
        """
        # Add Boolean Options first
        if self.config.has_section(self.section_boolean):
            options = self.get_boolean_options()
            formatted_options = ""
            for option in options:
                if not self.get_boolean_option_value(option):
                    continue
                formatted_options = formatted_options + ("--%s " % option)
        # Add String Options next
        if self.config.has_section(self.section_string):
            options = self.get_string_options()
            for option in options:
                if self.get_string_option_value(option) == "":
                    continue
                formatted_options = formatted_options + ("--%s %s " % option, self.get_string_option_value(option))
        # Return formatted string
        return formatted_options.strip()
