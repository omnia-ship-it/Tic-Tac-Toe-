# Tic-Tac-Toe Arena

#### Video Demo: <[https://youtu.be/GH9rMKxQL2Q]>

#### Description:

Tic-Tac-Toe Arena is a full-stack web application built with Flask that
allows users to create an account, log in, and play the classic game of
Tic-Tac-Toe against a computer opponent. What makes this project more than
a simple game is that the computer's decision-making is powered by the
Minimax algorithm, a well-known technique in game theory and artificial
intelligence that allows the computer to calculate the outcome of every
possible sequence of moves and always choose the optimal one. On "hard"
difficulty, this means the computer literally cannot be beaten; the best a
human opponent can achieve is a draw. On "easy" difficulty, the computer
instead chooses a random available move, which gives newer or younger
players a realistic chance to win and makes the game more approachable.

Beyond the game itself, the application also includes a full user account
system. Users can register with a username and password, and their
passwords are never stored in plain text; instead, they are hashed using
Werkzeug's security functions before being saved to the database. Every
match a user plays against the computer is recorded, and their cumulative
wins, losses, and draws are tracked in a SQLite database. A dedicated
leaderboard page then queries this database and displays the top players
ranked by their number of wins, which adds a small competitive and social
element to an otherwise simple game.

## Project Structure and File Overview

The project is organized as a standard Flask application. `app.py`
contains all of the Flask routes and is the entry point of the
application. It handles user registration and login (with sessions
managed through Flask's built-in `session` object), serves the main game
page, exposes a small JSON API used by the frontend to request the
computer's next move, saves match results to the database, and renders the
leaderboard page by querying and sorting users by their win count. It also
contains the `init_db()` function, which creates the `users` and `games`
tables if they do not already exist, so that the database is automatically
set up the first time the application runs.

`helpers.py` contains all of the game logic that does not depend on Flask
itself, which keeps `app.py` focused purely on routing and makes the game
logic easier to test and reason about independently. This file defines the
winning combinations for a 3x3 board, a `check_winner` function that scans
the board for any of those combinations, an `is_board_full` function used
to detect a draw, and the `minimax` function itself. `minimax` is a
recursive function that simulates every possible continuation of the game
from the current board state, alternating between the "maximizing" player
(the computer, represented as "O") and the "minimizing" player (the human,
represented as "X"), and returns a score of +1, -1, or 0 depending on
whether the resulting game favors the computer, the human, or ends in a
draw. The `best_move` function then uses this scoring system to try every
available move and select whichever one leads to the best guaranteed
outcome for the computer, unless the difficulty is set to "easy", in which
case it simply picks a random available cell instead.

The `templates/` folder contains the HTML pages, all of which extend a
shared `layout.html` template so that the navigation bar and overall page
structure stay consistent across the site. `login.html` and `register.html`
handle the authentication forms, `game.html` renders the interactive 3x3
board along with a dropdown to select difficulty, and `leaderboard.html`
displays a simple ranked table of all players. Finally, the `static/`
folder holds `styles.css`, which defines the visual design of the site,
and `game.js`, which contains all of the client-side logic for the game.
`game.js` is responsible for rendering the board in the browser, detecting
when a human player has won or drawn immediately without waiting on the
server, sending an asynchronous request to the `/api/move` endpoint
whenever it is the computer's turn, and finally reporting the result of
each finished match back to the server through the `/api/save_result`
endpoint so it can be permanently recorded.

## Design Choices

One of the more deliberate design decisions in this project was
implementing Minimax rather than having the computer play randomly or
follow a simple set of hard-coded rules. While a rule-based opponent
(for example, "always take the center if available, otherwise block an
immediate win") could have produced reasonably strong play, it would not
have guaranteed optimal behavior in every situation, and it would not have
demonstrated an understanding of recursion and game-tree search in the
way that Minimax does. Because a 3x3 Tic-Tac-Toe board has a relatively
small number of possible game states, Minimax can explore the entire game
tree without any performance concerns, which made it a practical and
appropriate choice for this specific problem, even though the same
approach would not scale to more complex games like chess without
additional techniques such as alpha-beta pruning.

Another consideration was where to place win-detection logic. It is
duplicated intentionally in both `game.js` and `helpers.py`: the
JavaScript version gives the player instant visual feedback the moment a
game ends, without waiting on a network round trip to the server, while
the Python version is the one that is actually trusted when a result is
saved to the database. This separation means that even if a user were to
manipulate the client-side JavaScript through their browser's developer
tools, they could not fake a win, since the server independently verifies
the state of the board before recording any result.

Finally, SQLite was chosen over a simpler storage format like a CSV file
because the application needed to represent a genuine relationship between
users and their games, and because features like the leaderboard rely on
SQL's ability to sort and filter data efficiently, something that would
have been considerably more cumbersome to implement by hand.