# Tic-Tac-Toe Arena

#### Video Demo: <YOUR YOUTUBE LINK HERE>

## Description

Tic-Tac-Toe Arena is a web application built with Flask that lets users
create an account, log in, and play Tic-Tac-Toe against a computer opponent
powered by the Minimax algorithm. On "hard" difficulty, the computer plays
optimally, so the best a human player can achieve is a draw.

Game results (win/loss/draw) are saved per user in a SQLite database, and a
leaderboard page ranks players by their number of wins.

## Features

- **User registration and login**, with passwords hashed using werkzeug.security
- **Fully interactive game board** built with JavaScript, with no page reloads
- **AI opponent** using the Minimax algorithm (recursive), with two difficulty levels: easy and hard
- **Result tracking** stored in a SQLite database linked to each user
- **Leaderboard** ranking players by number of wins

## File Structure

- `app.py` — all Flask routes: login, gameplay, saving results, leaderboard
- `helpers.py` — game logic: winner detection, the Minimax algorithm, and computer move selection
- `templates/` — HTML pages (layout, login, register, game, leaderboard)
- `static/styles.css` — styling
- `static/game.js` — client-side game logic and communication with the server via fetch

## Design Choices

- I used **Minimax** instead of fully random moves to demonstrate a real
  understanding of recursion and algorithms, which is a common benchmark
  for this kind of game.
- Win detection exists in two places (JavaScript for instant feedback, and
  Python to validate the result before saving it) so that a player can't
  fake a result by manipulating the browser console.
- I used SQLite instead of CSV files because of the relationship between
  users and games, and to support queries like ranking the leaderboard.

## How to Run

```bash
pip install flask
python app.py
```

Then open your browser at `http://127.0.0.1:5000`