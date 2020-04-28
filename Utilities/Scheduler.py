import os
import csv
import pickle
import re

from apscheduler.triggers.cron import CronTrigger
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
        self.sched.start()
        # Create scheduler.list file if it doesn't exist and create headers for it
        if not os.path.exists(self.list_file_path):
            list_file = open(self.list_file_path, 'w')
            list_file.write("")
            list_file.close()
    
    def add_scheduled_command(self, command, cron_string):
        """
        Creates scheduled command using the given scheduler command string.\n
        Schedules using cron-like syntax.\n
        https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html
        """
        # Check for empty strings
        if command == None or len(command) == 0 or cron_string == None or len(cron_string) == 0:
            return False

        # Check if it fits the amount arguments needed for cron
        cron_list = cron_string.split(" ")
        if (len(cron_list) < 11 or len(cron_list) > 12):
            return False

        year = None if cron_list[0] == "*" else cron_list[0]
        month = None if cron_list[1] == "*" else cron_list[1]
        day = None if cron_list[2] == "*" else cron_list[2]
        week = None if cron_list[3] == "*" else cron_list[3]
        day_of_week = None if cron_list[4] == "*" else cron_list[4]
        hour = None if cron_list[5] == "*" else cron_list[5]
        minute = None if cron_list[6] == "*" else cron_list[6]
        second = None if cron_list[7] == "*" else cron_list[7]
        start_date = None if cron_list[8] == "*" else cron_list[8]
        end_date = None if cron_list[9] == "*" else cron_list[9]
        timezone = None if cron_list[10] == "*" else cron_list[10]

        print("year \"" + str(year) + "\"")
        print("month \"" + str(month) + "\"")
        print("day \"" + str(day) + "\"")
        print("week \"" + str(week) + "\"")
        print("day_of_week \"" + str(day_of_week) + "\"")
        print("hour \"" + str(hour) + "\"")
        print("minute \"" + str(minute) + "\"")
        print("second \"" + str(second) + "\"")
        print("start_date \"" + str(start_date) + "\"")
        print("end_date \"" + str(end_date) + "\"")
        print("timezone \"" + str(timezone) + "\"")

        # Check if jitter is exists
        jitter = None
        if (len(cron_list) == 12):
            jitter = cron_list[11]

        # Try to schedule command like a cron task
        try:
            ct = CronTrigger(year=year, month=month, day=day, week=week, 
                            day_of_week=day_of_week, hour=hour, minute=minute, 
                            second=second, start_date=start_date, end_date=end_date, 
                            timezone=timezone, jitter=jitter)
            self.sched.add_job(self.input_handler, trigger=ct, args=[command])
            return True
        except Exception as e:
            print(str(e))
            return False

    def delete_scheduled_command(self, job_id):
        """
        Removes scheduled command with the job's id.
        """
        try:
            self.sched.remove_job(job_id)
            return True
        except Exception as e:
            print(e)
            return False

    def list_scheduled_commands(self):
        """
        Returns list of currently scheduled jobs.
        """
        try:
            return self.sched.print_jobs()
        except Exception as e:
            print(e)
            return None