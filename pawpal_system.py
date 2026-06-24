from dataclasses import dataclass
from datetime import date


@dataclass
class Owner:
    name: str
    available_minutes: int


@dataclass
class Pet:
    name: str
    breed: str


@dataclass
class Task:
    name: str
    duration: int
    priority: str
    is_recurring: bool


class Schedule:
    def __init__(self, date: date):
        self.date = date
        self.tasks: list[Task] = []
        self.total_time: int = 0

    def add_task(self, task: Task) -> bool:
        pass

    def display(self) -> None:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: list[Task]):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks

    def generate(self) -> Schedule:
        pass

    def filter_by_time(self, time: int) -> list[Task]:
        pass
