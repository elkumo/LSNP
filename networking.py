# Current Implementation: Milestone 1 and 2
# By Alexi Alberto and Elmo Mandigma

import socket
import threading
import csv
import os
from message_parser import parse_message, craft_message
from peer_state import (
    update_peer, store_post, store_dm,
    follow_user, unfollow_user, is_following
)
from constants import PORT, BROADCAST_ADDR, BUFFER_SIZE
from utils import log, get_timestamp
from avatar_likes import handle_like_message
from file_transfer import handle_avatar_field, handle_file_offer, handle_file_chunk
## added this ^^
# Load my_user_id and display_name from USER.csv
def load_user_info(csv_path="USER.csv"):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        user = next(reader)
        return user["my_user_id"], user["display_name"]

my_user_id, display_name = load_user_info()

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
#send profile. changed 10:57am
def send_profile(status="Ready to connect!", verbose=False):
    profile = {
        "TYPE": "PROFILE",
        "USER_ID": my_user_id,
        "DISPLAY_NAME": display_name,
        "STATUS": status
    }
    # Attach avatar if it exists
    avatar_path = f"data/files/{my_user_id.replace('@', '_')}_avatar.png"
    if os.path.exists(avatar_path):
        with open(avatar_path, "rb") as img:
            encoded = base64.b64encode(img.read()).decode("utf-8")
            profile["AVATAR"] = f"data:image/png;base64,{encoded}"

    send_message(profile, BROADCAST_ADDR, verbose)

def send_follow(target_user_id, verbose=False):
    if '@' not in target_user_id:
        print("Invalid user ID format. Expected user@ip.")
        return
    ip = target_user_id.split('@')[1]
    follow = {
        "TYPE": "FOLLOW",
        "FROM": my_user_id,
        "TO": target_user_id,
        "MESSAGE_ID": "f" + str(get_timestamp()),
        "TIMESTAMP": str(get_timestamp()),
        "TOKEN": f"{my_user_id}|{get_timestamp()+3600}|follow"
    }
    send_message(follow, addr=ip, verbose=verbose)

def send_unfollow(target_user_id, verbose=False):
    if '@' not in target_user_id:
        print("Invalid user ID format. Expected user@ip.")
        return
    ip = target_user_id.split('@')[1]
    unfollow = {
        "TYPE": "UNFOLLOW",
        "FROM": my_user_id,
        "TO": target_user_id,
        "MESSAGE_ID": "u" + str(get_timestamp()),
        "TIMESTAMP": str(get_timestamp()),
        "TOKEN": f"{my_user_id}|{get_timestamp()+3600}|follow"
    }
    send_message(unfollow, addr=ip, verbose=verbose)

def handle_avatar_message(msg):
    print(f"[AVATAR] Avatar received from {msg.get('USER_ID')}")

def handle_message(msg, ip, verbose):
    mtype = msg.get("TYPE")
    if mtype == "FOLLOW":
        from_user = msg.get("FROM")
        follow_user(from_user)
        print(f"User {from_user} has followed you.")
    elif mtype == "UNFOLLOW":
        from_user = msg.get("FROM")
        unfollow_user(from_user)
        print(f"User {from_user} has unfollowed you.")
    elif mtype == "POST":
        sender = msg.get("USER_ID")
        if is_following(sender) or sender == my_user_id:
            store_post(msg)
            print(f"User {sender} has posted.\n"
                  f"CONTENT: {msg.get('CONTENT')}\n")
        else:
            if verbose:
                print(f"Ignored a post from {sender} because you are not following them.")
    elif mtype == "PING":
        send_profile(verbose=verbose)
    elif mtype == "PROFILE":
        update_peer(
            msg.get("USER_ID"),
            msg.get("DISPLAY_NAME"),
            msg.get("STATUS")
        )
        if verbose:
            print(f"TYPE: {msg.get('TYPE')}\n"
                  f"USER_ID: {msg.get('USER_ID')}\n"
                  f"DISPLAY_NAME: {msg.get('DISPLAY_NAME')}\n"
                  f"STATUS: {msg.get('STATUS')}\n")
        else:
            print(f"DISPLAY_NAME: {msg.get('DISPLAY_NAME')}\n"
                  f"STATUS: {msg.get('STATUS')}\n")
    elif mtype == "DM":
        store_dm(msg)
        print(f"DM from {msg.get('FROM')} to {msg.get('TO')}: {msg.get('CONTENT')}")
    elif mtype == "FOLLOW":
        from_user = msg.get("FROM")
        print(f"User {from_user} has followed you.")
    elif mtype == "UNFOLLOW":
        from_user = msg.get("FROM")
        print(f"User {from_user} has unfollowed you.")
        # Avatar, Like, and File Transfer handlers, added
        if "AVATAR" in msg:
            handle_avatar_message(msg)
            handle_avatar_field(msg)
        if mtype == "LIKE":
            handle_like_message(msg)
        if mtype == "FILE_OFFER":
            handle_file_offer(msg)
        if mtype == "FILE_CHUNK":
            handle_file_chunk(msg)