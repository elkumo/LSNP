import os
import json
import base64
from datetime import datetime

# Directory to store incoming files and metadata
FILES_DIR = "data/files"
CHUNKS_DIR = "data/file_chunks"
OFFERS_FILE = "data/file_offers.json"

# Ensure necessary directories exist
os.makedirs(FILES_DIR, exist_ok=True)
os.makedirs(CHUNKS_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True)

# Load existing file offers
try:
    with open(OFFERS_FILE, "r") as f:
        file_offers = json.load(f)
except FileNotFoundError:
    file_offers = {}

# Save file offer metadata
def save_offers():
    with open(OFFERS_FILE, "w") as f:
        json.dump(file_offers, f, indent=2)


# AVATAR Handling ---


# Handle AVATAR field in any incoming message
def handle_avatar_field(msg):
    user_id = msg.get("USER_ID")
    avatar = msg.get("AVATAR")

    if user_id and avatar and avatar.startswith("data:image"):
        try:
            header, encoded = avatar.split(",", 1)
            ext = header.split("/")[1].split(";")[0]
            avatar_data = base64.b64decode(encoded)
            filename = f"{user_id.replace('@', '_')}_avatar.{ext}"
            path = os.path.join(FILES_DIR, filename)
            with open(path, "wb") as f:
                f.write(avatar_data)
            print(f"[AVATAR] Saved avatar image for {user_id} at {path}")
        except Exception as e:
            print(f"[AVATAR] Failed to save avatar: {e}")


# FILE_OFFER Handling ---


# Handle incoming FILE_OFFER message
def handle_file_offer(msg):
    offer_id = msg.get("FILE_ID")
    filename = msg.get("FILENAME")
    total_chunks = msg.get("TOTAL_CHUNKS")
    from_user = msg.get("FROM")

    if offer_id and filename and total_chunks:
        file_offers[offer_id] = {
            "FILENAME": filename,
            "TOTAL_CHUNKS": int(total_chunks),
            "FROM": from_user,
            "CHUNKS": {}
        }
        save_offers()
        print(f"[FILE_OFFER] Offer received from {from_user}: {filename} ({total_chunks} chunks)")
    else:
        print("[FILE_OFFER] Invalid file offer message.")

# FILE_CHUNK Handling---

# Handle incoming FILE_CHUNK message
def handle_file_chunk(msg):
    file_id = msg.get("FILE_ID")
    chunk_index = msg.get("CHUNK_INDEX")
    chunk_data = msg.get("CHUNK_DATA")

    if file_id not in file_offers:
        print(f"[FILE_CHUNK] Unknown file ID: {file_id}")
        return

    try:
        chunk_index = int(chunk_index)
        binary_data = base64.b64decode(chunk_data)

        # Save chunk to memory (optional: disk for large files)
        file_offers[file_id]["CHUNKS"][chunk_index] = chunk_data
        save_offers()

        # Save individual chunk file (optional)
        chunk_path = os.path.join(CHUNKS_DIR, f"{file_id}_{chunk_index}.chunk")
        with open(chunk_path, "wb") as f:
            f.write(binary_data)

        print(f"[FILE_CHUNK] Received chunk {chunk_index} of {file_id}")

        # Check if all chunks are received
        total = file_offers[file_id]["TOTAL_CHUNKS"]
        received = len(file_offers[file_id]["CHUNKS"])
        if received == total:
            reconstruct_file(file_id)

    except Exception as e:
        print(f"[FILE_CHUNK] Error processing chunk: {e}")

# Reconstruct full file---

# Reconstruct the full file from chunks
def reconstruct_file(file_id):
    info = file_offers[file_id]
    filename = info["FILENAME"]
    total_chunks = info["TOTAL_CHUNKS"]
    chunks = info["CHUNKS"]

    full_path = os.path.join(FILES_DIR, filename)
    with open(full_path, "wb") as f:
        for i in range(total_chunks):
            if i not in chunks:
                print(f"[FILE_REBUILD] Missing chunk {i}, aborting.")
                return
            chunk_data = base64.b64decode(chunks[i])
            f.write(chunk_data)

    print(f"[FILE_REBUILD] File reconstructed and saved at {full_path}")
    send_file_received_ack(file_id, info["FROM"])

# FILE_RECEIVED ACK---

# Send FILE_RECEIVED message back to sender
def send_file_received_ack(file_id, to_user):
    from networking import send_message  # imported here to avoid circular imports
    msg = {
        "TYPE": "FILE_RECEIVED",
        "FILE_ID": file_id,
        "TO": to_user,
        "TIMESTAMP": str(int(datetime.utcnow().timestamp()))
    }
    print(f"[FILE_RECEIVED] Sending acknowledgment for {file_id} to {to_user}")
    send_message(msg, addr=to_user.split("@")[1], verbose=False)
