import os

import logging as log
logging = log.getLogger(__name__)

class ServerPropertiesHandler:
    """
    Server Properties Handler handles launching of the setting
    and retrieval of server.properties file.
    """

    server_properties = "server.properties"

    # TODO: Store default values of server.properties in file
    def __init__(self, main_directory, server_directory):
        """
        Initializes Server Properties Handler by tying it to a Server Directory.
        """
        logging.info("Entry")
        self.main_directory = main_directory
        self.server_directory = server_directory
        logging.info("Exit")

    def read_server_properties_lines(self):
        """
        Reads all the lines from the server.properties file.
        """
        logging.info("Entry")
        server_properties_path = os.path.join(self.server_directory, ServerPropertiesHandler.server_properties)
        try:
            server_properties_file = open(server_properties_path, "r")
            server_properties_lines = server_properties_file.readlines()
            server_properties_file.close()
        except Exception as e:
            logging.error("Something went wrong with reading server properties. %s", str(e))
            logging.info("Exit")
            return None
        logging.info("Exit")
        return server_properties_lines

    def write_server_properties_lines(self, server_properties_lines):
        """
        Rewrites to all the lines of the server.properties file.
        """
        logging.info("Entry")
        server_properties_path = os.path.join(self.server_directory, ServerPropertiesHandler.server_properties)
        try:
            server_properties_file = open(server_properties_path, "w")
            server_properties_file.writelines(server_properties_lines)
            server_properties_file.close()
            logging.info("Exit")
            return True
        except Exception as e:
            logging.error("Something went wrong with writing to server properties. %s", str(e))
            logging.info("Exit")
            return False

    def set_property(self, property_name, value):
        """
        Sets a specific property value in server.properties.
        """
        logging.info("Entry")
        server_properties_lines = self.read_server_properties_lines()
        if server_properties_lines == None:
            logging.error("Server properties is empty. Not writing.")
            logging.info("Exit")
            return False
        i = 0
        found = False
        for line in server_properties_lines:
            if property_name in line:
                found = True
                break
            else:
                i += 1
        if found:
            server_properties_lines[i] = "%s=%s\n" % (property_name, str(value).lower())
            self.write_server_properties_lines(server_properties_lines)
            logging.info("Exit")
            return True
        else:
            logging.warning("Property not found. Not writing.")
            logging.info("Exit")
            return False
    
    def get_property(self, property_name):
        """
        Gets a specific property value in server.properties.
        """
        logging.info("Entry")
        server_properties_lines = self.read_server_properties_lines()
        if server_properties_lines == None:
            logging.warning("Server properties is empty. Not reading.")
            logging.info("Exit")
            return ""

        for line in server_properties_lines:
            if property_name in line:
                return line.split("=")[1].strip()
                break
            
        logging.info("Exit")
        return ""