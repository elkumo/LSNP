# Current Implementation: Milestone 1-3
# By Alexi Alberto and Elmo Mandigma

import time
import argparse
import csv
import uuid
import random
from game import print_board, store_tictactoe_invite, store_tictactoe_move, store_tictactoe_result
from networking import (
    send_message, start_listener,
    send_profile, send_ping,
    send_follow, send_unfollow
)
from peer_state import print_known_peers, print_messages, print_group_messages, groups, get_group_name
from utils import get_timestamp
from constants import PROFILE_INTERVAL

status = "Ready to connect!"  # Default status
last_tictactoe_to = None
last_tictactoe_gid = None

def set_status(new_status): # Update the global status variable
    global status
    status = new_status

def load_my_user_id(csv_path="USER.csv"): # Load my_user_id from USER.csv
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        user = next(reader)
        return user["my_user_id"]
    
my_user_id = load_my_user_id()

def create_post(): # Create a post message
    content = input("Post content: ").strip()
    now = get_timestamp()
    message_id = uuid.uuid4().hex[:8]
    return {
        "TYPE": "POST",
        "USER_ID": my_user_id,
        "CONTENT": content,
        "TTL": "3600",
        "MESSAGE_ID": message_id,
        "TOKEN": f"{my_user_id}|{now + 3600}|broadcast"
    }

def create_dm(target): # Create a direct message
    now = get_timestamp()
    message_id = uuid.uuid4().hex[:8]
    content = input("Message: ").strip()
    return {
        "TYPE": "DM",
        "FROM": my_user_id,
        "TO": target,
        "CONTENT": content,
        "TIMESTAMP": str(now),
        "MESSAGE_ID": message_id,
        "TOKEN": f"{my_user_id}|{now + 3600}|chat"
    }

def create_group_msg(): # Create a group message for creating a new group
    group_id = input("Group ID: ").strip()
    group_name = input("Group Name: ").strip()
    members = input("Members (comma-separated user@ip): ").strip()
    now = get_timestamp()
    return {
        "TYPE": "GROUP_CREATE",
        "FROM": my_user_id,
        "GROUP_ID": group_id,
        "GROUP_NAME": group_name,
        "MEMBERS": members,
        "TIMESTAMP": str(now),
        "TOKEN": f"{my_user_id}|{now + 3600}|group"
    }

def update_group_msg(): # Add or Remove members from a group
    group_id = input("Group ID: ").strip()
    add = input("Add members (comma-separated user@ip, blank for none): ").strip()
    remove = input("Remove members (comma-separated user@ip, blank for none): ").strip()
    now = get_timestamp()
    return {
        "TYPE": "GROUP_UPDATE",
        "FROM": my_user_id,
        "GROUP_ID": group_id,
        "ADD": add,
        "REMOVE": remove,
        "TIMESTAMP": str(now),
        "TOKEN": f"{my_user_id}|{now + 3600}|group"
    }

def group_message_msg(): # Create a group message
    group_id = input("Group ID: ").strip()
    content = input("Message: ").strip()
    now = get_timestamp()
    return {
        "TYPE": "GROUP_MESSAGE",
        "FROM": my_user_id,
        "GROUP_ID": group_id,
        "CONTENT": content,
        "TIMESTAMP": str(now),
        "TOKEN": f"{my_user_id}|{now + 3600}|group"
    }

def show_group_members(): # Show members of a group
    group_id = input("Group ID: ").strip()
    if group_id in groups:
        members = groups[group_id]["members"]
        print(f"Members of group '{get_group_name(group_id)}': {', '.join(members)}")
    else:
        print(f"Group '{group_id}' does not exist.")

def create_tictactoe_invite(): # Create a Tic Tac Toe invite message
    global last_tictactoe_to, last_tictactoe_gid
    to = input("Invite who (user@ip): ").strip()
    gid = f"g{random.randint(1, 255)}"
    symbol = input("Your symbol (X/O): ").strip().upper()
    now = get_timestamp()
    last_tictactoe_to = to
    last_tictactoe_gid = gid
    return {
        "TYPE": "TICTACTOE_INVITE",
        "FROM": my_user_id,
        "TO": to,
        "GAMEID": gid,
        "MESSAGE_ID": uuid.uuid4().hex[:8],
        "SYMBOL": symbol,
        "TIMESTAMP": str(now),
        "TOKEN": f"{my_user_id}|{now + 3600}|game"
    }

def create_tictactoe_move(): # Create a Tic Tac Toe move message
    from game import games
    global last_tictactoe_to, last_tictactoe_gid
    gid = last_tictactoe_gid or input("Game ID: ").strip()
    pos = input("Position (0-8): ").strip()
    # Get symbol from games dict if available
    symbol = games[gid]["symbols"].get(my_user_id) if gid in games else None
    if not symbol:
        symbol = input("Your symbol (X/O): ").strip().upper()
    now = get_timestamp()
    to = last_tictactoe_to or input("To (user@ip): ").strip()
    turn = 1
    if gid in games:
        turn = games[gid].get("turn", 0) + 1
    return {
        "TYPE": "TICTACTOE_MOVE",
        "FROM": my_user_id,
        "TO": to,
        "GAMEID": gid,
        "MESSAGE_ID": uuid.uuid4().hex[:8],
        "POSITION": pos,
        "SYMBOL": symbol,
        "TURN": str(turn),
        "TOKEN": f"{my_user_id}|{now + 3600}|game"
    }

