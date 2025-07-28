from constants import SEPARATOR, MESSAGE_TERMINATOR

def parse_message(data):
    try:
        text = data.decode('utf-8')
        if not text.endswith(MESSAGE_TERMINATOR):
            return None
        lines = text.strip().split('\n')
        msg = {}
        for line in lines:
            if SEPARATOR in line:
                key, value = line.split(SEPARATOR, 1)
                msg[key.strip()] = value.strip()
        return msg
    except Exception:
        return None

def craft_message(fields: dict) -> bytes:
    lines = [f"{k}{SEPARATOR}{v}" for k, v in fields.items()]
    return ("\n".join(lines) + MESSAGE_TERMINATOR).encode('utf-8')
