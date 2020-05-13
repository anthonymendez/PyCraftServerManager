import os
import re

from termcolor import colored
from ..Utilities.Singleton import Singleton

# TODO Move to it's own module possibly
def is_windows():
    return os.name == "nt"

if is_windows():
    import colorama
    colorama.init()

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
        self.default_server_runner = None
        self.temp_server_runner = None
        # Lookup dictionaries for server runners by names
        self.name_to_server = {}
        self.id_to_server = {}
        # Set main directory of python project
        self.main_directory = os.getcwd()
        # Set up commands array
        self.commands_functions_dict = {
            # Terminal Command: (fn pointer, argument count)
            "exit": (self.exit, 0),
            "schedule": (self.schedule, -1)
        }
        # Scheduler Class TODO: Redo class for InputHandler
        self.Scheduler = Scheduler(self.main_directory, self.server_dir, self.__push_to_input_queue, self)
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
                # Executes Minecraft Command
                succeded = self.__minecraft_command(command)
                if not succeded:
                    logging.error("Minecraft command failed.")
            elif is_specify_server:
                # Specifys server to run command on
                succeded = self.__specify_server(command)
                if not succeded:
                    logging.error("specify_server failed.")
            else:
                # Handles PyCraftServerManager command
                succeded = self.__pycraftservermanager_command(command)
                if not succeded:
                    logging.error("PyCraftServerManager command failed.")

        logging.info("Exit")

    def __specify_server(self, command):
        """
        Sets temporary server runner to the server runner associated with the given name or ID.
        """
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
            return False

        # Get serverrunner based on name or id
        server_runner = None
        if is_name:
            server_runner = self.name_to_server[specifier]
            pass
        elif is_id:
            server_runner = self.name_to_server[specifier]
            pass
        else:
            logging.error("Invalid specify server command.")
            return False

        # Set temporary server runner to server runner found
        if server_runner is None:
            logging.error("Server Runner not found.")
            return False
        self.temp_server_runner = server_runner

        # Prepend list with command string
        self.__input_queue.insert(0, real_command)
        is_input_queue_empty = len(self.__input_queue) == 0 
        return True

    def __minecraft_command(self, command):
        """
        Sends command to the given temporary server runner, then sets temporary server runner back to default.
        """
        succeded = self.temp_server_runner.minecraft_input_handler(command)
        self.temp_server_runner = self.default_server_runner
        return succeded

    def __pycraftservermanager_command(self, command):
        """
        Handles command like a PyCrafty command.
        """
        command_args = command.split(" ")
        # Check if this is an Input Handler command. If so, run.
        if command_args[0] in self.commands_functions_dict:
            function = self.commands_functions_dict.get(command_args[0])[0]
            arg_count = self.commands_functions_dict.get(command_args[0])[1]
            if arg_count == 0:
                return function()
            elif arg_count == -1:
                return function(command)
            elif arg_count == len(command_args) - 1:
                return function(command_args[1::])
        else:
            succeded = self.temp_server_runner.pycraft_input_handler(command)
            self.temp_server_runner = self.default_server_runner
            return succeded

    def exit(self):
        """
        Stops server if it's running and quits program.
        """
        logging.info("Entry")
        # TODO: Stop all running servers
        logging.info("Exit")

    def schedule(self, cmd_input_args):
        logging.info("Entry")
        # Check what type of schedule command it is
        schedule_command_type = cmd_input_args.split(" ")[1]
        # Add new scheduled command
        if (schedule_command_type == "add"):
            # Extract command and cron string
            # https://stackoverflow.com/a/2076356/12464369
            cmd_inputs_args_quoted = re.findall('"([^"]*)"', cmd_input_args)
            command = cmd_inputs_args_quoted[0]
            cron = cmd_inputs_args_quoted[1]
            logging.debug("Command: %s", command)
            logging.debug("Cron: %s", cron)
            print(cmd_inputs_args_quoted)
            # Create scheduled command
            if (self.Scheduler.add_scheduled_command(command, cron)):
                logging.info("Command successfully scheduled!")
                print(colored("Command successfully scheduled!", "green"))
            else:
                logging.warning("Command not scheduled!")
                print(colored("Command not scheduled!", "red"))
        # List all scheduled commands
        elif (schedule_command_type == "list"):
            logging.info("Listing scheduled commands.")
            if (not self.Scheduler.list_scheduled_commands()):
                logging.error("Something went wrong listing scheduled jobs!")
                print(colored("Something went wrong listing scheduled jobs!", "red"))
        # Delete command
        elif (schedule_command_type == "delete"):
            logging.info("Deleting scheduled command.")
            job_id = cmd_input_args.split(" ")[2]
            logging.debug("job_id: %s", str(job_id))
            if (not self.Scheduler.delete_scheduled_command(job_id)):
                logging.error("Something went wrong deleting a scheduled job!")
                print(colored("Something went wrong deleting a scheduled job!", "red"))
        # Not a valid command
        else:
            logging.warning("%s is not a valid schedule command type.", schedule_command_type)
            print(colored("%s is not a valid schedule command type." % (schedule_command_type), "red"))
        logging.info("Exit")