from ..Utilities.Singleton import Singleton

import logging as log
logging = log.getLogger(__name__)

@Singleton
class InputHandler():
    """
    Input Handler handles accepting user input, or scheduled commands.

    Used Singleton decorator to ensure only one exists.
    """
    
    def __init__(self):
        """
        Initializes Input Handler.
        """
        logging.info("Entry")
        super().__init__()
        self.stopped = False
        self.__input_queue = []
        # TODO: Create thread for user input
        # TODO: Create thread to handle input queue
        logging.info("Exit")

    def __push_to_input_queue(self, input_to_handle):
        """
        Function to handle pushing items to the input queue.
        
        Does not push items if input handler is in the process of stopping.
        """
        logging.info("Entry")

        is_string = isinstance(input_to_handle, str)

        if not self.stopped and is_string:
            logging.debug("Appending to input queue.")
            self.__input_queue.append(input_to_handle)
        elif self.stopped:
            logging.debug("Input Handler is stopping, not appending.")
        else:
            logging.error("User input is not a string!")

        logging.info("Exit")

    def __user_input_loop(self):
        """
        Function to handle user input. Runs in it's own thread loop.
        """
        logging.info("Entry")

        while not self.stopped:
            # TODO: Figure out how to put input on bottom of terminal
            logging.info("Waiting on user input.")
            cmd_input = input()
            logging.info("User input %s", str(cmd_input))

            if not isinstance(cmd_input, str):
                logging.error("User input is not string!")
                continue

            logging.debug("Appending user input to input queue.")
            cmd_input = cmd_input.strip()
            self.__push_to_input_queue(cmd_input)

        logging.info("Exit")

    def __input_loop(self):
        """
        Handles processing input queue. Runs in it's own thread loop.
        """
        logging.info("Entry")

        is_input_queue_empty = len(self.__input_queue) == 0
        while not self.stopped or is_input_queue_empty:
            # Wait for input queue to not be empty
            while is_input_queue_empty:
                is_input_queue_empty = len(self.__input_queue) == 0
            
            # Get input at beginning of list and update is_empty bool
            command = self.__input_queue.pop(0)
            is_input_queue_empty = len(self.__input_queue) == 0
            logging.info("Handling \"%s\"", command)

            is_minecraft_command = command[0] == '/'
            is_specify_server = command[0:2] == "id" or command[0:4] == "name"
            # Check command type
            if is_minecraft_command:
                # Minecraft Command
                pass
            elif is_specify_server:
                # Specifys server to run command on
                command_list = command.split(" ")
                specifier = None
                is_name = "name" == command_list[0:4]
                is_id = "id" in command_list[0:2]
                if "=" in command_list[0]:
                    specifier = command_list[0].split("=")[1]
                    real_command = " ".join(command_list[1::])
                elif "=" in command_list[1]:
                    specifier = command_list[2]
                    real_command = " ".join(command_list[3::])
                else:
                    logging.error("Invalid specify server command.")
                    continue

                # Get serverrunner based on name or id
                server_runner = None
                if is_name:
                    # TODO: Search by server name
                    pass
                elif is_id:
                    # TODO: Search by server id
                    pass
                else:
                    # TODO: Error out, invalid specify server command
                    pass

                # TODO: Select server as current temporary server
                if server_runner is None:
                    logging.error("Server Runner not found.")
                    continue

                # TODO: Prepend list with command string
                self.__input_queue.insert(0, real_command)
                is_input_queue_empty = len(self.__input_queue) == 0 
            else:
                # PyCraftServerManager command
                pass

        logging.info("Exit")