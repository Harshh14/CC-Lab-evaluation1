import matplotlib.pyplot as plt


# Actual measured results from the workload test
concurrency = [1, 2, 4, 8, 16]

response_time = [
    12.32,
    12.47,
    15.24,
    27.22,
    58.11
]

throughput = [
    79.82,
    157.92,
    256.22,
    283.79,
    265.16
]


# Graph 1: Concurrent Requests vs Response Time
plt.figure(figsize=(8, 5))

plt.plot(
    concurrency,
    response_time,
    marker="o"
)

plt.xlabel("Concurrent Requests")
plt.ylabel("Average Response Time (ms)")
plt.title("Concurrent Requests vs Average Response Time")

plt.xticks(concurrency)

plt.grid(True)

plt.savefig(
    "response_time_graph.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# Graph 2: Concurrent Requests vs Throughput
plt.figure(figsize=(8, 5))

plt.plot(
    concurrency,
    throughput,
    marker="o"
)

plt.xlabel("Concurrent Requests")
plt.ylabel("Throughput (Requests/sec)")
plt.title("Concurrent Requests vs Throughput")

plt.xticks(concurrency)

plt.grid(True)

plt.savefig(
    "throughput_graph.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()