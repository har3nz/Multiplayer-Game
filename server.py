import socket
import threading
import json
import time
import random

HOST = "0.0.0.0"
PORT = 65432

clients = {}
positions = {}
last_seen = {} 
lock = threading.Lock()

roles = ["red", "blue", "yellow"]
game_roles = {}
pacman_chosen = False
player_counter = 0 

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))
print(f"UDP server listening on {PORT}...")

def receive_loop():
    global player_counter
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            pos = json.loads(data.decode())
        except:
            continue
        with lock:
            if addr not in clients:
                player_counter += 1
                clients[addr] = f"player{player_counter}"
                print(f"{clients[addr]} joined")

            positions[addr] = pos
            last_seen[addr] = time.time()

threading.Thread(target=receive_loop, daemon=True).start()

UPDATE_RATE = 0.05
TIMEOUT = 2

while True:
    time.sleep(UPDATE_RATE)
    now = time.time()
    with lock:
        to_remove = [addr for addr, t in last_seen.items() if now - t > TIMEOUT]
        for addr in to_remove:
            positions.pop(addr, None)
            clients.pop(addr, None)
            game_roles.pop(addr, None)
            last_seen.pop(addr, None)

        # assign roles only when at least 2 players are in
        if len(clients) >= 2 and not game_roles:
            pacman_addr = random.choice(list(clients.keys()))
            game_roles[pacman_addr] = "pacman"
            for addr in clients:
                if addr != pacman_addr:
                    game_roles[addr] = random.choice(roles)

            print("Game started!")
            for addr in clients:
                print(f"{clients[addr]} : {game_roles[addr]}")

        # keep snapshot updated
        snapshot = {
        "positions": {clients[a]: p for a, p in positions.items()}
        }   

        # only include roles after game starts
        if game_roles:
            snapshot["roles"] = {clients[a]: game_roles.get(a, None) for a in clients}


        for caddr in clients:
            try:
                sock.sendto(json.dumps(snapshot).encode(), caddr)
            except:
                pass
