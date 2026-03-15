# levels.py — all levels rewritten in row-based sketch style

from tileset import *
from constants import COLS, ROWS


def build_tiles(tile_rows, tile_map):
    t = []
    for row, line in enumerate(tile_rows):
        if len(line) != COLS:
            raise ValueError(
                f"Row {row} has length {len(line)} but expected {COLS}: {line}"
            )
        for col, ch in enumerate(line):
            if ch in tile_map:
                t.append((tile_map[ch], col, row))
    return t


# =======================================================
# LEVEL 1 — learn moving platform + lever + gate + exit
# =======================================================
def build_level_1():
    W = T_W_DARK
    P = T_PL_STONE
    G = T_GH_BAR
    L = T_LAZ_FL

    tile_rows = [
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "G............................G",
        "G............................G",
        "G............................G",
        "G............................G",
        "G............................G",
        "G............................G",
        "G............................G",
        "G............................G",
        "G.......................#####G",
        "G..............--............G",
        "G..........-.................G",
        "G......--...........---------G",
        "G...#-.......................G",
        "#...#.............#..........G",
        "G---#.............#........--G",
        "G...#LLLLLLLLLLLLL#LLLLLLLL#.G",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    ]

    tile_map = {
        "#": W,
        "-": P,
        "G": G,
        "L": L,
    }

    t = build_tiles(tile_rows, tile_map)

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
# LEVEL 2 — your new sketch-style level
# =======================================================
def build_new_level():
    W = T_W_DARK
    F = T_FL_ANC
    P = T_PL_STONE
    G = T_GH_BAR
    H = T_LAZ_FL

    tile_rows = [
        "..........#...........G.......",
        "..........#...........G.......",
        "...-.#....#...........G.......",
        ".....#....#...........G.......",
        "....-#....#...........G.......",
        ".....#....G...........GG......",
        "...-.#....G...........G.......",
        "-....#....G...........G.......",
        ".....#....#...........G.......",
        ".....#....#...........-------.",
        ".-...#....#...................",
        ".....#....#...................",
        "....-#....#...................",
        ".....#........................",
        ".-...#........................",
        ".....#....---.................",
        ".....#........................",
        "=====#HHHHHHHHHHHHHHHHHHHHHHHH",
    ]

    tile_map = {
        '#': W,
        '=': F,
        '-': P,
        'G': G,
        'H': H,
        'L': T_LAZ_FL,
    }

    t = build_tiles(tile_rows, tile_map)

    objs = [
        {'type': 'spawn', 'col': 1, 'row': 16},
        {'type': 'pad',   'col': 1, 'row': 16, 'id': 0},
        {'type': 'mplat', 'col': 16, 'row': 10, 'axis': 'h', 'dist': 3, 'speed': 1.2},
        {'type': 'mplat', 'col': 22, 'row': 12, 'axis': 'h', 'dist': 3, 'speed': 1.2},
        {'type': 'mplat', 'col': 16, 'row': 14, 'axis': 'h', 'dist': 3, 'speed': 1.2},
        {'type': 'exit',  'col': 27, 'row': 8},
    ]
    return t, objs


