# levels.py — reworked progression with cleaner puzzle flow

from tileset import *
from constants import COLS, ROWS

GATE_HEIGHT = 4


# -------------------------------------------------------
# Layout helpers
# -------------------------------------------------------
def hwall(t, tid, x0, x1, y):
    for x in range(x0, x1 + 1):
        t.append((tid, x, y))


def vwall(t, tid, x, y0, y1):
    for y in range(y0, y1 + 1):
        t.append((tid, x, y))


def plat(t, tid, x0, x1, y):
    for x in range(x0, x1 + 1):
        t.append((tid, x, y))


def fill_rect(t, tid, x0, y0, x1, y1):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            t.append((tid, x, y))


def shell(t, wall_tid, floor_tid, trim_tid=None):
    """Common room shell."""
    hwall(t, wall_tid, 0, COLS - 1, 0)
    hwall(t, floor_tid, 0, COLS - 1, ROWS - 1)
    vwall(t, wall_tid, 0, 1, ROWS - 2)
    vwall(t, wall_tid, COLS - 1, 1, ROWS - 2)
    hwall(t, floor_tid, 1, COLS - 2, ROWS - 2)
    if trim_tid is not None:
        hwall(t, trim_tid, 1, COLS - 2, 1)


def vwall_with_gaps(t, tid, x, y0, y1, gaps):
    """
    Draw a vertical wall but leave out one or more inclusive gap ranges.

    gaps: list of (gap_start, gap_end) tuples, inclusive.
    """
    gaps = sorted(gaps)
    cur = y0

    for gap_start, gap_end in gaps:
        if gap_end < y0 or gap_start > y1:
            continue

        gap_start = max(gap_start, y0)
        gap_end = min(gap_end, y1)

        if cur <= gap_start - 1:
            vwall(t, tid, x, cur, gap_start - 1)

        cur = max(cur, gap_end + 1)

    if cur <= y1:
        vwall(t, tid, x, cur, y1)


def gate_gap(row, height=GATE_HEIGHT):
    """Return the inclusive vertical gap covered by a gate."""
    return (row, row + height - 1)


# =======================================================
# LEVEL 1 — learn pushing a box onto a plate
# =======================================================
def build_level_1():
    """Editor sketch level: moving platform + lever + gate + exit."""
    G = T_GH_BAR
    W = T_W_DARK
    P = T_PL_STONE
    H = T_PL_HAZ

    t = []

    # Outer ghost barrier frame
    hwall(t, G, 0, COLS - 1, 0)
    hwall(t, G, 0, COLS - 1, ROWS - 1)
    vwall(t, G, 0, 1, ROWS - 2)
    vwall(t, G, COLS - 1, 1, ROWS - 2)

    # Start ledge
    plat(t, P, 1, 4, 15)

    # Left-side supports / blocks
    t.append((W, 0, 14))
    vwall(t, W, 4, 13, 16)
    t.append((P, 5, 13))

    # Stepping platforms
    plat(t, P, 7, 8, 12)
    t.append((P, 11, 11))
    plat(t, P, 15, 16, 10)

    # Main right platform
    plat(t, P, 20, 28, 12)

    # Upper-right wall shelf above the gate area
    # Leave x=23 free because the gate sits there
    hwall(t, W, 24, 28, 9)

    # Bottom supports
    vwall(t, W, 18, 14, 16)
    vwall(t, W, 27, 15, 16)

    # Small lever island on the right
    plat(t, P, 27, 28, 15)

    # Lava floor
    plat(t, H, 5, 17, 16)
    plat(t, H, 19, 26, 16)

    objs = [
        {'type': 'spawn', 'col': 2, 'row': 14},
        {'type': 'pad',   'col': 2, 'row': 14, 'id': 0},

        {'type': 'gate',  'col': 23, 'row': 9, 'id': 'gate0', 'open': False},
        {'type': 'lever', 'col': 28, 'row': 14, 'id': 'lev0', 'targets': ['gate0']},

        {'type': 'mplat', 'col': 20, 'row': 15, 'axis': 'h', 'dist': 3, 'speed': 1.1},

        {'type': 'exit',  'col': 28, 'row': 11},
    ]

    return t, objs


