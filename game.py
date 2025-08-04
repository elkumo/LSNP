games = {}

def store_tictactoe_invite(msg):
    gid = msg["GAMEID"]
    games[gid] = {
        "players": [msg["FROM"], msg["TO"]],
        "symbol": msg["SYMBOL"],
        "board": [" "] * 9,
        "turn": 0,
        "next": msg["FROM"],
        "result": None,
        "winning_line": None
    }

def store_tictactoe_move(msg):
    gid = msg["GAMEID"]
    pos = int(msg["POSITION"])
    sym = msg["SYMBOL"]
    if gid in games:
        games[gid]["board"][pos] = sym
        games[gid]["turn"] = int(msg["TURN"])
        games[gid]["next"] = msg["TO"]

def store_tictactoe_result(msg):
    gid = msg["GAMEID"]
    if gid in games:
        games[gid]["result"] = msg["RESULT"]
        games[gid]["winning_line"] = msg.get("WINNING_LINE")

def print_board(gid):
    if gid not in games:
        print("No such game.")
        return
    b = games[gid]["board"]
    print(f"{b[0]}|{b[1]}|{b[2]}\n{b[3]}|{b[4]}|{b[5]}\n{b[6]}|{b[7]}|{b[8]}")
    if games[gid]["result"]:
        print(f"Result: {games[gid]['result']}")
        if games[gid]["winning_line"]:
            print(f"Winning line: {games[gid]['winning_line']}")
    else:
        print(f"Next turn: {games[gid]['next']}")