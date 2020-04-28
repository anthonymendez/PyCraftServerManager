import os
import csv
import schedule
import pickle

from threading import Thread

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

    def run_threaded_input_job(self, cmd_input):
        """
        Runs a given function in it's own thread.
        """
        job_thread = Thread(target=self.input_handler, args=[cmd_input])
        job_thread.start()

    def load_scheduled_jobs(self):
        """
        Loads all jobs in scheduler file to scheduler.jobs.
        """
        list_file = open(self.list_file_path, "w")
        pickle.dump(schedule.jobs, list_file)

    def save_scheduled_jobs(self):
        """
        Saves all jobs in scheduler to a file with serialized data.
        """
        list_file = open(self.list_file_path, "r")
        schedule.jobs = pickle.load(list_file)