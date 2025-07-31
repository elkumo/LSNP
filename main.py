# Current Implementation: Milestone 1 and 2
# By Alexi Alberto and Elmo Mandigma

import time
import argparse
from networking import (
    send_message, start_listener,
    send_profile, send_ping,
    send_follow, send_unfollow
)
from peer_state import print_known_peers, print_messages
from utils import get_timestamp
from constants import PROFILE_INTERVAL

my_user_id = "you@192.168.1.100"  # Replace with your actual IP or set dynamically

def create_post(content):
    return {
        "TYPE": "POST",
        "USER_ID": my_user_id,
        "CONTENT": content,
        "TTL": "3600",
        "MESSAGE_ID": "m" + str(get_timestamp()),
        "TOKEN": f"{my_user_id}|{get_timestamp()+3600}|broadcast"
    }

def create_dm(target, content):
    return {
        "TYPE": "DM",
        "FROM": my_user_id,
        "TO": target,
        "CONTENT": content,
        "TIMESTAMP": str(get_timestamp()),
        "MESSAGE_ID": "d" + str(get_timestamp()),
        "TOKEN": f"{my_user_id}|{get_timestamp()+3600}|chat"
    }

if __name__ == "__main__":
    # CLI arg to enable verbose mode
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()
    VERBOSE = args.verbose

    print("Starting LSNP peer...")
    start_listener(verbose=VERBOSE)
    send_profile(verbose=VERBOSE)

    print("\nLSNP is now running. Type 'help' for commands.\n")

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
            if cmd == "help":
                print("""
Available commands:
  post <message>                      - Broadcast a post
  dm <user_id> <message>              - Send a direct message
  follow <user_id>                    - Follow a user
  unfollow <user_id>                  - Unfollow a user
  show peers                          - Show known peers
  show messages                       - Show received posts and DMs
  exit                                - Quit the program
""")
            elif cmd.startswith("post "):
                content = cmd[5:].strip()
                send_message(create_post(content), verbose=VERBOSE)
            elif cmd.startswith("dm "):
                try:
                    parts = cmd.split(" ", 2)
                    to = parts[1]
                    content = parts[2]
                    send_message(create_dm(to, content), addr=to.split("@")[1], verbose=VERBOSE)
                except:
                    print("Usage: dm <user_id> <message>")
            elif cmd.startswith("follow "):
                to = cmd[7:].strip()
                send_follow(to, verbose=VERBOSE)
            elif cmd.startswith("unfollow "):
                to = cmd[9:].strip()
                send_unfollow(to, verbose=VERBOSE)
            elif cmd == "show peers":
                print_known_peers()
            elif cmd == "show messages":
                print_messages()
            elif cmd == "exit":
                print("Exiting LSNP...")
                break
            elif cmd == "":
                continue
            else:
                print("Unknown command. Type 'help' for options.")

    except KeyboardInterrupt:
        print("\nInterrupted. Exiting LSNP...")
