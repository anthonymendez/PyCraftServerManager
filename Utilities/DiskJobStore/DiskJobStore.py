from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.jobstores.base import BaseJobStore

class DiskJobStore(MemoryJobStore):
    """
    Stores jobs in an array in RAM and saves to a file.
    """

    def __init__(self):
        super().__init__()

    def get_all_jobs(self):
        return super().get_all_jobs()

    def get_due_jobs(self, now):
        return super().get_due_jobs(now)

    def get_next_run_time(self):
        return super().get_next_run_time()

    def lookup_job(self, job_id):
        return super().lookup_job(job_id)

    def remove_all_jobs(self):
        return super().remove_all_jobs()

    def remove_job(self, job_id):
        return super().remove_job(job_id)

    def shutdown(self):
        return super().shutdown()

    def update_job(self, job):
        return super().update_job(job)

    