# Current Implementation: Milestone 1 and 2
# By Alexi Alberto and Elmo Mandigma

import socket
import threading
import csv
import time
from message_parser import parse_message, craft_message
from peer_state import (
    update_peer, store_post, store_dm, follow_user,
    unfollow_user, is_following, create_group, update_group,
    store_group_message, is_group_member, get_group_name
)
from game import (
    store_tictactoe_invite, store_tictactoe_move, store_tictactoe_result, print_board
)
from constants import PORT, BROADCAST_ADDR, BUFFER_SIZE
from utils import log, get_timestamp

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

# Function to validate the token
def validate_token(token, expected_scope):
    try:
        user_id, expiry, scope = token.split('|')
        expiry = int(expiry)
        if time.time() > expiry:
            return False
        if scope != expected_scope:
            return False
        return True
    except Exception:
        return False

# Start a thread to listen for incoming messages
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

def send_profile(status="Ready to connect!", verbose=False):
    profile = {
        "TYPE": "PROFILE",
        "USER_ID": my_user_id,
        "DISPLAY_NAME": display_name,  # pulled from CSV
        "STATUS": status
    }
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

def handle_message(msg, ip, verbose):
    mtype = msg.get("TYPE")
    token = msg.get("TOKEN")
    # Validate for POST and DM
    if mtype in ["POST", "DM"]:
        expected_scope = "broadcast" if mtype == "POST" else "chat"
        if not validate_token(token, expected_scope):
            if verbose:
                print(f"Invalid token for {mtype} from {msg.get('USER_ID')}")
            return  # Ignore message with invalid token
    # Groups
    elif mtype in ["GROUP_CREATE", "GROUP_UPDATE", "GROUP_MESSAGE"]:
        if not validate_token(token, "group"):
            if verbose:
                print(f"Invalid token for {mtype} from {msg.get('FROM')}")
            return
    if mtype == "GROUP_CREATE":
        group_id = msg.get("GROUP_ID")
        group_name = msg.get("GROUP_NAME")
        members = msg.get("MEMBERS", "").split(",")
        creator = msg.get("FROM")
        create_group(group_id, group_name, members, creator)
        if my_user_id in members:
            print(f"You’ve been added to {group_name}")
        if verbose:
            print(f"Created group {group_name} ({group_id}) with members: {members}")
    elif mtype == "GROUP_UPDATE":
        group_id = msg.get("GROUP_ID")
        add = msg.get("ADD", "")
        remove = msg.get("REMOVE", "")
        add_list = [u for u in add.split(",") if u] if add else []
        remove_list = [u for u in remove.split(",") if u] if remove else []
        update_group(group_id, add=add_list, remove=remove_list)
        print(f'The group “{get_group_name(group_id)}” member list was updated.')
        if verbose:
            print(f"Group {group_id} updated. Added: {add_list}, Removed: {remove_list}")
    elif mtype == "GROUP_MESSAGE":
        group_id = msg.get("GROUP_ID")
        sender = msg.get("FROM")
        content = msg.get("CONTENT")
        if is_group_member(group_id, my_user_id):
            store_group_message(msg)
            print(f'{sender} sent “{content}”')
        elif verbose:
            print(f"Ignored group message for {group_id} (not a member).")
    # Commands
    elif mtype == "FOLLOW":
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
    # Game
    elif mtype == "TICTACTOE_INVITE":
        if not validate_token(token, "game"):
            return
        store_tictactoe_invite(msg)
        if not verbose:
            print(f"{msg['FROM'].split('@')[0]} is inviting you to play tic-tac-toe.")
        else:
            print(msg)
    elif mtype == "TICTACTOE_MOVE":
        if not validate_token(token, "game"):
            return
        store_tictactoe_move(msg)
        print_board(msg["GAMEID"])
    elif mtype == "TICTACTOE_RESULT":
        store_tictactoe_result(msg)
        print_board(msg["GAMEID"])