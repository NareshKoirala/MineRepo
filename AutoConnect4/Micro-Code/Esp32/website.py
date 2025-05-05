import usocket as socket
import ujson
from time import sleep

BROKER = "10.0.0.14"

game_updates = []
current_player = ["1"]  # Default to Player 1
playOn = ""
mode = ''

def read_file(filename):
    try:
        with open(filename, 'r') as f:
            return f.read()
    except OSError as e:
        print(f"Error reading {filename}: {e}")
        return None

def start_web_server(mqtt_client, tmc2209, step, run, pico_connected):
    global playOn, game_updates, current_player #, solenoid_pin

    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(0)
    print("Web server started on port 80")

    while True:
        mqtt_client.check_msg()

        if run[0]:
            run[0] = False
            print(f"Moving motor to column: {step[0]}")
            game_updates.append({"motorStatus": "running"})
            game_updates.append({"currentPlayer": current_player[0]})  # Update current player
            tmc2209.step_motor(steps=step[0], direction=0)
            sleep(1)
            tmc2209.solenoid(0)
            sleep(2)
            tmc2209.solenoid(1)
            tmc2209.step_motor(steps=step[0], direction=1)
            print("Motor movement complete, notifying Pico")
            mqtt_client.publish(b"motor_status", b"done")
            game_updates.append({"motorStatus": "done"})
            game_updates.append({"currentPlayer": current_player[0]})  # Update current player

        conn, addr = s.accept()
        request = conn.recv(1024).decode()

        request_line = request.split('\n')[0]
        path = request_line.split(' ')[1]

        if path == '/':
            html_content = read_file('index.html')
            if html_content is None:
                conn.send('HTTP/1.1 500 Internal Server Error\n')
                conn.send('Content-Type: text/plain\n')
                conn.send('Connection: close\n\n')
                conn.sendall('Error: Could not load index.html')
            else:
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: text/html\n')
                conn.send('Connection: close\n\n')
                conn.sendall(html_content)

        elif path == '/style.css':
            css_content = read_file('style.css')
            if css_content is None:
                conn.send('HTTP/1.1 500 Internal Server Error\n')
                conn.send('Content-Type: text/plain\n')
                conn.send('Connection: close\n\n')
                conn.sendall('Error: Could not load style.css')
            else:
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: text/css\n')
                conn.send('Connection: close\n\n')
                conn.sendall(css_content)

        elif path == '/script.js':
            js_content = read_file('script.js')
            if js_content is None:
                conn.send('HTTP/1.1 500 Internal Server Error\n')
                conn.send('Content-Type: text/plain\n')
                conn.send('Connection: close\n\n')
                conn.sendall('Error: Could not load script.js')
            else:
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: application/javascript\n')
                conn.send('Connection: close\n\n')
                conn.sendall(js_content)

        elif path.startswith('/move?'):
            params = path.split('?')[1].split('&')
            column = int(params[0].split('=')[1])

            mqtt_client.publish(b"sensor_col", str(column).encode())

            step[0] = column

            if playOn == 'hardware' or mode == 'person':
                run[0] = True
            
            print(f'motor check : player {current_player[0]}')
            
            if current_player[0] == "1":
                run[0] = False

            response = ujson.dumps({"success": True})
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: application/json\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)

        elif path.startswith('/set-mode?'):
            params = path.split('?')[1].split('&')
            mode = params[0].split('=')[1]
            play_on = params[1].split('=')[1]

            playOn = play_on

            mqtt_client.publish(b"game_mode", mode.encode())
            mqtt_client.publish(b"play_on", play_on.encode())
            
            response = ujson.dumps({"success": True})
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: application/json\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)

        elif path == '/game-update':
            update = game_updates.pop(0) if game_updates else {}
            # Always include the current player in every update
            if "currentPlayer" not in update:
                update["currentPlayer"] = current_player[0]
            response = ujson.dumps(update)
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: application/json\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)

        elif path == '/status':
            response = ujson.dumps({"connected": pico_connected[0]})
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: application/json\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)

        else:
            conn.send('HTTP/1.1 404 Not Found\n')
            conn.send('Connection: close\n\n')

        conn.close()