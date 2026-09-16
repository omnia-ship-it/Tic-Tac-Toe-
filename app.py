import sqlite3
from flask import Flask, render_template, request, redirect, session, jsonify, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

from helpers import best_move, check_winner, is_board_full

app = Flask(__name__)
app.secret_key = "Nona"  

DB_PATH = "tic_tac_toe.db"


def get_db():
    """Opens a new database connection with row_factory enabled so we can access columns by name"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates the tables if they don't already exist"""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            hash TEXT NOT NULL,
            wins INTEGER NOT NULL DEFAULT 0,
            losses INTEGER NOT NULL DEFAULT 0,
            draws INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            result TEXT NOT NULL,
            opponent_type TEXT NOT NULL,
            played_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()


def login_required(f):
    """Decorator that blocks access to a route if the user isn't logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
@login_required
def index():
    return render_template("game.html", username=session.get("username"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirmation = request.form.get("confirmation", "")

        if not username or not password:
            return render_template("register.html", error="Please enter a username and a password")

        if password != confirmation:
            return render_template("register.html", error="Passwords do not match")

        hashed = generate_password_hash(password)

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                (username, hashed),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("register.html", error="That username is already taken")
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        if user is None or not check_password_hash(user["hash"], password):
            return render_template("login.html", error="Invalid username or password")

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/api/move", methods=["POST"])
@login_required
def api_move():
    """
    Takes the current board state from the frontend, determines the computer's
    move (if needed), and returns the new board state along with the game
    status (ongoing / win / draw)
    """
    data = request.get_json()
    board = data.get("board")  # list of 9 items: "X", "O", or None
    difficulty = data.get("difficulty", "hard")  # "easy" or "hard"

    # The computer always plays as "O"
    move = best_move(board, difficulty)
    if move is not None:
        board[move] = "O"

    winner = check_winner(board)
    game_over = winner is not None or is_board_full(board)

    return jsonify({
        "board": board,
        "winner": winner,       # "X", "O", or None
        "game_over": game_over
    })


@app.route("/api/save_result", methods=["POST"])
@login_required
def save_result():
    """Records the match result in the database (win/loss/draw)"""
    data = request.get_json()
    result = data.get("result")  # "win", "loss", "draw"
    opponent_type = data.get("opponent_type", "ai")

    if result not in ("win", "loss", "draw"):
        return jsonify({"success": False, "error": "Invalid result"}), 400

    conn = get_db()
    column = {"win": "wins", "loss": "losses", "draw": "draws"}[result]
    conn.execute(
        f"UPDATE users SET {column} = {column} + 1 WHERE id = ?",
        (session["user_id"],),
    )
    conn.execute(
        "INSERT INTO games (user_id, result, opponent_type) VALUES (?, ?, ?)",
        (session["user_id"], result, opponent_type),
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True})


@app.route("/leaderboard")
@login_required
def leaderboard():
    conn = get_db()
    players = conn.execute("""
        SELECT username, wins, losses, draws,
               (wins - losses) AS score
        FROM users
        ORDER BY wins DESC, losses ASC
        LIMIT 20
    """).fetchall()
    conn.close()

    return render_template("leaderboard.html", players=players)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)