# test_main.py — The Lazarus Project (test launcher with level select)
# To run: python3 test_main.py
# Requires: pip install pygame
# lazarus_tileset.png must be in the same directory
#
# CONTROLS
#   A/D or ←/→       Walk
#   W/↑/SPACE        Jump (living)
#   S/↓              Float down (ghost, if your player supports it)
#   Q                Toggle ghost form
#   E                Activate lever (near one)
#   R                Restart level
#   ESC              Quit
#
# TEST TITLE CONTROLS
#   LEFT / RIGHT     Change selected level
#   Type digits      Enter level number (e.g. 12, 13)
#   BACKSPACE        Edit typed level
#   ENTER / SPACE    Start selected level

import pygame, sys, math, os, random, json
from constants import *
from tileset import TileSet
from player import Player
from level_runtime import Camera, Level, make_far_layer, make_mid_layer, _current_solids
import level_runtime
from levels import LEVELS

# Try to import sound manager (optional feature)
try:
    from sound_manager import SoundManager
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False
    print("Sound manager not available - running without sound")

# ── font refs shared across modules ─────────────────────
import player as _player_mod

_fsm = None
_fmed = None
_fbig = None
_SAVE_FILE = "lazarus_test_save.json"


def _save_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), _SAVE_FILE)


def load_progress():
    data = {'selected_level': 0, 'stats': {}}
    try:
        with open(_save_path(), 'r', encoding='utf-8') as f:
            raw = json.load(f)
        if isinstance(raw, dict):
            data.update(raw)
    except Exception:
        pass

    selected = int(data.get('selected_level', 0))
    selected = max(0, min(selected, len(LEVELS) - 1))
    stats_data = data.get('stats', {})
    if not isinstance(stats_data, dict):
        stats_data = {}
    return selected, stats_data


def save_progress(selected_level, stats):
    payload = {
        'version': 1,
        'selected_level': max(0, min(int(selected_level), len(LEVELS) - 1)),
        'stats': stats.to_dict(),
    }
    try:
        path = _save_path()
        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2)
        os.replace(tmp, path)
    except Exception:
        pass


# ── Game state tracking ──────────────────────────────────
class GameStats:
    """Track player statistics across the game"""
    def __init__(self):
        self.total_deaths = 0
        self.level_attempts = [0] * len(LEVELS)
        self.level_best_cycles = [DEFAULT_CYCLES] * len(LEVELS)
        self.ghost_time_used = 0

    def record_death(self, level_idx):
        self.total_deaths += 1
        if 0 <= level_idx < len(self.level_attempts):
            self.level_attempts[level_idx] += 1

    def record_level_complete(self, level_idx, cycles_remaining):
        if 0 <= level_idx < len(self.level_best_cycles):
            self.level_best_cycles[level_idx] = min(
                self.level_best_cycles[level_idx],
                DEFAULT_CYCLES - cycles_remaining
            )

    def to_dict(self):
        return {
            'total_deaths': int(self.total_deaths),
            'level_attempts': [int(v) for v in self.level_attempts],
            'level_best_cycles': [int(v) for v in self.level_best_cycles],
            'ghost_time_used': int(self.ghost_time_used),
        }

    def load_from_dict(self, data):
        if not isinstance(data, dict):
            return
        self.total_deaths = max(0, int(data.get('total_deaths', self.total_deaths)))
        self.ghost_time_used = max(0, int(data.get('ghost_time_used', self.ghost_time_used)))

        attempts = data.get('level_attempts', self.level_attempts)
        if isinstance(attempts, list):
            for i in range(min(len(attempts), len(self.level_attempts))):
                self.level_attempts[i] = max(0, int(attempts[i]))

        best = data.get('level_best_cycles', self.level_best_cycles)
        if isinstance(best, list):
            for i in range(min(len(best), len(self.level_best_cycles))):
                self.level_best_cycles[i] = max(0, int(best[i]))


