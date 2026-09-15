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
    
    gameOver = true;

    if (result === "win") setStatus("🎉 مبروك! كسبتي!");
    else if (result === "loss") setStatus("😅 خسرتي، جربي تاني");
    else setStatus("🤝 تعادل!");

    
    fetch("/api/save_result", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ result: result, opponent_type: "ai" }),
    }).catch(err => console.error("فشل حفظ النتيجة:", err));
}

async function handleCellClick(e) {
    if (gameOver) return;

    const index = parseInt(e.target.dataset.index, 10);
    if (board[index] !== null) return; 

    
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

   
    setStatus("الكمبيوتر بيفكر... 🤔");

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
            setStatus("دورك (X)");
        }
    } catch (err) {
        console.error("فشل الاتصال بالسيرفر:", err);
        setStatus("حصل خطأ، جربي تحدّثي الصفحة");
    }
}

function resetGame() {
    board = Array(9).fill(null);
    gameOver = false;
    renderBoard();
    setStatus("دورك (X)");
}

cells.forEach(cell => cell.addEventListener("click", handleCellClick));
resetBtn.addEventListener("click", resetGame);