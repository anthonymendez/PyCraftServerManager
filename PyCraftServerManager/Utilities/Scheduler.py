import os
import csv
import pickle
import re
import pickle

import logging as log
logging = log.getLogger(__name__)

from threading import Thread
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from ..Utilities.DiskJobStore.DiskJobStore import DiskJobStore

server_runner_ = None

class Scheduler():
    """
    Scheduler class handles running commands at regular intervals.
    """

    def __init__(self, main_directory, server_directory, input_handler, server_runner):
        """
        Initializes Scheduler for server by:\n
        \tTying it to a Server Directory.\n
        \tTying it to the server runner's input handler function
        \tCreating the scheduler file.
        """
        logging.info("Entry")
        # Store all current server properties
        self.main_directory = main_directory
        self.server_directory = server_directory
        self.input_handler = input_handler
        self.sched = BackgroundScheduler()
        global server_runner_
        server_runner_ = server_runner
        jobstore = DiskJobStore(server_runner=server_runner_, scheduler=self.sched)
        self.sched.add_jobstore(jobstore)
        self.sched.start()
        self.job_count = len(jobstore.get_all_jobs())
        logging.info("Exit")
    
    def add_scheduled_function(self, function, function_args, cron_string):
        """
        Creates scheduled function using the given function.\n
        Schedules using cron-like syntax.\n
        https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html
        """
        logging.info("Entry")
        # Check for None or empty strings
        if function == None or cron_string == None or len(cron_string) == 0:
            logging.error("None or Empty strings present in arguments.")
            logging.info("Exit")
            return False

        # Check if it fits the amount arguments needed for cron
        cron_list = cron_string.split(" ")
        if (len(cron_list) < 11 or len(cron_list) > 12):
            logging.warning("Not 11 or 12 arguments in cron list. Count: %s", str(len(cron_list)))
            logging.info("Exit")
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

        cron_print_str = """year \"%s\"
        month \"%s\"
        day \"%s\"
        week \"%s\"
        day_of_week \"%s\"
        hour \"%s\"
        minute \"%s\"
        second \"%s\"
        start_date \"%s\"
        end_date \"%s\"
        timezone \"%s\"""" % (
            str(year),
            str(month),
            str(day),
            str(week),
            str(day_of_week),
            str(hour),
            str(minute),
            str(second),
            str(start_date),
            str(end_date),
            str(timezone)
        )
        logging.debug(cron_print_str)
        print(cron_print_str)

        # Check if jitter is exists
        jitter = None
        if (len(cron_list) == 12):
            jitter = cron_list[11]
            jitter_str = "debug \"%s\"" % str(jitter)
            logging.debug(jitter_str)
            print(jitter_str)

        # Try to schedule command like a cron task
        try:
            ct = CronTrigger(year=year, month=month, day=day, week=week, 
                            day_of_week=day_of_week, hour=hour, minute=minute, 
                            second=second, start_date=start_date, end_date=end_date, 
                            timezone=timezone, jitter=jitter)
            self.sched.add_job(run_function, trigger=ct, args=[function, function_args], id=str(self.job_count))
            self.job_count += 1
            logging.info("Scheduled new command.")
            logging.info("Exit")
            return True
        except Exception as e:
            logging.warning("Something went wrong with scheduling command. %s", str(e))
            logging.info("Exit")
            return False

    def add_scheduled_command(self, command, cron_string):
        """
        Creates scheduled command using the given scheduler command string.\n
        Schedules using cron-like syntax.\n
        https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html
        """
        logging.info("Entry")
        # Check for empty strings
        if command == None or len(command) == 0 or cron_string == None or len(cron_string) == 0:
            logging.error("None arguments or Empty strings present in arguments.")
            logging.info("Exit")
            return False

        # Check if it fits the amount arguments needed for cron
        cron_list = cron_string.split(" ")
        if (len(cron_list) < 11 or len(cron_list) > 12):
            logging.warning("Not 11 or 12 arguments in cron list. Count: %s", str(len(cron_list)))
            logging.info("Exit")
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

        cron_print_str = """year \"%s\"
        month \"%s\"
        day \"%s\"
        week \"%s\"
        day_of_week \"%s\"
        hour \"%s\"
        minute \"%s\"
        second \"%s\"
        start_date \"%s\"
        end_date \"%s\"
        timezone \"%s\"""" % (
            str(year),
            str(month),
            str(day),
            str(week),
            str(day_of_week),
            str(hour),
            str(minute),
            str(second),
            str(start_date),
            str(end_date),
            str(timezone)
        )
        logging.debug(cron_print_str)
        print(cron_print_str)

        # Check if jitter is exists
        jitter = None
        if (len(cron_list) == 12):
            jitter = cron_list[11]
            jitter_str = "debug \"%s\"" % str(jitter)
            logging.debug(jitter_str)
            print(jitter_str)

        # Try to schedule command like a cron task
        try:
            ct = CronTrigger(year=year, month=month, day=day, week=week, 
                            day_of_week=day_of_week, hour=hour, minute=minute, 
                            second=second, start_date=start_date, end_date=end_date, 
                            timezone=timezone, jitter=jitter)
            self.sched.add_job(run_function, trigger=ct, args=[self.input_handler, command], id=str(self.job_count))
            self.job_count += 1
            logging.info("Scheduled new command.")
            logging.info("Exit")
            return True
        except Exception as e:
            logging.exception("Something went wrong with scheduling command. %s.", str(e))
            logging.info("Exit")
            return False

    def delete_scheduled_command(self, job_id):
        """
        Removes scheduled command with the job's id.
        """
        logging.info("Entry")
        try:
            self.sched.remove_job(job_id)
            logging.info("Removed job %s", str(job_id))
            logging.info("Exit")
            return True
        except Exception as e:
            logging.warning("Something went wrong with removing command. %s", str(e))
            logging.info("Exit")
            return False

    def list_scheduled_commands(self):
        """
        Returns list of currently scheduled jobs.
        """
        logging.info("Entry")
        try:
            job_list = self.sched.get_jobs()
            for job in job_list:
                job_info = "ID: %s; " % job.id
                job_info += "Function: %s; " % str(job.func) 
                job_info += "Args: %s; " % str(job.args)
                job_info += "%s; " % str(job.trigger)
                job_info += "Next run time: %s" % str(job.next_run_time)
                logging.info(job_info)
                print(job_info)
            logging.info("Exit")
            return True
        except Exception as e:
            logging.warning("Something went wrong with listing commands. %s", str(e))
            logging.info("Exit")
            return False

def run_function(function, args):
    """
    Handles running given function with input arguments.
    """
    logging.info("Entry")
    try:
        function(server_runner_, args)
    except Exception as e:
        logging.error(e)
    logging.info("Exit")