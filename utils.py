# Current Implementation: Milestone 1 and 2
# By Alexi Alberto and Elmo Mandigma

import time

def get_timestamp():
    return int(time.time())

def log(message, verbose=True):
    if verbose:
        for field in str(message).split(','):
            print(f"[{time.strftime('%H:%M:%S')}] {field.strip()}")
