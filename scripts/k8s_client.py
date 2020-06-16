from kubernetes import client, config


class Client(object):
    def __init__(self, namespace):
        self.namespace = namespace
        config.load_kube_config()
        self.client = client.CoreV1Api()

    def get_pod_phase(self, pod_name):
        try:
            pod = self.client.read_namespaced_pod(namespace=self.namespace,
                                                  name=pod_name)
            return pod.status.phase
        except Exception:
            return "Pod %s not found" % pod_name

    def get_pod_status(self, pod_name):
        try:
            pod = self.client.read_namespaced_pod(namespace=self.namespace,
                                                  name=pod_name)
            return pod.status.to_str()
        except Exception:
            return "Pod %s not found" % pod_name

    def get_pod_label_status(self, pod_name):
        try:
            pod = self.client.read_namespaced_pod(namespace=self.namespace,
                                                  name=pod_name)
            return pod.metadata.labels["status"]
        except Exception:
            return "Pod %s not found" % pod_name

    def get_pod_log(self, pod_name):
        try:
            return self.client.read_namespaced_pod_log(
                namespace=self.namespace, name=pod_name)
        except Exception:
            return "Pod %s not found" % pod_name

    def delete_pod(self, pod_name):
        self.client.delete_namespaced_pod(
            pod_name,
            self.namespace,
            body=client.V1DeleteOptions(grace_period_seconds=0),
        )

    def get_pods(self, job_name):
        pods = self.client.list_namespaced_pod(namespace=self.namespace).items
        res = []
        for pod in pods:
            if job_name in pod.metadata.name:
                res.append(pod)
        return res

    def get_cpus(self, job_name):
        cpu = 0
        pods = self.client.list_namespaced_pod(namespace=self.namespace).items
        for pod in pods:
            if job_name in pod.metadata.name and pod.status.phase == 'Running':
                for container in pod.spec.containers:
                    requests = container.resources.requests
                    if requests:
                        t = requests.get('cpu', None)
                        if 'm' in t:
                            cpu += float(t.split('m')[0])
                        else:
                            cpu += float(t)
        return cpu
