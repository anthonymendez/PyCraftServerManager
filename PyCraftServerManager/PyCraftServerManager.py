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

from Utilities.Utilities import *

if is_windows():
    import colorama
    colorama.init()

__stopping_all = True
__cmd_input_queue = []

input_queue_lock = Lock()

def init():
    """
    Starts PyCraftServerManager input thread.
    """
    stopping_all = False
    pass

def input_loop_thread():
    """
    Handles accepting input from the user in a thread until an exit is met.
    """
    logging.info("Entry")
    while not __stopping_all:
        logging.info("Waiting on user input.")
        cmd_input = input()
        logging.info("User input: %s", str(cmd_input))

        if isinstance(cmd_input, str):
            logging.info("Passing user input to input handler")
            cmd_input = cmd_input.strip()
            push_to_input_queue(cmd_input)
        else:
            logging.error("User input is not string.")
            # self.server_process.sendline("stop".encode("utf-8"))
            # self.server_process.terminate(force=True)
            break
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
    return False

def exit():
    """
    Handles shutting off servers and exiting PyCraftServerManager.
    """
    pass