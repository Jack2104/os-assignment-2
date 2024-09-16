import json
import matplotlib.pyplot as plt

FRAME_MIN = 100
FP_SUFFIX = "_data.json"
FP_DIR = "data/"

file_names = ["bzip", "sixpack", "swim", "gcc"]


def plot_results(name, data_fp, min_frames):
    data = {}

    with open(data_fp, "r") as data_file:
        data = json.load(data_file)

    increments = data[name]["increments"]

    # curr_start_frame = 0
    curr_start_index = 50

    if name == "sixpack":
        curr_start_index = 100
    elif name == "gcc":
        curr_start_index = 100
    elif name == "swim":
        curr_start_index = 80

    # for count in increments:
    #     if curr_start_frame >= min_frames:
    #         break

    #     curr_start_index += 1
    #     curr_start_frame = count

    increments = data[name]["increments"][curr_start_index::]
    rand_results = data[name]["rand"][curr_start_index::]
    lru_results = data[name]["lru"][curr_start_index::]
    clock_results = data[name]["clock"][curr_start_index::]

    plt.plot(increments, rand_results, label="rand")
    plt.plot(increments, lru_results, label="lru")
    plt.plot(increments, clock_results, label="clock")

    plt.title(name)
    plt.xlabel("Frame Count")
    plt.ylabel("Page Fault Rate (%)")
    plt.legend(loc="upper right")

    plt.savefig(f"{name}_plot_constrained.png", bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    for trace in file_names:
        plot_results(trace, FP_DIR + trace + FP_SUFFIX, FRAME_MIN)
