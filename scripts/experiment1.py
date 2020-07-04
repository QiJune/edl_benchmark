from api import API
import time
from threading import Thread


def run_experiment(namespace, config, filename):
    handle = API(namespace, edl_job_config=config)
    results = []
    stop_flag = False

    start_time = time.time()

    def monitor(handle):
        while not stop_flag:
            res = handle.get_expriment1_cpus(start_time)
            results.append(res)
            time.sleep(2)

    monitor_thread = Thread(target=monitor, args=(handle, ))
    monitor_thread.daemon = True

    job_count = 2

    # 1. create jobs
    edl_jobs = handle.create_edl_jobs(job_count)
    monitor_thread.start()

    if filename == "experiment1-studygroup":
        # 2. start edl jobs
        for job in edl_jobs:
            handle.start_edl_job(job)
            time.sleep(100)

        # 3. wait for some edl jobs complete
        handle.wait_edl_job_completed(edl_jobs[0])
        handle.delete_edl_job(edl_jobs[0])

        handle.wait_edl_job_completed(edl_jobs[1])
        handle.delete_edl_job(edl_jobs[1])
    else:
        handle.start_edl_job(edl_jobs[0])
        handle.wait_edl_job_completed(edl_jobs[0])
        handle.delete_edl_job(edl_jobs[0])

        handle.start_edl_job(edl_jobs[1])
        handle.wait_edl_job_completed(edl_jobs[1])
        handle.delete_edl_job(edl_jobs[1])

    # 4. stop job
    stop_flag = True
    monitor_thread.join()

    # 5. save results
    with open(filename + ".csv", "w") as f:
        f.write("time,edl_job\n")
        for res in results:
            res = [str(r) for r in res]
            f.write(",".join(res) + "\n")


if __name__ == '__main__':
    namespace = "default"
    image = "o0o0o/elasticdl:mnist-0704"

    edl_cpu_job_config = {
        "image": image,
        "num_epochs": 2,
        "job_name": "edl-cpu-qianren",
        "ps_num": 2,
        "worker_num": 6,
        "master_cpu": 1,
        "master_memory": "2048Mi",
        "master_priority": "low",
        "ps_cpu": 1,
        "ps_memory": "2048Mi",
        "ps_priority": "low",
        "worker_cpu": 1,
        "worker_memory": "2048Mi",
        "worker_priority": "low",
    }

    run_experiment(namespace, edl_cpu_job_config, "experiment1-studygroup")
    time.sleep(30)
    run_experiment(namespace, edl_cpu_job_config, "experiment1-controlgroup")
