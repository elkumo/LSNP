# Current Implementation: Milestone 1 and 2
# By Alexi Alberto and Elmo Mandigma

import argparse
import time
from networking import (
    send_message, start_listener,
    send_profile, send_ping,
    send_follow, send_unfollow
)
from peer_state import print_known_peers, print_messages
from utils import get_timestamp
from constants import PROFILE_INTERVAL

my_user_id = "you@192.168.1.100"  # Change to your actual IP if needed

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--post", help="Send a POST message")
    parser.add_argument("--dm", nargs=2, metavar=("TO", "CONTENT"))
    parser.add_argument("--show", choices=["peers", "messages"])
    parser.add_argument("--follow", help="User ID to follow")
    parser.add_argument("--unfollow", help="User ID to unfollow")
    args = parser.parse_args()

    start_listener(verbose=args.verbose)
    send_profile(verbose=args.verbose)

    if args.post:
        send_message(create_post(args.post), verbose=args.verbose)

    if args.dm:
        to, content = args.dm
        send_message(create_dm(to, content), addr=to.split("@")[1], verbose=args.verbose)

    if args.follow:
        send_follow(args.follow, verbose=args.verbose)

    if args.unfollow:
        send_unfollow(args.unfollow, verbose=args.verbose)

    if args.show == "peers":
        print_known_peers()
    elif args.show == "messages":
        print_messages()

    try:
        ping_profile_toggle = True
        while True:
            if ping_profile_toggle:
                send_ping(verbose=args.verbose)
            else:
                send_profile(verbose=args.verbose)
            ping_profile_toggle = not ping_profile_toggle
            time.sleep(PROFILE_INTERVAL)
    except KeyboardInterrupt:
        print("Exiting...")
