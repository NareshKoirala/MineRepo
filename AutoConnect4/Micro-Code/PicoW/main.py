from connect_wifi import connect
from robust import MQTTClient
import sensor
import game_logic
import random
import time

# Pin configuration for sensors (Pico GPIO pins)
pins = [16, 17, 18, 19, 20, 21, 22]  # GPIO pins for sensors (columns 0-6)
TOPIC = "sensor"
BROKER = "172.20.10.9"

# Game state variables (use regular variables, not lists)
mqtt_message = None
sent_message = False
current = 1  # Start with Player 1
game_mode = None
play_on = None
motor_status = None
col_from_web = None

# Connect to Wi-Fi (assuming Pico W)
connect('chels', 'naresh1029')

# Initialize sensor and game board
sensor_pin = sensor.sensor_init(pins)
game_logic.setup_board(7, 6)

# Sensor interrupt handler
def pin_handler(pin):
    global mqtt_message, sent_message
    # print(f"here : irq : {mqtt_message} : {sent_message}")
    if mqtt_message == None and sent_message == False:
        pin_id = str(pin).split('GPIO')[1].split(',')[0]
        mqtt_message = str(int(pin_id) - 16)  # Convert GPIO pin to column (0-6)
        print(f"Sensor triggered: Column {mqtt_message}")
        sent_message = True

# Unified MQTT callback
def callback(topic, msg):
    global motor_status, col_from_web, current, game_mode, play_on
    print(f"Received: Topic={topic}, Msg={msg}")
    try:
        client.publish(b"connection", b"1")

        topic = topic.decode()
        msg = msg.decode()

        if topic == "motor_status":
            motor_status = msg
            print(f"Motor status updated: {motor_status}")
        elif topic == "sensor_col":
            col_from_web = int(msg)
            print(f"Received column from ESP32: {col_from_web}")
        elif topic == "game_mode":
            game_mode = msg
            print(f"Game mode set to: {game_mode}")
        elif topic == "play_on":
            play_on = msg
            print(f"Play on set to: {play_on}")
    except ValueError as e:
        print(f"Invalid message format: {e}")

# Initialize MQTT with umqtt.robust
client = MQTTClient(
    client_id="pico_client",
    server=BROKER,
    port=1883,
    keepalive=60
)

client.DEBUG = True  # Enable debug logs for MQTT
client.set_callback(callback)
client.connect()
client.subscribe(b"motor_status")
client.subscribe(b"sensor_col")
client.subscribe(b"game_mode")
client.subscribe(b"play_on")
print(f"Connected to broker at {BROKER}")

# Set up sensor interrupt
sensor.sensor_irq(sensor_pin, pin_handler)

print(f"Initial player: {current}")

# Initial MQTT publications
client.publish(b"connection", b"1")
client.publish(b"start", str(current).encode())

def winner_checker(winner):
    print(f"Winner detected: Player {winner}")
    client.publish(b"sensor", f"wins {winner}".encode())
    # Reset the game state after a win
    game_logic.setup_board(7, 6)  # Reset the board
    global current, motor_status, sent_message, mqtt_message, col_from_web, game_mode, play_on
    current = 1  # Reset to Player 1
    motor_status = None
    sent_message = False
    mqtt_message = ''
    col_from_web = None
    game_mode = None
    play_on = None
    client.publish(b"start", str(current).encode())
    print("Game reset after win")

def from_sensor():
    global sent_message, mqtt_message, current, game_logic
    if sent_message:
        column = int(mqtt_message)
        print(f"Player 1 move: Column {column}")
        if game_logic.make_move(column, current):
            client.publish(b"sensor", str(column).encode())
            current = 2
            client.publish(b"start", str(current).encode())
            time.sleep(2)
            print(f"Turn switched to Player {current}")
        else:
            client.publish(b"sensor", b"column_full")
            print(f"Invalid move: Column {column} is full")
        sent_message = False  # Reset after processing
        mqtt_message = None

def from_web_person():
    global col_from_web, current
    if col_from_web is not None:
        print(f"Player {current} move: Column {col_from_web}")
        if game_logic.make_move(col_from_web, current):
            current = 3 - current
            client.publish(b"start", str(current).encode())
            print(f"Turn switched to Player {current}")

        col_from_web = None  # Reset after processing
    sent_message = False  # Reset after processing
    mqtt_message = None

def from_computer():
    global current, motor_status, game_mode
    
    # Computer makes a move
    if game_mode == 'c_easy':
        column = game_logic.easy_computer_move()
    elif game_mode == 'c_medium':
        column = game_logic.medium_computer_move(current)
    else:
        column = game_logic.hard_computer_move(current)

    time.sleep(2)
    if column != -1 and game_logic.make_move(column, current):
        print(f"Computer (Player {current}) move: Column {column}")
        client.publish(b"sensor", str(column).encode())
        current = 3 - current  # Switch player (1 -> 2, 2 -> 1)
        client.publish(b"start", str(current).encode())
        print(f"Turn switched to Player {current}")
    else:
        print("Computer couldn't make a move (board full?)")
            
    sent_message = False  # Reset after processing
    mqtt_message = None


def display_board():
    for row in game_logic.BOARD:
        print(' '.join(map(str, row)))
    print("\n")

def waitModePlay():
    print("Waiting for game mode and play settings...")
    while game_mode is None or play_on is None:
        client.check_msg()
        
    print(f"Starting game with mode={game_mode}, play_on={play_on}")


def main():
    global sent_message, mqtt_message, current, motor_status, game_mode, play_on

    # Wait for game_mode and play_on to be set by the ESP32 with a timeout
    waitModePlay()
        

    while True:
        client.check_msg()  # Non-blocking MQTT check
        
        winner = game_logic.check_winner()
        if winner != 0:
            winner_checker(winner)
            waitModePlay()
        else:
            if game_mode == "person":
                if current == 1:
                    from_sensor()
                    # display_board()
                elif current == 2:
                    from_web_person()
                    # display_board()

            elif game_mode == "c_easy":
                if current == 1:
                    if play_on == "computer":
                        from_computer()  # Player 1 is computer
                    else:
                        from_sensor()  # Player 1 uses sensors


                elif current == 2:
                    if play_on == "computer":
                        from_web_person()  # Player 2 uses web UI
                    else:
                        from_computer()  # Player 2 is computer
                    
                
            elif game_mode == "c_medium":
                if current == 1:
                    if play_on == "computer":
                        from_computer()  # Player 1 is computer
                    else:
                        from_sensor()  # Player 1 uses sensors


                elif current == 2:
                    if play_on == "computer":
                        from_web_person()  # Player 2 uses web UI
                    else:
                        from_computer()  # Player 2 is computer
                    


            elif game_mode == "c_hard":
                if current == 1:
                    if play_on == "computer":
                        from_computer()  # Player 1 is computer
                    else:
                        from_sensor()  # Player 1 uses sensors


                elif current == 2:
                    if play_on == "computer":
                        from_web_person()  # Player 2 uses web UI
                    else:
                        from_computer()  # Player 2 is computer
                    
        
        time.sleep(0.1)

if __name__ == "__main__":
    main()