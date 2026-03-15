# entities.py — Box, Plate, Gate, TorchLight, MovingPlatform, Enemy, Lever

import pygame, math, random
from constants import *
from tileset import (T_BOX_L, T_PLATE_ON, T_PLATE_OFF, T_W_IRON,
                     T_PL_STONE, T_PL_DARK)
from particles import burst, P

# ══════════════════════════════════════════════════════════
# TORCH LIGHT
# ══════════════════════════════════════════════════════════
class TorchLight:
    def __init__(self, x, y, radius=80, color=(255,140,40)):
        self.x=x; self.y=y; self.radius=radius; self.color=color
        self.t=random.uniform(0, math.pi*2)

    def draw(self, surf, cam, gt):
        self.t += 0.08
        flicker = 0.85+0.15*math.sin(self.t)
        r = int(self.radius*flicker)
        sx,sy = cam.apply(self.x, self.y)
        if not (-r < sx < SW+r and -r < sy < SH+r): return
        glow = pygame.Surface((r*2,r*2), pygame.SRCALPHA)
        for rad,a in [(r,8),(int(r*0.6),18),(int(r*0.3),35),(int(r*0.12),60)]:
            pygame.draw.circle(glow, (*self.color,a), (r,r), rad)
        surf.blit(glow, (sx-r, sy-r))

# ══════════════════════════════════════════════════════════
# BOX
# ══════════════════════════════════════════════════════════
class Box:
    W=TILE; H=TILE

    def __init__(self, col, row, tileset):
        self.x=float(col*TILE); self.y=float(row*TILE)
        self.vx=0.0; self.vy=0.0; self.on_ground=False
        self.tileset=tileset

    def rect(self): return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def update(self, solid_rects, other_boxes):
        self.vy = min(self.vy+0.55, 16)
        self.on_ground = False
        collidables = solid_rects+[b.rect() for b in other_boxes]

        self.x += self.vx
        self.x  = max(0.0, min(self.x, (COLS-1)*TILE-self.W))
        r = self.rect()
        for s in collidables:
            if r.colliderect(s):
                if self.vx > 0:
                    self.x = float(s.left - self.W)
                elif self.vx < 0:
                    self.x = float(s.right)
                self.vx = 0
                break
        self.vx *= 0.5

        self.y += self.vy
        r = self.rect()
        for s in collidables:
            if r.colliderect(s):
                if self.vy > 0:
                    self.y=float(s.top-self.H); self.vy=0; self.on_ground=True
                elif self.vy < 0:
                    self.y=float(s.bottom); self.vy=0
                break

        if self.y > ROWS*TILE+TILE*2:
            self.y=float((ROWS-2)*TILE-self.H); self.vy=0.0

    def draw(self, surf, cam, t):
        sx,sy = cam.apply(int(self.x), int(self.y))
        shd = pygame.Surface((TILE,4), pygame.SRCALPHA)
        pygame.draw.ellipse(shd,(0,0,0,40),(0,0,TILE,4)); surf.blit(shd,(sx,sy+TILE))
        surf.blit(self.tileset.get(T_BOX_L[0],T_BOX_L[1]),(sx,sy))
        glow=pygame.Surface((TILE+4,TILE+4),pygame.SRCALPHA)
        a=int(50+40*math.sin(t*0.08))
        pygame.draw.rect(glow,(200,170,80,a),(0,0,TILE+4,TILE+4),2)
        surf.blit(glow,(sx-2,sy-2))

