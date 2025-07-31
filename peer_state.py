# Current Implementation: Milestone 1 and 2
# By Alexi Alberto and Elmo Mandigma

peers = {}
posts = []
dms = []

def update_peer(user_id, display_name, status):
    peers[user_id] = {'name': display_name, 'status': status}

def store_post(user_id, content):
    posts.append((user_id, content))

def store_dm(user_id, content):
    dms.append((user_id, content))

def print_known_peers():
    for uid, info in peers.items():
        print(f"{info['name']} ({uid}): {info['status']}")

def print_messages():
    print("=== POSTS ===")
    for uid, msg in posts:
        name = peers.get(uid, {}).get('name', uid)
        print(f"{name}: {msg}")
    print("=== DMs ===")
    for uid, msg in dms:
        name = peers.get(uid, {}).get('name', uid)
        print(f"{name} -> you: {msg}")
