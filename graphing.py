# This file is for taking a trace values and turning them into a graph

# import libraroes
import json
import matplotlib.pyplot as plt

# Open the file
trace = "swim"

with open(trace+"_data.json") as json_file:
    data = json.load(json_file)
    data = data[trace]

# get increments values and line values
increments = data["increments"]
rand,lru,clock = data["rand"],data["lru"],data["clock"]

plt.plot(increments, rand, label="rand")
plt.plot(increments, lru, label="lru")
plt.plot(increments, clock, label="clock")

plt.title(trace)
plt.xlabel("Frame Count")
plt.ylabel("Page Fault Rate (%)")
plt.legend(loc="upper right")

plt.savefig(f"{trace}_plot.png", bbox_inches="tight")
plt.close()