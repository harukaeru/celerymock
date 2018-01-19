from db import dequeue, task_funcs
from add import add


def run_worker(process_number):
    task_funcs['add'] = add.run

    while True:
        dequeue(process_number)
