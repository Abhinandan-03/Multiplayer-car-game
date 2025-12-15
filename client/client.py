import socket
import threading
import json
import pygame
import time

TCP_PORT = 50000


# ---------------------- CLIENT ----------------------
class Client:
    def __init__(self):
        self.sock = None
        self.players = []
        self.running = True
        self.connected = False
        self.status = "Searching for rooms..."
        self.id = None

    def connect(self, host):
        self.status = "Connecting..."
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, TCP_PORT))
            threading.Thread(target=self.recv_loop, daemon=True).start()
        except:
            self.status = "Connected"

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
                        self.connected = True
                        self.status = "Connected!"

                    elif msg["type"] == "state":
                        self.players = msg["players"]

            except:
                break


# ---------------------- FAKE SEARCH THREAD ----------------------
def search_and_connect(client):
    time.sleep(2)  # simulate searching
    client.connect("127.0.0.1")  # change IP if server is remote


# ---------------------- PYGAME SETUP ----------------------
pygame.init()
screen = pygame.display.set_mode((1000, 700))
pygame.display.set_caption("PatchFest Multiplayer Racer")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

client = Client()

# 🔥 Start search -> connect flow
threading.Thread(target=search_and_connect, args=(client,), daemon=True).start()


# ---------------------- MAIN LOOP ----------------------
running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    screen.fill((30, 30, 30))

    # Draw players (after connected)
    for p in client.players:
        pygame.draw.rect(screen, (0, 255, 0), (p["x"], p["y"], 40, 40))

    # Status text
    status_surface = font.render(client.status, True, (255, 255, 255))
    screen.blit(status_surface, (20, 20))

    pygame.display.flip()
    clock.tick(60)


# ---------------------- CLEANUP ----------------------
client.running = False
pygame.quit()

