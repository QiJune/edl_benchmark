from mako.template import Template
import os
import tempfile


class NginxJobScheduler(object):
    def __init__(self,
                 job_name,
                 image,
                 cpu_num,
                 memory,
                 replicas,
                 priority):
        self.job_name = job_name
        self.image = image
        self.cpu_num = cpu_num
        self.memory = memory
        self.replicas = replicas
        self.priority = priority

        filepath = os.path.dirname(
            os.path.dirname(os.path.abspath(
                __file__))) + '/sample_yaml/nginx.yaml.template'

        self.nginx_template = Template(filename=filepath)

    def start_job(self):
        nginx_yaml = self.nginx_template.render(job_name=self.job_name,
                                                image=self.image,
                                                cpu=self.cpu_num,
                                                memory=self.memory,
                                                replicas=self.replicas,
                                                priority=self.priority)

        with tempfile.TemporaryDirectory() as td:
            f_name = os.path.join(td, self.job_name + ".yaml")
            with open(f_name, "w") as f:
                f.write(nginx_yaml)
            os.system("kubectl create -f " + f_name)

    def scale_deployment(self, replicas_num):
        cmd = "kubectl scale deployment.v1.apps/" + self.job_name + \
              " --replicas=" + str(replicas_num)
        os.system(cmd)

    def delete_job(self):
        cmd = "kubectl delete deployment " + self.job_name
        os.system(cmd)

    def print_pods(self):
        cmd = "kubectl get pods | grep " + self.job_name
        os.system(cmd)
