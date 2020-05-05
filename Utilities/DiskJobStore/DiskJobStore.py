import pickle
import os

from apscheduler.jobstores.memory import MemoryJobStore

class DiskJobStore(MemoryJobStore):
    """
    Stores jobs in an array in RAM and saves to a file.
    """

    def __init__(self, disk_dir = "DiskJobStore", jobs_file_name = "jobs.diskjobstore", jobs_index_file = "jobs_index.diskjobstore"):
        """
        Handles initializing DiskJobStore.
        """
        super().__init__()
        self.disk_dir = disk_dir
        self.jobs_file_path = os.path.join(self.disk_dir, jobs_file_name)
        self.jobs_index_file_path = os.path.join(self.disk_dir, jobs_index_file)
        
        # Create directory if it has not been created.
        if not os.path.exists(self.disk_dir):
            os.mkdir(self.disk_dir)

        # Create file if it has not been created.
        if not os.path.exists(self.jobs_file_path):
            open(file=self.jobs_file_path, mode="w").close()
        # If file does exist, load values from it.
        else:
            self._jobs = pickle.load(open(file=self.jobs_index_file_path, mode="r"))

        # Same procedure here
        if not os.path.exists(self.jobs_index_file_path):
            open(file=self.jobs_index_file_path, mode="w").close()
        else:
            self._jobs_index = pickle.load(open(file=self.jobs_index_file_path, mode="r"))


    def lookup_job(self, job_id):
        """
        Look up stored job. Retrieves from memory.\n
        Returns `None` if not found.
        """
        return super().lookup_job(job_id)

    def get_due_jobs(self, now):
        """
        Get list of jobs that have `next_run_time` earlier than `now`.
        """
        return super().get_due_jobs(now)

    def get_next_run_time(self):
        """
        Returns the earliest run time of all the jobs stored in this job store, or `None` if there are no active jobs.\n
        Retrieves from memory.
        """
        return super().get_next_run_time()

    def get_all_jobs(self):
        """
        Returns a list of all jobs in this job store. The returned jobs should be sorted by next run time (ascending). Paused jobs (next_run_time == None) should be sorted last.\n
        The job store is responsible for setting the `scheduler` and `jobstore` attributes of the returned jobs to point to the scheduler and itself, respectively.\n
        Retrieves from memory.
        """
        return super().get_all_jobs()

    def add_job(self, job):
        """
        Adds the given job to the store.\n
        Store in memory and in the disk.
        """
        return super().add_job(job)

    def update_job(self, job):
        """
        Replaces the job in the store with the given newer version.
        """
        return super().update_job(job)

    def remove_job(self, job_id):
        """
        Removes all jobs from this store.\n
        Removes from memory and from disk.
        """
        return super().remove_job(job_id)

    def remove_all_jobs(self):
        """
        Removes all jobs from this store.
        """
        return super().remove_all_jobs()

    def shutdown(self):
        """
        Frees any resources still bound to this job store.
        """
        return super().shutdown()

    