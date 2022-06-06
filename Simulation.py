from random import randint, uniform, choice
import matplotlib.pyplot as plt
import numpy as np


class Processor:
    def __init__(self, id: int):
        self.id = id
        self.usage = 0.0
        self.current_processes = []

    def complete_process(self, process):
        process.completed = True
        self.usage -= process.processor_usage
        self.usage = round(self.usage, 2)
        self.current_processes.remove(process)

    def add_process(self, process):
        process.completion_time = process.arrival_time + process.waiting_time + process.burst_time
        self.current_processes.append(process)
        self.usage += process.processor_usage
        self.usage = round(self.usage, 2)

    def migrate_process(self, process, processor):
        self.usage -= process.processor_usage
        self.usage = round(self.usage, 2)
        processor.add_process(process)

    def reset(self):
        self.usage = 0
        self.current_processes = []


class Process:
    def __init__(self, arrival_time: int, burst_time: int, processor_usage: float):
        self.arrival_time = arrival_time
        self.waiting_time = 0
        self.burst_time = burst_time
        self.completion_time = -1
        self.processor_usage = processor_usage
        self.completed = False

    def __str__(self) -> str:
        return str(f"AT:{self.arrival_time},WT:{self.waiting_time},BT:{self.burst_time},PU:{self.processor_usage},"
                   f"C:{self.completed}")

    def reset(self):
        self.waiting_time = 0
        self.completion_time = -1
        self.completed = False


class Generator:
    def __init__(self, processes=100):
        self.processes = processes
        self.density = 3
        self.min_usage = 0.03
        self.max_usage = 0.5
        self.min_burst = 0
        self.max_burst = 10

    def set_density(self, density: int):
        if density >= 0:
            self.density = density

    def set_min_processor_usage(self, min_usage: float):
        if 0 <= min_usage <= 1:
            self.min_usage = min_usage

    def set_max_processor_usage(self, max_usage: float):
        if 0 <= max_usage <= 1:
            self.max_usage = max_usage

    def set_min_burst_time(self, min_burst: int):
        if min_burst >= 0:
            self.min_burst = min_burst

    def set_max_burst_time(self, max_burst: int):
        if max_burst >= 0:
            self.max_burst = max_burst

    def create(self) -> list:
        last_arrival = 0
        processes_list = []
        for i in range(self.processes):
            last_arrival += randint(0, self.density)
            processes_list.append(
                Process(last_arrival,
                        randint(self.min_burst, self.max_burst),
                        round(uniform(self.min_usage, self.max_usage), 2)))

        return processes_list


def handle_process(processor, process, parameters: list) -> bool:
    max_attempts, max_usage, _, _ = parameters
    processors_to_choose = [i for i in processors if i != processor]
    for i in range(max_attempts):
        chosen_processor = choice(processors_to_choose)
        if chosen_processor.usage < max_usage:
            parameters[3] += 1
            if chosen_processor.usage + process.processor_usage <= 1:
                chosen_processor.add_process(process)
                parameters[4] += 1
                return True
            else:
                return False
        processors_to_choose.remove(chosen_processor)
        if len(processors_to_choose) == 0 or i == max_attempts - 1:
            if chosen_processor.usage + process.processor_usage <= 1:
                processor.add_process(process)
                return True
            else:
                return False


def handle_waiting_processes(waiting_processes: list, processor, process, parameters: list):
    for waiting_process in waiting_processes:
        if handle_process(processor, process, parameters):
            waiting_process.waiting_time = process.completion_time - waiting_process.arrival_time
            waiting_processes.remove(waiting_process)


def handle_process_migration(parameters: list):
    if parameters[2] > 0:
        for processor in processors:
            if processor.usage < parameters[1]:
                processors_to_choose = [i for i in processors if i != processor]
                for i in range(len(processors) - 1):
                    chosen_processor = choice(processors_to_choose)
                    if chosen_processor.usage > parameters[1]:
                        equal_usage(chosen_processor, processor, parameters)


def equal_usage(processor1, processor2, parameters: list):
    processor1.current_processes.sort(key=lambda x: x.processor_usage)
    for i in range(parameters[2]):
        if processor2.usage < parameters[1]:
            processor1.migrate_process(processor1.current_processes[i], processor2)


def update_processors_usage(current_time: int, waiting_processes: list, parameters: list):
    for processor in processors:
        for process in processor.current_processes:
            if current_time >= process.arrival_time + process.waiting_time + process.burst_time:
                processor.complete_process(process)
                handle_waiting_processes(waiting_processes, processor, process, parameters)
                handle_process_migration(parameters)


def add_current_usage(avg_usages: list):
    avg = sum(i.usage for i in processors) / processors_amount
    avg_usages.append(avg)


def is_finished() -> bool:
    for i in processors:
        if len(i.current_processes) > 0:
            return True
    return False


def start(title: str, max_attempts: int, max_usage: float, max_migrations=0):
    parameters = [max_attempts, max_usage, max_migrations, 0, 0]
    [i.reset() for i in processors]
    [i.reset() for i in processes]
    avg_usages = []

    waiting_processes = []
    for process in processes:
        current_time = process.arrival_time
        update_processors_usage(current_time, waiting_processes, parameters)
        processor = choice(processors)
        if not handle_process(processor, process, parameters):
            waiting_processes.append(process)

        add_current_usage(avg_usages)

    for processor in processors:
        processor.current_processes.sort(key=lambda x: x.completion_time)

    while is_finished():
        for processor in processors:
            if len(processor.current_processes) > 0:
                process = processor.current_processes[0]
                processor.complete_process(process)
                handle_waiting_processes(waiting_processes, processor, process, parameters)

        add_current_usage(avg_usages)

    plt.plot(np.linspace(1, len(avg_usages), len(avg_usages)), avg_usages, label="Part AVG")
    plt.axhline(y=(sum(avg_usages) / len(avg_usages)), color='r', label="All Time AVG")
    ax = plt.gca()
    ax.set_ylim([0, 1])
    ax.set_title(title)
    plt.legend()
    plt.show()

    print(f"Asks for usage: {parameters[3]}, Process migrations: {parameters[4]}")


processors_amount = 5

processors = [Processor(i) for i in range(processors_amount)]
generator = Generator()
generator.set_density(1)
generator.set_min_burst_time(3)
processes = generator.create()

start("1", 2, 0.7)
start("2", processors_amount, 0.7)
start("3", processors_amount, 0.7, 5)
