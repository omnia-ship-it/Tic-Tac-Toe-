import random

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  
    (0, 4, 8), (2, 4, 6),             
]


def check_winner(board):
    """
    بترجع "X" أو "O" لو حد فاز، أو None لو مفيش فايز لسه.
    board: list من 9 عناصر (None, "X", "O")
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
    خوارزمية Minimax الكلاسيكية.
    الكمبيوتر ("O") هو الـ maximizing player، واللاعب ("X") هو الـ minimizing player.
    بترجع قيمة تقييم الحالة الحالية للوحة: +1 لصالح O، -1 لصالح X، 0 للتعادل.
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
    بترجع رقم الخانة (0-8) اللي المفروض الكمبيوتر يلعب فيها.
    - "easy": حركة عشوائية من الخانات الفاضية
    - "hard": أفضل حركة ممكنة باستخدام Minimax (اللعبة تبقى مستحيلة الفوز عليها)
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