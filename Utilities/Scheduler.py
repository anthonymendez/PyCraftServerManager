import os
import csv
import pickle
import re

from apscheduler.triggers import cron
from apscheduler.schedulers.background import BackgroundScheduler
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
        self.sched = BackgroundScheduler()
        # Create scheduler.list file if it doesn't exist and create headers for it
        if not os.path.exists(self.list_file_path):
            list_file = open(self.list_file_path, 'w')
            list_file.write("")
            list_file.close()
    
    def create_scheduled_command(self, command, cron_string):
        """
        Creates scheduled command using the given scheduler command string.\n
        """
        # Check for empty strings
        if command == None or len(command) == 0 or cron_string == None or len(cron_string) == 0:
            return False

        # Check if it fits the amount arguments needed for cron
        cron_list = cron_string.splits(" ")
        if (len(cron_list) < 11 or len(cron_list > 12)):
            return False

        year = cron_list[0]
        month = cron_list[1]
        day = cron_list[2]
        week = cron_list[3]
        day_of_week = cron_list[4]
        hour = cron_list[5]
        minute = cron_list[6]
        second = cron_list[7]
        start_date = cron_list[8]
        end_date = cron_list[9]
        timezone = cron_list[10]

        # Check if jitter is exists
        jitter = None
        if (len(cron_list) == 12):
            jitter = cron_list[11]

        # Try to schedule command like a cron task
        try:
            self.sched.add_job(self.input_handler, "cron", args=[command], 
                            year=year, month=month, day=day, week=week, 
                            day_of_week=day_of_week, hour=hour, minute=minute, 
                            second=second, start_date=start_date, end_date=end_date, 
                            timezone=timezone, jitter=jitter)
            return True
        except Exception as e:
            print(e)
            return False