import time

def get_timestamp():
    return int(time.time())

def log(message, verbose=True):
    if verbose:
        print(f"[{time.strftime('%H:%M:%S')}] {message}")
