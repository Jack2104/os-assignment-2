import gzip
import numpy as np
import math
import matplotlib.pyplot as plt
import sys
from clockmmu import ClockMMU
from lrummu import LruMMU
from randmmu import RandMMU

PAGE_OFFSET = 12  # page is 2^12 = 4KB
MAX_INCREMENTS = (
    10  # Maximum number of increments (of cache sizes) that each trace will runn
)
FRAME_TABLE_MULTIPLE = 1.2  # The multiple that determines any "extra" space in the maximum frame table size


class Trace:
    def __init__(self, name, traces):
        self.name = name
        self.traces = traces
        self.increments = []
        self.rand_results = []
        self.lru_results = []
        self.clock_results = []

    def NumMemoryAccesses(self):
        return len(self.traces)

    def UniqueFrames(self):
        return len(np.unique(self.traces[0:, 0]))

    def collect_results(self, frame_count):
        rand = RandMMU(frame_count)
        lru = LruMMU(frame_count)
        clock = ClockMMU(frame_count)

        # Perform all the memory reads/writes for the current trace with the current frame count
        for trace_cmd in self.traces:
            if trace_cmd[1] == "R":
                rand.read_memory(trace_cmd[0])
                lru.read_memory(trace_cmd[0])
                clock.read_memory(trace_cmd[0])
            elif trace_cmd[1] == "W":
                rand.write_memory(trace_cmd[0])
                lru.write_memory(trace_cmd[0])
                clock.write_memory(trace_cmd[0])

        rand_fault_rate = rand.get_total_page_faults() / self.NumMemoryAccesses()
        lru_fault_rate = lru.get_total_page_faults() / self.NumMemoryAccesses()
        clock_fault_rate = clock.get_total_page_faults() / self.NumMemoryAccesses()

        self.rand_results.append(rand_fault_rate)
        self.lru_results.append(lru_fault_rate)
        self.clock_results.append(clock_fault_rate)

        trace.increments.append(frame_count)

    def plot_results(self):
        plt.plot(self.increments, self.rand_results, label="rand")
        plt.plot(self.increments, self.lru_results, label="lru")
        plt.plot(self.increments, self.clock_results, label="clock")

        plt.title(self.name)
        plt.xlabel("Frame Count")
        plt.ylabel("Page Fault Rate (%)")
        plt.legend(loc="upper right")

        plt.savefig(f"{self.name}_plot.png", bbox_inches="tight")
        plt.close()


file_names = ["bzip", "sixpack", "swim", "gcc"]
traces = []

for file_name in file_names:
    curr_traces = []

    with gzip.open(file_name + ".trace.gz", "rt") as file:
        for trace_line in file:
            curr_trace = trace_line.split()

            if len(curr_trace) == 0:
                continue

            logical_address = int(curr_trace[0], 16)
            curr_trace[0] = logical_address >> PAGE_OFFSET

            curr_traces.append(curr_trace)

    traces.append(Trace(file_name, np.array(curr_traces)))


# Loop through each trace
for trace in traces:
    print(f"\ncollecting results for {trace.name}...")

    # Determine the increment size for the current trace
    max_table_size = math.ceil(trace.UniqueFrames() * FRAME_TABLE_MULTIPLE)
    increment_size = math.ceil(max_table_size / MAX_INCREMENTS)

    print(
        f"| unique frames: {trace.UniqueFrames()}, total frames: {trace.NumMemoryAccesses()}"
    )
    print(f"| maximum frame count: {max_table_size}")
    print(f"| increment size: {increment_size}")
    print("| ")

    # Loop through each increment/frame_count for the current trace and collect the results (memory reads/writes)
    for frame_count in range(
        increment_size, max_table_size + increment_size, increment_size
    ):
        if frame_count % (increment_size) == 0:
            print(f"\r| frame count : {frame_count}", end="")

        trace.collect_results(frame_count)

    print("| ")
    print("| saving plot...")

    trace.plot_results()

    print("-> done!")

"""
for x in range(1, 2):
    print(str(x * 10) + "% of unique frames")

    for i in range(0, 4):
        traces[i].increments.append(x * 0.1)

        frames = int(math.ceil(traces[i].UniqueFrames() * x * 0.1))
        rand = RandMMU(frames)
        lru = LruMMU(frames)
        clock = ClockMMU(frames)

        for j, trace_cmd in enumerate(traces[i].traces):
            if j % 10000 == 0:
                print(
                    "\rtrace : " + file_names[i] + " mem. address : " + str(j), end=""
                )

            if trace_cmd[1] == "R":
                rand.read_memory(trace_cmd[0])
                lru.read_memory(trace_cmd[0])
                clock.read_memory(trace_cmd[0])
            elif trace_cmd[1] == "W":
                rand.write_memory(trace_cmd[0])
                lru.write_memory(trace_cmd[0])
                clock.write_memory(trace_cmd[0])

        rand_fault_rate = rand.get_total_page_faults() / traces[i].NumMemoryAccesses()
        lru_fault_rate = lru.get_total_page_faults() / traces[i].NumMemoryAccesses()
        clock_fault_rate = clock.get_total_page_faults() / traces[i].NumMemoryAccesses()

        traces[i].rand_results.append(rand_fault_rate)
        traces[i].lru_results.append(lru_fault_rate)
        traces[i].clock_results.append(clock_fault_rate)

        print()

for i in range(0, 4):
    plt.figure(i)

    plt.plot(traces[i].increments, traces[i].rand_results, label="rand")
    plt.plot(traces[i].increments, traces[i].lru_results, label="lru")
    plt.plot(traces[i].increments, traces[i].clock_results, label="clock")

    plt.show()
"""
