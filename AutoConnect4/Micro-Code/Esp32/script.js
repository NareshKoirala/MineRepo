// Define global variables outside the ready block
let picoConnected = false;
let myList = [0, 0, 0, 0, 0, 0, 0];
let gameMode = null;
let playOn = null;
let currentPlayer = 1;
let movePending = false;
let lastMoveTime = 0;
let motorRunning = false;

$(document).ready(() => {
    $("#game-mode").change(function() {
        const mode = $(this).val();
        $("#computer-options").toggle(mode.startsWith("c_"));
    });

    $("#start-game").click(function() {
        gameMode = $("#game-mode").val();
        playOn = $("#play-on").val();
        if (!gameMode || !playOn) {
            alert("Please select both game mode and play option!");
            return;
        }
        $("#menu").hide();
        $("#game-area").show();
        MakeBoard();
        lastModified();
        updateConnectionStatus();
        updateCurrentPlayer();
        updateButtonState();
        updateMotorStatus();

        fetch(`/set-mode?mode=${gameMode}&playOn=${playOn}`)
            .then(response => {
                if (!response.ok) throw new Error("Failed to set game mode");
                return response.json();
            })
            .then(data => {
                if (!data.success) {
                    alert("Failed to set game mode!");
                    resetGame();
                }
            })
            .catch(error => {
                console.log("Error setting game mode:", error);
                alert("Error communicating with ESP32. Please try again.");
                resetGame();
            });
    });

    setInterval(checkConnectionStatus, 500);
    setInterval(checkGameUpdates, 500);  // Poll for game updates

    $("#game").on("click", "button", (e) => {
        if (!picoConnected && playOn === "hardware") {
            alert("Pico not connected! Game is disabled.");
            return;
        }

        if (movePending) {
            alert("Waiting for the other player's move!");
            return;
        }

        let column = parseInt(e.target.id);

        if (myList[column] >= 6) {
            alert("Column is full!");
            return;
        }

        
        const buttons = $("#game button");        
        buttons.prop("disabled", true).css("opacity", "0.5");

        movePending = true;
        motorRunning = true;
        play(currentPlayer, column);
        currentPlayer = 1
        updateMotorStatus();
        // updateButtonState();

        fetch(`/move?column=${column}`)
            .then(response => {
                if (!response.ok) throw new Error("Network response was not ok");
                return response.json();
            })
            .then(data => {
                if (!data.success) {
                    alert("Failed to process move!");
                    movePending = false;
                    motorRunning = false;
                    updateMotorStatus();
                }
            })
            .catch(error => {
                console.log("Error sending move:", error);
                alert("Error communicating with ESP32!");
                movePending = false;
                motorRunning = false;
                updateMotorStatus();
            });
    });
});

function play(player, column) {
    for (let row = 5; row >= 0; row--) {
        const cell = $(`#${row}${column}`);
        if (cell.hasClass("Grey")) {
            cell.removeClass("Grey").addClass(player === 1 ? "Yellow" : "Red");
            break;
        }
    }
    myList[column] = Math.min(myList[column] + 1, 6);
    updateCurrentPlayer();
    updateButtonState();
}

function checkGameUpdates() {
    fetch('/game-update')
        .then(response => {
            if (!response.ok) throw new Error("Failed to fetch game update");
            return response.json();
        })
        .then(data => {
            if (data.move) {
                play(currentPlayer, data.move.column);
                movePending = false;
                motorRunning = true;
                // currentPlayer = 2
                updateMotorStatus();
            }
            if (data.winner) {
                alert(`Player ${data.winner} wins!`);
                resetGame();
            }
            if (data.columnFull) {
                alert("Column is full!");
                movePending = false;
                motorRunning = false;
                updateMotorStatus();
            }
            if (data.motorStatus) {
                motorRunning = data.motorStatus === "running";
                if (!motorRunning) {
                    movePending = false;
                }
                updateMotorStatus();
            }
            if (data.currentPlayer) {  // Handle currentPlayer updates from ESP32
                currentPlayer = parseInt(data.currentPlayer);
                updateCurrentPlayer();
                updateButtonState();
            }
        })
        .catch(error => {
            console.log("Error checking game updates:", error);
        });
}

function resetGame() {
    // myList = [0, 0, 0, 0, 0, 0, 0];
    // currentPlayer = 1;
    // movePending = false;
    // lastMoveTime = 0;
    // motorRunning = false;
    // $("#game-area").hide();
    // $("#menu").show();
    // $("#game").empty();
    // $(".Yellow, .Red").removeClass("Yellow Red").addClass("Grey");
    // $(".p1").addClass("Yellow");
    // $(".p2").addClass("Red");
    // updateCurrentPlayer();
    // updateButtonState();
    // updateMotorStatus();
    window.location.reload();
}

function lastModified() {
    $("#Modified").text(`Last Modified: ${document.lastModified}`);
}

function MakeBoard() {
    const rows = 7, columns = 7;
    let table = $("#game").empty()[0];
    const headerRow = document.createElement("tr");
    for (let i = 0; i < columns; i++) {
        const th = document.createElement("th");
        const button = document.createElement("button");
        button.textContent = "Place Token";
        button.id = i.toString();
        th.appendChild(button);
        headerRow.appendChild(th);
    }
    table.appendChild(headerRow);

    for (let i = 0; i < rows - 1; i++) {
        const tr = document.createElement("tr");
        for (let j = 0; j < columns; j++) {
            const td = document.createElement("td");
            const div = document.createElement("div");
            div.classList.add("Grey");
            div.id = `${i}${j}`;
            td.appendChild(div);
            tr.appendChild(td);
        }
        table.appendChild(tr);
    }
    updateButtonState();
}

function updateConnectionStatus() {
    const statusElement = $("#connection-status");
    if (statusElement.length) {
        statusElement.text(`Connection Status: ${picoConnected ? "Connected" : "Disconnected"}`)
            .css("color", picoConnected ? "#28a745" : "#dc3545");
    }
}

function checkConnectionStatus() {
    fetch('/status')
        .then(response => {
            if (!response.ok) throw new Error("Failed to fetch status");
            return response.json();
        })
        .then(data => {
            picoConnected = data.connected;
            updateConnectionStatus();
        })
        .catch(error => {
            console.log("Error checking status:", error);
            picoConnected = false;
            updateConnectionStatus();
        });
}

function updateCurrentPlayer() {
    const playerElement = $("#current-player");
    if (playerElement.length) {
        playerElement.html(`Current Player: <span class="player-color ${currentPlayer === 1 ? 'Yellow' : 'Red'}"></span> Player ${currentPlayer}`);
    }
}

function updateButtonState() {
    const buttons = $("#game button");
    if (currentPlayer === 2) 
    {
        buttons.prop("disabled", false).css("opacity", "1");
    } 
    else 
    {
        buttons.prop("disabled", true).css("opacity", "0.5");
    }

    if (gameMode === "c_easy" && playOn === "hardware")
    {
        buttons.prop("disabled", true).css("opacity", "0.5");
    }
}

function updateMotorStatus() {
    const motorElement = $("#motor-status");
    if (motorElement.length) {
        motorElement.text(`Motor Status: ${motorRunning ? "Running..." : "Idle"}`)
            .css("color", motorRunning ? "#e74c3c" : "#666");
    }
}