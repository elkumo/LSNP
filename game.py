games = {} # Dictionary to store game states

WINNING_LINES = [ # Define winning lines for Tic Tac Toe
    [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
    [0, 4, 8], [2, 4, 6]              # diagonals
]

def store_tictactoe_invite(msg): # Store a Tic Tac Toe game invitation
    gid = msg["GAMEID"]
    inviter = msg["FROM"]
    invitee = msg["TO"]
    inviter_symbol = msg["SYMBOL"]
    invitee_symbol = "O" if inviter_symbol == "X" else "X"
    games[gid] = {
        "players": [inviter, invitee],
        "symbols": {inviter: inviter_symbol, invitee: invitee_symbol},
        "board": [" "] * 9,
        "turn": 0,
        "next": inviter,
        "result": None,
        "winning_line": None
    }

def store_tictactoe_move(msg): # Store a Tic Tac Toe move
    gid = msg["GAMEID"]
    pos = int(msg["POSITION"])
    sym = msg["SYMBOL"]
    if gid not in games:
        return
    if games[gid]["board"][pos] != " ":
        print("Invalid move: cell already taken.")
        return
    games[gid]["board"][pos] = sym
    games[gid]["turn"] = int(msg["TURN"])
    games[gid]["next"] = msg["TO"]
    # Check for win/draw
    result, line = check_result(games[gid]["board"], sym)
    if result:
        games[gid]["result"] = result
        games[gid]["winning_line"] = line

def store_tictactoe_result(msg): # Store the result of a Tic Tac Toe game
    gid = msg["GAMEID"]
    if gid in games:
        games[gid]["result"] = msg["RESULT"]
        games[gid]["winning_line"] = msg.get("WINNING_LINE")

def print_board(gid): # Print the Tic Tac Toe board and game status
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

def check_result(board, symbol): # Check the Tic Tac Toe board for a win or draw
    for line in WINNING_LINES:
        if all(board[i] == symbol for i in line):
            return f"{symbol} wins", line
    if all(cell != " " for cell in board):
        return "Draw", None
    return None, None