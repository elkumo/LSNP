import json
import os

LIKES_FILE = "data/likes.json"
os.makedirs("data", exist_ok=True)

# Load or initialize likes store
try:
    with open(LIKES_FILE, "r") as f:
        likes = json.load(f)
except FileNotFoundError:
    likes = {}

def save_likes():
    with open(LIKES_FILE, "w") as f:
        json.dump(likes, f, indent=2)

# Handle a LIKE message for any target (post, dm, avatar, etc.)
def handle_like_message(msg):
    if msg.get("TYPE") != "LIKE":
        return
    # Accept any ID field as the like target
    target_id = (
        msg.get("MESSAGE_ID") or
        msg.get("DM_ID") or
        msg.get("AVATAR_ID") or
        msg.get("ID")
    )
    liker = msg.get("FROM")
    if target_id and liker:
        if target_id not in likes:
            likes[target_id] = []
        if liker not in likes[target_id]:
            likes[target_id].append(liker)
            save_likes()
            print(f"[LIKE] {liker} liked {target_id}")
        else:
            print(f"[LIKE] Duplicate like ignored for {liker} on {target_id}")
    else:
        print("[LIKE] Invalid LIKE message format.")

def get_likes(target_id):
    return likes.get(target_id, [])

def print_likes_summary():
    print("=== Likes Summary ===")
    for target_id, users in likes.items():
        print(f"{target_id} liked by: {', '.join(users)}")