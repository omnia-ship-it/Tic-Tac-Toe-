// Board state: an array of 9 items (null, "X", "O")
let board = Array(9).fill(null);
let gameOver = false;

const cells = document.querySelectorAll(".cell");
const statusEl = document.getElementById("status");
const resetBtn = document.getElementById("reset-btn");
const difficultySelect = document.getElementById("difficulty");

const WIN_LINES = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],
    [0, 3, 6], [1, 4, 7], [2, 5, 8],
    [0, 4, 8], [2, 4, 6],
];

function checkWinnerLocal(b) {
    for (const [a, b2, c] of WIN_LINES) {
        if (b[a] && b[a] === b[b2] && b[a] === b[c]) {
            return b[a];
        }
    }
    return null;
}

function isBoardFull(b) {
    return b.every(cell => cell !== null);
}

function renderBoard() {
    cells.forEach((cell, i) => {
        cell.textContent = board[i] || "";
        cell.classList.remove("x", "o");
        if (board[i] === "X") cell.classList.add("x");
        if (board[i] === "O") cell.classList.add("o");
    });
}

function setStatus(text) {
    statusEl.textContent = text;
}

function endGame(result) {
    // result: "win" (player won), "loss" (computer won), "draw"
    gameOver = true;

    if (result === "win") setStatus("🎉 You won!");
    else if (result === "loss") setStatus("😅 You lost, try again");
    else setStatus("🤝 It's a draw!");

    // Save the result to the server
    fetch("/api/save_result", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ result: result, opponent_type: "ai" }),
    }).catch(err => console.error("Failed to save result:", err));
}

async function handleCellClick(e) {
    if (gameOver) return;

    const index = parseInt(e.target.dataset.index, 10);
    if (board[index] !== null) return; // cell already taken

    // Player's move (X)
    board[index] = "X";
    renderBoard();

    const winner = checkWinnerLocal(board);
    if (winner === "X") {
        endGame("win");
        return;
    }
    if (isBoardFull(board)) {
        endGame("draw");
        return;
    }

    // Computer's turn
    setStatus("Computer is thinking... 🤔");

    try {
        const response = await fetch("/api/move", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                board: board,
                difficulty: difficultySelect.value,
            }),
        });
        const data = await response.json();

        board = data.board;
        renderBoard();

        if (data.winner === "O") {
            endGame("loss");
        } else if (data.game_over) {
            endGame("draw");
        } else {
            setStatus("Your turn (X)");
        }
    } catch (err) {
        console.error("Failed to reach the server:", err);
        setStatus("Something went wrong, please refresh the page");
    }
}

function resetGame() {
    board = Array(9).fill(null);
    gameOver = false;
    renderBoard();
    setStatus("Your turn (X)");
}

cells.forEach(cell => cell.addEventListener("click", handleCellClick));
resetBtn.addEventListener("click", resetGame);