# ══════════════════════════════════════════════════════════
# HUD
# ══════════════════════════════════════════════════════════
def draw_hud(surf, player, lnum, hint_t, gt, stats=None):
    pan = pygame.Surface((340, 78), pygame.SRCALPHA)
    pan.fill((6, 4, 3, 200))
    surf.blit(pan, (10, 10))

    for i in range(DEFAULT_CYCLES):
        cx = 22 + i * 28
        cy = 28
        alive = i < player.cycles
        c = C_GREEN if alive else (20, 20, 30)
        e = (65, 185, 95) if alive else (32, 32, 44)
        pygame.draw.circle(surf, c, (cx, cy), 10)
        pygame.draw.circle(surf, e, (cx, cy), 10, 2)
        if alive:
            inner = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(inner, (195, 255, 205, 180), (4, 4), 4)
            surf.blit(inner, (cx - 4, cy - 4))

    ft = _fsm.render("◈  GHOST", True, C_SOUL) if player.ghost \
         else _fsm.render("◆  LIVING", True, C_LIVING)
    surf.blit(ft, (155, 20))

    if stats:
        deaths_txt = _fsm.render(f"Deaths: {stats.total_deaths}", True, (120, 100, 80))
        surf.blit(deaths_txt, (155, 36))
        ghost_secs = max(0.0, player.gtimer / FPS)
        ghost_txt = _fsm.render(f"Ghost Timer: {ghost_secs:.1f}s", True, (120, 100, 80))
        surf.blit(ghost_txt, (155, 50))

    if player.ghost or player.gtimer > 0:
        bw = 160
        bx = 14
        by2 = 66
        max_timer = getattr(player, "GHOST_BURST_FRAMES", 1)
        f = player.gtimer / max_timer if max_timer > 0 else 0
        f = max(0, min(1, f))

        bg2 = pygame.Surface((bw, 6), pygame.SRCALPHA)
        bg2.fill((8, 8, 24, 200))
        surf.blit(bg2, (bx, by2))
        bc = (72, 130, 255) if f > 0.3 else (215, 55, 55)
        pygame.draw.rect(surf, bc, (bx, by2, int(bw * f), 6))
        for ti in range(1, 4):
            pygame.draw.line(surf, (35, 35, 55), (bx + bw * ti // 4, by2), (bx + bw * ti // 4, by2 + 6), 1)
        pygame.draw.rect(surf, (95, 125, 215), (bx, by2, bw, 6), 1)
        lbl = _fsm.render("SOUL TIMER" if player.ghost else "RECHARGING", True,
                          (75, 115, 195) if player.ghost else (48, 48, 75))
        surf.blit(lbl, (bx, by2 + 9))
    else:
        if hasattr(player, "ghost_bursts_left") and hasattr(player, "MAX_GHOST_BURSTS"):
            rl = _fsm.render(
                f"GHOST BURSTS: {player.ghost_bursts_left}/{player.MAX_GHOST_BURSTS}",
                True,
                (58, 158, 78) if player.ghost_bursts_left > 0 else (185, 70, 70)
            )
        else:
            rl = _fsm.render("SOUL READY  [Q]", True, (58, 158, 78))
        surf.blit(rl, (14, 66))

    names = [
        "I · THE ANTECHAMBER",
        "II · THE DESCENT HALLS",
        "III · THE INNER SANCTUM",
        "IV · THE CLOCKWORK VAULT",
        "V · THE HAUNTED AQUEDUCT",
        "VI · THE LAZARUS CHAMBER"
    ]
    level_label = names[lnum - 1] if 1 <= lnum <= len(names) else f"LEVEL {lnum}"
    ln = _fsm.render(level_label, True, C_DIM)
    surf.blit(ln, (SW - ln.get_width() - 14, 14))

    for i in range(len(LEVELS)):
        cx = SW - 14 - i * 14
        cy = 32
        c = C_GREEN if i < lnum else (30, 30, 40)
        pygame.draw.circle(surf, c, (cx, cy), 4)

    if hint_t > 0:
        a = min(255, hint_t * 3)
        lines = [
            "Q — Ghost: blocked by solid walls, passes through ghost barriers  |  E — Activate levers  |  M — Toggle Sound",
            "Push boxes onto plates to open gates  |  Ride moving platforms  |  P — Pause"
        ]
        for i, line in enumerate(lines):
            ht = _fsm.render(line, True, (138, 125, 105))
            hs = pygame.Surface(ht.get_size(), pygame.SRCALPHA)
            hs.blit(ht, (0, 0))
            hs.set_alpha(a)
            surf.blit(hs, (SW // 2 - ht.get_width() // 2, SH - 44 + i * 18))


def draw_overlay(surf, title, sub='', col=C_WHITE, sub2=''):
    ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
    for y in range(SH):
        ed = min(y, SH - y) / SH
        a = int(185 * (1 - ed ** 0.4))
        pygame.draw.line(ov, (0, 0, 0, a), (0, y), (SW, y))
    surf.blit(ov, (0, 0))
    t = _fbig.render(title, True, col)
    surf.blit(t, (SW // 2 - t.get_width() // 2, SH // 2 - 52))
    if sub:
        s = _fmed.render(sub, True, (155, 142, 122))
        surf.blit(s, (SW // 2 - s.get_width() // 2, SH // 2 + 8))
    if sub2:
        s2 = _fsm.render(sub2, True, (95, 88, 75))
        surf.blit(s2, (SW // 2 - s2.get_width() // 2, SH // 2 + 40))


# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════
def main():
    global _fsm, _fmed, _fbig

    pygame.init()
    screen = pygame.display.set_mode((SW, SH))
    pygame.display.set_caption("THE LAZARUS PROJECT — TEST")
    clock = pygame.time.Clock()

    _fsm = pygame.font.SysFont("consolas", 13)
    _fmed = pygame.font.SysFont("consolas", 20, bold=True)
    _fbig = pygame.font.SysFont("consolas", 40, bold=True)

    _player_mod._fsm = _fsm

    sd = os.path.dirname(os.path.abspath(__file__))
    ts_path = os.path.join(sd, "lazarus_tileset.png")
    if not os.path.exists(ts_path):
        print(f"ERROR: lazarus_tileset.png not found at:\n  {ts_path}")
        sys.exit(1)

    tileset = TileSet(ts_path)
    far_layer = make_far_layer()
    mid_layer = make_mid_layer()

    sound_mgr = None
    if SOUND_AVAILABLE:
        try:
            sound_mgr = SoundManager(enabled=True)
        except Exception:
            sound_mgr = None
            print("Could not initialize sound manager")

    stats = GameStats()

    selected_level, saved_stats = load_progress()
    stats.load_from_dict(saved_stats)

    cur = selected_level
    level_entry = str(selected_level + 1)
    hint_t = 520
    gt = 0

    def load(idx, cycles=DEFAULT_CYCLES):
        td, obs = LEVELS[idx]()
        lvl = Level(td, obs, tileset)
        sx, sy = lvl.spawn_pos
        p = Player(sx, sy - Player.H)
        p.cycles = cycles
        if hasattr(p, "reset_ghost_bursts"):
            p.reset_ghost_bursts()
        return lvl, p

    level, player = load(cur)
    cam = Camera()
    state = 'title'
    state_t = 0
    paused = False

    running = True
    while running:
        clock.tick(FPS)
        gt += 1
        state_t += 1

        interact_pressed = False
        prev_dead = player.dead if state == 'play' and not paused else False

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False

                if ev.key == pygame.K_m and sound_mgr:
                    sound_mgr.toggle()

                if state == 'title':
                    if ev.key == pygame.K_LEFT:
                        selected_level = max(0, selected_level - 1)
                        level_entry = ""

                    elif ev.key == pygame.K_RIGHT:
                        selected_level = min(len(LEVELS) - 1, selected_level + 1)
                        level_entry = ""

                    elif ev.key == pygame.K_BACKSPACE:
                        level_entry = level_entry[:-1]
                        if level_entry:
                            n = int(level_entry)
                            selected_level = max(0, min(len(LEVELS) - 1, n - 1))

                    elif ev.unicode.isdigit():
                        if len(level_entry) < 3:
                            level_entry += ev.unicode
                            n = int(level_entry)
                            if n >= 1:
                                selected_level = max(0, min(len(LEVELS) - 1, n - 1))

                    elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if level_entry:
                            n = int(level_entry)
                            selected_level = max(0, min(len(LEVELS) - 1, n - 1))
                        cur = selected_level
                        level, player = load(cur)
                        state = 'play'
                        state_t = 0
                        hint_t = 200

                elif state == 'play':
                    if ev.key == pygame.K_p:
                        paused = not paused

                    if not paused:
                        if ev.key == pygame.K_q:
                            prev_ghost = player.ghost
                            player.toggle_ghost(level.all_solids())
                            if sound_mgr and prev_ghost != player.ghost:
                                sound_mgr.play('ghost_on' if player.ghost else 'ghost_off')

                        if ev.key == pygame.K_e:
                            interact_pressed = True

                        if ev.key == pygame.K_r:
                            level, player = load(cur, player.cycles)
                            state = 'play'
                            state_t = 0
                            hint_t = 200

                elif state in ('dead', 'gameover', 'win'):
                    if ev.key == pygame.K_r:
                        if state in ('gameover', 'win'):
                            cur = selected_level
                            level, player = load(cur, DEFAULT_CYCLES)
                        else:
                            level, player = load(cur, player.cycles)
                        state = 'play'
                        state_t = 0
                        hint_t = 200

        if state == 'play' and not paused:
            hint_t = max(0, hint_t - 1)
            keys = pygame.key.get_pressed()

            player.update(
                keys,
                level.all_solids(),
                level.living_solids(),
                level.boxes,
                level.moving_platforms,
                level.particles,
                cam,
                level_runtime._current_solids,
                sound_mgr
            )
            level.update(player, cam, interact_pressed, sound_mgr)
            cam.update(player.x + Player.W // 2, player.y + Player.H // 2)

            if player.dead and not prev_dead:
                player.cycles = max(0, player.cycles - 1)
                if sound_mgr:
                    sound_mgr.play('death')
                stats.record_death(cur)
                save_progress(selected_level, stats)

            if player.dead:
                state = 'gameover' if player.cycles <= 0 else 'dead'
                state_t = 0

            if level.reached_exit:
                if sound_mgr:
                    sound_mgr.play('exit')
                stats.record_level_complete(cur, player.cycles)
                cur += 1
                selected_level = min(cur, len(LEVELS) - 1)
                level_entry = str(selected_level + 1)
                save_progress(selected_level, stats)

                if cur >= len(LEVELS):
                    state = 'win'
                    state_t = 0
                else:
                    level, player = load(cur, player.cycles)
                    state = 'play'
                    state_t = 0

        elif state == 'dead' and state_t > 85:
            player.respawn()
            state = 'play'
            state_t = 0

        # ── RENDER ──────────────────────────────────────
        screen.fill(C_BG)

        if state == 'title':
            screen.blit(far_layer, (0, 0))
            screen.blit(mid_layer, (0, 0))

            ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 140))
            screen.blit(ov, (0, 0))

            t1 = _fbig.render("THE LAZARUS PROJECT", True, C_ACCENT)
            screen.blit(t1, (SW // 2 - t1.get_width() // 2, SH // 2 - 110))

            t2 = _fmed.render(
                f"Testing launcher  —  {len(LEVELS)} levels",
                True,
                (120, 105, 80)
            )
            screen.blit(t2, (SW // 2 - t2.get_width() // 2, SH // 2 - 60))

            lines = [
                "Choose any level to jump straight in.",
                "LEFT / RIGHT changes level.",
                "Type digits for larger level numbers, then press ENTER.",
                "",
                "Controls: A/D - Move | W/SPACE - Jump | E - Use Lever | Q - Ghost Toggle | P - Pause | M - Sound"
            ]
            for i, line in enumerate(lines):
                lt = _fsm.render(line, True, (90, 80, 62))
                screen.blit(lt, (SW // 2 - lt.get_width() // 2, SH // 2 - 8 + i * 16))

            sel_txt = f"Selected Level: {selected_level + 1}/{len(LEVELS)}"

            st = _fmed.render(sel_txt, True, (170, 150, 110))
            screen.blit(st, (SW // 2 - st.get_width() // 2, SH // 2 + 92))

            pt = _fmed.render("ENTER / SPACE to start", True, (70, 62, 48))
            screen.blit(pt, (SW // 2 - pt.get_width() // 2, SH // 2 + 128))

            ct = _fsm.render(
                "BACKSPACE edits typed number",
                True,
                (95, 88, 75)
            )
            screen.blit(ct, (SW // 2 - ct.get_width() // 2, SH // 2 + 158))

        else:
            level.draw(screen, cam, far_layer, mid_layer, player, gt, _fsm)
            player.draw(screen, cam, level.boxes, level_runtime._current_solids)
            draw_hud(screen, player, cur + 1, hint_t, gt, stats)

            if state == 'dead':
                draw_overlay(
                    screen,
                    f"RESURRECTION  {DEFAULT_CYCLES - player.cycles}/{DEFAULT_CYCLES}",
                    "The soul returns...",
                    C_ACCENT
                )
            elif state == 'gameover':
                draw_overlay(
                    screen,
                    "ALL CYCLES EXHAUSTED",
                    "The Lazarus Project has failed.",
                    C_RED,
                    "R — Restart"
                )
            elif state == 'win':
                draw_overlay(
                    screen,
                    "YOU ESCAPED THE TEMPLE",
                    "The Lazarus Project lives on.",
                    C_GREEN,
                    "R — Play again"
                )

            if paused:
                pov = pygame.Surface((SW, SH), pygame.SRCALPHA)
                pov.fill((0, 0, 0, 180))
                screen.blit(pov, (0, 0))
                pt = _fbig.render("PAUSED", True, C_ACCENT)
                screen.blit(pt, (SW // 2 - pt.get_width() // 2, SH // 2 - 30))
                ps = _fmed.render("Press P to resume", True, (155, 142, 122))
                screen.blit(ps, (SW // 2 - ps.get_width() // 2, SH // 2 + 10))
                stat_y = SH // 2 + 60
                st1 = _fsm.render(f"Total Deaths: {stats.total_deaths}", True, (120, 110, 95))
                screen.blit(st1, (SW // 2 - st1.get_width() // 2, stat_y))

        pygame.display.flip()

    pygame.quit()
    save_progress(selected_level, stats)
    sys.exit()


if __name__ == '__main__':
    main()