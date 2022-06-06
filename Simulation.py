from random import randint, uniform, choice
from Processor import Processor, Process
from Visualization import ProcessVisualization
import matplotlib.pyplot as plt
import numpy as np


class Generator:
    def __init__(self, processes_amount=100, processors_amount=16):
        self.processes = processes_amount
        self.processors = processors_amount - 1

        self.density = 3
        self.max_simultaneous = 3
        self.simultaneous_randomness = 7
        self.min_usage = 0.03
        self.max_usage = 0.5
        self.min_burst = 0
        self.max_burst = 10

    def set_density(self, density: int):
        if density > 0:
            self.density = density

    def set_max_simultaneous(self, max: int):
        if max >= 0:
            self.max_simultaneous = max

    def set_simultaneous_randomness(self, random: int):
        if 0 <= random <= 10:
            self.simultaneous_randomness = random

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
        counter = 0
        processes_list = []
        for i in range(self.processes):
            if counter == self.max_simultaneous or randint(0, 10) >= self.simultaneous_randomness:
                counter = 0
                last_arrival += randint(1, self.density)
            processes_list.append(
                Process(randint(0, self.processors),
                        last_arrival,
                        randint(self.min_burst, self.max_burst),
                        round(uniform(self.min_usage, self.max_usage), 2)))

        return processes_list


def handle_process(processor, process, parameters: list) -> bool:
    max_attempts, max_usage, _, _, _ = parameters
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
            if processor.usage + process.processor_usage <= 1:
                processor.add_process(process)
                return True
            else:
                return False


def handle_waiting_processes(waiting_processes: list, process, parameters: list):
    for waiting_process in waiting_processes:
        if handle_process(processors[waiting_process.id], waiting_process, parameters):
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
                        parameters[3] += 1
                        equal_usage(chosen_processor, processor, parameters)


def equal_usage(processor1, processor2, parameters: list):
    processor1.current_processes.sort(key=lambda x: x.processor_usage)
    for i in range(parameters[2]):
        if len(processor1.current_processes) > 0:
            if processor2.usage < parameters[1] and processor2.usage < processor1.usage:
                parameters[4] += 1
                processor1.migrate_process(processor1.current_processes[0], processor2)
        else:
            break


def update_processors_usage(current_time: int, parameters: list):
    for processor in processors:
        for process in processor.current_processes:
            if current_time >= process.arrival_time + process.waiting_time + process.burst_time:
                processor.complete_process(process)
                handle_process_migration(parameters)


def add_current_usage(processors_usages, logs):
    processors_usages[logs] = [i.usage for i in processors]


def is_finished() -> bool:
    for i in processors:
        if len(i.current_processes) > 0:
            return True
    return False


def start(title: str, max_attempts: int, max_usage: float, max_migrations=0):
    processors_usages = np.ndarray([processes_amount + 10, processors_amount])
    logs = 0

    parameters = [max_attempts, max_usage, max_migrations, 0, 0]
    [i.reset() for i in processors]
    [i.reset() for i in processes]
    avg_usages = []

    waiting_processes = []
    for process in processes:
        current_time = process.arrival_time

        update_processors_usage(current_time, parameters)
        handle_waiting_processes(waiting_processes, process, parameters)
        handle_process_migration(parameters)

        if not handle_process(processors[process.id], process, parameters):
            waiting_processes.append(process)

        add_current_usage(processors_usages, logs)
        logs += 1

    for processor in processors:
        processor.current_processes.sort(key=lambda x: x.completion_time)

    while is_finished():
        process = 0
        for processor in processors:
            if len(processor.current_processes) > 0:
                process = processor.current_processes[0]
                processor.complete_process(process)

        if not process == 0:
            handle_waiting_processes(waiting_processes, process, parameters)
            handle_process_migration(parameters)

        add_current_usage(processors_usages, logs)
        logs += 1

    processors_usages = processors_usages[:logs, :]
    fig, (ax1, ax2) = plt.subplots(2)
    fig.suptitle(title)
    fig.set_size_inches(20, 10)
    ax1.bar([i.id for i in processors], np.mean(processors_usages, axis=0))
    ax2.plot(np.linspace(1, logs, logs), np.mean(processors_usages, axis=1))
    ax2.axhline(y=np.mean(processors_usages), color='r', label="All Time AVG")
    plt.legend()
    fig.savefig(title + ".png")
    plt.show()

    print(f"Asks for usage: {parameters[3]}, Process migrations: {parameters[4]}")


processes_amount = 1000
processors_amount = 50

processors = [Processor(i) for i in range(processors_amount)]
generator = Generator(processes_amount, processors_amount)
generator.set_density(2)
generator.set_max_simultaneous(15)
generator.set_min_burst_time(7)
generator.set_max_burst_time(40)
processes = generator.create()

ProcessVisualization(processes)

start("1", 1, 0.7)
start("2", processors_amount, 0.7)
start("3", processors_amount, 0.7, 5)
