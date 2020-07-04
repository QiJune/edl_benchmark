from nginx_job import NginxJobScheduler
from edl_cpu_job import EdlCPUJobScheduler
import time
import copy
from k8s_client import Client


class API(object):
    def __init__(self,
                 namespace,
                 nginx_job_config=None,
                 edl_job_config=None):
        self.client = Client(namespace)
        self.nginx_job_config = nginx_job_config
        self.edl_job_config = edl_job_config

    def create_nginx_jobs(self, num_jobs):
        jobs = []
        for i in range(num_jobs):
            conf = copy.deepcopy(self.nginx_job_config)
            conf["job_name"] = self.nginx_job_config["job_name"] + "-" + str(i)
            job = NginxJobScheduler(**conf)
            jobs.append(job)
        self.nginx_jobs = jobs
        return jobs

    def start_nginx_job(self, job):
        job.start_job()

    def scale_nginx_job(self, job, sleep_time, sequences):
        for s in sequences:
            job.scale_deployment(s)
            time.sleep(sleep_time)

    def delete_nginx_jobs(self, jobs):
        for job in jobs:
            job.delete_job()

    def create_edl_jobs(self, num_jobs):
        jobs = []
        for i in range(num_jobs):
            conf = copy.deepcopy(self.edl_job_config)
            conf["job_name"] = self.edl_job_config["job_name"] + "-" + str(i)
            job = EdlCPUJobScheduler(**conf)
            jobs.append(job)
        self.edl_jobs = jobs
        return jobs

    def start_edl_job(self, job):
        job.start_job()

    def wait_edl_job_running(self, job):
        job.wait_running(self.client)

    def wait_edl_job_completed(self, job):
        job.wait_completed(self.client)

    def delete_edl_job(self, job):
        job.delete_job(self.client)

    def get_edl_job_log(self, job):
        return job.get_master_log(self.client)

    def delete_edl_jobs(self, jobs):
        for job in jobs:
            job.delete_job(self.client)

    def get_experiment1_start_time(self, start_time, res):
        cur_time = int(time.time() - start_time)
        for job in self.edl_jobs:
            if job.job_name in res:
                continue
            if job.check_running(self.client):
                return (job.job_name, cur_time)
        return None

    def get_expriment1_cpus(self, start_time):
        cur_time = int(time.time() - start_time)
        edl_cpus = self.client.get_cpus(self.edl_job_config["job_name"])
        return (cur_time, edl_cpus)

    def get_expriment2_cpus(self, start_time):
        cur_time = int(time.time() - start_time)
        nginx_cpus = self.client.get_cpus(self.nginx_job_config["job_name"])
        edl_cpus = self.client.get_cpus(self.edl_job_config["job_name"])
        total_cpus = nginx_cpus + edl_cpus
        return (cur_time, nginx_cpus, edl_cpus, total_cpus)