# =======================================================
# LEVEL 2 — first ghost route
# =======================================================
def build_level_2():
    S = T_W_SAND
    D = T_W_DARK
    F = T_FL_ANC
    FS = T_FL_SIL
    P = T_PL_STONE
    PS = T_PL_SIL

    t = []
    shell(t, D, F, T_W_CARVE)

    plat(t, FS, 1, 9, 14)
    plat(t, P, 12, 18, 11)
    plat(t, PS, 21, 28, 8)

    vwall(t, S, 10, 2, ROWS - 2)

    # Ghost-only path in the first divider
    vwall(t, T_GH_BAR, 10, 7, 11)

    objs = [
        {'type': 'spawn', 'col': 2, 'row': 13},
        {'type': 'pad', 'col': 2, 'row': 13, 'id': 0},
        {'type': 'box', 'col': 5, 'row': 13},
        {'type': 'plate', 'col': 7, 'row': 13, 'id': 0, 'targets': ['gate0']},
        {'type': 'gate', 'col': 20, 'row': 8, 'id': 'gate0', 'open': False},
        {'type': 'enemy', 'col': 14, 'row': 10, 'patrol': 2},
        {'type': 'spike', 'col': 22, 'row': 16},
        {'type': 'spike', 'col': 23, 'row': 16},
        {'type': 'exit', 'col': 26, 'row': 7},
        {'type': 'pad', 'col': 23, 'row': 7, 'id': 1},
    ]
    return t, objs


# =======================================================
# LEVEL 3 — lever + box combo
# =======================================================
def build_level_3():
    S = T_W_SAND
    D = T_W_OBS
    B = T_W_ENG
    F = T_FL_ANC
    FS = T_FL_SIL
    P = T_PL_STONE
    PC = T_PL_CARVE
    PD = T_PL_DARK

    t = []
    shell(t, D, F, T_W_CARVE)

    plat(t, FS, 1, 8, 14)
    plat(t, PC, 11, 17, 11)
    plat(t, P, 21, 28, 8)
    plat(t, PD, 12, 15, 6)

    # Walls with full gate-sized gaps
    vwall_with_gaps(t, S, 9, 2, ROWS - 2, [gate_gap(10)])
    vwall_with_gaps(t, B, 19, 2, ROWS - 2, [gate_gap(8)])

    # Ghost barrier with same gate-sized gap rule
    vwall_with_gaps(t, T_GH_BARD, 19, 6, 10, [gate_gap(8)])

    objs = [
        {'type': 'spawn', 'col': 2, 'row': 13},
        {'type': 'pad', 'col': 2, 'row': 13, 'id': 0},
        {'type': 'box', 'col': 4, 'row': 13},
        {'type': 'plate', 'col': 6, 'row': 13, 'id': 0, 'targets': ['gate0']},
        {'type': 'gate', 'col': 9, 'row': 10, 'id': 'gate0', 'open': False},
        {'type': 'lever', 'col': 13, 'row': 5, 'id': 'lev0', 'targets': ['gate1']},
        {'type': 'gate', 'col': 19, 'row': 8, 'id': 'gate1', 'open': False},
        {'type': 'enemy', 'col': 14, 'row': 10, 'patrol': 2},
        {'type': 'spike', 'col': 22, 'row': 16},
        {'type': 'spike', 'col': 23, 'row': 16},
        {'type': 'spike', 'col': 24, 'row': 16},
        {'type': 'exit', 'col': 26, 'row': 7},
        {'type': 'pad', 'col': 24, 'row': 7, 'id': 1},
    ]
    return t, objs


