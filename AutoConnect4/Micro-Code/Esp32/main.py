from connect_wifi import connect
from robust import MQTTClient
import tmc2209
import website
import time

# Connect to Wi-Fi
connect('chels', 'naresh1029')

# MQTT setup
BROKER = "172.20.10.9"
TOPIC = "sensor"

step = [-1]
run = [False]
pico_connected = [False]
start = None

def callback(topic, msg):
    global start
    print(f"Received: {msg}, Topic: {topic}")
    try:
        topic = topic.decode()
        msg = msg.decode()
        if topic == "connection":
            pico_connected[0] = True
        elif topic == "sensor":
            if "wins" in msg:
                website.game_updates.append({"winner": int(msg.split()[1])})
            elif msg == "column_full":
                website.game_updates.append({"columnFull": True})
            else:
                column = int(msg)
                step[0] = column
                if website.playOn == 'hardware' or website.mode == 'person':
                    run[0] = True
                if website.current_player[0] == '1':
                    run[0] = False
                website.game_updates.append({"move": {"player": website.current_player[0], "column": column}})
                if website.playOn != "hardware":
                    website.game_updates.append({"motorStatus": "running"})
                    website.game_updates.append({"motorStatus": "done"})
        elif topic == "start":
            website.current_player[0] = msg
            website.game_updates.append({"currentPlayer": website.current_player[0]})  # Notify web UI of player change
        elif topic == "motor_status" and msg == "done":
            print("Motor move confirmed")
    except ValueError:
        print("Invalid message format")

# Initialize MQTT
client = MQTTClient(
    client_id="esp32_client",
    server=BROKER,
    port=1883,
    keepalive=60
)

client.DEBUG = True  # Optional: enable debug logs
client.set_callback(callback)
client.connect()
client.subscribe(b"connection")
client.subscribe(b"sensor")
client.subscribe(b"start")
client.subscribe(b"motor_status")

print(f"Connected to broker at {BROKER}")

# Initialize motor driver (ESP32 GPIO pins)
tmc2209.tmc_init(14, 12, 27, 33, 32)

tmc2209.solenoid(1)
tmc2209.solenoid_1(0)
time.sleep(1)
tmc2209.solenoid_1(1)

# Start the web server
website.start_web_server(client, tmc2209, step, run, pico_connected)