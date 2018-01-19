from db import enqueue


class Task:
    def __init__(self, func):
        self.func = func

    def run(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def delay(self, *args, **kwargs):
        func_name = self.func.__name__
        enqueue(func_name, *args, **kwargs)


def taskfy(func):
    return Task(func)
