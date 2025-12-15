import socket
import threading
import json
import pygame
import time
import array
import math 

TCP_PORT = 50000

def make_beep(freq=440, duration_ms=100, volume=0.3):
    sample_rate = 44100
    n_samples = int(sample_rate * duration_ms / 1000)
    buf = array.array("h")

    for i in range(n_samples):
        t = i / sample_rate
        val = int(volume * 32767 * math.sin(2 * math.pi * freq * t))
        buf.append(val)

    return pygame.mixer.Sound(buffer=buf)


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


def search_and_connect(client):
    time.sleep(2)  # simulate searching
    client.connect("127.0.0.1")  # change IP if server is remote


pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1)
screen = pygame.display.set_mode((1000, 700))
pygame.display.set_caption("PatchFest Multiplayer Racer")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

move_sound = make_beep(freq=300, duration_ms=60, volume=0.25)
connect_sound = make_beep(freq=750, duration_ms=200, volume=0.4)

client = Client()
threading.Thread(target=search_and_connect, args=(client,), daemon=True).start()


running = True
while running:
    moved = False
    
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        moved = True
    if keys[pygame.K_RIGHT]:
        moved = True
    if keys[pygame.K_UP]:
        moved = True
    if keys[pygame.K_DOWN]:
        moved = True

    if moved:
        move_sound.play()

    # Play connect sound ONCE
    if client.connected and not client.played_connect_sound:
        connect_sound.play()
        client.played_connect_sound = True

    screen.fill((30, 30, 30))

    # Draw players (after connected)
    for p in client.players:
        pygame.draw.rect(screen, (0, 255, 0), (p["x"], p["y"], 40, 40))

    # Status text
    status_surface = font.render(client.status, True, (255, 255, 255))
    screen.blit(status_surface, (20, 20))

    pygame.display.flip()
    clock.tick(60)


client.running = False
pygame.quit()

