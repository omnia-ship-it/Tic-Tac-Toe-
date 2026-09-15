import sqlite3
from flask import Flask, render_template, request, redirect, session, jsonify, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

from helpers import best_move, check_winner, is_board_full

app = Flask(__name__)
app.secret_key = "Nona"  

DB_PATH = "tic_tac_toe.db"


def get_db():
    """بتفتح اتصال جديد بقاعدة البيانات مع تفعيل row_factory عشان نقدر نستخدم الأعمدة بالاسم"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """بتنشئ الجداول لو مش موجودة"""
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
    """Decorator بيمنع الوصول لصفحة معينة لو المستخدم مش مسجل دخوله"""
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
            return render_template("register.html", error="لازم تدخلي اسم المستخدم وكلمة السر")

        if password != confirmation:
            return render_template("register.html", error="كلمتا السر مش متطابقتين")

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
            return render_template("register.html", error="اسم المستخدم ده موجود قبل كده")
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
            return render_template("login.html", error="اسم المستخدم أو كلمة السر غلط")

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
    بياخد حالة اللوحة الحالية من الفرونت اند، يحدد حركة الكمبيوتر (لو مطلوبة)،
    ويرجع حالة اللوحة الجديدة بالإضافة لحالة اللعبة (مستمرة / فوز / تعادل)
    """
    data = request.get_json()
    board = data.get("board")  
    difficulty = data.get("difficulty", "hard")  

   
    move = best_move(board, difficulty)
    if move is not None:
        board[move] = "O"

    winner = check_winner(board)
    game_over = winner is not None or is_board_full(board)

    return jsonify({
        "board": board,
        "winner": winner,       
        "game_over": game_over
    })


@app.route("/api/save_result", methods=["POST"])
@login_required
def save_result():
    """بتسجل نتيجة الماتش في قاعدة البيانات (فوز/خسارة/تعادل)"""
    data = request.get_json()
    result = data.get("result")  
    opponent_type = data.get("opponent_type", "ai")

    if result not in ("win", "loss", "draw"):
        return jsonify({"success": False, "error": "نتيجة غير صالحة"}), 400

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