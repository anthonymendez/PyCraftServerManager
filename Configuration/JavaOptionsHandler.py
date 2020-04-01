import os
import configparser

class JavaOptionsHandler:
    """
    Java Option Handler handles modifiyng jar launch options.\n
    Loads and stores launch options from java_options.ini.
    """

    def __init__(self):
        """
        Initializes Java Options Handler
        """
        self.config = configparser.ConfigParser()
        self.config_file = "java_options.ini"
        self.config.read(self.config_file)
        self.category_booleans = "JAVA_BOOLEANS"
        self.category_numeric = "JAVA_NUMERIC"
        self.category_strings = "JAVA_STRINGS"
        self.category_others = []

    def __read_category(self, category):
        """
        Internal Function to return array of all values in a category.
        """
        return config[category]

    def read_boolean_options(self):
        """
        Returns array of all java boolean options in config file.
        """
        return self.__read_category(self.category_booleans)

    def read_numeric_options(self):
        """
        Returns array of all java numeric options in config file.
        """
        return self.__read_category(self.category_numeric)

    def read_strings_options(self):
        """
        Returns array of all java string options in config file.
        """
        return self.__read_category(self.category_strings)

    # TODO: Implement
    def get_formatted_options(self):
        """
        Returns string of formatted options for use when launching server jar.
        """
        return ""