# Current Implementation: Milestone 1 and 2
# By Alexi Alberto and Elmo Mandigma

import socket
import threading
from message_parser import parse_message, craft_message
from peer_state import update_peer, store_post, store_dm
from constants import PORT, BROADCAST_ADDR, BUFFER_SIZE
from utils import log, get_timestamp

# Change your IP and user ID if needed
my_user_id = "you@192.168.100.171" #pull from csv file. not hardcoded

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', PORT))

def start_listener(verbose=False):
    def listen():
        while True:
            try:
                data, addr = sock.recvfrom(BUFFER_SIZE)
                msg = parse_message(data)
                if not msg:
                    continue
                if verbose:
                    log(f"< RECV from {addr[0]}: {msg}", verbose)
                handle_message(msg, addr[0], verbose)
            except Exception as e:
                log(f"Error: {e}", verbose)
    thread = threading.Thread(target=listen, daemon=True)
    thread.start()

def send_message(msg_dict, addr=BROADCAST_ADDR, verbose=False):
    message = craft_message(msg_dict)
    if verbose:
        log(f"> SEND to {addr}: {msg_dict}", verbose)
    sock.sendto(message, (addr, PORT))

def send_ping(verbose=False):
    ping = {
        "TYPE": "PING",
        "USER_ID": my_user_id
    }
    send_message(ping, BROADCAST_ADDR, verbose)

def send_profile(verbose=False):
    profile = {
        "TYPE": "PROFILE",
        "USER_ID": my_user_id,
        "DISPLAY_NAME": "You", #pull string from independent csv file
        "STATUS": "Ready to connect!"
    }
    send_message(profile, BROADCAST_ADDR, verbose)

def send_follow(target_user_id, verbose=False):
    follow = {
        "TYPE": "FOLLOW",
        "FROM": my_user_id,
        "TO": target_user_id,
        "MESSAGE_ID": "f" + str(get_timestamp()),
        "TIMESTAMP": str(get_timestamp()),
        "TOKEN": f"{my_user_id}|{get_timestamp()+3600}|follow"
    }
    send_message(follow, addr=target_user_id.split('@')[1], verbose=verbose)

def send_unfollow(target_user_id, verbose=False):
    unfollow = {
        "TYPE": "UNFOLLOW",
        "FROM": my_user_id,
        "TO": target_user_id,
        "MESSAGE_ID": "u" + str(get_timestamp()),
        "TIMESTAMP": str(get_timestamp()),
        "TOKEN": f"{my_user_id}|{get_timestamp()+3600}|follow"
    }
    send_message(unfollow, addr=target_user_id.split('@')[1], verbose=verbose)

def handle_message(msg, ip, verbose):
    mtype = msg.get("TYPE")
    if mtype == "PING":
        send_profile(verbose=verbose)
    elif mtype == "PROFILE":
        update_peer(
            msg.get("USER_ID"),
            msg.get("DISPLAY_NAME"),
            msg.get("STATUS")
        )
    elif mtype == "POST":
        store_post(msg.get("USER_ID"), msg.get("CONTENT"))
    elif mtype == "DM":
        store_dm(msg.get("FROM"), msg.get("CONTENT"))
    elif mtype == "FOLLOW":
        from_user = msg.get("FROM")
        print(f"User {from_user} has followed you.")
    elif mtype == "UNFOLLOW":
        from_user = msg.get("FROM")
        print(f"User {from_user} has unfollowed you.")
