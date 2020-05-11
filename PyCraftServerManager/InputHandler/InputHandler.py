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
            input_current = self.__input_queue.pop(0)
            is_input_queue_empty = len(self.__input_queue) == 0
            logging.info("Handling \"%s\"", input_current)

            is_minecraft_command = input_current[0] == '/'
            is_specify_server = input_current[0:2] == "id" or input_current[0:4] == "name"
            # Check command type
            if is_minecraft_command:
                # Minecraft Command
                pass
            elif is_specify_server:
                # Specifys server to run command on
                pass
            else:
                # PyCraftServerManager command
                pass

        logging.info("Exit")