import socket
import threading
import json
import time
import random
import math

HOST = "0.0.0.0"
PORT = 65432

clients = {}
positions = {}
last_seen = {} 
ready_status = {}
lock = threading.Lock()

roles = ["red", "blue", "orange"]
game_roles = {}
pacman_chosen = False
player_counter = 0
game_state = "playing"
reset_timer = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))
print(f"UDP server listening on {PORT}...")

def receive_loop():
    global player_counter
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            message = json.loads(data.decode())
        except:
            continue
        with lock:
            if addr not in clients:
                player_counter += 1
                clients[addr] = f"player{player_counter}"
                ready_status[addr] = True
                print(f"{clients[addr]} joined")

            if "ready" in message:
                ready_status[addr] = message["ready"]
                print(f"{clients[addr]} ready status: {ready_status[addr]}")
            else:
                positions[addr] = message
            
            last_seen[addr] = time.time()

threading.Thread(target=receive_loop, daemon=True).start()

UPDATE_RATE = 0.05
TIMEOUT = 2
COLLISION_DISTANCE = 15
RESET_DELAY = 3

def check_collisions():
    global game_state, reset_timer
    if game_state != "playing" or len(game_roles) < 2:
        return
    
    pacman_addr = None
    ghost_addrs = []
    
    for addr, role in game_roles.items():
        if role == "pacman":
            pacman_addr = addr
        else:
            ghost_addrs.append(addr)
    
    if not pacman_addr or not ghost_addrs:
        return
    
    if pacman_addr not in positions:
        return
    
    pacman_pos = positions[pacman_addr]
    
    for ghost_addr in ghost_addrs:
        if ghost_addr not in positions:
            continue
        
        ghost_pos = positions[ghost_addr]
        distance = math.sqrt((pacman_pos["x"] - ghost_pos["x"])**2 + (pacman_pos["y"] - ghost_pos["y"])**2)
        
        if distance < COLLISION_DISTANCE:
            print(f"Collision detected! Distance: {distance:.1f} between {clients[pacman_addr]} and {clients[ghost_addr]}")
            game_state = "resetting"
            reset_timer = time.time()
            return

def reset_game():
    global game_roles, game_state, positions
    if len(clients) >= 2:
        game_roles.clear()
        pacman_addr = random.choice(list(clients.keys()))
        game_roles[pacman_addr] = "pacman"
        
        ghost_spawn_positions = [(377, 268), (325, 266), (419, 266)]
        ghost_index = 0
        
        for addr in clients:
            if addr != pacman_addr:
                game_roles[addr] = random.choice(roles)
                if addr in positions:
                    spawn_pos = ghost_spawn_positions[ghost_index % len(ghost_spawn_positions)]
                    positions[addr]["x"] = spawn_pos[0]
                    positions[addr]["y"] = spawn_pos[1]
                    positions[addr]["dir"] = "None"
                    ghost_index += 1
            else:
                if addr in positions:
                    positions[addr]["x"] = 400
                    positions[addr]["y"] = 305
                    positions[addr]["dir"] = "None"
        
        print("Game reset! New roles:")
        for addr in clients:
            print(f"{clients[addr]} : {game_roles[addr]}")
        
        game_state = "playing"

while True:
    time.sleep(UPDATE_RATE)
    now = time.time()
    with lock:
        to_remove = [addr for addr, t in last_seen.items() if now - t > TIMEOUT]
        for addr in to_remove:
            positions.pop(addr, None)
            clients.pop(addr, None)
            game_roles.pop(addr, None)
            ready_status.pop(addr, None)
            last_seen.pop(addr, None)

        if game_state == "resetting" and now - reset_timer > RESET_DELAY:
            reset_game()
        
        ready_count = sum(1 for ready in ready_status.values() if ready)
        all_ready = len(clients) >= 2 and ready_count == len(clients)
        
        if all_ready and not game_roles:
            pacman_addr = random.choice(list(clients.keys()))
            game_roles[pacman_addr] = "pacman"
            
            ghost_spawn_positions = [(377, 268), (325, 266), (419, 266)]
            ghost_index = 0
            
            for addr in clients:
                if addr != pacman_addr:
                    game_roles[addr] = random.choice(roles)
                    if addr in positions:
                        spawn_pos = ghost_spawn_positions[ghost_index % len(ghost_spawn_positions)]
                        positions[addr]["x"] = spawn_pos[0]
                        positions[addr]["y"] = spawn_pos[1]
                        positions[addr]["dir"] = "None"
                        ghost_index += 1
                else:
                    if addr in positions:
                        positions[addr]["x"] = 400
                        positions[addr]["y"] = 305
                        positions[addr]["dir"] = "None"

            print("Game started!")
            for addr in clients:
                print(f"{clients[addr]} : {game_roles[addr]}")
        
        if game_state == "playing":
            check_collisions()

        snapshot = {
            "positions": {clients[a]: p for a, p in positions.items()},
            "game_state": game_state
        }   

        if game_roles:
            snapshot["roles"] = {clients[a]: game_roles.get(a, None) for a in clients}

        for caddr in clients:
            try:
                sock.sendto(json.dumps(snapshot).encode(), caddr)
            except:
                pass
