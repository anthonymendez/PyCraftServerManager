# import pickle
import dill as pickle
import os


from threading import Lock
from apscheduler.util import datetime_to_utc_timestamp
from apscheduler.job import Job
from apscheduler.jobstores.memory import MemoryJobStore

class DiskJobStore(MemoryJobStore):
    """
    Stores jobs in an array in RAM and saves to a file.
    """

    def __init__(self, disk_dir = "DiskJobStore", jobs_file_name = "jobs.diskjobstore", jobs_index_file = "jobs_index.diskjobstore", server_runner = None):
        """
        Handles initializing DiskJobStore.
        """
        super().__init__()
        self.disk_dir = disk_dir
        self.jobs_file_path = os.path.join(self.disk_dir, jobs_file_name)
        self.jobs_index_file_path = os.path.join(self.disk_dir, jobs_index_file)
        self.disk_lock = Lock()
        # Create directory if it has not been created.
        if not os.path.exists(self.disk_dir):
            os.mkdir(self.disk_dir)

        # Load from jobs and jobs_index from disk.
        self._load_from_disk()

    def lookup_job(self, job_id):
        """
        Look up stored job.

        Retrieves from memory.

        Returns `None` if not found.
        """
        return super().lookup_job(job_id)

    def get_due_jobs(self, now):
        """
        Get list of jobs that have `next_run_time` earlier than `now`.

        Retrieves from memory.
        """
        return super().get_due_jobs(now)

    def get_next_run_time(self):
        """
        Returns the earliest run time of all the jobs stored in this job store, or `None` if there are no active jobs.

        Retrieves from memory.
        """
        return super().get_next_run_time()

    def get_all_jobs(self):
        """
        Returns a list of all jobs in this job store. The returned jobs should be sorted by next run time (ascending). Paused jobs (next_run_time == None) should be sorted last.

        The job store is responsible for setting the `scheduler` and `jobstore` attributes of the returned jobs to point to the scheduler and itself, respectively.

        Retrieves from memory.
        """
        return super().get_all_jobs()

    def add_job(self, job):
        """
        Adds the given job to the store.

        Store in memory and in the disk.
        """
        super_value = super().add_job(job)
        self._save_to_disk()
        return super_value

    def update_job(self, job):
        """
        Replaces the job in the store with the given newer version.

        Store in memory and in the disk.
        """
        super_value = super().update_job(job)
        self._save_to_disk()
        return super_value

    def remove_job(self, job_id):
        """
        Removes all jobs from this store.

        Removes from memory and from disk.
        """
        super_value = super().remove_job(job_id)
        self._save_to_disk()
        return super_value

    def remove_all_jobs(self):
        """
        Removes all jobs from this store.

        Removes from memory and from disk.
        """
        super_value = super().remove_all_jobs()
        self._save_to_disk()
        return super_value

    def shutdown(self):
        """
        Frees any resources still bound to this job store.

        Performs final save to disk before exiting.
        """
        self._save_to_disk()
        return super().shutdown()

    def _load_from_disk(self):
        """
        Sets `self._jobs` to what currently exists in `self.jobs_file_path` file.

        Sets `self._jobs_index` to what currently exists in `self.jobs_index_file_path` file.
        """
        with self.disk_lock:

            # Create file if it has not been created.
            if not os.path.exists(self.jobs_index_file_path):
                with open(file=self.jobs_index_file_path, mode="wb") as new_file:
                    pickle.dump([], file=new_file)
            # If file does exist, load values from it.
            else:
                try:
                    with open(file=self.jobs_index_file_path, mode="rb") as disk_file:
                        self._jobs_index = pickle.load(file=disk_file)
                except EOFError as e:
                    self._logger.debug("End of file error. Doing nothing.")
                except Exception as e:
                    self._logger.exception("Couldn't load self._jobs.")
                    
            # Create file if it has not been created.
            if not os.path.exists(self.jobs_file_path):
                with open(file=self.jobs_file_path, mode="wb") as new_file:
                    pickle.dump([], file=new_file)
            # If file does exist, load values from it.
            else:
                try:
                    with open(file=self.jobs_file_path, mode="rb") as disk_file:
                        self._jobs = pickle.load(file=disk_file)
                        for job in self._jobs:
                            self.update_job(job)
                except EOFError as e:
                    self._logger.debug("End of file error. Doing nothing.")
                except Exception as e:
                    self._logger.exception("Couldn't load self._jobs.")

    def _save_to_disk(self):
        """
        Saves `self._jobs` to `self.jobs_file_path` file.

        Saves `self._jobs_index` to `self.jobs_index_file_path` file.
        """
        with self.disk_lock:
            print(self._jobs)
            pickle.dump(self._jobs, open(file=self.jobs_file_path, mode="wb"))
            pickle.dump(self._jobs_index, open(file=self.jobs_index_file_path, mode="wb"))