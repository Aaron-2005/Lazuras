# constants.py — shared globals for The Lazarus Project

SW, SH  = 960, 576
TILE    = 32
FPS     = 60
COLS    = 30
ROWS    = 18

# Colours
C_BG      = (8,   6,   5)
C_SOUL    = (140, 190, 255)
C_LIVING  = (220, 200, 140)
C_GREEN   = (80,  220, 130)
C_GOLD    = (220, 170,  40)
C_RED     = (210,  55,  55)
C_WHITE   = (255, 255, 255)
C_DIM     = (80,   72,  62)
C_ACCENT  = (80,  140, 255)
C_TORCH   = (255, 165,  60)

# Physics constants
GRAVITY_LIVING = 0.50
GRAVITY_GHOST = 0.30
TERMINAL_VELOCITY = 14.0
GHOST_TERMINAL_VEL = 10.0

# Game balance
DEFAULT_CYCLES = 4
GHOST_DURATION = 450  # frames
DOUBLE_JUMP_ENABLED = True
