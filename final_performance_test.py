import requests
import time
import statistics
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

URL = "http://localhost:5003/enrollment/101"

# Required workload levels from the lab
WORKLOADS = [1, 2, 4, 8, 16]

# Number of requests generated for each concurrent worker
REQUESTS_PER_WORKER = 50

CONTAINERS = [
    "student-service",
    "course-service",
    "enrollment-service"
]


# ---------------------------------------------------------
# SEND ONE HTTP REQUEST
# ---------------------------------------------------------

def send_request():

    start = time.perf_counter()

    try:

        response = requests.get(
            URL,
            timeout=10
        )

        end = time.perf_counter()

        return {
            "success": response.status_code == 200,
            "response_time": (end - start) * 1000
        }

    except requests.RequestException:

        end = time.perf_counter()

        return {
            "success": False,
            "response_time": (end - start) * 1000
        }


# ---------------------------------------------------------
# GET CURRENT DOCKER CPU AND MEMORY
# ---------------------------------------------------------

def get_docker_stats():

    command = [
        "docker",
        "stats",
        "--no-stream",
        "--format",
        "{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}"
    ]

    try:

        output = subprocess.check_output(
            command,
            text=True
        )

    except Exception:

        return {}


    stats = {}

    for line in output.strip().splitlines():

        parts = line.split("|")

        if len(parts) != 4:
            continue

        name = parts[0]

        cpu_text = parts[1].replace("%", "").strip()

        memory_usage_text = parts[2].strip()

        memory_percent_text = parts[3].replace("%", "").strip()

        try:

            cpu = float(cpu_text)

            memory_percent = float(
                memory_percent_text
            )

        except ValueError:

            continue

        stats[name] = {
            "cpu": cpu,
            "memory_usage": memory_usage_text,
            "memory_percent": memory_percent
        }

    return stats


# ---------------------------------------------------------
# MONITOR DOCKER CONTAINERS
# ---------------------------------------------------------

def monitor_containers(
    stop_event,
    cpu_samples,
    memory_samples
):

    while not stop_event.is_set():

        stats = get_docker_stats()

        for container in CONTAINERS:

            if container not in stats:
                continue

            cpu_samples[container].append(
                stats[container]["cpu"]
            )

            memory_samples[container].append(
                stats[container]["memory_percent"]
            )

        # Take a sample every 0.2 seconds
        time.sleep(0.2)


# ---------------------------------------------------------
# RUN ONE WORKLOAD
# ---------------------------------------------------------

def run_workload(concurrency):

    total_requests = (
        concurrency *
        REQUESTS_PER_WORKER
    )

    results = []


    # CPU samples
    cpu_samples = {
        container: []
        for container in CONTAINERS
    }


    # Memory samples
    memory_samples = {
        container: []
        for container in CONTAINERS
    }


    stop_event = threading.Event()


    monitor_thread = threading.Thread(
        target=monitor_containers,
        args=(
            stop_event,
            cpu_samples,
            memory_samples
        )
    )


    print()
    print("=" * 80)
    print(
        f"WORKLOAD W{concurrency} "
        f"({concurrency} CONCURRENT REQUESTS)"
    )
    print("=" * 80)


    # Start monitoring
    monitor_thread.start()


    # Start workload
    start_time = time.perf_counter()


    with ThreadPoolExecutor(
        max_workers=concurrency
    ) as executor:

        futures = []

        for _ in range(total_requests):

            futures.append(
                executor.submit(
                    send_request
                )
            )


        for future in as_completed(futures):

            results.append(
                future.result()
            )


    end_time = time.perf_counter()


    # Stop monitoring
    stop_event.set()

    monitor_thread.join()


    # -----------------------------------------------------
    # REQUEST METRICS
    # -----------------------------------------------------

    total_time = (
        end_time -
        start_time
    )


    successful = sum(
        1
        for result in results
        if result["success"]
    )


    failed = (
        total_requests -
        successful
    )


    response_times = [
        result["response_time"]
        for result in results
    ]


    average_response = statistics.mean(
        response_times
    )


    throughput = (
        successful /
        total_time
    )


    # -----------------------------------------------------
    # CPU METRICS
    # -----------------------------------------------------

    container_cpu = {}

    for container in CONTAINERS:

        samples = cpu_samples[container]

        if samples:

            container_cpu[container] = (
                statistics.mean(samples)
            )

        else:

            container_cpu[container] = 0.0


    # Average CPU across all three containers
    overall_cpu = statistics.mean(
        list(container_cpu.values())
    )


    # -----------------------------------------------------
    # MEMORY METRICS
    # -----------------------------------------------------

    container_memory = {}

    for container in CONTAINERS:

        samples = memory_samples[container]

        if samples:

            container_memory[container] = (
                statistics.mean(samples)
            )

        else:

            container_memory[container] = 0.0


    # Average memory utilization across containers
    overall_memory = statistics.mean(
        list(container_memory.values())
    )


    # -----------------------------------------------------
    # DISPLAY WORKLOAD RESULT
    # -----------------------------------------------------

    print(
        f"Total Requests        : "
        f"{total_requests}"
    )

    print(
        f"Successful Requests   : "
        f"{successful}"
    )

    print(
        f"Failed Requests       : "
        f"{failed}"
    )

    print(
        f"Average Response Time : "
        f"{average_response:.2f} ms"
    )

    print(
        f"Throughput            : "
        f"{throughput:.2f} requests/sec"
    )

    print(
        f"Average CPU           : "
        f"{overall_cpu:.2f}%"
    )

    print(
        f"Average Memory        : "
        f"{overall_memory:.2f}%"
    )


    print()
    print("CPU by container:")

    for container in CONTAINERS:

        print(
            f"  {container:<20}"
            f"{container_cpu[container]:.2f}%"
        )


    print()
    print("Memory by container:")

    for container in CONTAINERS:

        print(
            f"  {container:<20}"
            f"{container_memory[container]:.2f}%"
        )


    return {
        "workload": concurrency,
        "total": total_requests,
        "successful": successful,
        "failed": failed,
        "response": average_response,
        "throughput": throughput,
        "cpu": overall_cpu,
        "memory": overall_memory
    }


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print()
    print("=" * 80)
    print("CLOUD MICROSERVICE PERFORMANCE TEST")
    print("=" * 80)

    print()
    print(
        f"Target API: {URL}"
    )

    print(
        f"Requests per worker: "
        f"{REQUESTS_PER_WORKER}"
    )

    print()


    all_results = []


    for workload in WORKLOADS:

        result = run_workload(
            workload
        )

        all_results.append(
            result
        )


        # Pause between workloads
        time.sleep(3)


    # -----------------------------------------------------
    # FINAL TABLE
    # -----------------------------------------------------

    print()
    print()
    print("=" * 110)
    print("FINAL PERFORMANCE RESULTS")
    print("=" * 110)


    print(
        f"{'Workload':<10}"
        f"{'Concurrent':<12}"
        f"{'Requests':<10}"
        f"{'Avg RT(ms)':<15}"
        f"{'Throughput':<15}"
        f"{'Failed':<10}"
        f"{'CPU %':<12}"
        f"{'Memory %':<12}"
    )


    print("-" * 110)


    for result in all_results:

        print(
            f"W{result['workload']:<9}"
            f"{result['workload']:<12}"
            f"{result['total']:<10}"
            f"{result['response']:<15.2f}"
            f"{result['throughput']:<15.2f}"
            f"{result['failed']:<10}"
            f"{result['cpu']:<12.2f}"
            f"{result['memory']:<12.2f}"
        )


    print("=" * 110)


if __name__ == "__main__":

    main()