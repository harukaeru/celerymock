def get_current_turn():
    with open(f"mutexfiles/turn", 'r') as f:
        return f.read()


def give_turn_to(next_process_id):
    with open(f"mutexfiles/turn", 'w') as f:
        return f.write(str(next_process_id))


def read_flag(process_id):
    with open(f"mutexfiles/{process_id}", 'r') as f:
        return f.read() == '1'


def flag_on(process_id):
    with open(f"mutexfiles/{process_id}", 'w') as f:
        f.write('1')


def flag_off(process_id):
    with open(f"mutexfiles/{process_id}", 'w') as f:
        f.write('0')


def p_mutex(process_id):
    other_process_id = 1 - process_id
    flag_on(process_id)

    while read_flag(other_process_id):
        turn = get_current_turn()
        flag_off(process_id)

        while turn == other_process_id:
            pass
        flag_on(process_id)


def v_mutex(process_id):
    other_process_id = 1 - process_id
    give_turn_to(other_process_id)
    flag_off(process_id)
