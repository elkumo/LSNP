
import time
import os
import json

# Path to store valid messages with well-formed tokens
VALID_TOKEN_LOG = "data/valid_tokens.jsonl"
os.makedirs("data", exist_ok=True)

# Validate token format and return parsed fields or None
def parse_token(token):
    try:
        parts = token.strip().split("|")
        if len(parts) != 3:
            return None
        user_id, expiration, scope = parts
        expiration = int(expiration)
        return user_id, expiration, scope
    except Exception:
        return None

# Check if token is expired (returns True if still valid)
def is_token_valid(expiration):
    current_time = int(time.time())
    return expiration > current_time

# Validate full token and return status + message
def validate_token_structure(msg, expected_scope=None, log_valid=True):
    token = msg.get("TOKEN")
    if not token:
        return False, "Missing token."

    parsed = parse_token(token)
    if not parsed:
        return False, "Malformed token."

    user_id, expiration, scope = parsed

    if expected_scope and scope != expected_scope:
        return False, f"Scope mismatch. Required: {expected_scope}, got: {scope}"

    if not is_token_valid(expiration):
        return False, "Token expired."

    # Log messages with valid structure (even expired or wrong scope)
    if log_valid:
        store_valid_token_message(msg)

    return True, "Valid token."

# Log messages with valid token structure (append-only)
def store_valid_token_message(msg):
    with open(VALID_TOKEN_LOG, "a", encoding="utf-8") as f:
        json.dump(msg, f)
        f.write("\n")

# Utility function to print all logged messages
def print_logged_token_messages():
    try:
        with open(VALID_TOKEN_LOG, "r", encoding="utf-8") as f:
            for line in f:
                msg = json.loads(line)
                print(f"{msg.get('TYPE', 'UNKNOWN')}: {msg}")
    except FileNotFoundError:
        print("[TOKENS] No logged messages found.")
