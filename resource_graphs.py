import matplotlib.pyplot as plt


# Final measured workload data
concurrency = [1, 2, 4, 8, 16]

cpu = [
    1.87,
    18.10,
    15.42,
    71.03,
    35.91
]

memory = [
    0.69,
    0.69,
    0.69,
    0.71,
    0.70
]


# -------------------------------------------------
# CPU GRAPH
# -------------------------------------------------

plt.figure(figsize=(8, 5))

plt.plot(
    concurrency,
    cpu,
    marker="o"
)

plt.xlabel("Concurrent Requests")
plt.ylabel("Average CPU Utilization (%)")
plt.title("Concurrent Requests vs CPU Utilization")

plt.xticks(concurrency)

plt.grid(True)

plt.savefig(
    "cpu_utilization_graph.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# -------------------------------------------------
# MEMORY GRAPH
# -------------------------------------------------

plt.figure(figsize=(8, 5))

plt.plot(
    concurrency,
    memory,
    marker="o"
)

plt.xlabel("Concurrent Requests")
plt.ylabel("Average Memory Utilization (%)")
plt.title("Concurrent Requests vs Memory Utilization")

plt.xticks(concurrency)

plt.grid(True)

plt.savefig(
    "memory_utilization_graph.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()