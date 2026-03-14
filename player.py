# player.py — Player class, draw_living, draw_ghost

import pygame, math, random
from constants import *
from particles import P, burst

# ── Small font ref (set by main.py after pygame.init) ───
_fsm = None


def draw_living(surf, sx, sy, facing, vx, on_gnd, t, has_box_nearby=False):
    bob  = math.sin(t*0.2)*1.5 if on_gnd and abs(vx) > 0.3 else 0
    by   = sy + int(bob)
    walk = math.sin(t*0.38)*6  if on_gnd and abs(vx) > 0.5 else 0

    shd = pygame.Surface((24,5), pygame.SRCALPHA)
    pygame.draw.ellipse(shd, (0,0,0,45), (0,0,24,5))
    surf.blit(shd, (sx-1, sy+31))

    lc = (28,38,95)
    r_leg = int(walk); l_leg = -int(walk)
    pygame.draw.rect(surf, lc, (sx+4,  by+20, 6, 10+r_leg))
    pygame.draw.rect(surf, lc, (sx+12, by+20, 6, 10+l_leg))
    bc = (18,14,12)
    pygame.draw.rect(surf, bc, (sx+3,  by+28+r_leg, 8, 4))
    pygame.draw.rect(surf, bc, (sx+11, by+28+l_leg, 8, 4))

    cc = (195,190,180)
    pygame.draw.rect(surf, cc, (sx+3, by+9, 16, 13))
    pygame.draw.line(surf, (162,158,148), (sx+11,by+9),  (sx+7, by+20), 1)
    pygame.draw.line(surf, (162,158,148), (sx+11,by+9),  (sx+15,by+20), 1)

    sw = math.sin(t*0.38)*5 if on_gnd and abs(vx) > 0.5 else 0
    fa = int(sw) if facing > 0 else -int(sw)
    pygame.draw.rect(surf, cc, (sx+18, by+10+fa, 5, 11))
    pygame.draw.rect(surf, cc, (sx-1,  by+10-fa, 5, 11))
    pygame.draw.rect(surf, (48,46,42), (sx+18, by+19+fa, 5, 4))
    pygame.draw.rect(surf, (48,46,42), (sx-1,  by+19-fa, 5, 4))

    pygame.draw.rect(surf, (180,162,142), (sx+8, by+7, 6, 4))
    pygame.draw.rect(surf, (180,162,142), (sx+4, by-2, 14, 10))
    pygame.draw.rect(surf, (180,162,142), (sx+3, by+1, 16, 8))

    pygame.draw.rect(surf, (48,48,52), (sx+4, by-4, 14, 8))
    pygame.draw.rect(surf, (48,48,52), (sx+3, by-2, 16, 6))
    voff = 2 if facing > 0 else 1
    vs = pygame.Surface((9,4), pygame.SRCALPHA); vs.fill((75,155,215,190))
    surf.blit(vs, (sx+4+voff, by-2))
    pygame.draw.rect(surf, C_GREEN, (sx+4, by-4, 14, 2))

    if has_box_nearby and _fsm:
        ht = _fsm.render("PUSH", True, (220,200,140))
        surf.blit(ht, (sx+11-ht.get_width()//2, sy-22))


def draw_ghost(surf, sx, sy, facing, vx, t, gfrac):
    hover = math.sin(t*0.06)*7; rip = t*0.10
    sy_h  = sy + int(hover)

    if gfrac < 0.25:
        wa = int(100*abs(math.sin(t*0.28)))
        ws = pygame.Surface((42,42), pygame.SRCALPHA)
        pygame.draw.circle(ws, (255,70,70,wa), (21,21), 21)
        surf.blit(ws, (sx-10, sy_h-10))

    for rad, a in [(38,12),(26,22),(16,38)]:
        gs = pygame.Surface((rad*2,rad*2), pygame.SRCALPHA)
        pygame.draw.circle(gs, (75,120,255,a), (rad,rad), rad)
        surf.blit(gs, (sx+11-rad, sy_h+12-rad))

    cf = -1 if facing > 0 else 1
    for i in range(5):
        cx2 = sx+11+cf*(7+i*6); cy2 = sy_h+14+int(math.sin(rip+i*0.9)*4)
        ca  = max(0, 90-i*20);  cr  = max(1, 4-i)
        cs  = pygame.Surface((cr*2,cr*2), pygame.SRCALPHA)
        pygame.draw.circle(cs, (95,135,255,ca), (cr,cr), cr)
        surf.blit(cs, (cx2-cr, cy2-cr))

    robe = (16,12,25); edge = (48,36,72)
    pts_l = [(sx+4, sy_h+8)]; pts_r = [(sx+18, sy_h+8)]
    for i in range(9):
        fx = i/8.0
        wl = math.sin(rip+fx*math.pi*2.3)*2.8
        wr = math.sin(rip+fx*math.pi*2.3+0.7)*2.8
        pts_l.append((sx+3+int(wl)-int(fx*4),  sy_h+8+i*3))
        pts_r.append((sx+19-int(wr)+int(fx*4), sy_h+8+i*3))
    pygame.draw.polygon(surf, robe, pts_l+list(reversed(pts_r)))
    pygame.draw.lines(surf, edge, False, pts_l, 1)
    pygame.draw.lines(surf, edge, False, pts_r, 1)
    hem_y = sy_h+8+8*3
    for i in range(6):
        hx  = sx+2+i*4; wv = math.sin(rip*1.9+i*1.4)*3.5
        hlen = 5+int(abs(math.sin(rip*0.8+i))*8)
        pygame.draw.line(surf, robe, (hx,hem_y), (int(hx+wv),hem_y+hlen), 2)
        if i%2 == 0:
            pygame.draw.line(surf, edge, (hx,hem_y), (int(hx+wv),hem_y+hlen//2), 1)

    pygame.draw.ellipse(surf, (13,10,22), (sx+1,sy_h-4,20,16))
    pygame.draw.ellipse(surf, (6,4,12),   (sx+4,sy_h+1,14,9))
    pygame.draw.arc(surf, edge, (sx+1,sy_h-4,20,16), math.pi*0.15, math.pi*0.85, 2)

    fl  = 0.55+0.45*math.sin(t*0.29+math.cos(t*0.11))
    ea  = int(210*fl); ex_b = sx+6 if facing > 0 else sx+4
    for ei in range(2):
        ex = ex_b+ei*6; ey = sy_h+3
        eg = pygame.Surface((12,6), pygame.SRCALPHA)
        pygame.draw.ellipse(eg, (75,175,255,ea//2), (0,0,12,6))
        surf.blit(eg, (ex-6,ey-3))
        pygame.draw.line(surf, (155,215,255), (ex-4,ey), (ex+4,ey), 2)
        pygame.draw.circle(surf, (215,240,255), (ex,ey), 1)

    hc = (188,182,168); bc2 = (218,212,198)
    hv = math.sin(t*0.09)*4
    pygame.draw.line(surf, (32,26,48), (sx+19,sy_h+11), (sx+23,sy_h+14+int(hv)), 2)
    pygame.draw.circle(surf, hc, (sx+23, sy_h+14+int(hv)), 4)
    for fi in range(3):
        fa2 = (-0.4+fi*0.4+math.pi/2)
        fx2 = sx+23+int(math.cos(fa2)*6); fy2 = sy_h+14+int(hv)+int(math.sin(fa2)*6)
        pygame.draw.line(surf, bc2, (sx+23,sy_h+14+int(hv)), (fx2,fy2), 1)
    pygame.draw.line(surf, (32,26,48), (sx+3,sy_h+11), (sx-1,sy_h+14-int(hv)), 2)
    pygame.draw.circle(surf, hc, (sx-1, sy_h+14-int(hv)), 4)

    sc=(68,58,42); bl=(182,196,218); bs=(228,238,255)
    if facing > 0:
        pygame.draw.line(surf, sc, (sx+19,sy_h+7), (sx+30,sy_h+32), 3)
        bp = []
        for a in range(-2,13):
            ang = math.pi*0.52+a*0.10
            bp.append((sx+30+int(math.cos(ang)*14), sy_h+4+int(math.sin(ang)*14)))
        if len(bp) > 1:
            pygame.draw.lines(surf, bl, False, bp, 3)
            pygame.draw.lines(surf, bs, False, bp[:7], 1)
        pygame.draw.line(surf, bl, (sx+30,sy_h+4), (sx+32,sy_h+12), 2)
    else:
        pygame.draw.line(surf, sc, (sx+3,sy_h+7), (sx-8,sy_h+32), 3)
        bp = []
        for a in range(-2,13):
            ang = math.pi*0.48-a*0.10
            bp.append((sx-8+int(math.cos(ang)*14), sy_h+4+int(math.sin(ang)*14)))
        if len(bp) > 1:
            pygame.draw.lines(surf, bl, False, bp, 3)
            pygame.draw.lines(surf, bs, False, bp[:7], 1)

    for i in range(3):
        ang   = t*0.07+i*(math.pi*2/3)
        orb_r = 15+4*math.sin(t*0.05+i)
        ox2   = sx+11+int(math.cos(ang)*orb_r)
        oy2   = sy_h+12+int(math.sin(ang)*orb_r*0.45)
        os    = pygame.Surface((8,8), pygame.SRCALPHA)
        oa    = 90+int(90*math.sin(t*0.10+i))
        pygame.draw.circle(os, (110,155,255,oa),   (4,4), 4)
        pygame.draw.circle(os, (195,218,255,oa//2),(4,4), 2)
        surf.blit(os, (ox2-4, oy2-4))


class Player:
    W, H = 22, 30
    SPD=3.8;  JMP=-15.0; GRAV=0.50; MXFALL=14.0
    PUSH_FORCE=2.8
    GSPD=5.5; GFLOAT=4.2; GGRAV=0.03; GMXDY=2.5
    GDUR=450
    # Double-jump
    MAX_JUMPS = 2

    def __init__(self, x, y):
        self.cycles=4; self.spawn_x=float(x); self.spawn_y=float(y)
        self._init()

    def _init(self):
        self.x=self.spawn_x; self.y=self.spawn_y
        self.vx=self.vy=0.0; self.on_gnd=False
        self.ghost=False; self.gtimer=0; self.dead=False
        self.anim=0; self.facing=1; self.coy=0; self.jbuf=0
        self.trail=[]; self.inventory=None
        self.jumps_left = self.MAX_JUMPS
        self.ghost_jump_ready = True

    def set_spawn(self, x, y): self.spawn_x=float(x); self.spawn_y=float(y)

    def respawn(self):
        self.cycles = max(0, self.cycles-1)
        self.dead   = False
        self._init()

    def rect(self): return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def toggle_ghost(self, solid_rects):
        if self.ghost:
            if self._safe(solid_rects): self.ghost=False
        elif self.gtimer <= 0:
            self.ghost=True
            self.gtimer=self.GDUR
            self.ghost_jump_ready = True  # Reset the jump here

    def _safe(self, solid_rects):
        r = self.rect()
        return not any(r.colliderect(s) for s in solid_rects)

    def update(self, keys, solid_rects, boxes, moving_platforms, particles, cam,
               current_solids_ref, sound_mgr=None):
        self.anim += 1
        if self.dead: return

        L = keys[pygame.K_LEFT]  or keys[pygame.K_a]
        R = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        U = keys[pygame.K_UP]    or keys[pygame.K_w] or keys[pygame.K_SPACE]
        D = keys[pygame.K_DOWN]  or keys[pygame.K_s]

        # ── GHOST ────────────────────────────────────────
        if self.ghost:
            self.gtimer -= 1
            if self.gtimer <= 0:
                self.ghost = False; self.gtimer = 0
                if not self._safe(solid_rects):
                    self.dead = True; cam.shake(7, 14)
                    burst(particles, self.x+self.W//2, self.y+self.H//2, C_RED, 24, 4.5, life=40)
                    return

            # 1. HORIZONTAL MOVEMENT (Glides through walls)
            if R:   self.vx = min(self.vx + 1.3,  self.GSPD);  self.facing = 1
            elif L: self.vx = max(self.vx - 1.3, -self.GSPD);  self.facing = -1
            else:   self.vx *= 0.82
            self.x += self.vx

            # 2. VERTICAL MOVEMENT & 1.5x JUMP
            if U and getattr(self, 'ghost_on_gnd', False):
                self.vy = -10.5  # Calculated impulse for 1.5x height
                self.ghost_on_gnd = False
                burst(particles, self.x+self.W//2, self.y+self.H, (120, 180, 255), 15, 3.5)
                if sound_mgr:
                    sound_mgr.play('jump')
            
            # Apply "Heavier" Ghost Gravity so we don't float off the map
            # This replaces the tiny 0.03 GGRAV with a snappier 0.30
            self.vy += 0.30 
            self.vy = min(self.vy, 10.0) # Terminal velocity
            self.y += self.vy

            # 3. LAND ON EVERYTHING (Floors, Boxes, Moving Platforms)
            self.ghost_on_gnd = False
            r = self.rect()
            
            # Combine all objects the ghost can stand on
            landables = solid_rects + [b.rect() for b in boxes]
            mp_rects = [p.rect() for p in moving_platforms]
            all_landables = landables + mp_rects
            
            for i, s in enumerate(all_landables):
                if r.colliderect(s):
                    # One-way landing logic: 
                    # Only land if falling (vy > 0) AND were above the platform.
                    # This prevents the "shooting up" glitch when walking through walls.
                    if self.vy > 0 and (self.y + self.H - self.vy) <= s.top + 5:
                        self.y = float(s.top - self.H)
                        self.vy = 0
                        self.ghost_on_gnd = True
                        
                        # Ride moving platforms
                        if i >= len(landables):
                            pi = i - len(landables)
                            if 0 <= pi < len(moving_platforms):
                                self.x += moving_platforms[pi].vx

            # Wall pass sound
            if sound_mgr and any(r.colliderect(s) for s in solid_rects):
                if not hasattr(self, 'wall_timer'):
                    self.wall_timer = 0
                self.wall_timer += 1
                if self.wall_timer > 10:  # Every ~10 frames when passing through
                    sound_mgr.play('wall_pass')
                    self.wall_timer = 0
            else:
                if hasattr(self, 'wall_timer'):
                    self.wall_timer = 0

            # 4. BOUNDARIES & VISUALS
            self.x = max(0, min(self.x, COLS*TILE-self.W))
            self.y = max(-TILE*3, min(self.y, ROWS*TILE+TILE))

            self.trail.append((self.x+self.W//2, self.y+self.H//2))
            if len(self.trail) > 24: self.trail.pop(0)
            
            if self.anim % 3 == 0:
                particles.append(P(
                    self.x+self.W//2+random.uniform(-8,8),
                    self.y+self.H+random.uniform(-6,0),
                    random.uniform(-0.4,0.4), random.uniform(-1.8,-0.2),
                    (65,105,235), 38, grav=-0.04, sz=2))
            return

        # ── LIVING ───────────────────────────────────────
        self.trail.clear()
        if R:   self.vx=min(self.vx+1.1,  self.SPD);  self.facing=1
        elif L: self.vx=max(self.vx-1.1, -self.SPD);  self.facing=-1
        else:   self.vx*=0.70

        if U: self.jbuf=8
        else: self.jbuf=max(0, self.jbuf-1)

        if self.on_gnd:
            self.coy=10; self.jumps_left=self.MAX_JUMPS
        else:
            self.coy=max(0, self.coy-1)

        # Jump (coyote + double-jump)
        if self.jbuf > 0 and self.jumps_left > 0:
            if self.coy > 0 or self.jumps_left == self.MAX_JUMPS:
                self.vy=self.JMP; self.coy=0; self.jbuf=0
                self.jumps_left -= 1
                burst(particles, self.x+self.W//2, self.y+self.H,
                      C_GREEN, 8, 2.0, grav=0.2, life=16, sz=2)
                if sound_mgr:
                    sound_mgr.play('jump')
            elif self.jumps_left > 0:
                self.vy=self.JMP*0.85; self.jbuf=0
                self.jumps_left -= 1
                burst(particles, self.x+self.W//2, self.y+self.H//2,
                      C_ACCENT, 10, 2.5, grav=0.15, life=18, sz=2)
                if sound_mgr:
                    sound_mgr.play('jump')

        self.vy = min(self.vy+self.GRAV, self.MXFALL)
        self.on_gnd = False

        box_rects = [b.rect() for b in boxes]
        mp_rects = [p.rect() for p in moving_platforms]
        all_solid = solid_rects + box_rects + mp_rects

        self.x += self.vx
        for i, s in enumerate(all_solid):
            r = self.rect()
            if not r.colliderect(s):
                continue

            # If the collided object is a box, apply push
            if len(solid_rects) <= i < len(solid_rects) + len(boxes):
                bi = i - len(solid_rects)
                boxes[bi].vx = self.PUSH_FORCE * (1 if self.facing > 0 else -1)

            if self.vx > 0:
                self.x = float(s.left - self.W)
            elif self.vx < 0:
                self.x = float(s.right)

            self.vx = 0

        self.y += self.vy
        for i, s in enumerate(all_solid):
            r = self.rect()
            if r.colliderect(s):
                if self.vy > 0:
                    self.y = float(s.top - self.H)
                    self.vy = 0
                    self.on_gnd = True

                    if i >= len(solid_rects) + len(boxes):
                        pi = i - len(solid_rects) - len(boxes)
                        if 0 <= pi < len(moving_platforms):
                            self.x += moving_platforms[pi].vx

                elif self.vy < 0:
                    self.y = float(s.bottom)
                    self.vy = 0

        # Walk sound
        if self.on_gnd and abs(self.vx) > 0.5 and sound_mgr:
            if not hasattr(self, 'walk_timer'):
                self.walk_timer = 0
            self.walk_timer += abs(self.vx)
            if self.walk_timer > 20:  # Every ~20 pixels
                sound_mgr.play('walk')
                self.walk_timer = 0

    def draw(self, surf, cam, boxes, current_solids):
        sx, sy = cam.apply(int(self.x), int(self.y))
        if self.ghost:
            for i, (tx,ty) in enumerate(self.trail):
                tsx,tsy = cam.apply(int(tx),int(ty))
                f=i/max(1,len(self.trail)); a=int(80*f*f); r2=max(1,int(7*f))
                ts=pygame.Surface((r2*2,r2*2),pygame.SRCALPHA)
                pygame.draw.circle(ts,(65,95,245,a),(r2,r2),r2)
                surf.blit(ts,(tsx-r2,tsy-r2))
            draw_ghost(surf,sx,sy,self.facing,self.vx,self.anim,
                       self.gtimer/self.GDUR)
        else:
            near_box=any(self.rect().inflate(8,4).colliderect(b.rect()) for b in boxes)
            draw_living(surf,sx,sy,self.facing,self.vx,self.on_gnd,self.anim,near_box)

        # Soul pips
        for i in range(4):
            cx=sx+3+i*6; cy=sy-9
            c = C_GREEN if i < self.cycles else (26,26,36)
            b = (68,188,98) if i < self.cycles else (40,40,52)
            pygame.draw.circle(surf,c,(cx,cy),3)
            pygame.draw.circle(surf,b,(cx,cy),3,1)

        # Ghost bar
        if self.ghost or self.gtimer > 0:
            bw=self.W+10; bx=sx-5; by=sy-16
            f=self.gtimer/self.GDUR
            pygame.draw.rect(surf,(10,10,28),(bx,by,bw,4))
            bc=(75,135,255) if f > 0.3 else (215,55,55)
            pygame.draw.rect(surf,bc,(bx,by,int(bw*f),4))
            pygame.draw.rect(surf,(125,155,228),(bx,by,int(bw*f),4),1)

        if self.ghost:
            r=self.rect(); danger=any(r.colliderect(s) for s in current_solids)
            if danger:
                da=int(160*abs(math.sin(self.anim*0.32)))
                ds=pygame.Surface((self.W+8,5),pygame.SRCALPHA)
                ds.fill((255,55,55,da)); surf.blit(ds,(sx-4,sy+self.H+2))
