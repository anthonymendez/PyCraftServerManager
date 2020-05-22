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
    try:
        if not __stopping_all:
            with input_queue_lock:
                __cmd_input_queue.append(cmd_input)
            return True
    except Exception as e:
        logging.exception(e)
        return False

def prepend_to_input_queue(cmd_input):
    """
    Pushes command to the beginning of the input queue.

    Returns bool on success.
    """
    try:
        with input_queue_lock:
            __cmd_input_queue.insert(0, cmd_input)
            return True
    except Exception as e:
        logging.exception(e)
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

    cmd_input_split = cmd_input.split(" ")
    is_specifying_server = "name" in cmd_input_split[0] or "id" in cmd_input_split[0]
    is_minecraft_command = cmd_input[0] == "/"

    if is_specifying_server:
        # Set temporary server runner to specified server
        is_name_1 = "name" == cmd_input_split[0]
        is_name_2 =  "name" == cmd_input_split[0].split("=")[0]
        is_id_1 = "id" == cmd_input_split[0]
        is_id_2 = "id" == cmd_input_split[0].split("=")[0]
        if is_name_1 or is_name_2:
            if is_name_1:
                name = cmd_input_split[2]
            else:
                name = cmd_input_split[0].split("=")[1]
            temp_server_runner = get_server_runner_by_name(name)
        elif is_id_1 or is_id_2:
            if is_id_1:
                id_ = cmd_input_split[2]
            else:
                id_ = cmd_input_split[0].split("=")[1]
            temp_server_runner = get_server_runner_by_id(id_)
        else:
            logging.warning("Invalid specify server command.")
            return False

        # Push command back to the head of the input queue list
        if is_name_1 or is_id_1:
            new_cmd_input = " ".join(cmd_input_split[3::])
        else:
            new_cmd_input = " ".join(cmd_input_split[1::])
        return prepend_to_input_queue(new_cmd_input)

    elif is_minecraft_command:
        # Send minecraft command to temporary server runner
        # temp_server_runner.send(cmd_input[1::])

        # Set temporary server runner back to default
        temp_server_runner = def_server_runner
        pass
    else:
        # Handle PyCraftServerManager command
        try:
            return handle_pycraftservermanager_command(cmd_input)
        except Exception as e:
            logging.exception(e)
            return False
    
    return False

def handle_server_command():
    pass

def handle_pycraftservermanager_command(cmd_input):
    """
    Handles input for launching PyCraftServerManager commands.
    """
    with pycraft_input_handler_lock:
        logging.info("Command is a PyCraftServerManager command.")
        cmd_input_args = cmd_input.split(" ")
        command = cmd_input_args[0]
        if command in commands_functions_dict:
            print(colored("Command \"%s\" received!" % cmd_input, "green"))
            fn = commands_functions_dict.get(command)[0]
            if fn is None:
                logging.warning("Command not programmed yet! Coming soon!")
                print(colored("Command not programmed yet! Coming soon!", "yellow"))
            else:
                logging.debug("Given valid command.")
                args_required = commands_functions_dict.get(command)[1]
                if args_required == -1:
                    fn_return = fn(cmd_input)
                elif args_required == 0:
                    fn_return = fn()
                elif len(cmd_input_args) - 1 == args_required:
                    fn_return = fn(cmd_input_args[1::])
                else:
                    logging.warning("Argument count not matched. Required %d. Received %d." % (len(cmd_input_args) - 1, args_required))
                    print(colored("Argument count not matched. Required %d. Received %d." % (len(cmd_input_args) - 1, args_required), "red"))

                # Check what function returned if it did return anything
                if isinstance(fn_return, bool):
                    if not fn_return:
                        logging.warning("Command \"%s\" did not run successfully." % cmd_input)
                        print(colored("Command \"%s\" did not run successfully." % cmd_input, "red"))
                    else:
                        logging.debug("Command \"%s\" ran successfully." % cmd_input)
                    
                    return fn_return
                
                else:
                    logging.warning("Command \"%s\" did not return bool." % str(cmd_input))
                    print(colored("Command \"%s\" did not return bool." % str(cmd_input), "red"))
                    return False

        else:
            logging.warning("Command not recognized.")
            print(colored("Command not recognized.", "red"))
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

def backup(server_runner = None, name = None, id = None, backup_all = False):
    """
    Backups server with the given server runner object, name or id.

    If backup_all is True, ignores all given conditions and backups all servers running.
    """
    pass

def exit():
    """
    Handles shutting off servers and exiting PyCraftServerManager.
    """
    for server_runner in __server_runners:
        server_runner.stop()

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
pycraft_input_handler_lock = Lock()

# Threads to handle input command
user_input_loop = None
input_queue_handler = None

# List of ServerRunners
__server_runners = []

# Temporary and Default Server Runners
temp_server_runner = None
def_server_runner = None

# PyCraftServerManager function names to functions
commands_functions_dict = {
    # Terminal Command: (fn pointer, argument count)
    "backup": (backup, 1),
    "exit": (exit, 0),
    "schedule": (schedule, -1),
    "jar": (jar, -1)
}