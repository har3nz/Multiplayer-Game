import socket
import threading
import json
import pygame
import random

HOST = "hands-role.gl.at.ply.gg"
PORT = 5496

class Player:
    def __init__(self, W, H, tilemap=None):
        self.x = W / 2
        self.y = H / 2 + 5
        self.vx = 0
        self.vy = 0
        self.speed = 150
        self.sprites = Sprites()
        self.original_player = self.sprites.pacman_sprite
        self.player = self.original_player
        self.dir = "None"
        self.tilemap = tilemap
        self.collision_size = int(16 * 1.3)
        self.collision_surface = pygame.Surface((self.collision_size, self.collision_size), pygame.SRCALPHA)
        pygame.draw.circle(self.collision_surface, (255, 255, 255, 255), (self.collision_size//2, self.collision_size//2), self.collision_size//2)
        self.collision_mask = pygame.mask.from_surface(self.collision_surface)

    def check_collision(self, new_x, new_y):
        if not self.tilemap or not hasattr(self.tilemap, 'collision_mask'):
            return False
        
        map_offset_x = 120
        map_offset_y = 5
        
        sprite_center_x = new_x + self.original_player.get_width()//2
        sprite_center_y = new_y + self.original_player.get_height()//2
        mask_x = int(sprite_center_x - self.collision_size//2 - map_offset_x - 2)
        mask_y = int(sprite_center_y - self.collision_size//2 - map_offset_y - 2)
        
        if (mask_x < -self.collision_size or mask_y < -self.collision_size or 
            mask_x >= self.tilemap.collision_mask.get_size()[0] or 
            mask_y >= self.tilemap.collision_mask.get_size()[1]):
            return True
        
        overlap = self.tilemap.collision_mask.overlap(self.collision_mask, (mask_x, mask_y))
        return overlap is not None
    
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

        new_x = self.x + self.vx * dt
        new_y = self.y + self.vy * dt
        
        if not self.check_collision(new_x, self.y):
            self.x = new_x
        else:
            self.vx = 0
            if self.check_collision(self.x, self.y):
                for push in [-2, 2, -4, 4]:
                    if not self.check_collision(self.x + push, self.y):
                        self.x += push
                        break
            
        if not self.check_collision(self.x, new_y):
            self.y = new_y
        else:
            self.vy = 0
            if self.check_collision(self.x, self.y):
                for push in [-2, 2, -4, 4]:
                    if not self.check_collision(self.x, self.y + push):
                        self.y += push
                        break

    def draw(self, window):
        window.blit(self.player, (self.x, self.y))

class Ghosts:
    def __init__(self, W, H, ghost_type, tilemap=None):
        self.sprites = Sprites()
        #Ghost Stuff
        self.orange_ghost_sprite = self.sprites.orange_ghost_sprite
        self.red_ghost_sprite = self.sprites.red_ghost_sprite
        self.teal_ghost_sprite = self.sprites.teal_ghost_sprite
        self.vuln_ghost_sprite = self.sprites.vuln_ghost_sprite
        # Eyes
        self.left_eyes_sprite = self.sprites.left_eyes_sprite
        self.right_eyes_sprite = self.sprites.right_eyes_sprite
        self.top_eyes_sprite = self.sprites.top_eyes_sprite
        self.bottom_eyes_sprite = self.sprites.bottom_eyes_sprite

        self.tilemap = tilemap
        self.collision_size = int(16 * 1.3)
        self.collision_surface = pygame.Surface((self.collision_size, self.collision_size), pygame.SRCALPHA)
        self.collision_mask = pygame.mask.from_surface(self.collision_surface)


        self.ghost_type = ghost_type

        self.spawn_locs = [
                            (377, 268),
                            (325, 266),
                            (419, 266)
                            ]
        self.spawn_loc = random.randchoice(self.spawnlocs)
        self.x, self.y = self.spawn_loc
        self.dir = "None"
        

    def check_collision(self, new_x, new_y):
        if not self.tilemap or not hasattr(self.tilemap, 'collision_mask'):
            return False
        
        map_offset_x = 120
        map_offset_y = 5
        
        sprite_center_x = new_x + self.original_player.get_width()//2
        sprite_center_y = new_y + self.original_player.get_height()//2
        mask_x = int(sprite_center_x - self.collision_size//2 - map_offset_x - 2)
        mask_y = int(sprite_center_y - self.collision_size//2 - map_offset_y - 2)
        
        if (mask_x < -self.collision_size or mask_y < -self.collision_size or 
            mask_x >= self.tilemap.collision_mask.get_size()[0] or 
            mask_y >= self.tilemap.collision_mask.get_size()[1]):
            return True
        
        overlap = self.tilemap.collision_mask.overlap(self.collision_mask, (mask_x, mask_y))
        return overlap is not None
    
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

        new_x = self.x + self.vx * dt
        new_y = self.y + self.vy * dt
        
        if not self.check_collision(new_x, self.y):
            self.x = new_x
        else:
            self.vx = 0
            if self.check_collision(self.x, self.y):
                for push in [-2, 2, -4, 4]:
                    if not self.check_collision(self.x + push, self.y):
                        self.x += push
                        break
            
        if not self.check_collision(self.x, new_y):
            self.y = new_y
        else:
            self.vy = 0
            if self.check_collision(self.x, self.y):
                for push in [-2, 2, -4, 4]:
                    if not self.check_collision(self.x, self.y + push):
                        self.y += push
                        break

    def draw(self, window):
        window.blit(self.player, (self.x, self.y))



class Sprites:
    def __init__(self):
        self.tilemap_sprite = pygame.transform.scale_by(pygame.image.load("sprites/tilemap.png").convert_alpha(), 2.0)
        self.pacman_sprite = pygame.transform.scale_by(pygame.image.load("sprites/pacman.png").convert_alpha(), 1.3)

        #Ghost Stuff
        self.orange_ghost_sprite = pygame.transform.scale_by(pygame.image.load("sprites/ghosts/orange_ghost.png").convert_alpha(), 1.3)
        self.red_ghost_sprite = pygame.transform.scale_by(pygame.image.load("sprites/ghosts/red_ghost.png").convert_alpha(), 1.3)
        self.teal_ghost_sprite = pygame.transform.scale_by(pygame.image.load("sprites/ghosts/teal_ghost.png").convert_alpha(), 1.3)

        self.vuln_ghost_sprite = pygame.transform.scale_by(pygame.image.load("sprites/ghosts/vuln_ghost.png").convert_alpha(), 1.3)

        # Eyes
        self.left_eyes_sprite = pygame.transform.scale_by(pygame.image.load("sprites/ghosts/left_eyes.png").convert_alpha(), 1.3)
        self.right_eyes_sprite = pygame.transform.scale_by(pygame.image.load("sprites/ghosts/right_eyes.png").convert_alpha(), 1.3)
        self.top_eyes_sprite = pygame.transform.scale_by(pygame.image.load("sprites/ghosts/top_eyes.png").convert_alpha(), 1.3)
        self.bottom_eyes_sprite = pygame.transform.scale_by(pygame.image.load("sprites/ghosts/bottom_eyes.png").convert_alpha(), 1.3)


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
        
        self.collision_mask = pygame.mask.from_surface(self.map_surface)
    
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

        self.player = Player(self.W, self.H, self.Tilemap)
        self.other_players = {}
        self.my_role = None
        self.game_state = "playing"
        self.identification_attempts = 0
        self.sprites = Sprites()
        self.roles_cache = {}

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.1)
        self.sent_role = False

        self.last_send = 0
        self.UPDATE_INTERVAL = 0.05
        threading.Thread(target=self.receive_positions, daemon=True).start()

    def receive_positions(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(1024)
                snapshot = json.loads(data.decode())

                positions = snapshot.get("positions", {})
                roles = snapshot.get("roles", {})
                game_state = snapshot.get("game_state", "playing")
                
                if game_state != self.game_state:
                    if game_state == "resetting":
                        print("Game is resetting...")
                        self.my_role = None
                    elif game_state == "playing" and self.game_state == "resetting":
                        print("Game resumed!")
                        self.player.x = self.W / 2
                        self.player.y = self.H / 2
                        self.my_name = None
                        self.identification_attempts = 0
                    self.game_state = game_state

                if self.my_name is None and self.identification_attempts < 50:
                    self.identification_attempts += 1
                    
                    best_match = None
                    best_distance = float('inf')
                    
                    for name, pos in positions.items():
                        distance = abs(pos["x"] - self.player.x) + abs(pos["y"] - self.player.y)
                        if distance < best_distance and distance < 30:
                            best_distance = distance
                            best_match = name
                    
                    if best_match and self.identification_attempts > 5:
                        self.my_name = best_match
                        print(f"I am {self.my_name} (distance: {best_distance:.1f})")

                if self.my_name and roles and (self.my_role is None or game_state == "playing"):
                    if self.my_name in roles:
                        new_role = roles[self.my_name]
                        if new_role != self.my_role:
                            self.my_role = new_role
                            print(f"My role: {self.my_role}")
                
                if roles:
                    if roles != self.roles_cache:
                        print(f"Roles updated: {roles}")
                        self.roles_cache = roles

                self.other_players = positions
            except:
                continue


    def update(self):
        while self.running:
            dt = self.clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    print(pygame.mouse.get_pos())

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
                
                player_role = self.roles_cache.get(name)
                
                if not player_role or not self.roles_cache:
                    other_sprite = self.player.original_player
                    if other_pos.get("dir") == "left":
                        other_sprite = pygame.transform.rotate(other_sprite, 180)
                    elif other_pos.get("dir") == "right":
                        other_sprite = pygame.transform.rotate(other_sprite, 0)
                    elif other_pos.get("dir") == "up":
                        other_sprite = pygame.transform.rotate(other_sprite, 90) 
                    elif other_pos.get("dir") == "down":
                        other_sprite = pygame.transform.rotate(other_sprite, -90)
                    else:
                        other_sprite = self.player.original_player
                    
                    self.window.blit(other_sprite, (other_pos["x"], other_pos["y"]))
                    
                elif player_role == "pacman":
                    other_sprite = self.player.original_player
                    if other_pos.get("dir") == "left":
                        other_sprite = pygame.transform.rotate(other_sprite, 180)
                    elif other_pos.get("dir") == "right":
                        other_sprite = pygame.transform.rotate(other_sprite, 0)
                    elif other_pos.get("dir") == "up":
                        other_sprite = pygame.transform.rotate(other_sprite, 90) 
                    elif other_pos.get("dir") == "down":
                        other_sprite = pygame.transform.rotate(other_sprite, -90)
                    else:
                        other_sprite = self.player.original_player
                    
                    self.window.blit(other_sprite, (other_pos["x"], other_pos["y"]))
                    
                else:
                    if player_role == "red":
                        ghost_sprite = self.sprites.red_ghost_sprite
                    elif player_role == "blue":
                        ghost_sprite = self.sprites.teal_ghost_sprite
                    elif player_role == "yellow":
                        ghost_sprite = self.sprites.orange_ghost_sprite
                    else:
                        ghost_sprite = self.sprites.red_ghost_sprite
                    
                    self.window.blit(ghost_sprite, (other_pos["x"], other_pos["y"]))
                    
                    direction = other_pos.get("dir", "right")
                    if direction == "left":
                        eye_sprite = self.sprites.left_eyes_sprite
                    elif direction == "right":
                        eye_sprite = self.sprites.right_eyes_sprite
                    elif direction == "up":
                        eye_sprite = self.sprites.top_eyes_sprite
                    elif direction == "down":
                        eye_sprite = self.sprites.bottom_eyes_sprite
                    else:
                        eye_sprite = self.sprites.right_eyes_sprite
                    
                    self.window.blit(eye_sprite, (other_pos["x"], other_pos["y"]))

            pygame.display.flip()

        self.sock.close()

if __name__ == "__main__":
    Game().update()