# =======================================================
# LEVEL 3 — first ghost route
# =======================================================
def build_level_2():
    S = T_W_SAND
    D = T_W_DARK
    F = T_FL_ANC
    FS = T_FL_SIL
    P = T_PL_STONE
    PS = T_PL_SIL
    C = T_W_CARVE
    G = T_GH_BAR

    tile_rows = [
        "##############################",
        "#cccccccccccccccccccccccccccc#",
        "#.........w..................#",
        "#.........w..................#",
        "#.........w..................#",
        "#.........w..................#",
        "#.........w..................#",
        "#.........G..................#",
        "#.........G..........pppppppp#",
        "#.........G..................#",
        "#.........G..................#",
        "#.........G.-------..........#",
        "#.........w..................#",
        "#.........w..................#",
        "#sssssssssw..................#",
        "#.........w..................#",
        "#=========w==================#",
        "==============================",
    ]

    tile_map = {
        "#": D,
        "c": C,
        "w": S,
        "s": FS,
        "-": P,
        "p": PS,
        "=": F,
        "G": G,
    }

    t = build_tiles(tile_rows, tile_map)

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
# LEVEL 4 — lever + box combo
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
    C = T_W_CARVE
    G = T_GH_BARD

    tile_rows = [
        "##############################",
        "#cccccccccccccccccccccccccccc#",
        "#........w.........b.........#",
        "#........w.........b.........#",
        "#........w.........b.........#",
        "#........w.........b.........#",
        "#........w..dddd...g.........#",
        "#........w.........g.........#",
        "#........w...........--------#",
        "#........w...................#",
        "#............................#",
        "#..........ppppppp...........#",
        "#..................b.........#",
        "#..................b.........#",
        "#ssssssssw.........b.........#",
        "#........w.........b.........#",
        "#========w=========b=========#",
        "==============================",
    ]

    tile_map = {
        "#": D,
        "c": C,
        "w": S,
        "b": B,
        "g": G,
        "s": FS,
        "p": PC,
        "-": P,
        "d": PD,
        "=": F,
    }

    t = build_tiles(tile_rows, tile_map)

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
# LEVEL 5 — moving platform tutorial
# =======================================================
def build_level_4():
    S = T_W_COBB
    D = T_W_ENG
    F = T_FL_MIX
    FS = T_FL_DKSIL
    P = T_PL_STONE
    PC = T_PL_CARVE
    PD = T_PL_DARK
    C = T_W_CARVE

    tile_rows = [
        "##############################",
        "#cccccccccccccccccccccccccccc#",
        "#........w..........w........#",
        "#........w...................#",
        "#........w...................#",
        "#........w..........w........#",
        "#........w....ddd...w........#",
        "#........w..........w........#",
        "#........w..........w..pppppp#",
        "#...ddd..w..........w........#",
        "#...................w........#",
        "#...........------..w........#",
        "#...................w........#",
        "#...................w........#",
        "#sssssss.w..........w........#",
        "#........w..........w........#",
        "#========w==========w========#",
        "==============================",
    ]

    tile_map = {
        "#": D,
        "c": C,
        "w": S,
        "s": FS,
        "-": P,
        "p": PC,
        "d": PD,
        "=": F,
    }

    t = build_tiles(tile_rows, tile_map)

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
# LEVEL 6 — two boxes, two switches, more timing
# =======================================================
def build_level_5():
    S = T_W_BSLT
    D = T_W_OBS
    F = T_FL_GRATE
    FS = T_FL_MOSS
    P = T_PL_MOSS
    PB = T_PL_BONE
    PD = T_PL_DARK
    M = T_W_MOSS
    G = T_GH_BAR

    tile_rows = [
        "##############################",
        "#mmmmmmmmmmmmmmmmmmmmmmmmmmmm#",
        "#.......w........w...........#",
        "#.......w........w...........#",
        "#.......w........w...........#",
        "#.......w........w........sss#",
        "#.......w........G...........#",
        "#.......w........G...........#",
        "#.......w..........dddddd....#",
        "#.......w................w...#",
        "#........................w...#",
        "#.........bbbbbb.............#",
        "#................w...........#",
        "#................w...........#",
        "#pppppp.w........w...........#",
        "#.......w........w...........#",
        "#=======w========w===========#",
        "==============================",
    ]

    tile_map = {
        "#": D,
        "m": M,
        "w": S,
        "s": FS,
        "p": P,
        "b": PB,
        "d": PD,
        "G": G,
        "=": F,
    }

    t = build_tiles(tile_rows, tile_map)

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
# LEVEL 7 — final mixed-mechanics stage
# =======================================================
def build_level_6():
    S = T_W_IRON
    D = T_W_OBS
    F = T_LAZ_FL
    P = T_PL_CARVE
    PL = T_LAZ_WL
    PD = T_PL_DARK
    C = T_W_CARVE
    G = T_GH_BAR
    GD = T_GH_BARD

    tile_rows = [
        "##############################",
        "#cccccccccccccccccccccccccccc#",
        "#.....w.......w..............#",
        "#.....w.......w..............#",
        "#.....w.......g..ddd.........#",
        "#.....w.......g........WWWWWW#",
        "#.....G...ddd.g..............#",
        "#.....G.......g..............#",
        "#.WWW.G......................#",
        "#.....G........ddddd.........#",
        "#............................#",
        "#............................#",
        "#.......ppppp.w..............#",
        "#.............w..............#",
        "#pppppw.......w..............#",
        "#.....w.......w..............#",
        "#LLLLLwLLLLLLLwLLLLLLLLLLLLLL#",
        "LLLLLLLLLLLLLLLLLLLLLLLLLLLLLL",
    ]

    tile_map = {
        "#": D,
        "c": C,
        "w": S,
        "p": P,
        "W": PL,
        "d": PD,
        "G": G,
        "g": GD,
        "L": F,
    }

    t = build_tiles(tile_rows, tile_map)

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
    build_new_level,
    build_level_2,
    build_level_3,
    build_level_4,
    build_level_5,
    build_level_6,
]