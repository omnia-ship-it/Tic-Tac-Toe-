import random


WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # columns
    (0, 4, 8), (2, 4, 6),              # diagonals
]


def check_winner(board):
    """
    Returns "X" or "O" if someone has won, or None if there's no winner yet.
    board: a list of 9 items (None, "X", "O")
    """
    for a, b, c in WIN_LINES:
        if board[a] is not None and board[a] == board[b] == board[c]:
            return board[a]
    return None


def is_board_full(board):
    return all(cell is not None for cell in board)


def available_moves(board):
    return [i for i, cell in enumerate(board) if cell is None]


def minimax(board, is_maximizing):
    """
    The classic Minimax algorithm.
    The computer ("O") is the maximizing player, and the human ("X") is the
    minimizing player. Returns the evaluation score of the current board
    state: +1 favors O, -1 favors X, 0 is a draw.
    """
    winner = check_winner(board)
    if winner == "O":
        return 1
    elif winner == "X":
        return -1
    elif is_board_full(board):
        return 0

    if is_maximizing:
        best_score = -float("inf")
        for move in available_moves(board):
            board[move] = "O"
            score = minimax(board, False)
            board[move] = None
            best_score = max(best_score, score)
        return best_score
    else:
        best_score = float("inf")
        for move in available_moves(board):
            board[move] = "X"
            score = minimax(board, True)
            board[move] = None
            best_score = min(best_score, score)
        return best_score


def best_move(board, difficulty="hard"):
    """
    Returns the cell index (0-8) the computer should play.
    - "easy": a random move among the empty cells
    - "hard": the best possible move using Minimax (the game becomes unbeatable)
    """
    moves = available_moves(board)
    if not moves:
        return None

    if difficulty == "easy":
        return random.choice(moves)

    
    best_score = -float("inf")
    move_choice = moves[0]

    for move in moves:
        board[move] = "O"
        score = minimax(board, False)
        board[move] = None

        if score > best_score:
            best_score = score
            move_choice = move

    return move_choice