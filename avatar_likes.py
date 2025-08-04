import json
import os
from datetime import datetime

# File paths for storing avatars and likes
AVATAR_FILE = "data/avatars.json"
LIKES_FILE = "data/likes.json"

# Ensure the data folder exists
os.makedirs("data", exist_ok=True)

# Load or initialize avatar store
try:
    with open(AVATAR_FILE, "r") as f:
        avatars = json.load(f)
except FileNotFoundError:
    avatars = {}

# Load or initialize likes store
try:
    with open(LIKES_FILE, "r") as f:
        likes = json.load(f)
except FileNotFoundError:
    likes = {}

# Save avatars and likes to their respective files
def save_data():
    with open(AVATAR_FILE, "w") as f:
        json.dump(avatars, f, indent=2)
    with open(LIKES_FILE, "w") as f:
        json.dump(likes, f, indent=2)

# =======================
# AVATAR Handling
# =======================

# Handle a message that includes an AVATAR field
def handle_avatar_message(msg):
    # Get user ID and avatar from the message
    user_id = msg.get("USER_ID")
    avatar = msg.get("AVATAR")

    # Store avatar if both fields are present
    if user_id and avatar:
        avatars[user_id] = avatar
        save_data()
        print(f"[AVATAR] Stored avatar for {user_id}")
    else:
        print("[AVATAR] Invalid AVATAR message format.")

# Get avatar for a specific user
def get_avatar(user_id):
    return avatars.get(user_id, "No avatar available.")

# Print all stored avatars
def print_all_avatars():
    for user, avatar in avatars.items():
        print(f"{user}: {avatar}")

# =======================
# LIKE Handling
# =======================

# Handle a message that is a LIKE type
def handle_like_message(msg):
    # Check if message type is LIKE
    if msg.get("TYPE") != "LIKE":
        return

    # Extract necessary fields
    post_id = msg.get("MESSAGE_ID")
    liker = msg.get("FROM")

    # Validate fields and store like
    if post_id and liker:
        if post_id not in likes:
            likes[post_id] = []
        if liker not in likes[post_id]:
            likes[post_id].append(liker)
            save_data()
            print(f"[LIKE] {liker} liked post {post_id}")
        else:
            print(f"[LIKE] Duplicate like ignored for {liker} on {post_id}")
    else:
        print("[LIKE] Invalid LIKE message format.")

# Get the list of users who liked a post
def get_likes(post_id):
    return likes.get(post_id, [])

# Print a summary of all likes
def print_likes_summary():
    print("=== Post Likes ===")
    for post_id, users in likes.items():
        print(f"Post {post_id} liked by: {', '.join(users)}")
