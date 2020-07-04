from mako.template import Template
import os
import tempfile
import time


class EdlCPUJobScheduler(object):
    def __init__(
        self,
        image,
        num_epochs,
        job_name,
        ps_num,
        worker_num,
        master_cpu,
        master_memory,
        master_priority,
        ps_cpu,
        ps_memory,
        ps_priority,
        worker_cpu,
        worker_memory,
        worker_priority,
    ):
        self.image = image
        self.num_epochs = num_epochs
        self.job_name = job_name
        self.ps_num = ps_num
        self.worker_num = worker_num
        self.master_cpu = master_cpu
        self.master_memory = master_memory
        self.master_priority = master_priority
        self.ps_cpu = ps_cpu
        self.ps_memory = ps_memory
        self.ps_priority = ps_priority
        self.worker_cpu = worker_cpu
        self.worker_memory = worker_memory
        self.worker_priority = worker_priority
        self.master_pod_name = "elasticdl-" + self.job_name + "-master"
        self.ps_pod_names = [
            "elasticdl-" + self.job_name + "-ps-" + str(i)
            for i in range(self.ps_num)
        ]

        filepath = os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))) + '/sample_yaml/edl_cpu.yaml.template'
        edl_template = Template(filename=filepath)
        self.edl_yaml = edl_template.render(
            image=self.image,
            job_name=self.job_name,
            num_epochs=str(self.num_epochs),
            ps_num=str(self.ps_num),
            worker_num=str(self.worker_num),
            master_cpu=self.master_cpu,
            master_memory=self.master_memory,
            master_priority=self.master_priority,
            ps_cpu=self.ps_cpu,
            ps_memory=self.ps_memory,
            ps_priority=self.ps_priority,
            worker_cpu=self.worker_cpu,
            worker_memory=self.worker_memory,
            worker_priority=self.worker_priority)

    def start_job(self):
        with tempfile.TemporaryDirectory() as td:
            f_name = os.path.join(td, self.job_name + ".yaml")
            with open(f_name, "w") as f:
                f.write(self.edl_yaml)
            os.system("kubectl create -f " + f_name)

    def _check_ps_running(self, ps_pod_phases):
        for phase in ps_pod_phases:
            if phase != "Running":
                return False
        return True

    def wait_running(self, client):
        while True:
            if self.check_running(client):
                break
            time.sleep(2)

    def check_running(self, client):
        master_pod_phase = client.get_pod_phase(self.master_pod_name)
        if master_pod_phase != "Running":
            return False
        ps_pod_phases = [client.get_pod_phase(ps) for ps in self.ps_pod_names]
        if self._check_ps_running(ps_pod_phases):
            return True
        return False

    def wait_completed(self, client):
        while True:
            master_pod_phase = client.get_pod_phase(self.master_pod_name)
            if master_pod_phase == "Succeeded":
                break
            time.sleep(2)

    def delete_job(self, client):
        client.delete_pod(self.master_pod_name)

    def get_master_log(self, client):
        return client.get_pod_log(self.master_pod_name)

    def print_pods(self):
        cmd = "kubectl get pods | grep " + self.job_name
        os.system(cmd)
