import socket
import threading
import json
import pygame
import time

DISCOVERY_PORT = 50001
TCP_PORT = 50000


# ---------------------- DISCOVER ROOMS ----------------------
def discover_rooms(timeout=1.5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(0.4)

    found = []
    start = time.time()

    while time.time() - start < timeout:
        try:
            sock.sendto(b"DISCOVER_ROOM", ("<broadcast>", DISCOVERY_PORT))
            data, addr = sock.recvfrom(1024)
            info = json.loads(data.decode())
            found.append(info)
        except:
            pass

    sock.close()
    return found


# ---------------------- CLIENT ----------------------
class Client:
    def __init__(self):
        self.sock = None
        self.players = []
        self.running = True
        self.id = None

    def connect(self, host):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, TCP_PORT))
        threading.Thread(target=self.recv_loop, daemon=True).start()

    def recv_loop(self):
        buf = b""
        while self.running:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break

                buf += data
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    msg = json.loads(line.decode())

                    if msg["type"] == "welcome":
                        self.id = msg["id"]

                    elif msg["type"] == "state":
                        self.players = msg["players"]
            except:
                break

    def send_input(self, dx, dy):
        msg = json.dumps({"dx": dx, "dy": dy}) + "\n"
        try:
            self.sock.sendall(msg.encode())
        except:
            pass


# ---------------------- BACKGROUND DISCOVERY ----------------------
def discovery_loop(client):
    while client.running and client.sock is None:
        rooms = discover_rooms()
        if rooms:
            client.connect(rooms[0]["host"])
            return
        time.sleep(1)   # wait and retry silently


# ---------------------- PYGAME LOOP ----------------------
pygame.init()
screen = pygame.display.set_mode((1000, 700))
pygame.display.set_caption("PatchFest Multiplayer Racer")
clock = pygame.time.Clock()

client = Client()

# 🔥 start discovery in background (NO PRINTING)
threading.Thread(target=discovery_loop, args=(client,), daemon=True).start()

running = True
while running:
    dx = dy = 0

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: dx = -5
    if keys[pygame.K_RIGHT]: dx = 5
    if keys[pygame.K_UP]: dy = -5
    if keys[pygame.K_DOWN]: dy = 5

    client.send_input(dx, dy)

    screen.fill((30, 30, 30))
    for p in client.players:
        pygame.draw.rect(screen, (0, 255, 0), (p["x"], p["y"], 40, 40))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
client.running = False





