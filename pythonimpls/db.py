import os
import datetime
import json
from mutex import p_mutex, v_mutex


task_funcs = {}


def enqueue(func_name, *args, **kwargs):
    serialized_data = json.dumps([func_name, args, kwargs])
    filename = str(datetime.datetime.timestamp(datetime.datetime.now()))
    with open(f'database/{filename}', 'w') as f:
        f.write(serialized_data)


def dequeue(process_id):
    p_mutex(process_id)
    filenames = os.listdir('database')
    if not len(filenames):
        v_mutex(process_id)
        return

    peek_filename = f'database/{filenames[0]}'
    with open(peek_filename, 'r') as f:
        data = json.loads(f.read())
    func_name = data[0]
    task_func = task_funcs[func_name]
    task_func(*data[1], **data[2])
    os.remove(peek_filename)
    v_mutex(process_id)
