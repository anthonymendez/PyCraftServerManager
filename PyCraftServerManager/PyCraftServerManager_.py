import os
import logging
from datetime import datetime

# Set up Logging
time_now = str(datetime.now()).replace(" ", "_").replace("-", "_").replace(":", "_").replace(".", "_")
log_path = os.path.join("log", time_now)
if not os.path.exists("log"):
    os.mkdir("log")
if not os.path.exists(log_path):
    os.mkdir(log_path)
log_path = os.path.join(log_path, "master.log")
logging.basicConfig(format="%(asctime)s - %(filename)s - %(funcName)s - %(name)s - %(levelname)s - %(message)s", 
                    filename=log_path, 
                    level=logging.DEBUG)

from threading import Thread, Lock
from termcolor import colored

from PyCraftServerManager.Utilities.Utilities_ import *

# Import colorama for terminal colors on Windows
if is_windows():
    import colorama
    colorama.init()

def init():
    """
    Starts PyCraftServerManager input thread.
    """
    global __stopping_all
    __stopping_all = False
    # Creates threads for user input and handling input queue
    user_input_loop = Thread(target=input_loop_thread)
    input_queue_handler = Thread(target=input_queue_handler_thread)
    user_input_loop.start()
    input_queue_handler.start()

def input_loop_thread():
    """
    Handles accepting input from the user in a thread until an exit is met.
    """
    logging.info("Entry")
    global __stopping_all
    logging.debug("__stopping_all: %s", str(__stopping_all))
    while not __stopping_all:
        logging.info("Waiting on user input.")
        try:
            cmd_input = input(">")
        except EOFError as e:
            logging.warning(e)
            break
        except Exception as e:
            logging.error(e)
            break

        logging.info("User input: %s", str(cmd_input))

        if not isinstance(cmd_input, str):
            logging.error("User input is not string.")
            break
        
        # Trim string and check if its empty
        cmd_input = cmd_input.strip()
        if len(cmd_input) == 0:
            logging.info("User input empty.")
            continue

        logging.info("Passing user input to input handler.")
        push_to_input_queue(cmd_input)
        if cmd_input == "exit":
            logging.info("Exiting program.")
            break

    __stopping_all = True
    logging.info("Exit")

def push_to_input_queue(cmd_input):
    """
    Pushes to input queue only if `stopping_all` is false.

    Returns bool on success.
    """
    if not __stopping_all:
        with input_queue_lock:
            __cmd_input_queue.append(cmd_input)
        return True
    else:
        return False

def input_queue_handler_thread():
    """
    Handles processing cmd_input_queue. 
    
    Only exits when `exit` command is sent and input queue is empty.
    """
    while not __stopping_all or not len(__cmd_input_queue) == 0:
        # If queue is empty, just start loop again
        if len(__cmd_input_queue) == 0:
            continue

        # Remove first item off the queue
        cmd_input = None
        with input_queue_lock:
            cmd_input = __cmd_input_queue.pop(0)

        # Run command and check if it ran successfully.
        if __input_command_handler(cmd_input):
            print("Command ran successfully.")
        else:
            print("Command did not run successfully.")

def __input_command_handler(cmd_input):
    """
    Handles commands passed to it by input_queue_handler_thread.
    
    Returns bool if command was successfully run.
    """
    if not isinstance(cmd_input, str):
        logging.warning("cmd_input %s is not of type string.", str(cmd_input))
        return False

    if len(cmd_input) == 0:
        logging.warning("Empty command passed in.")
        return True

    is_specifying_server = "name" in cmd_input.split(" ")[0] or "id" in cmd_input.split(" ")[0]
    is_minecraft_command = cmd_input[0] == "/"

    if is_specifying_server:
        # Set temporary server runner to specified server
        # Push command back to the head of the input queue list
        pass
    elif is_minecraft_command:
        # Send minecraft command to temporary server runner
        # Set temporary sesrver runner back to default
        pass
    else:
        # Handle PyCraftServerManager command
        pass
    
    return False

def get_server_runner_by_name(name):
    """
    Retrieves a server runner by name. None if not found.
    """
    for server_runner in __server_runners:
        if server_runner.name == name:
            return server_runner
    # Server Runner not found
    return None

def get_server_runner_by_id(id):
    """
    Retrieves a server runner by id. None if not found.
    """
    for server_runner in __server_runners:
        if server_runner.id == id:
            return server_runner
    # Server Runner not found
    return None

def backup(server_runner = None, name = None, id = None):
    """
    Backups server with the given name or id.
    """
    pass

def exit():
    """
    Handles shutting off servers and exiting PyCraftServerManager.
    """
    pass

def schedule():
    """
    Schedules command or function.
    """
    pass

def jar():
    """
    Handles jar actions.
    """
    pass

# If program is stopping to exit
__stopping_all = True

# List to hold input commands to run
__cmd_input_queue = []

# Lock for inserting and removing from input queue
input_queue_lock = Lock()

# Threads to handle input command
user_input_loop = None
input_queue_handler = None

# List of ServerRunners
__server_runners = []

# PyCraftServerManager function names to functions
commands_functions_dict = {
    # Terminal Command: (fn pointer, argument count)
    "backup": (backup, 1),
    "exit": (exit, 0),
    "schedule": (schedule, -1),
    "jar": (jar, -1)
}