# main.py — The Lazarus Project
# To run: python3 main.py
# Requires: pip install pygame
# lazarus_tileset.png must be in the same directory
#
# CONTROLS
#   A/D or ←/→       Walk
#   W/↑/SPACE         Jump (living) | Float up (ghost)
#   S/↓               Float down (ghost)
#   Q                 Toggle ghost form
#   E                 Activate lever (near one)
#   R                 Restart level
#   ESC               Quit

import pygame, sys, math, os, random
from constants import *
from tileset import TileSet
from player import Player
from level_runtime import Camera, Level, make_far_layer, make_mid_layer, _current_solids
import level_runtime
from levels import LEVELS

# ── font refs shared across modules ─────────────────────
import player as _player_mod

_fsm  = None
_fmed = None
_fbig = None


# ══════════════════════════════════════════════════════════
# HUD
# ══════════════════════════════════════════════════════════
def draw_hud(surf, player, lnum, hint_t, gt):
    pan=pygame.Surface((300,52),pygame.SRCALPHA); pan.fill((6,4,3,200))
    surf.blit(pan,(10,10))

    for i in range(4):
        cx=22+i*28; cy=28
        alive = i < player.cycles
        c = C_GREEN if alive else (20,20,30)
        e = (65,185,95) if alive else (32,32,44)
        pygame.draw.circle(surf,c,(cx,cy),10)
        pygame.draw.circle(surf,e,(cx,cy),10,2)
        if alive:
            inner=pygame.Surface((8,8),pygame.SRCALPHA)
            pygame.draw.circle(inner,(195,255,205,180),(4,4),4)
            surf.blit(inner,(cx-4,cy-4))

    ft = _fsm.render("◈  GHOST",True,C_SOUL) if player.ghost \
         else _fsm.render("◆  LIVING",True,C_LIVING)
    surf.blit(ft,(155,20))

    if player.ghost or player.gtimer > 0:
        bw=160; bx=14; by2=66
        f=player.gtimer/player.GDUR
        bg2=pygame.Surface((bw,6),pygame.SRCALPHA); bg2.fill((8,8,24,200))
        surf.blit(bg2,(bx,by2))
        bc=(72,130,255) if f > 0.3 else (215,55,55)
        pygame.draw.rect(surf,bc,(bx,by2,int(bw*f),6))
        for ti in range(1,4):
            pygame.draw.line(surf,(35,35,55),(bx+bw*ti//4,by2),(bx+bw*ti//4,by2+6),1)
        pygame.draw.rect(surf,(95,125,215),(bx,by2,bw,6),1)
        lbl=_fsm.render("SOUL TIMER" if player.ghost else "RECHARGING",True,
                         (75,115,195) if player.ghost else (48,48,75))
        surf.blit(lbl,(bx,by2+9))
    else:
        rl=_fsm.render("SOUL READY  [Q]",True,(58,158,78))
        surf.blit(rl,(14,66))

    names=["I · THE ANTECHAMBER","II · THE DESCENT HALLS","III · THE INNER SANCTUM",
           "IV · THE CLOCKWORK VAULT","V · THE HAUNTED AQUEDUCT","VI · THE LAZARUS CHAMBER"]
    ln=_fsm.render(names[min(lnum-1,5)],True,C_DIM)
    surf.blit(ln,(SW-ln.get_width()-14,14))

    # Level progress dots
    for i in range(len(LEVELS)):
        cx=SW-14-i*14; cy=32
        c=C_GREEN if i < lnum else (30,30,40)
        pygame.draw.circle(surf,c,(cx,cy),4)

    if hint_t > 0:
        a=min(255,hint_t*3)
        lines=["Q — Ghost: fly through walls to scout  |  E — Activate levers",
               "Push boxes onto plates to open gates  |  Ride moving platforms"]
        for i,line in enumerate(lines):
            ht=_fsm.render(line,True,(138,125,105))
            hs=pygame.Surface(ht.get_size(),pygame.SRCALPHA)
            hs.blit(ht,(0,0)); hs.set_alpha(a)
            surf.blit(hs,(SW//2-ht.get_width()//2,SH-44+i*18))


def draw_overlay(surf, title, sub='', col=C_WHITE, sub2=''):
    ov=pygame.Surface((SW,SH),pygame.SRCALPHA)
    for y in range(SH):
        ed=min(y,SH-y)/SH; a=int(185*(1-ed**0.4))
        pygame.draw.line(ov,(0,0,0,a),(0,y),(SW,y))
    surf.blit(ov,(0,0))
    t=_fbig.render(title,True,col)
    surf.blit(t,(SW//2-t.get_width()//2,SH//2-52))
    if sub:
        s=_fmed.render(sub,True,(155,142,122))
        surf.blit(s,(SW//2-s.get_width()//2,SH//2+8))
    if sub2:
        s2=_fsm.render(sub2,True,(95,88,75))
        surf.blit(s2,(SW//2-s2.get_width()//2,SH//2+40))


# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════
def main():
    global _fsm, _fmed, _fbig

    pygame.init()
    screen=pygame.display.set_mode((SW,SH))
    pygame.display.set_caption("THE LAZARUS PROJECT")
    clock=pygame.time.Clock()

    _fsm =pygame.font.SysFont("consolas",13)
    _fmed=pygame.font.SysFont("consolas",20,bold=True)
    _fbig=pygame.font.SysFont("consolas",40,bold=True)

    # Share font with player module for PUSH hint
    _player_mod._fsm = _fsm

    sd      =os.path.dirname(os.path.abspath(__file__))
    ts_path =os.path.join(sd,"lazarus_tileset.png")
    if not os.path.exists(ts_path):
        print(f"ERROR: lazarus_tileset.png not found at:\n  {ts_path}")
        sys.exit(1)

    tileset    = TileSet(ts_path)
    far_layer  = make_far_layer()
    mid_layer  = make_mid_layer()

    cur=0; hint_t=520; gt=0

    def load(idx, cycles=4):
        td,obs = LEVELS[idx]()
        lvl    = Level(td, obs, tileset)
        sx,sy  = lvl.spawn_pos
        p      = Player(sx, sy-Player.H); p.cycles=cycles
        return lvl, p

    level, player = load(cur)
    cam=Camera(); state='title'; state_t=0

    running=True
    while running:
        clock.tick(FPS); gt+=1; state_t+=1

        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: running=False
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_ESCAPE: running=False
                if state=='title':
                    state='play'; state_t=0
                elif state=='play':
                    if ev.key==pygame.K_q:
                        player.toggle_ghost(level.all_solids())
                    if ev.key==pygame.K_r:
                        level,player=load(cur,player.cycles)
                        state='play'; state_t=0; hint_t=200
                elif state in ('dead','gameover','win'):
                    if ev.key==pygame.K_r:
                        if state in ('gameover','win'):
                            cur=0; level,player=load(0,4)
                        else:
                            level,player=load(cur,player.cycles)
                        state='play'; state_t=0; hint_t=200

        if state=='play':
            hint_t=max(0,hint_t-1)
            keys=pygame.key.get_pressed()
            player.update(keys, level.all_solids(), level.boxes,
                          level.moving_platforms, level.particles, cam,
                          level_runtime._current_solids)
            level.update(player, cam)
            cam.update(player.x+Player.W//2, player.y+Player.H//2)

            if player.dead:
                state='gameover' if player.cycles<=0 else 'dead'; state_t=0
            if level.reached_exit:
                cur+=1
                if cur >= len(LEVELS): state='win'; state_t=0
                else: level,player=load(cur,player.cycles); state='play'; state_t=0

        elif state=='dead' and state_t > 85:
            player.respawn(); state='play'; state_t=0

        # ── RENDER ──────────────────────────────────────
        screen.fill(C_BG)
        if state=='title':
            screen.blit(far_layer,(0,0)); screen.blit(mid_layer,(0,0))
            ov=pygame.Surface((SW,SH),pygame.SRCALPHA); ov.fill((0,0,0,140))
            screen.blit(ov,(0,0))
            t1=_fbig.render("THE LAZARUS PROJECT",True,C_ACCENT)
            screen.blit(t1,(SW//2-t1.get_width()//2,SH//2-100))
            t2=_fmed.render("An underground temple escape  —  6 levels",True,(120,105,80))
            screen.blit(t2,(SW//2-t2.get_width()//2,SH//2-48))
            lines=[
                "A lab deep underground. The Lazarus Project has failed. You must escape.",
                "GHOST: scout the temple, fly through walls, flip levers.",
                "LIVING: push boxes onto plates, ride moving platforms, reach the exit.",
                "Ghost timer drains — plan where to rematerialise or die inside a wall.",
                "Cultist guards patrol — they cannot see your ghost form.",
            ]
            for i,line in enumerate(lines):
                lt=_fsm.render(line,True,(90,80,62))
                screen.blit(lt,(SW//2-lt.get_width()//2,SH//2+2+i*20))
            pt=_fmed.render("Press any key",True,(70,62,48))
            screen.blit(pt,(SW//2-pt.get_width()//2,SH//2+118))
        else:
            level.draw(screen,cam,far_layer,mid_layer,player,gt,_fsm)
            player.draw(screen,cam,level.boxes,level_runtime._current_solids)
            draw_hud(screen,player,cur+1,hint_t,gt)

            if state=='dead':
                draw_overlay(screen,f"RESURRECTION  {5-player.cycles}/4",
                             "The soul returns...",C_ACCENT)
            elif state=='gameover':
                draw_overlay(screen,"ALL CYCLES EXHAUSTED",
                             "The Lazarus Project has failed.",C_RED,"R — Restart")
            elif state=='win':
                draw_overlay(screen,"YOU ESCAPED THE TEMPLE",
                             "The Lazarus Project lives on.",C_GREEN,"R — Play again")

        pygame.display.flip()

    pygame.quit(); sys.exit()


if __name__=='__main__': main()
