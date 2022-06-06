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
        self.current_processes.remove(process)
        processor.add_process(process)

    def reset(self):
        self.usage = 0
        self.current_processes = []


class Process:
    def __init__(self, id: int, arrival_time: int, burst_time: int, processor_usage: float):
        self.id = id
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
