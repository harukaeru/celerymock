from taskfy import taskfy


@taskfy
def add(a, b):
    c = a + b
    print(c)
    return c
