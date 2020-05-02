import os

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
        self.main_directory = main_directory
        self.server_directory = server_directory

    def read_server_properties_lines(self):
        """
        Reads all the lines from the server.properties file.
        """
        server_properties_path = os.path.join(self.server_directory, ServerPropertiesHandler.server_properties)
        try:
            server_properties_file = open(server_properties_path, "r")
            server_properties_lines = server_properties_file.readlines()
            server_properties_file.close()
        except Exception as e:
            print(e)
            return None
        return server_properties_lines

    def write_server_properties_lines(self, server_properties_lines):
        """
        Rewrites to all the lines of the server.properties file.
        """
        server_properties_path = os.path.join(self.server_directory, ServerPropertiesHandler.server_properties)
        try:
            server_properties_file = open(server_properties_path, "w")
            server_properties_file.writelines(server_properties_lines)
            server_properties_file.close()
            return True
        except Exception as e:
            print(e)
            return False

    def set_property(self, property_name, value):
        """
        Sets a specific property value in server.properties.
        """
        server_properties_lines = self.read_server_properties_lines()
        if server_properties_lines == None:
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
            return True
        else:
            return False
    
    def get_property(self, property_name):
        """
        Gets a specific property value in server.properties.
        """
        server_properties_lines = self.read_server_properties_lines()
        if server_properties_lines == None:
            return ""

        for line in server_properties_lines:
            if property_name in line:
                return line.split("=")[1].strip()
                break
        return ""
