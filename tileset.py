# tileset.py — tile definitions, tileset loader

import pygame
from constants import TILE

# ── Tile IDs (col, row) on the spritesheet ──────────────
# Row 0 – floors
T_FL_SIL   = (0,0); T_FL_CRKL  = (1,0); T_FL_CRKH  = (2,0)
T_FL_ANC   = (3,0); T_FL_MIX   = (4,0); T_FL_GRATE = (5,0)
T_FL_MOSS  = (6,0); T_FL_DIAM  = (7,0)
# Row 1 – temple walls
T_W_SAND   = (0,1); T_W_CRKSND = (1,1); T_W_DARK   = (2,1)
T_W_CARVE  = (3,1); T_W_PILL   = (4,1); T_W_MOSS   = (5,1)
T_W_RUIN   = (6,1); T_W_IRON   = (7,1)
# Row 2 – bg / ghost
T_BG       = (0,2); T_BG2      = (1,2); T_BG_WARM  = (2,2)
T_BG_DEEP  = (3,2); T_GH_BAR   = (4,2); T_GH_BARD  = (5,2)
T_BG_GLOW  = (6,2); T_BG_SHIM  = (7,2)
# Row 3 – more walls
T_W_COBB   = (0,3); T_W_ENG    = (1,3); T_W_BSLT   = (2,3)
T_W_BONE   = (3,3); T_W_OBS    = (4,3); T_W_EARTH  = (5,3)
T_W_RUBBLE = (6,3); T_FL_DKSIL = (7,3)
# Row 4 – platforms
T_PL_STONE = (0,4); T_PL_SIL   = (1,4); T_PL_CRKD  = (2,4)
T_PL_DARK  = (3,4); T_PL_CARVE = (4,4); T_PL_MOSS  = (5,4)
T_PL_HAZ   = (6,4); T_PL_BONE  = (7,4)
# Row 5 – special
T_VOID     = (0,5); T_VOID_E   = (1,5); T_LAZ_FL   = (2,5)
T_LAZ_WL   = (3,5); T_BOX_L    = (4,5); T_BOX_D    = (5,5)
T_PLATE_ON = (6,5); T_PLATE_OFF= (7,5)

SOLID_TILES = {
    T_W_SAND,T_W_CRKSND,T_W_DARK,T_W_CARVE,T_W_PILL,T_W_MOSS,T_W_RUIN,T_W_IRON,
    T_W_COBB,T_W_ENG,T_W_BSLT,T_W_BONE,T_W_OBS,T_W_EARTH,T_W_RUBBLE,
    T_FL_SIL,T_FL_CRKL,T_FL_CRKH,T_FL_ANC,T_FL_MIX,T_FL_GRATE,T_FL_MOSS,T_FL_DIAM,
    T_FL_DKSIL,T_LAZ_FL,T_LAZ_WL,T_VOID_E,
    T_PL_STONE,T_PL_SIL,T_PL_CRKD,T_PL_DARK,T_PL_CARVE,T_PL_MOSS,T_PL_BONE,
}
GHOST_TILES = {T_GH_BAR, T_GH_BARD}


class TileSet:
    def __init__(self, path):
        raw = pygame.image.load(path).convert_alpha()
        w, h = raw.get_size()
        self.sheet   = pygame.transform.scale(raw, (w*2, h*2))
        self.tile_px = TILE * 2
        self._cache  = {}

    def get(self, col, row, alpha=255):
        k = (col, row, alpha)
        if k not in self._cache:
            src = pygame.Rect(col*self.tile_px, row*self.tile_px, self.tile_px, self.tile_px)
            t   = pygame.transform.scale(self.sheet.subsurface(src), (TILE, TILE))
            if alpha < 255:
                t = t.copy(); t.set_alpha(alpha)
            self._cache[k] = t
        return self._cache[k]