# =======================================================
# LEVEL 4 — moving platform tutorial
# =======================================================
def build_level_4():
    S = T_W_COBB
    D = T_W_ENG
    F = T_FL_MIX
    FS = T_FL_DKSIL
    P = T_PL_STONE
    PC = T_PL_CARVE

    t = []
    shell(t, D, F, T_W_CARVE)

    plat(t, FS, 1, 7, 14)
    plat(t, P, 12, 17, 11)
    plat(t, PC, 23, 28, 8)

    vwall_with_gaps(t, S, 9, 2, ROWS - 2, [gate_gap(10)])
    vwall(t, S, 20, 2, ROWS - 2)

    # Safety shelves around platform jumps
    plat(t, T_PL_DARK, 4, 6, 9)
    plat(t, T_PL_DARK, 14, 16, 6)

    objs = [
        {'type': 'spawn', 'col': 2, 'row': 13},
        {'type': 'pad', 'col': 2, 'row': 13, 'id': 0},
        {'type': 'lever', 'col': 5, 'row': 8, 'id': 'lev0', 'targets': ['gate0']},
        {'type': 'gate', 'col': 9, 'row': 10, 'id': 'gate0', 'open': False},
        {'type': 'mplat', 'col': 8, 'row': 12, 'axis': 'h', 'dist': 4, 'speed': 1.2},
        {'type': 'mplat', 'col': 19, 'row': 9, 'axis': 'v', 'dist': 3, 'speed': 1.0},
        {'type': 'enemy', 'col': 14, 'row': 10, 'patrol': 2},
        {'type': 'spike', 'col': 10, 'row': 16},
        {'type': 'spike', 'col': 11, 'row': 16},
        {'type': 'spike', 'col': 21, 'row': 16},
        {'type': 'spike', 'col': 22, 'row': 16},
        {'type': 'exit', 'col': 26, 'row': 7},
        {'type': 'pad', 'col': 24, 'row': 7, 'id': 1},
    ]
    return t, objs


# =======================================================
# LEVEL 5 — two boxes, two switches, more timing
# =======================================================
def build_level_5():
    S = T_W_BSLT
    D = T_W_OBS
    F = T_FL_GRATE
    FS = T_FL_MOSS
    P = T_PL_MOSS
    PB = T_PL_BONE
    PD = T_PL_DARK

    t = []
    shell(t, D, F, T_W_MOSS)

    plat(t, P, 1, 6, 14)
    plat(t, PB, 10, 15, 11)
    plat(t, PD, 19, 24, 8)
    plat(t, FS, 26, 28, 5)

    vwall_with_gaps(t, S, 8, 2, ROWS - 2, [gate_gap(10)])
    vwall_with_gaps(t, S, 17, 2, ROWS - 2, [gate_gap(8)])
    vwall_with_gaps(t, S, 25, 2, 10, [gate_gap(5)])

    vwall_with_gaps(t, T_GH_BAR, 17, 6, 10, [gate_gap(8)])

    objs = [
        {'type': 'spawn', 'col': 2, 'row': 13},
        {'type': 'pad', 'col': 2, 'row': 13, 'id': 0},
        {'type': 'box', 'col': 4, 'row': 13},
        {'type': 'box', 'col': 11, 'row': 10},
        {'type': 'plate', 'col': 5, 'row': 13, 'id': 0, 'targets': ['gate0']},
        {'type': 'plate', 'col': 13, 'row': 10, 'id': 1, 'targets': ['gate1']},
        {'type': 'gate', 'col': 8, 'row': 10, 'id': 'gate0', 'open': False},
        {'type': 'gate', 'col': 17, 'row': 8, 'id': 'gate1', 'open': False},
        {'type': 'lever', 'col': 21, 'row': 7, 'id': 'lev0', 'targets': ['gate2']},
        {'type': 'gate', 'col': 25, 'row': 5, 'id': 'gate2', 'open': False},
        {'type': 'mplat', 'col': 7, 'row': 12, 'axis': 'h', 'dist': 2, 'speed': 1.4},
        {'type': 'mplat', 'col': 18, 'row': 9, 'axis': 'h', 'dist': 3, 'speed': 1.3},
        {'type': 'enemy', 'col': 12, 'row': 10, 'patrol': 2},
        {'type': 'enemy', 'col': 21, 'row': 7, 'patrol': 2},
        {'type': 'spike', 'col': 9, 'row': 16},
        {'type': 'spike', 'col': 10, 'row': 16},
        {'type': 'spike', 'col': 18, 'row': 16},
        {'type': 'spike', 'col': 19, 'row': 16},
        {'type': 'exit', 'col': 27, 'row': 4},
    ]
    return t, objs


