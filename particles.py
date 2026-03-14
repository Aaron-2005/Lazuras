# particles.py — particle system

import pygame, math, random
from constants import SW, SH


class P:
    __slots__ = ('x','y','vx','vy','col','life','ml','grav','sz')
    def __init__(self, x, y, vx, vy, col, life, grav=0.14, sz=3):
        self.x=float(x); self.y=float(y); self.vx=vx; self.vy=vy
        self.col=col; self.life=self.ml=life; self.grav=grav; self.sz=sz

    def upd(self):
        self.x+=self.vx; self.y+=self.vy
        self.vy+=self.grav; self.vx*=0.93; self.life-=1

    def draw(self, surf, cam):
        if self.life <= 0: return
        f  = self.life/self.ml; a = int(255*f); sz = max(1, int(self.sz*f))
        sx, sy = cam.apply(int(self.x), int(self.y))
        if not (-sz < sx < SW+sz and -sz < sy < SH+sz): return
        tmp = pygame.Surface((sz*2, sz*2), pygame.SRCALPHA)
        pygame.draw.circle(tmp, (*self.col[:3], a), (sz, sz), sz)
        surf.blit(tmp, (sx-sz, sy-sz))


def burst(ps, x, y, col, n=16, spd=3.0, grav=0.15, life=28, sz=3):
    for _ in range(n):
        a = random.uniform(0, math.pi*2); s = random.uniform(0.3, spd)
        ps.append(P(x, y, math.cos(a)*s, math.sin(a)*s, col,
                    life+random.randint(-5,5), grav, sz))
