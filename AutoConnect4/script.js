// Define global variables outside the ready block
let rows_count = [0, 0, 0, 0, 0, 0, 0];
let gameMode = null;
let currentPlayer = Math.floor(Math.random() * 2) + 1;
let movePending = false;

let gameStart = false;

const rows = 6;
const cols = 7;
let board = new Array(rows);
let winning_move = [];

$(document).ready(() => {

    updateCurrentPlayer();

    $("#start-game").click(function () {
        gameMode = $("#game-mode").val();

        if (!gameMode) {
            alert("Please select game mode option!");
            return;
        }

        if(gameMode !== "person" && currentPlayer === 2){
            movePending = true;
        }

        $("#menu").hide();
        $("#game-area").show();
        MakeBoard();
        updateCurrentPlayer();
        gameStart = true;
    });

    setInterval(computer_move, 500);

    $("#game").on("click", "button", (e) => {
        if(gameMode !== "person" && currentPlayer === 2) {
            alert("Computer Move");
            return;
        }

        if (movePending) {
            alert("Waiting for the computers move!");
            return;
        }

        let column = parseInt(e.target.id);

        if (!valid_col_move(column)) {
            alert("Column is full!");
            return;
        }

        play(currentPlayer, column);

        currentPlayer = currentPlayer === 1 ? 2 : 3 - currentPlayer;
        updateCurrentPlayer();

        check_winner_main();

        if (gameMode != "person") {
            movePending = true;
        }
    });
});

function check_winner_main() {
    if (gameStart) {
        let winner = check_winner();
        if (winner !== 0) {
            alert("Player " + winner + " WON!!!!!!!!!");
            resetGame();
        }
    }
}

function computer_move() {
    if (movePending) {
        let computerColumn = -1;

        if (gameMode === "c_easy") {
            computerColumn = easy_computer_move();
        }
        else if (gameMode === "c_medium") {
            computerColumn = medium_computer_move(currentPlayer);
        }
        else {
            computerColumn = hard_computer_move(currentPlayer);
        }

        if (computerColumn !== -1) {
            play(currentPlayer, computerColumn);
            currentPlayer = currentPlayer === 1 ? 2 : 3 - currentPlayer;
            updateCurrentPlayer();

            check_winner_main();
            movePending = false;
        }
    }
}

function play(player, column) {

    board[rows - 1 - rows_count[column]][column] = player;

    for (let row = rows - 1; row >= 0; row--) {
        const cell = $(`#${row}${column}`);
        if (cell.hasClass("Grey")) {
            cell.removeClass("Grey").addClass(player === 1 ? "Yellow" : "Red");
            break;
        }
    }
    rows_count[column] = Math.min(rows_count[column] + 1, 6);
}

function resetGame() {
    window.location.reload();
}

function MakeBoard() {
    let table = $("#game").empty()[0];

    for (let r = 0; r < rows; r++) {
        board[r] = new Array(cols).fill(0);
    }

    const headerRow = document.createElement("tr");

    for (let i = 0; i < cols; i++) {
        const th = document.createElement("th");
        const button = document.createElement("button");
        button.textContent = "Place Token";
        button.id = i.toString();
        th.appendChild(button);
        headerRow.appendChild(th);
    }
    table.appendChild(headerRow);

    for (let i = 0; i < rows; i++) {
        const tr = document.createElement("tr");
        for (let j = 0; j < cols; j++) {
            const td = document.createElement("td");
            const div = document.createElement("div");
            div.classList.add("Grey");
            div.id = `${i}${j}`;
            div.textContent = `${i}${j}`; // Add label
            td.appendChild(div);
            tr.appendChild(td);
        }
        table.appendChild(tr);
    }
}

function updateCurrentPlayer() {
    const playerElement = $("#current-player");

    if (playerElement.length) {
        playerElement.html(`Current Player: <span class="player-color ${currentPlayer === 1 ? 'Yellow' : 'Red'}"></span> Player ${currentPlayer}`);
    }
}

function valid_col_move(col) {
    return board[0][col] == 0;
}

function easy_computer_move() {
    let available_cols = [];

    for (let c = 0; c < cols; c++) {
        if (valid_col_move(c)) {
            available_cols.push(c);
        }
    }

    if (available_cols.length === 0) {
        return -1;
    }


    let rando_pos = Math.floor(Math.random() * available_cols.length);
    return available_cols[rando_pos];
}

function medium_computer_move(pl) {
    let available_cols = [];
    let index = -1;
    let max_weight = 0;

    for (let i = 0; i < winning_move.length; i++) {

        let move = winning_move[i];
        let r = move[3];
        let c = move[4];

        if (pl !== move[0] && max_weight <= move[1] && rows_count[c] === rows - r) {
            max_weight = move[1];
            available_cols.push(c);
            index = available_cols.length;
        }
    }

    // console.log(available_cols);
    // console.log(winning_move);
    // console.log(rows_count);
    // console.log("Max_weight: " + max_weight + ", index: " + index);

    if (available_cols.length === 0) {
        return easy_computer_move();
    }


    let rando_pos = Math.floor(Math.random() * available_cols.length);
    return available_cols[rando_pos];
}

function hard_computer_move() {
    let available_cols = [];
    let index = -1;
    let max_weight = 0;

    for (let i = 0; i < winning_move.length; i++) {

        let move = winning_move[i];
        let r = move[3];
        let c = move[4];

        if (pl !== move[0] && max_weight <= move[1] && rows_count[c] === rows - r) {
            max_weight = move[1];
            available_cols.push(c);
            index = available_cols.length;
        }
    }

    // console.log(available_cols);
    // console.log(winning_move);
    // console.log(rows_count);
    // console.log("Max_weight: " + max_weight + ", index: " + index);

    if (available_cols.length === 0) {
        return easy_computer_move();
    }


    let rando_pos = Math.floor(Math.random() * available_cols.length);
    return available_cols[rando_pos];
}

function check_winner() {
    winning_move = []

    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            if (board[r][c] !== 0 && (
                check_line(r, c, 1, 0) ||
                check_line(r, c, 0, 1) ||
                check_line(r, c, 1, 1) ||
                check_line(r, c, 1, -1)
            )) {
                return board[r][c];
            }
        }
    }

    return 0;
}

function check_line(row, col, delta_row, delta_col) {
    let player_current = board[row][col]

    for (let i = 1; i < 4; i++) {
        let r = row + i * delta_row;
        let c = col + i * delta_col;

        if (r < 0 || r >= rows || c < 0 || c >= cols || board[r][c] !== player_current) {
            if (i >= 2 && r >= 0 && c >= 0 && r < rows && c < cols && board[r][c] === 0) {
                let save = [player_current, 10 * i, i - 1, r, c];
                winning_move.push(save);
            }
            return false;
        }
    }

    return true;
}

function move_checker() {

}