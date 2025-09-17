import socket
import threading
import json
import pygame

HOST = "hands-role.gl.at.ply.gg"
PORT = 5496

class Player:
    def __init__(self, W, H):
        self.x = W / 2
        self.y = H / 2
        self.vx = 0
        self.vy = 0
        self.speed = 150
        self.sprites = Sprites()
        self.original_player = self.sprites.pacman_sprite
        self.player = self.original_player
        self.dir = "None"

    def controls(self, dt):
        keys = pygame.key.get_pressed()
        self.vx = 0
        self.vy = 0
        if keys[pygame.K_a]: 
            self.dir = "left"
            self.player = pygame.transform.rotate(self.original_player, 180)
        elif keys[pygame.K_d]: 
            self.dir = "right"
            self.player = pygame.transform.rotate(self.original_player, 0)
        elif keys[pygame.K_w]: 
            self.dir = "up"
            self.player = pygame.transform.rotate(self.original_player, 90)
        elif keys[pygame.K_s]: 
            self.dir = "down"
            self.player = pygame.transform.rotate(self.original_player, -90)
        
        if self.dir == "left":
            self.vx = -self.speed
        elif self.dir == "right":
            self.vx = self.speed
        elif self.dir == "down":
            self.vy = self.speed
        elif self.dir == "up":
            self.vy = -self.speed




        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, window):
        window.blit(self.player, (self.x, self.y))

class Sprites:
    def __init__(self):
        self.tilemap_sprite = pygame.transform.scale_by(pygame.image.load("sprites/tilemap.png").convert_alpha(), 2.0)
        self.pacman_sprite = pygame.transform.scale_by(pygame.image.load("sprites/pacman.png").convert_alpha(), 1.3)


class Tilemap:
    def __init__(self):
        self.tiles = []
        self.sprites = Sprites()
        self.tilemap_sprite = self.sprites.tilemap_sprite
        
        self.tilemap = [
                        [0, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 3],
                        [6, 16, 18, -1, 16, 17, 18, -1, 9, -1, 16, 17, 18, -1, 16, 18, 8],
                        [6, 20, 22, -1, 20, 21, 22, -1, 7, -1, 20, 21, 22, -1, 20, 22, 8],
                        [6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 8],
                        [6, 15, 19, -1, 4, -1 ,15, 24, 28, 24, 19, -1, 4, -1, 15, 19, 8],
                        [6, -1, -1, -1, 9, -1, -1, -1, 9, -1, -1, -1, 9, -1, -1, -1, 8],
                        [17, 17, 18, -1, 41, 24, 19, -1, 14, -1, 15, 24, 29, -1, 16, 17, 17],
                        [21, 21, 22, -1, 14, -1, 34, 21, 21, 21, 26, -1, 14, -1, 20, 21, 21],
                        [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                        [17, 17, 18, -1, 4, -1, 35, 17, 17, 17, 5, -1, 4, -1, 16, 17, 17],
                        [21, 21, 22, -1, 14, -1, 15, 24, 28, 24, 19, -1, 14, -1, 20, 21, 21],
                        [6, -1, -1, -1, -1, -1, -1, -1, 9, -1, -1, -1, -1, -1, -1, -1, 8],
                        [6, 15, 36, -1, 15, 24, 19, -1, 14, -1, 15, 24, 19, -1, 37, 19, 8],
                        [6, -1, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 9, -1, 8],
                        [38, 40, 14, -1, 4, -1, 15, 24, 28, 24, 19, -1, 4, -1, 14, 25, 39],
                        [6, -1, -1, -1, 9, -1, -1, -1, 9, -1, -1, -1, 9, -1, -1, -1, 8],
                        [6, 15, 24, 24, 23, 24, 19, -1, 14, -1, 15, 24, 23, 24, 24, 19, 8],
                        [30, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 33]
                        ]
        
        for y in range(0, self.tilemap_sprite.get_height(), 32):
            for x in range(0, self.tilemap_sprite.get_width(), 32):
                rect = pygame.Rect(x, y, 32, 32)
                tile = self.tilemap_sprite.subsurface(rect).copy()
                self.tiles.append(tile)

        map_width = len(self.tilemap[0]) * 32
        map_height = len(self.tilemap) * 32
        self.map_surface = pygame.Surface((map_width, map_height), pygame.SRCALPHA)

        for row, line in enumerate(self.tilemap):
            for col, tile_index in enumerate(line):
                if tile_index == -1 or tile_index >= len(self.tiles):
                    continue
                self.map_surface.blit(self.tiles[tile_index], (col*32, row*32))
    
    def draw(self, window):
        window.blit(self.map_surface, (120, 5))

            
class Game:
    def __init__(self):
        pygame.init()
        self.W, self.H = 800, 600
        self.my_name = None
        self.window = pygame.display.set_mode((self.W, self.H))
        self.clock = pygame.time.Clock()
        self.running = True

        self.Tilemap = Tilemap()

        self.player = Player(self.W, self.H)
        self.other_players = {}

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.1)

        self.last_send = 0
        self.UPDATE_INTERVAL = 0.05
        threading.Thread(target=self.receive_positions, daemon=True).start()

    def receive_positions(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(1024)
                snapshot = json.loads(data.decode())
                if self.my_name is None:
                    for name, pos in snapshot.items():
                        if abs(pos["x"] - self.player.x) < 1 and abs(pos["y"] - self.player.y) < 1:
                            self.my_name = name
                            print(self.my_name)
                            break
                self.other_players = snapshot
            except:
                continue


    def update(self):
        while self.running:
            dt = self.clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.player.controls(dt)

            

            info = {"x": self.player.x, "y": self.player.y, "dir": self.player.dir}
            
            self.last_send += dt
            if self.last_send >= self.UPDATE_INTERVAL:
                self.last_send = 0
                self.sock.sendto(json.dumps(info).encode(), (HOST, PORT))

            self.window.fill((0,4,22))
            self.Tilemap.draw(self.window)
            self.player.draw(self.window)

            for name, other_pos in self.other_players.items():
                if name == self.my_name:
                    continue
                other_sprite = self.player.original_player
                if other_pos.get("dir") == "left":
                    other_sprite = pygame.transform.rotate(other_sprite, 180)
                elif other_pos.get("dir") == "right":
                    other_sprite = pygame.transform.rotate(other_sprite, 0)
                elif other_pos.get("dir") == "up":
                    other_sprite = pygame.transform.rotate(other_sprite, 90)
                elif other_pos.get("dir") == "down":
                    other_sprite = pygame.transform.rotate(other_sprite, -90)

                self.window.blit(other_sprite, (other_pos["x"], other_pos["y"]))

            pygame.display.flip()

        self.sock.close()

if __name__ == "__main__":
    Game().update()
