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

    $("#reset-game").click(function (){resetGame();});

    $("#start-game").click(function () {
        gameMode = $("#game-mode").val();

        if (!gameMode) {
            alert("Please select game mode option!");
            return;
        }

        $("#menu").hide();
        $("#game-area").show();
        MakeBoard();
        updateCurrentPlayer();
        gameStart = true;

        if(gameMode !== "person" && currentPlayer === 2){
            movePending = true;
            computer_move();
        }
    });

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


        if (gameMode != "person") {
            movePending = true;
            computer_move();
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
            // div.textContent = `${i}${j}`; // Add label
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

    check_winner_main();
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

/*
    11 = 20
    22 = 20 * 2
    111 = 30 * 3
    222 = 30 * 4
*/

function highPrioty_moves(blocking, winning, pl) {
    let best_moves = [];

    for(let i = 0; i < winning_move.length; i++){
        const move = winning_move[i];

        let weight = 0;
        let pos = 0;

        if(move.horizontal && move.horizontal[0] !== 0 && weight < move.horizontal[0]){
            weight = move.horizontal[0];
            pos = move.horizontal[2];
        }
        if(move.vertical && move.vertical[0] !== 0 && weight < move.vertical[0] && 5 - move.vertical[1] === rows_count[move.vertical[2]]){
            weight = move.vertical[0];
            pos = move.vertical[2];
        }
        if(move.leftDiagonal && move.leftDiagonal[0] !== 0 && weight < move.leftDiagonal[0] && 5 - move.leftDiagonal[1] === rows_count[move.leftDiagonal[2]]){
            weight = move.leftDiagonal[0];
            pos = move.leftDiagonal[2];
        }
        if(move.rightDiagonal && move.rightDiagonal[0] !== 0 && weight < move.rightDiagonal[0] && 5 - move.rightDiagonal[1] === rows_count[move.rightDiagonal[2]]){
            weight = move.rightDiagonal[0];
            pos = move.rightDiagonal[2];
        }

        if ((blocking && pl !== move.player) || (winning && pl === move.player)) {
            const multiplier = weight === 20 ? (blocking ? 1 : 2) : (blocking ? 3 : 4);
            best_moves.push([weight * multiplier, pos]);
        }
    }
    return best_moves;
}

function medium_computer_move(pl) {
    let available_cols = [];
    let col = [];
    let max_weight = 0;

    move_checker();

    if(winning_move.length !== 0){
        available_cols = highPrioty_moves(true, false, pl);
    }

    if (available_cols.length === 0) {
        return easy_computer_move();
    }
    else if(available_cols.length > 0 && available_cols.length < 2){
        return available_cols[0][1];
    }
    else{
        for(let i = 0; i < available_cols.length; i++){
            if(available_cols[i][0] >= max_weight){
                max_weight = available_cols[i][0];
                col.push(available_cols[i][1]);
            }
        }
    }

    let rando_pos = Math.floor(Math.random() * col.length);
    return col[rando_pos];
}

function hard_computer_move(pl) {
    let available_cols = [];
    let col = [];
    let max_weight = 0;

    move_checker();

    if(winning_move.length !== 0){
        available_cols = highPrioty_moves(true, true, pl);
    }

    if (available_cols.length === 0) {
        return easy_computer_move();
    }
    else if(available_cols.length > 0 && available_cols.length < 2){
        return available_cols[0][1];
    }
    else{
        for(let i = 0; i < available_cols.length; i++){
            if(available_cols[i][0] >= max_weight){
                max_weight = available_cols[i][0];
                col.push(available_cols[i][1]);
            }
        }
    }
    
    let rando_pos = Math.floor(Math.random() * col.length);
    return col[rando_pos];
}

function check_winner() {
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
    let player_current = board[row][col];

    for (let i = 1; i < 4; i++) {
        let r = row + i * delta_row;
        let c = col + i * delta_col;

        if (r < 0 || r >= rows || c < 0 || c >= cols || board[r][c] !== player_current) {
            return false;
        }
    }
    return true;
}

function check_Line_return(row, col, delta_row, delta_col) {
    let player_current = board[row][col];
    let count = 1; // Count the starting position

    for (let i = 1; i < 4; i++) {
        let r = row + i * delta_row;
        let c = col + i * delta_col;

        if (r < 0 || r >= rows || c < 0 || c >= cols) {
            return false;
        }

        if (board[r][c] === player_current) {
            count++;
        } else if (board[r][c] === 0 && count >= 2) {
            // Check if the empty position is playable (gravity)
            if (r === rows - 1 || board[r + 1][c] !== 0) {
                return [count * 10, r, c];
            }
            return false;
        } else {
            return false;
        }
    }
    return false;
}

function check_Full_Line(row, col, delta_row, delta_col) {
    let forward = check_Line_return(row, col, delta_row, delta_col);
    let backward = check_Line_return(row, col, -delta_row, -delta_col);

    // If both directions have no valid move, return false
    if (!forward && !backward) {
        return false;
    }

    // If only one direction has a valid move, return it
    if (forward && !backward) {
        return forward;
    }
    if (!forward && backward) {
        return backward;
    }

    // If both directions have valid moves, choose the one with the higher score
    let forward_count = forward[0] / 10;
    let backward_count = backward[0] / 10;
    let total_count = forward_count + backward_count - 1; // Subtract 1 to avoid double-counting starting position

    if (total_count >= 2) {
        // Return the empty position from the direction with more pieces
        return total_count === forward_count ? forward : backward;
    }

    return false;
}

function move_checker() {
    winning_move = [];

    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            let player = board[r][c];

            if (board[r][c] !== 0) {
                let horizontal = check_Full_Line(r, c, 0, 1);   // Left and Right
                let vertical = check_Full_Line(r, c, 1, 0);     // Up and Down
                let right_dia = check_Full_Line(r, c, 1, 1);    // Down-right and Up-left
                let left_dia = check_Full_Line(r, c, 1, -1);    // Down-left and Up-right

                // console.log(r + " " + c + " hori: " + JSON.stringify(horizontal) + " ver: " + JSON.stringify(vertical) + " ld: " + JSON.stringify(left_dia) + " rD: " + JSON.stringify(right_dia));

                if (horizontal || vertical || left_dia || right_dia) {
                    let obj_move = {
                        player: player,
                        startPos: [r, c],
                        horizontal: horizontal,
                        vertical: vertical,
                        leftDiagonal: left_dia,
                        rightDiagonal: right_dia
                    };
                    winning_move.push(obj_move);
                }
            }
        }
    }
}