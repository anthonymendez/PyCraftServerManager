import os

import logging as log
logging = log.getLogger(__name__)

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
        Also creates an empty string for Java and Game options.\n
        Reads in the options as well.
        """
        logging.info("Entry")
        self.main_directory = main_directory
        self.server_directory = server_directory
        self.java_options = []
        self.game_options = []
        self.read_options()
        logging.info("Exit")

    def read_options(self):
        """
        Goes through and reads the options for the game set java_options and game_options strings.
        """
        logging.info("Entry")
        # Open launch.properties and read in all the lines
        launch_properties_path = os.path.join(self.main_directory, LaunchOptionsHandler.launch_properties)
        # If file does not exist, create it.
        if not os.path.exists(launch_properties_path):
            launch_properties_file = open(launch_properties_path, "w")
            lines = [self.java_section + "\n", self.game_section + "\n"]
            launch_properties_file.writelines(lines)
            launch_properties_file.close()
            logging.info("File does not exist. Created.")
        else:
            launch_properties_file = open(launch_properties_path, "r")
            launch_properties_lines = launch_properties_file.readlines()
            launch_properties_file.close()
            logging.info("File exists. Read.")
        # Clear out java and game options array
        self.java_options.clear()
        self.game_options.clear()
        # If i = 0, haven't hit a section header
        # If i = 1, hit JAVA section header
        # If i = 2, hit GAME section header
        i = 0
        for line in launch_properties_lines:

            # Trim and check if it's empty
            line = line.strip()
            if line == "":
                continue

            logging.debug("Line Before: \"%s\"", line)

            if line == LaunchOptionsHandler.java_section or line == LaunchOptionsHandler.game_section:
                i += 1
                continue

            # Check if it's prepended with dashes
            # If not, prepend with dashes
            if i == 1:
                if not line[0] == "-":
                    line = "-" + line
            elif i == 2:
                while not line[0:2] == "--":
                    line = "-" + line

            logging.debug("Line After: \"%s\"", line)

            # Add to the appropriate option string
            if i == 1:
                logging.info("Adding to Java Options.")
                self.java_options.append(line)
            elif i == 2:
                logging.info("Adding to Game Options")
                self.game_options.append(line)
        logging.info("Exit")

    def add_option(self, option, is_java_option):
        """
        Adds a new option to the launch_properties.\n
        If is_java_option is true, adds new option under JAVA section.\n
        Otherwise, adds new option under GAME section.\n
        NOTE: Function will not perform error checking for valid option or format. It will only prepend with dashes. YOU need to check if the option is valid yourself.
        Returns a boolean saying whether or not it was successfully inserted.
        """
        logging.info("Entry")
        # TODO: Add check to see if option was already added
        # Open launch.properties and read in all the lines
        launch_properties_path = os.path.join(self.main_directory, LaunchOptionsHandler.launch_properties)
        launch_properties_file = open(launch_properties_path, "r")        
        launch_properties_lines = launch_properties_file.readlines()
        launch_properties_file.close()

        logging.debug("Option Before: %s", option)

        # Check if option is prepended with dashes
        # If it is not, prepend with dashes
        if is_java_option:
            if not option[0] == '-':
                option = '-' + option
        else:
            while not option[0:2] == '--':
                option = '-' + option

        logging.debug("Option After: %s", option)

        # Append new line
        option = option + "\n"

        # Check if the option is in any of lines, if so, we just return true
        if option in launch_properties_lines:
            logging.info("Option already in launch properties.")
            logging.info("Exit")
            return True

        # If not a Java option, we can just add it to the end of the lines
        # Otherwise, we have to find the index of [GAME] and insert it there
        inserted = False
        if is_java_option:
            for i, line in enumerate(launch_properties_lines):
                # Trim and check if it's empty
                line = line.strip()
                if line == "":
                    continue

                if line == LaunchOptionsHandler.game_section:
                    launch_properties_lines.insert(i, option)
                    inserted = True
                    logging.debug("Inserted option.")
                    break
        else:
            launch_properties_lines.append(option)
            logging.debug("Appended option.")
            inserted = True

        # Reopen launch.properties and write the modified lines
        if inserted:
            launch_properties_path = os.path.join(self.main_directory, LaunchOptionsHandler.launch_properties)
            launch_properties_file = open(launch_properties_path, "w")        
            launch_properties_file.writelines(launch_properties_lines)
            launch_properties_file.close()
            self.read_options()
            logging.debug("Wrote changed option.")

        logging.info("Exit")
        return inserted

    def delete_option(self, option):
        """
        Deletes an option from launch_properties.\n
        You can specify an option with, or without dashes prepended. It will be stripped from the option for comparison either way.\n
        NOTE: Function will not perform error checking for valid option or format. It will only prepend with dashes. YOU need to check if the option is valid yourself.\n
        Returns a boolean saying whether or not it was successfully deleted.
        """
        logging.info("Entry")
        
        logging.debug("Option Before: %s", option)

        # Strip option of dashes if it has any
        while option[0] == '-':
            option = option[1::]

        logging.debug("Option After: %s", option)

        # Open launch.properties and read in all the lines
        launch_properties_path = os.path.join(self.main_directory, LaunchOptionsHandler.launch_properties)
        launch_properties_file = open(launch_properties_path, "r")        
        launch_properties_lines = launch_properties_file.readlines()
        launch_properties_file.close()

        # Iterate through the lines until we find the option specified
        deleted = False
        for i, line in enumerate(launch_properties_lines):
            # Trim and check if it's empty
            line = line.strip()
            if line == "":
                continue

            # Strip line of dashes
            while line[0] == '-':
                line = line[1::]

            # Check if it matches option
            # If so, remove it from the lines array and set found to true
            if option == line:
                launch_properties_lines.pop(i)
                deleted = True
                logging.debug("Deleted option.")
                break

        # Reopen launch.properties and write the modified lines
        if deleted:
            launch_properties_path = os.path.join(self.main_directory, LaunchOptionsHandler.launch_properties)
            launch_properties_file = open(launch_properties_path, "w")        
            launch_properties_file.writelines(launch_properties_lines)
            launch_properties_file.close()
            logging.debug("Wrote deleted option.")
            self.read_options()

        return deleted
