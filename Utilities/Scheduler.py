import os
import csv
import pickle
import re

from apscheduler.triggers import cron
from threading import Thread

# TODO: Move to it's own module
def is_int(s):
    """
    Checks if a given string is an integer.\n
    https://stackoverflow.com/a/1265696
    """
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()

class Scheduler():
    """
    Scheduler class handles running commands at regular intervals.
    """

    list_file_name = "scheduler.list"

    def __init__(self, main_directory, server_directory, input_handler):
        """
        Initializes Scheduler for server by:\n
        \tTying it to a Server Directory.\n
        \tTying it to the server runner's input handler function
        \tCreating the scheduler file.
        """
        # Store all current server properties
        self.main_directory = main_directory
        self.server_directory = server_directory
        self.input_handler = input_handler
        self.list_file_path = os.path.join(self.server_directory, self.list_file_name)
        # Create scheduler.list file if it doesn't exist and create headers for it
        if not os.path.exists(self.list_file_path):
            list_file = open(self.list_file_path, 'w')
            list_file.write("")
            list_file.close()
    
    def create_scheduled_command(self, command, scheduler_commands):
        """
        Creates scheduled command using the given scheduler command string.\n
        """
        # Check for empty strings
        if command == None or len(command) == 0 or scheduler_commands == None or len(scheduler_commands) == 0:
            return False

        # Check if the first argument is an integer. If so it is the interval for every command.
        