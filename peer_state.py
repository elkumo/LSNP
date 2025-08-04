# Current Implementation: Milestone 1 and 2
# By Alexi Alberto and Elmo Mandigma

peers = {}
posts = []
dms = []
following = set()
groups = {}
group_messages = []

def follow_user(user_id):
    following.add(user_id)

def unfollow_user(user_id):
    following.discard(user_id)

def is_following(user_id):
    return user_id in following

def create_group(group_id, name, members, creator):
    groups[group_id] = {
        'name': name,
        'members': set(members),
        'creator': creator
    }

def update_group(group_id, add=None, remove=None):
    if group_id in groups:
        if add:
            groups[group_id]['members'].update(add)
        if remove:
            groups[group_id]['members'].difference_update(remove)

def store_group_message(msg):
    group_messages.append(msg)

def is_group_member(group_id, user_id):
    return group_id in groups and user_id in groups[group_id]["members"]

def get_group_name(group_id):
    return groups[group_id]["name"] if group_id in groups else group_id

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

def print_group_messages():
    print("=== GROUP MESSAGES ===")
    for msg in group_messages:
        print_key_value_message(msg)
        print()