# ══════════════════════════════════════════════════════════
# PRESSURE PLATE
# ══════════════════════════════════════════════════════════
class Plate:
    W=TILE; H=TILE//2

    def __init__(self, col, row, pid, targets, tileset):
        self.col=col; self.row=row
        self.x=col*TILE; self.y=row*TILE+TILE//2
        self.id=pid; self.targets=targets
        self.active=False; self.tileset=tileset

    def rect(self): return pygame.Rect(self.x, self.y, self.W, self.H)

    def draw(self, surf, cam, t, fsm):
        sx,sy = cam.apply(self.x, self.y)
        tid = T_PLATE_ON if self.active else T_PLATE_OFF
        surf.blit(self.tileset.get(tid[0],tid[1]),(sx,sy+TILE//2-8))
        if not self.active and fsm:
            pt = fsm.render("▼", True, (160,140,80))
            surf.blit(pt,(sx+TILE//2-pt.get_width()//2, sy-14))

# ══════════════════════════════════════════════════════════
# LEVER  — new! toggle gates directly, no box needed
# ══════════════════════════════════════════════════════════
class Lever:
    W=12; H=20

    def __init__(self, col, row, lid, targets):
        self.col=col; self.row=row
        self.x=col*TILE+TILE//2-self.W//2
        self.y=row*TILE
        self.id=lid; self.targets=targets
        self.active=False
        self._cooldown=0

    def rect(self):
        return pygame.Rect(self.x-4, self.y, self.W+8, self.H)

    def interact_rect(self):
        return self.rect().inflate(20, 12)

    def try_activate(self, player_rect, interact_pressed, particles):
        if self._cooldown > 0:
            return False
        if interact_pressed and self.interact_rect().colliderect(player_rect):
            self.active = not self.active
            self._cooldown = 30
            burst(particles, self.x+self.W//2, self.y, C_GOLD, 12, 2.0, life=24)
            return True
        return False

    def update(self):
        if self._cooldown > 0:
            self._cooldown -= 1

    def draw(self, surf, cam, t):
        sx,sy = cam.apply(self.x, self.y)
        # Base
        pygame.draw.rect(surf,(62,55,44),(sx,sy+12,self.W,8))
        pygame.draw.rect(surf,(90,80,62),(sx+1,sy+12,self.W-2,4))
        # Handle
        angle = -0.6 if self.active else 0.6
        hx = sx+self.W//2+int(math.sin(angle)*14)
        hy = sy+12+int(-math.cos(angle)*14)
        pygame.draw.line(surf,(145,128,95),(sx+self.W//2,sy+14),(hx,hy),3)
        col = C_GREEN if self.active else (160,60,60)
        pygame.draw.circle(surf,col,(hx,hy),4)
        # Label
        pulse = abs(math.sin(t*0.08))
        lc = (int(80+60*pulse),int(200+40*pulse),int(80+40*pulse)) if not self.active \
             else (80,80,80)
        pygame.draw.circle(surf,lc,(sx+self.W//2,sy+8),3)

# ══════════════════════════════════════════════════════════
# GATE
# ══════════════════════════════════════════════════════════
class Gate:
    def __init__(self, col, row, gid, tileset, start_open=False):
        self.col=col; self.row=row
        self.x=col*TILE; self.base_y=row*TILE
        self.open=start_open
        self.y=float(self.base_y-TILE*4) if start_open else float(self.base_y)
        self.id=gid; self.tileset=tileset

    def rect(self):
        if self.open and self.y <= self.base_y-TILE*4:
            return pygame.Rect(-TILE*2,-TILE*2,0,0)
        return pygame.Rect(self.x, int(self.y), TILE, TILE*4)

    def update(self):
        if self.open:
            if self.y > self.base_y-TILE*4:
                self.y = max(float(self.base_y-TILE*4), self.y-4)
        else:
            if self.y < self.base_y:
                self.y = min(float(self.base_y), self.y+4)

    def draw(self, surf, cam, t):
        sx,sy = cam.apply(self.x, int(self.y))
        if self.open and self.y <= self.base_y-TILE*4: return
        for i in range(4):
            surf.blit(self.tileset.get(T_W_IRON[0],T_W_IRON[1]),(sx,sy+i*TILE))
        pygame.draw.rect(surf,(80,72,62),(sx+2,sy,TILE-4,TILE*4),2)
        gc=(80,210,100) if self.open else (80,80,80)
        pygame.draw.circle(surf,gc,(sx+TILE//2,sy+TILE*2),5)

# ══════════════════════════════════════════════════════════
# MOVING PLATFORM
# ══════════════════════════════════════════════════════════
class MovingPlatform:
    W=TILE*3; H=TILE//2

    def __init__(self, col, row, axis, dist, speed, tileset):
        """
        axis  : 'h' horizontal or 'v' vertical
        dist  : tiles to travel each direction
        speed : pixels per frame
        """
        self.ox=col*TILE; self.oy=row*TILE
        self.x=float(self.ox); self.y=float(self.oy)
        self.axis=axis; self.dist=dist*TILE; self.speed=speed
        self.vx=0.0; self.vy=0.0; self.dir=1
        self.tileset=tileset

    def rect(self): return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def update(self):
        if self.axis == 'h':
            self.x += self.speed*self.dir
            self.vx  = self.speed*self.dir; self.vy=0
            if abs(self.x-self.ox) >= self.dist: self.dir *= -1
        else:
            self.y += self.speed*self.dir
            self.vy  = self.speed*self.dir; self.vx=0
            if abs(self.y-self.oy) >= self.dist: self.dir *= -1

    def draw(self, surf, cam, t):
        sx,sy = cam.apply(int(self.x), int(self.y))
        for i in range(3):
            surf.blit(self.tileset.get(T_PL_STONE[0],T_PL_STONE[1]),
                      (sx+i*TILE, sy))
        # Glow edge
        pulse=int(30+20*math.sin(t*0.06))
        pygame.draw.rect(surf,(80,140,255,pulse),(sx,sy,self.W,2))

# ══════════════════════════════════════════════════════════
# ENEMY  — patrols a platform, kills on touch (living form)
# ══════════════════════════════════════════════════════════
class Enemy:
    W=18; H=28
    SPD=1.4
    JUMP_FORCE = -8.0
    GRAVITY = 0.5
    MAX_FALL = 12.0
    ATTACK_RANGE = 40
    MEMORY_TIME = 90  # frames to keep chasing after losing sight

    def __init__(self, col, row, patrol_dist):
        self.ox=col*TILE; self.oy=row*TILE
        self.x=float(self.ox); self.y=float(self.oy)
        self.patrol_dist=patrol_dist*TILE
        self.dir=1; self.facing=1
        self.anim=random.randint(0,60)
        self.alive=True
        self.alert=False; self.alert_t=0

        # AI state
        self.state = 'patrol'   # patrol, chase, attack
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.jump_timer = 0

        # Wander (random movement when not on same platform)
        self.wander_timer = random.randint(30, 90)
        self.wander_dir = random.choice([-1, 1])

        # Memory
        self.last_player_x = None
        self.memory_timer = 0

    def rect(self): return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def _world_to_tile(self, wx, wy):
        return int(wx // TILE), int(wy // TILE)

    def _is_solid(self, tx, ty, solid_rects):
        if tx < 0 or tx >= COLS or ty < 0 or ty >= ROWS:
            return True
        world_x, world_y = tx * TILE, ty * TILE
        test_rect = pygame.Rect(world_x, world_y, TILE, TILE)
        return any(test_rect.colliderect(s) for s in solid_rects)

    def _on_same_platform(self, player_rect, solid_rects):
        """
        Returns True only if the enemy and player are standing on
        the same horizontal surface (feet within 1 tile vertically,
        no solid tile gap between them at foot level).
        """
        e_foot_y = self.y + self.H
        p_foot_y = player_rect.bottom

        # Must be on roughly the same vertical level (within 1 tile)
        if abs(e_foot_y - p_foot_y) > TILE * 1.2:
            return False

        # Walk tiles between them at foot level — all must be empty
        e_tx = int(self.x // TILE)
        p_tx = int(player_rect.centerx // TILE)
        foot_ty = int((e_foot_y + 2) // TILE)   # tile just below feet

        left_tx  = min(e_tx, p_tx)
        right_tx = max(e_tx, p_tx)

        for tx in range(left_tx, right_tx + 1):
            # There must be solid ground below each tile we walk over
            if not self._is_solid(tx, foot_ty, solid_rects):
                return False  # gap in the platform — not connected

        return True

    def _ground_ahead(self, solid_rects):
        """Check there's solid ground one step ahead (edge detection)."""
        check_x = self.x + (self.W + 2 if self.dir > 0 else -4)
        check_tx, check_ty = self._world_to_tile(check_x, self.y + self.H + 4)
        return self._is_solid(check_tx, check_ty, solid_rects)

    def _wall_ahead(self, solid_rects):
        """Check for a wall directly in front."""
        check_x = self.x + (self.W + 2 if self.dir > 0 else -2)
        check_tx, check_ty = self._world_to_tile(check_x, self.y + self.H // 2)
        return self._is_solid(check_tx, check_ty, solid_rects)

    def _update_ai(self, player_rect, player_ghost, solid_rects):
        if player_ghost:
            self.state = 'patrol'
            self.memory_timer = 0
            return

        same_platform = self._on_same_platform(player_rect, solid_rects)
        dx = player_rect.centerx - (self.x + self.W // 2)
        dist = abs(dx)

        if same_platform and dist <= self.ATTACK_RANGE:
            self.state = 'attack'
            self.memory_timer = self.MEMORY_TIME
            self.last_player_x = player_rect.centerx

        elif same_platform:
            # Player is on same platform but further away — chase
            self.state = 'chase'
            self.memory_timer = self.MEMORY_TIME
            self.last_player_x = player_rect.centerx

        else:
            # Different platform — count down memory then go back to wander
            if self.memory_timer > 0:
                self.memory_timer -= 1
                # Keep chasing last known x briefly
                self.state = 'chase'
            else:
                self.state = 'patrol'

    def update(self, solid_rects, player_rect, player_ghost, particles):
        if not self.alive: return
        self.anim += 1

        self._update_ai(player_rect, player_ghost, solid_rects)

        if self.jump_timer > 0:
            self.jump_timer -= 1

        # Gravity
        self.vy = min(self.vy + self.GRAVITY, self.MAX_FALL)

        # --- Movement ---
        if self.state == 'patrol':
            # Random wander: pick a new direction periodically
            self.wander_timer -= 1
            if self.wander_timer <= 0:
                self.wander_dir = random.choice([-1, 1])
                self.wander_timer = random.randint(40, 120)

            # Edge + wall check
            self.dir = self.wander_dir
            if not self._ground_ahead(solid_rects) or self._wall_ahead(solid_rects):
                self.wander_dir *= -1
                self.dir = self.wander_dir
                self.wander_timer = random.randint(30, 80)

            self.x += self.SPD * 0.6 * self.dir   # wander slower than chase
            self.facing = self.dir

        elif self.state in ('chase', 'attack'):
            target_x = self.last_player_x if self.last_player_x else (self.x + self.W // 2)
            dx = target_x - (self.x + self.W // 2)

            if abs(dx) > 8:
                self.dir = 1 if dx > 0 else -1
                self.facing = self.dir

                # Edge + wall check — stop at platform edge while chasing
                if self._ground_ahead(solid_rects) and not self._wall_ahead(solid_rects):
                    self.x += self.SPD * self.dir
                else:
                    # Hit edge or wall — if there's a wall, try to jump it
                    if self._wall_ahead(solid_rects) and self.on_ground and self.jump_timer <= 0:
                        self.vy = self.JUMP_FORCE
                        self.jump_timer = 40
                        self.on_ground = False

        # Clamp to world
        self.x = max(0, min(self.x, (COLS - 1) * TILE - self.W))

        # Horizontal collision
        r = self.rect()
        for s in solid_rects:
            if r.colliderect(s):
                if self.vx > 0:
                    self.x = float(s.left - self.W)
                elif self.vx < 0:
                    self.x = float(s.right)
                self.vx = 0
                break

        # Vertical collision
        self.y += self.vy
        self.on_ground = False
        r = self.rect()
        for s in solid_rects:
            if r.colliderect(s):
                if self.vy > 0:
                    self.y = float(s.top - self.H)
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.y = float(s.bottom)
                    self.vy = 0
                break

        # Alert state
        self.alert = self.state in ['chase', 'attack']
        if self.alert:
            self.alert_t = 60
        elif self.alert_t > 0:
            self.alert_t -= 1

    def draw(self, surf, cam, t):
        if not self.alive: return
        sx,sy = cam.apply(int(self.x), int(self.y))
        walk = math.sin(self.anim*0.22)*5

        # Shadow
        shd=pygame.Surface((22,4),pygame.SRCALPHA)
        pygame.draw.ellipse(shd,(0,0,0,50),(0,0,22,4))
        surf.blit(shd,(sx-2,sy+self.H))

        # Legs
        lc=(55,22,22)
        pygame.draw.rect(surf,lc,(sx+3,  sy+18,5,8+int(walk)))
        pygame.draw.rect(surf,lc,(sx+10, sy+18,5,8-int(walk)))

        # Body — hooded cultist
        bc=(72,28,28)
        pygame.draw.rect(surf,bc,(sx+2,sy+7,14,13))
        # Cloak sides
        pygame.draw.polygon(surf,(55,20,20),
                            [(sx,sy+10),(sx+2,sy+7),(sx+2,sy+20),(sx-2,sy+22)])
        pygame.draw.polygon(surf,(55,20,20),
                            [(sx+18,sy+10),(sx+16,sy+7),(sx+16,sy+20),(sx+20,sy+22)])

        # Arms
        pygame.draw.rect(surf,bc,(sx+16,sy+8,4,10))
        pygame.draw.rect(surf,bc,(sx-2, sy+8,4,10))

        # Hood / head
        pygame.draw.ellipse(surf,(42,16,16),(sx+2,sy-2,14,14))
        pygame.draw.ellipse(surf,(20,8,8),  (sx+4,sy+1,10,8))

        # Glowing eyes
        if self.state == 'attack':
            eye_color = (80, 160, 255)   # bright blue for attack
        elif self.state == 'chase':
            eye_color = (120, 200, 255)  # lighter blue for chase
        else:
            eye_color = (255, 60, 60)    # default red when patrolling

        pygame.draw.circle(surf,eye_color,(sx+5, sy+4),2)
        pygame.draw.circle(surf,eye_color,(sx+13,sy+4),2)
