import os
import csv
import schedule

class Scheduler():
    """
    Scheduler class handles running commands at regular intervals.
    """

    list_file_name = "scheduler.csv"

    def __init__(self, main_directory, server_directory):
        """
        Initializes Scheduler for server by tying it to a Server Directory and creating the scheduler file.
        """
        # Store all current server properties
        self.main_directory = main_directory
        self.server_directory = server_directory
        self.list_file_path = os.path.join(self.server_directory, self.list_file_name)
        # Create scheduler.list file if it doesn't exist and create headers for it
        if not os.path.exists(self.list_file_path):
            list_file = open(self.list_file_path, 'w')
            list_file.write("")
            list_file.close()

        