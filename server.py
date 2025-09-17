import socket
import threading
import json
import time

HOST = "0.0.0.0"
PORT = 65432

clients = {}
positions = {}
client_count = 0
last_seen = {} 
lock = threading.Lock()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))
print(f"UDP server listening on {PORT}...")

def receive_loop():
    global client_count
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            pos = json.loads(data.decode())
        except:
            continue
        with lock:
            if addr not in clients:
                client_count += 1
                clients[addr] = f"player{client_count}"
            positions[addr] = pos
            last_seen[addr] = time.time()


threading.Thread(target=receive_loop, daemon=True).start()

UPDATE_RATE = 0.05
TIMEOUT = 5

while True:
    time.sleep(UPDATE_RATE)
    now = time.time()
    with lock:
        to_remove = [addr for addr, t in last_seen.items() if now - t > TIMEOUT]
        for addr in to_remove:
            positions.pop(addr, None)
            clients.pop(addr, None)
            last_seen.pop(addr, None)

        snapshot = {clients[a]: p for a, p in positions.items()}
        for caddr in clients:
            try:
                sock.sendto(json.dumps(snapshot).encode(), caddr)
            except:
                pass
