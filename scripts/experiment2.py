from api import API
import time
from threading import Thread


def run_experiment(namespace, nginx_job_config, edl_cpu_job_config, filename):
    handle = API(namespace,
                 nginx_job_config=nginx_job_config,
                 edl_job_config=edl_cpu_job_config)
    results = []
    stop_flag = False

    def monitor(handle):
        start_time = time.time()
        while not stop_flag:
            res = handle.get_expriment2_cpus(start_time)
            results.append(res)
            time.sleep(2)

    monitor_thread = Thread(target=monitor, args=(handle, ))
    monitor_thread.daemon = True

    # 1. create jobs
    nginx_jobs = handle.create_nginx_jobs(1)
    edl_jobs = handle.create_edl_jobs(1)
    monitor_thread.start()

    # 2. start and wait edl jobs running
    for job in edl_jobs:
        handle.start_edl_job(job)

    for job in edl_jobs:
        handle.wait_edl_job_running(job)

    time.sleep(50)

    # 3. scale nginx jobs
    handle.start_nginx_job(nginx_jobs[0])
    sequences = [4, 8, 12, 8, 4]
    handle.scale_nginx_job(nginx_jobs[0], 100, sequences)

    # 4. stop job
    handle.delete_nginx_jobs(nginx_jobs)
    handle.delete_edl_jobs(edl_jobs)
    stop_flag = True
    monitor_thread.join()

    # 5. save results
    with open(filename + ".csv", "w") as f:
        f.write("time,nignx_job,edl_job,total\n")
        for res in results:
            res = [str(r) for r in res]
            f.write(",".join(res) + "\n")


if __name__ == '__main__':
    namespace = "default"

    nginx_job_config = {
        "job_name": "nginx",
        "image": "nginx:1.7.9",
        "cpu_num": 1,
        "memory": "2048Mi",
        "replicas": 1,
        "priority": "high",
    }

    image = "o0o0o/elasticdl:mnist-0704"

    edl_cpu_job_config = {
        "image": image,
        "num_epochs": 30,
        "job_name": "edl-cpu-qianren",
        "ps_num": 2,
        "worker_num": 16,
        "master_cpu": 2,
        "master_memory": "4096Mi",
        "master_priority": "high",
        "ps_cpu": 1,
        "ps_memory": "2048Mi",
        "ps_priority": "high",
        "worker_cpu": 1,
        "worker_memory": "2048Mi",
        "worker_priority": "low",
    }

    run_experiment(namespace, nginx_job_config, edl_cpu_job_config,
                   "experiment2-studygroup")