# =======================================================
# LEVEL 6 — final mixed-mechanics stage
# =======================================================
def build_level_6():
    S = T_W_IRON
    D = T_W_OBS
    F = T_LAZ_FL
    FS = T_FL_DKSIL
    P = T_PL_CARVE
    PL = T_LAZ_WL
    PD = T_PL_DARK

    t = []
    shell(t, D, F, T_W_CARVE)

    plat(t, P, 1, 5, 14)
    plat(t, P, 8, 12, 12)
    plat(t, PD, 15, 19, 9)
    plat(t, PL, 23, 28, 5)

    plat(t, PL, 2, 4, 8)
    plat(t, PD, 10, 12, 6)
    plat(t, PD, 17, 19, 4)

    vwall_with_gaps(t, S, 6, 2, ROWS - 2, [gate_gap(10)])
    vwall_with_gaps(t, S, 14, 2, ROWS - 2, [gate_gap(8)])
    vwall_with_gaps(t, S, 22, 2, 10, [gate_gap(5), gate_gap(9)])

    vwall_with_gaps(t, T_GH_BAR, 6, 6, 10, [gate_gap(10)])
    vwall_with_gaps(t, T_GH_BARD, 14, 4, 8, [gate_gap(8)])

    objs = [
        {'type': 'spawn', 'col': 2, 'row': 13},
        {'type': 'pad', 'col': 2, 'row': 13, 'id': 0},

        {'type': 'box', 'col': 3, 'row': 13},
        {'type': 'box', 'col': 9, 'row': 11},

        {'type': 'plate', 'col': 4, 'row': 7, 'id': 0, 'targets': ['gate1']},
        {'type': 'plate', 'col': 11, 'row': 5, 'id': 1, 'targets': ['gate2']},
        {'type': 'lever', 'col': 5, 'row': 13, 'id': 'lev0', 'targets': ['gate0']},
        {'type': 'lever', 'col': 18, 'row': 3, 'id': 'lev1', 'targets': ['gate3']},

        {'type': 'gate', 'col': 6, 'row': 10, 'id': 'gate0', 'open': False},
        {'type': 'gate', 'col': 14, 'row': 8, 'id': 'gate1', 'open': False},
        {'type': 'gate', 'col': 22, 'row': 5, 'id': 'gate2', 'open': False},
        {'type': 'gate', 'col': 22, 'row': 9, 'id': 'gate3', 'open': False},

        {'type': 'mplat', 'col': 6, 'row': 12, 'axis': 'h', 'dist': 2, 'speed': 1.4},
        {'type': 'mplat', 'col': 13, 'row': 9, 'axis': 'v', 'dist': 3, 'speed': 1.1},
        {'type': 'mplat', 'col': 21, 'row': 6, 'axis': 'v', 'dist': 2, 'speed': 1.0},

        {'type': 'enemy', 'col': 10, 'row': 11, 'patrol': 2},
        {'type': 'enemy', 'col': 16, 'row': 8, 'patrol': 2},
        {'type': 'enemy', 'col': 24, 'row': 4, 'patrol': 2},

        {'type': 'spike', 'col': 7, 'row': 16},
        {'type': 'spike', 'col': 8, 'row': 16},
        {'type': 'spike', 'col': 15, 'row': 16},
        {'type': 'spike', 'col': 16, 'row': 16},
        {'type': 'spike', 'col': 23, 'row': 16},
        {'type': 'spike', 'col': 24, 'row': 16},

        {'type': 'exit', 'col': 27, 'row': 4},
    ]
    return t, objs


LEVELS = [
    build_level_1,
    build_level_2,
    build_level_3,
    build_level_4,
    build_level_5,
    build_level_6,
]
