import os

class ServerPropertiesHandler:
    """
    Server Properties Handler handles launching of the setting
    and retrieval of server.properties file.
    """

    server_properties = "server.properties"

    # TODO: Store default values of server.properties in file
    def __init__(self, main_directory, server_director):
        """
        Initializes Server Properties Handler by tying it to a Server Directory.
        """
        self.main_directory = main_directory
        self.server_directory = server_director

    def __read_server_properties_lines(self):
        """
        Reads all the lines from the server.properties file.
        """
        server_properties_path = os.path.join(self.server_directory, ServerPropertiesHandler.server_properties)
        server_properties_file = open(server_properties_path, "r")
        server_properties_lines = server_properties_file.readlines()
        server_properties_file.close()
        return server_properties_lines

    def __write_server_properties_lines(self, server_properties_lines):
        """
        Rewrites to all the lines of the server.properties file.
        """
        server_properties_path = os.path.join(self.server_directory, ServerPropertiesHandler.server_properties)
        server_properties_file = open(server_properties_path, "w")
        server_properties_file.writelines(server_properties_lines)
        server_properties_file.close()

    def set_property(self, property_name, value):
        """
        Sets a specific property value in server.properties.
        """
        server_properties_lines = self.__read_server_properties_lines()
        i = 0
        for line in server_properties_lines:
            if property_name in line:
                break
            else:
                i += 1
        server_properties_lines[i] = "%s=%s\n" % (property_name, str(value).lower())
        self.__write_server_properties_lines(server_properties_lines)
    
    def get_property(self, property_name):
        """
        Gets a specific property value in server.properties.
        """
        server_properties_lines = self.__read_server_properties_lines()
        for line in server_properties_lines:
            if property_name in line:
                return line.split("=")[1].strip()
                break
        return ""
