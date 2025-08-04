# Current Implementation: Milestone 1 and 2
# By Alexi Alberto and Elmo Mandigma

import time
import argparse
import csv
import uuid
from networking import (
    send_message, start_listener,
    send_profile, send_ping,
    send_follow, send_unfollow
)
from peer_state import print_known_peers, print_messages
from utils import get_timestamp
from constants import PROFILE_INTERVAL

status = "Ready to connect!"  # Default status

def set_status(new_status):
    global status
    status = new_status

def load_my_user_id(csv_path="USER.csv"):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        user = next(reader)
        return user["my_user_id"]
    
my_user_id = load_my_user_id()  # Replace with your real IP

def create_post():
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

def create_dm(target):
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

def print_key_value_message(msg):
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
  profile                             - Send your profile
  ping                                - Manually broadcast a PING
  status <new_status>                 - Update your status
  show peers                          - Show known peers
  show messages                       - Show received posts and DMs
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
                        print(f"TYPE: {dm_msg['type']}\n"
                              f"FROM: {dm_msg['FROM']}\n"
                              f"TO: {dm_msg['TO']}\n"
                              f"CONTENT: {dm_msg['CONTENT']}\n")
                    else:
                        print_key_value_message(dm_msg)
                    send_message(dm_msg, addr=to.split("@")[1], verbose=VERBOSE)
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
            elif cmd.startswith("status"):
                new_status = cmd[len("status") :].strip()
                set_status(new_status)
                print(f"Status updated to: {status}")
            elif cmd == "exit": # Exit the program
                print("Exiting LSNP...")
                break
            elif cmd == "": # Ignore empty input
                continue
            else: # Unknown command
                print("Unknown command. Type 'help' for options.")

    except KeyboardInterrupt:
        print("\nInterrupted. Exiting LSNP...")