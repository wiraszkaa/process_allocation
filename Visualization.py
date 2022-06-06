import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from Processor import Process


def add_process(process: Process, ax, rows_coverage: list):
    if process.processor_usage >= 0.35:
        color = 'red'
    elif process.processor_usage >= 0.15:
        color = 'yellow'
    else:
        color = 'green'

    added = False
    for i, coverage in enumerate(rows_coverage):
        if coverage <= process.arrival_time:
            create_rectangle(ax, process, i, rows_coverage, color)
            added = True
            break

    if not added:
        rows_coverage.append(process.arrival_time + process.burst_time)
        i = len(rows_coverage) - 1
        create_rectangle(ax, process, i, rows_coverage, color)


def create_rectangle(ax, process, i, rows_coverage, color):
    ax.add_patch(Rectangle((process.arrival_time, i * 4), process.burst_time, 4, edgecolor='black', facecolor=color, fill=True))
    ax.text(process.arrival_time + 0.3, (i * 4) + 0.3, process_str(process), fontsize=7)
    rows_coverage[i] = process.arrival_time + process.burst_time


def process_str(process: Process):
    return f"{process.arrival_time}-{process.arrival_time + process.burst_time}\n{process.id}-{process.processor_usage}"


class ProcessVisualization:
    def __init__(self, processes: list):
        fig, ax = plt.subplots()
        fig.set_size_inches(40, 21)
        ax.plot(0, 0)
        rows_coverage = [0]

        for process in processes:
            add_process(process, ax, rows_coverage)

        fig.savefig('processes.png')
        plt.show()

