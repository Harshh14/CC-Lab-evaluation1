import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed


URL = "http://localhost:5003/enrollment/101"

WORKLOADS = [1, 2, 4, 8, 16]

REQUESTS_PER_USER = 10


def send_request():
    start_time = time.perf_counter()

    try:
        response = requests.get(URL, timeout=10)

        end_time = time.perf_counter()

        response_time = (end_time - start_time) * 1000

        return {
            "success": response.status_code == 200,
            "response_time": response_time
        }

    except requests.RequestException:
        end_time = time.perf_counter()

        response_time = (end_time - start_time) * 1000

        return {
            "success": False,
            "response_time": response_time
        }


def run_workload(concurrency):

    total_requests = concurrency * REQUESTS_PER_USER

    results = []

    start_time = time.perf_counter()

    with ThreadPoolExecutor(max_workers=concurrency) as executor:

        futures = [
            executor.submit(send_request)
            for _ in range(total_requests)
        ]

        for future in as_completed(futures):
            results.append(future.result())

    end_time = time.perf_counter()

    total_time = end_time - start_time

    successful_requests = sum(
        1 for result in results
        if result["success"]
    )

    failed_requests = total_requests - successful_requests

    response_times = [
        result["response_time"]
        for result in results
    ]

    average_response_time = statistics.mean(response_times)

    throughput = successful_requests / total_time

    return {
        "concurrency": concurrency,
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "average_response_time": average_response_time,
        "throughput": throughput
    }


def main():

    print("=" * 70)
    print("CLOUD MICROSERVICE LOAD TEST")
    print("=" * 70)

    print(f"Target API: {URL}")
    print(f"Requests per concurrent user: {REQUESTS_PER_USER}")
    print()

    results = []

    for workload in WORKLOADS:

        print("-" * 70)
        print(f"Testing concurrency level: {workload}")

        result = run_workload(workload)

        results.append(result)

        print(f"Total Requests       : {result['total_requests']}")
        print(f"Successful Requests  : {result['successful_requests']}")
        print(f"Failed Requests      : {result['failed_requests']}")
        print(
            f"Average Response Time: "
            f"{result['average_response_time']:.2f} ms"
        )
        print(
            f"Throughput           : "
            f"{result['throughput']:.2f} requests/sec"
        )

        time.sleep(2)

    print()
    print("=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)

    print(
        f"{'Concurrency':<15}"
        f"{'Avg Response(ms)':<20}"
        f"{'Throughput(req/s)':<20}"
        f"{'Failed':<10}"
    )

    for result in results:

        print(
            f"{result['concurrency']:<15}"
            f"{result['average_response_time']:<20.2f}"
            f"{result['throughput']:<20.2f}"
            f"{result['failed_requests']:<10}"
        )


if __name__ == "__main__":
    main()