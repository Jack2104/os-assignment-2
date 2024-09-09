import gzip
import numpy as np
import math
import matplotlib.pyplot as plt
import sys
from clockmmu import ClockMMU
from lrummu import LruMMU
from randmmu import RandMMU

PAGE_OFFSET = 12  # page is 2^12 = 4KB

class Trace():
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
       
file_names = [ 'bzip', 'sixpack', 'swim', 'gcc' ]
traces = []   

for file in file_names:
    curr_traces = []   
    
    with gzip.open(file + '.trace.gz', 'rt') as file:
        for trace_line in file.read().split("\n"):
            curr_trace = trace_line.split()
            
            if len(curr_trace) == 0:
                continue
            
            logical_address = int(curr_trace[0], 16)
            curr_trace[0] = logical_address >> PAGE_OFFSET
            
            curr_traces.append(curr_trace)
              
    traces.append(Trace(file, np.array(curr_traces)))


for x in range(1,2):
    print(str(x * 10) + "% of unique frames" )

    for i in range(0, 4):
        traces[i].increments.append(x * 0.1)
        
        frames = int(math.ceil(traces[i].UniqueFrames() * x * 0.1))
        rand = RandMMU(frames)
        lru = LruMMU(frames)
        clock = ClockMMU(frames)
        
        for j in range(0, traces[i].NumMemoryAccesses()):
            if (j % 10000 == 0):
                print("\rtrace : " + file_names[i] + " mem. address : " + str(j), end='')
            trace_cmd = traces[i].traces[j]
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

