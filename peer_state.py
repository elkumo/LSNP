# Current Implementation: Milestone 1 and 2
# By Alexi Alberto and Elmo Mandigma

peers = {}
posts = []
dms = []
following = set()

def follow_user(user_id):
    following.add(user_id)

def unfollow_user(user_id):
    following.discard(user_id)

def is_following(user_id):
    return user_id in following

def update_peer(user_id, display_name, status):
    peers[user_id] = {'name': display_name, 'status': status}

def store_post(msg):
    posts.append(msg)

def store_dm(msg):
    dms.append(msg)

def print_known_peers():
    for uid, info in peers.items():
        print(f"{info['name']} ({uid}): {info['status']}")

def print_key_value_message(msg):
    for key in ["TYPE", "FROM", "TO", "USER_ID", "CONTENT", "STATUS", "TIMESTAMP", "MESSAGE_ID", "TOKEN"]:
        if key in msg:
            print(f"{key}: {msg[key]}")

def print_messages():
    print("=== POSTS ===")
    for post in posts:
        print_key_value_message(post)
        print()

    print("=== DMs ===")
    for dm in dms:
        print_key_value_message(dm)
        print()