def print_key_value_message(msg): # Print message in key-value format
    for key in ["TYPE", "FROM", "TO", "CONTENT", "TIMESTAMP", "MESSAGE_ID", "TOKEN"]:
        if key in msg:
            print(f"{key}: {msg[key]}")

if __name__ == "__main__":
    # CLI arg to enable verbose mode
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()
    VERBOSE = args.verbose

    print("Starting LSNP peer...")
    start_listener(verbose=VERBOSE)
    send_profile(verbose=VERBOSE)

    print("\nLSNP is now running. Type 'help' or '?' for commands.\n")

    try:
        ping_profile_toggle = True
        last_ping = time.time()

        while True:
            # Periodic PING/PROFILE
            now = time.time()
            if now - last_ping > PROFILE_INTERVAL:
                if ping_profile_toggle:
                    send_ping(verbose=VERBOSE)
                else:
                    send_profile(verbose=VERBOSE)
                ping_profile_toggle = not ping_profile_toggle
                last_ping = now

            # User input loop
            cmd = input(">> ").strip()
            if cmd == "help" or cmd == "?" or cmd == "h":
                print("""
Available commands:
  help / h / ?                        - Show this help message
  post                                - Broadcast a post
  dm <user_id>                        - Send a direct message
  follow <user_id>                    - Follow a user
  unfollow <user_id>                  - Unfollow a user
  group create                        - Create a group
  group update                        - Update a group
  group msg                           - Send a message to a group
  ping                                - Manually broadcast a PING
  profile                             - Send your profile
  show messages                       - Show received posts and DMs
  show peers                          - Show known peers
  status <new_status>                 - Update your status
  tictactoe invite                    - Invite a user to play Tic Tac Toe
  tictactoe move                      - Make a move in a Tic Tac Toe game
  exit                                - Quit the program
""")
            elif cmd.startswith("post"): # Create a post
                post_msg = create_post()
                if not VERBOSE:
                    print(f"TYPE: {post_msg['TYPE']}\n"
                          f"USER_ID: {post_msg['USER_ID']}\n"
                          f"CONTENT: {post_msg['CONTENT']}\n")
                else:
                    print_key_value_message(post_msg)
                send_message(post_msg, verbose=VERBOSE)
            elif cmd.startswith("dm"):
                try:
                    parts = cmd.split(" ", 1)
                    to = parts[1]
                    dm_msg = create_dm(to)
                    if not VERBOSE:
                        print(f"TYPE: {dm_msg['TYPE']}\n"
                              f"FROM: {dm_msg['FROM']}\n"
                              f"TO: {dm_msg['TO']}\n"
                              f"CONTENT: {dm_msg['CONTENT']}\n")
                    else:
                        print_key_value_message(dm_msg)
                    send_message(dm_msg, addr=to.split("@")[1], verbose=VERBOSE)
                    print(f"You dmed {to}: {dm_msg['CONTENT']}")
                except:
                    print("Usage: dm <user_id>")
            elif cmd.startswith("follow"): # Follow a user
                to = cmd[7:].strip()
                send_follow(to, verbose=VERBOSE)
            elif cmd.startswith("unfollow"): # Unfollow a user
                to = cmd[9:].strip()
                send_unfollow(to, verbose=VERBOSE)
            elif cmd == "profile": # Manually broadcast profile
                send_profile(status=status, verbose=VERBOSE)
            elif cmd == "ping": # Manually broadcast a ping
                send_ping(verbose=VERBOSE)
            elif cmd == "show peers": # Show known peers
                print_known_peers()
            elif cmd == "show messages": # Show received posts and DMs
                print_messages()
            elif cmd.startswith("status"): # Update status
                new_status = cmd[len("status") :].strip()
                set_status(new_status)
                print(f"Status updated to: {status}")
            elif cmd.startswith("group create"): # Create a new group
                group_msg = create_group_msg()
                send_message(group_msg, verbose=VERBOSE)
            elif cmd.startswith("group update"): # Update an existing group
                group_msg = update_group_msg()
                send_message(group_msg, verbose=VERBOSE)
            elif cmd.startswith("group msg"): # Send a message to a group
                group_msg = group_message_msg()
                send_message(group_msg, verbose=VERBOSE)
            elif cmd == "show group messages": # Show messages in all groups
                print_group_messages()
            elif cmd.startswith("group members"): # Show members of a group
                show_group_members()
            elif cmd == "tictactoe invite": # Invite a user to play Tic Tac Toe
                msg = create_tictactoe_invite()
                send_message(msg, addr=msg["TO"].split("@")[1], verbose=VERBOSE)
                store_tictactoe_invite(msg)
                print_board(msg["GAMEID"])
                print(f"You sent a tictactoe invite to {msg['TO']} with Game ID {msg['GAMEID']}.\n"
                      f"You will be playing as {msg['SYMBOL']}\n")
            elif cmd == "tictactoe move": # Make a move in a Tic Tac Toe game
                msg = create_tictactoe_move()
                send_message(msg, addr=msg["TO"].split("@")[1], verbose=VERBOSE)
                store_tictactoe_move(msg)  # Update local board immediately
                print_board(msg["GAMEID"])
            elif cmd == "exit": # Exit the program
                print("Exiting LSNP...")
                break
            elif cmd == "": # Ignore empty input
                continue
            else: # Unknown command
                print("Unknown command. Type 'help' for options.")

    except KeyboardInterrupt: # Handle Ctrl+C gracefully
        print("\nInterrupted. Exiting LSNP...")