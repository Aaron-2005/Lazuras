# level_runtime.py — Level class, camera, background

import pygame, math, random
from constants import *
from tileset import SOLID_TILES, GHOST_TILES
from entities import (Box, Plate, Gate, TorchLight,
                      MovingPlatform, Enemy, Lever)
from particles import burst, P

_current_solids = []   # global ref used by Player.draw


# ══════════════════════════════════════════════════════════
# CAMERA
# ══════════════════════════════════════════════════════════
class Camera:
    def __init__(self): self.x=self.y=0.0; self.shk=0; self.shk_m=0

    def update(self, px, py):
        self.x += (px-SW//2-self.x)*0.09
        self.y += (py-SH//2-self.y)*0.09
        self.x  = max(0, min(self.x, COLS*TILE-SW))
        self.y  = max(0, min(self.y, ROWS*TILE-SH))
        if self.shk > 0: self.shk -= 1

    def shake(self, m=4, f=8): self.shk_m=m; self.shk=f

    def apply(self, x, y):
        ox=oy=0
        if self.shk>0:
            ox=random.randint(-self.shk_m,self.shk_m)
            oy=random.randint(-self.shk_m,self.shk_m)
        return x-int(self.x)+ox, y-int(self.y)+oy


# ══════════════════════════════════════════════════════════
# BACKGROUND LAYERS
# ══════════════════════════════════════════════════════════
def make_bg():
    s = pygame.Surface((COLS*TILE, ROWS*TILE))
    for row in range(ROWS):
        for col in range(COLS):
            v    = random.randint(-2,2)
            dist = abs(row-ROWS//2)/(ROWS//2)
            lum  = 12-int(dist*4)
            r=max(4,lum+3+v); g=max(3,lum+2+v); b=max(3,lum+v)
            s.fill((r,g,b),(col*TILE,row*TILE,TILE,TILE))
    return s

def make_far_layer():
    s   = pygame.Surface((SW*2,SH), pygame.SRCALPHA)
    rng = random.Random(77)
    col = (30,24,16,28)
    for _ in range(8):
        x=rng.randint(0,SW*2); h=rng.randint(80,200); w=rng.randint(12,26)
        pygame.draw.rect(s,col,(x,SH-h,w,h))
        pygame.draw.ellipse(s,col,(x-w//2,SH-h-w//2,w*2,w))
    for x in range(0,SW*2,4):
        h=rng.randint(20,55)
        pygame.draw.rect(s,col,(x,SH-h,4,h))
    return s

def make_mid_layer():
    s   = pygame.Surface((SW*2,SH), pygame.SRCALPHA)
    rng = random.Random(88)
    col = (20,16,11,38)
    for _ in range(14):
        x=rng.randint(0,SW*2); h=rng.randint(40,150); w=rng.randint(18,40)
        pygame.draw.rect(s,col,(x,SH-h,w,h))
        for bx in range(x,x+w,8):
            bh=rng.randint(4,14)
            pygame.draw.rect(s,col,(bx,SH-h-bh,6,bh))
    return s


# ══════════════════════════════════════════════════════════
# LEVEL
# ══════════════════════════════════════════════════════════
class Level:
    def __init__(self, tile_data, objects, tileset):
        global _current_solids
        self.tileset=tileset; self.tile_map={}
        self.solid_rects=[]; self.ghost_barrier_rects=[]; self.particles=[]; self.t=0
        self.reached_exit=False

        # First pass — build tile_map so later entries overwrite earlier ones.
        # This means a T_GH_BAR placed on top of a solid wall wins at that cell.
        for (tid, col, row) in tile_data:
            self.tile_map[(col, row)] = tid

        # Second pass — build collision rects from the resolved map only.
        # No position can be both a solid rect AND a ghost barrier rect.
        for (col, row), tid in self.tile_map.items():
            if tid in SOLID_TILES:
                self.solid_rects.append(pygame.Rect(col*TILE, row*TILE, TILE, TILE))
            if tid in GHOST_TILES:
                self.ghost_barrier_rects.append(pygame.Rect(col*TILE, row*TILE, TILE, TILE))

        self.boxes=[]; self.plates=[]; self.gates={}
        self.levers=[]; self.moving_platforms=[]; self.enemies=[]
        self.pads=[]; self.spikes=[]; self.exit_rect=None
        self.spawn_pos=(2*TILE,15*TILE); self.torches=[]

        for obj in objects:
            ot=obj['type']; ox=obj['col']*TILE; oy=obj['row']*TILE
            if ot=='spawn':
                self.spawn_pos=(ox,oy)
            elif ot=='box':
                self.boxes.append(Box(obj['col'],obj['row'],tileset))
            elif ot=='plate':
                self.plates.append(
                    Plate(obj['col'],obj['row'],obj['id'],obj['targets'],tileset))
            elif ot=='gate':
                g=Gate(obj['col'],obj['row'],obj['id'],tileset,obj.get('open',False))
                self.gates[obj['id']]=g
            elif ot=='lever':
                self.levers.append(
                    Lever(obj['col'],obj['row'],obj['id'],obj['targets']))
            elif ot=='mplat':
                self.moving_platforms.append(
                    MovingPlatform(obj['col'],obj['row'],
                                   obj['axis'],obj['dist'],obj['speed'],tileset))
            elif ot=='enemy':
                self.enemies.append(
                    Enemy(obj['col'],obj['row'],obj.get('patrol',3)))
            elif ot=='spike':
                self.spikes.append(pygame.Rect(ox,oy+20,TILE,12))
            elif ot=='pad':
                self.pads.append(
                    {'rect':pygame.Rect(ox,oy,TILE,TILE),'id':obj['id'],'touched':False})
            elif ot=='exit':
                self.exit_rect=pygame.Rect(ox,oy,TILE,TILE)

        # Auto-place torches
        rng=random.Random(sum(col+row for (_,col,row) in tile_data[:50]))
        for (col,row),tid in self.tile_map.items():
            if tid in SOLID_TILES and row < ROWS-2:
                if rng.random() < 0.04:
                    self.torches.append(TorchLight(
                        col*TILE+TILE//2, row*TILE+TILE,
                        radius=rng.randint(60,100),
                        color=(255,rng.randint(120,160),30)))

        self.bg=make_bg()
        self._rebuild_gates()
        _current_solids=self.all_solids()

    def _rebuild_gates(self):
        self.gate_solid=[g.rect() for g in self.gates.values()
                         if not (g.open and g.y <= g.base_y-TILE*4)]

    def all_solids(self):
        """Solid tiles + gates. Used by ghost — no ghost barriers."""
        return self.solid_rects + self.gate_solid

    def living_solids(self):
        """Solid tiles + gates + ghost barriers. Used by living player."""
        return self.solid_rects + self.gate_solid + self.ghost_barrier_rects

    def _activate_targets(self, targets, particles, sound_mgr=None):
        for tid in targets:
            if tid in self.gates:
                self.gates[tid].open=True
                burst(particles,
                      self.gates[tid].x+TILE//2, self.gates[tid].base_y,
                      C_GOLD,20,3.5,life=35)
                if sound_mgr:
                    sound_mgr.play('gate')

    def _deactivate_targets(self, targets):
        for tid in targets:
            if tid in self.gates:
                if not any(p.active for p in self.plates if tid in p.targets) \
                   and not any(lv.active for lv in self.levers if tid in lv.targets):
                    self.gates[tid].open=False
                    self.gates[tid].y=float(self.gates[tid].base_y)

    def update(self, player, cam, interact_pressed=False, sound_mgr=None):
        global _current_solids
        self.t+=1; self.reached_exit=False
        all_s=self.all_solids()
        _current_solids=all_s

        # Moving platforms
        for mp in self.moving_platforms: mp.update()

        # Gates
        for g in self.gates.values(): g.update()
        self._rebuild_gates()

        # Boxes
        mp_rects=[mp.rect() for mp in self.moving_platforms]
        for i,b in enumerate(self.boxes):
            others=[bx for j,bx in enumerate(self.boxes) if j!=i]
            b.update(all_s+mp_rects, others)

        # Pressure plates
        for plate in self.plates:
            was=plate.active
            plate.active=any(plate.rect().colliderect(b.rect()) for b in self.boxes)
            if plate.active and not was:
                burst(self.particles,plate.x+TILE//2,plate.y+TILE//2,C_GREEN,14,2.5,life=30)
                self._activate_targets(plate.targets, self.particles, sound_mgr)
                if sound_mgr:
                    sound_mgr.play('plate')
            elif not plate.active and was:
                self._deactivate_targets(plate.targets)

        # Levers
        # Levers
        for lv in self.levers:
            lv.update()
            if not player.ghost:
                changed = lv.try_activate(player.rect(), interact_pressed, self.particles)
                if changed:
                    if lv.active:
                        self._activate_targets(lv.targets, self.particles, sound_mgr)
                        if sound_mgr:
                            sound_mgr.play('lever')
                    else:
                        self._deactivate_targets(lv.targets)

        # Enemies
        for e in self.enemies:
            e.update(all_s, player.rect(), player.ghost, self.particles)
            if not player.ghost and e.alive:
                if player.rect().colliderect(e.rect()):
                    player.dead=True; cam.shake(6,12)
                    burst(self.particles,
                          player.rect().centerx,player.rect().centery,
                          C_RED,22,4.0,life=38)

        if not player.dead and not player.ghost:
            for s in self.spikes:
                if player.rect().colliderect(s):
                    player.dead=True; cam.shake(5,10)
                    burst(self.particles,
                          player.rect().centerx,player.rect().centery,
                          C_RED,22,4.0,life=38)
            for pad in self.pads:
                if player.rect().colliderect(pad['rect']):
                    player.set_spawn(pad['rect'].x,pad['rect'].y-player.H)
                    if not pad['touched']:
                        pad['touched']=True
                        burst(self.particles,
                              pad['rect'].centerx,pad['rect'].top,
                              C_GREEN,12,2.0,life=28,sz=2)
                        if sound_mgr:
                            sound_mgr.play('checkpoint')
            if self.exit_rect and player.rect().colliderect(self.exit_rect):
                self.reached_exit=True

        for p in self.particles: p.upd()
        self.particles=[p for p in self.particles if p.life>0]

    # ── DRAW ─────────────────────────────────────────────
    def draw(self, surf, cam, far_layer, mid_layer, player, gt, fsm):
        px  = int(cam.x*0.08)%SW
        surf.blit(far_layer,(-px,0)); surf.blit(far_layer,(SW-px,0))
        px2 = int(cam.x*0.18)%SW
        surf.blit(mid_layer,(-px2,0)); surf.blit(mid_layer,(SW-px2,0))
        bx,by = cam.apply(0,0); surf.blit(self.bg,(bx,by))

        for tc in self.torches: tc.draw(surf,cam,gt)

        # Ghost-only tiles — bright when ghost, dim when living
        for (col,row),tid in self.tile_map.items():
            if tid not in GHOST_TILES: continue
            sx,sy=cam.apply(col*TILE,row*TILE)
            if sx<-TILE or sx>SW or sy<-TILE or sy>SH: continue
            alpha=150+int(70*math.sin(gt*0.07+col*0.4)) if player.ghost else 28
            surf.blit(self.tileset.get(tid[0],tid[1],alpha),(sx,sy))

        # Solid tiles
        for (col,row),tid in self.tile_map.items():
            if tid not in SOLID_TILES: continue
            sx,sy=cam.apply(col*TILE,row*TILE)
            if sx<-TILE or sx>SW or sy<-TILE or sy>SH: continue
            surf.blit(self.tileset.get(tid[0],tid[1]),(sx,sy))
            pygame.draw.line(surf,(110,95,72),(sx,sy),(sx+TILE-1,sy),1)
            pygame.draw.line(surf,(22,18,14),(sx,sy+TILE-1),(sx+TILE-1,sy+TILE-1),1)

        # Moving platforms
        for mp in self.moving_platforms: mp.draw(surf,cam,gt)

        # Gates
        for g in self.gates.values(): g.draw(surf,cam,gt)

        # Levers
        for lv in self.levers: lv.draw(surf,cam,gt)

        # Plates
        for plate in self.plates: plate.draw(surf,cam,gt,fsm)

        # Boxes
        for b in self.boxes: b.draw(surf,cam,gt)

        # Enemies
        for e in self.enemies: e.draw(surf,cam,gt)

        # Spikes
        for s in self.spikes:
            sx,sy=cam.apply(s.x,s.y)
            for i in range(3):
                tx=sx+4+i*9
                pygame.draw.polygon(surf,(155,145,128),[(tx,sy+12),(tx+4,sy+12),(tx+2,sy)])
                pygame.draw.polygon(surf,(205,195,180),[(tx+1,sy+10),(tx+3,sy+10),(tx+2,sy+2)])

        # Pads
        for pad in self.pads:
            sx,sy=cam.apply(pad['rect'].x,pad['rect'].y)
            pulse=abs(math.sin(gt*0.06)); act=pad['touched']
            gc=(int(38+52*pulse),int(175+50*pulse),int(75+45*pulse)) if act \
               else (int(15+25*pulse),int(65+42*pulse),int(42+26*pulse))
            for r2 in [13,8,4]:
                gs=pygame.Surface((r2*2,r2*2),pygame.SRCALPHA)
                pygame.draw.ellipse(gs,(*gc,int(55*r2/13)+20),(0,0,r2*2,r2))
                surf.blit(gs,(sx+TILE//2-r2,sy+26))
            pygame.draw.ellipse(surf,gc,(sx+4,sy+26,TILE-8,6))

        # Exit portal
        if self.exit_rect:
            sx,sy=cam.apply(self.exit_rect.x,self.exit_rect.y)
            pulse=abs(math.sin(gt*0.07))
            for r2 in [22,15,9,5]:
                a2=int(45+65*pulse)*r2//22
                gs=pygame.Surface((r2*2,r2*2),pygame.SRCALPHA)
                pygame.draw.circle(gs,(75,155,255,a2),(r2,r2),r2)
                surf.blit(gs,(sx+TILE//2-r2,sy+TILE//2-r2))
            pygame.draw.circle(surf,(175,222,255),(sx+TILE//2,sy+TILE//2),5)
            if fsm:
                et=fsm.render("EXIT",True,(175,222,255))
                surf.blit(et,(sx+TILE//2-et.get_width()//2,sy-16))

        # Particles
        for p in self.particles: p.draw(surf,cam)

        # Ghost world overlay
        if player.ghost:
            ov=pygame.Surface((SW,SH),pygame.SRCALPHA)
            ov.fill((15,25,70,40)); surf.blit(ov,(0,0))
