"""
╔══════════════════════════════════════════════════════════╗
║            THE LAZARUS PROJECT                           ║
║   An underground temple escape — two worlds, one body    ║
╠══════════════════════════════════════════════════════════╣
║  pip install pygame   |   lazarus_tileset.png same dir   ║
╠══════════════════════════════════════════════════════════╣
║  CONTROLS                                                ║
║   A / D  or  ←/→     Walk                               ║
║   W / ↑ / SPACE      Jump (living) | Float up (ghost)    ║
║   S / ↓              Float down (ghost only)             ║
║   Q                  Toggle ghost form                   ║
║   R                  Restart level                       ║
║   ESC                Quit                                ║
╠══════════════════════════════════════════════════════════╣
║  THE MECHANIC                                            ║
║   Ghost  — fly through walls, scout, read the level.     ║
║            CANNOT push boxes or step on pressure plates. ║
║   Living — solid. Push boxes onto pressure plates to     ║
║            open gates. Reach the soul-exit portal.       ║
║   Ghost timer drains. If it hits 0 inside a wall → die.  ║
╚══════════════════════════════════════════════════════════╝
"""
import pygame, sys, math, os, random

# ══════════════════════════════════════════════════════════
SW, SH   = 960, 576
TILE     = 32
FPS      = 60
COLS     = 30
ROWS     = 18

# ══════════════════════════════════════════════════════════
# TILE IDs
# ══════════════════════════════════════════════════════════
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

# ══════════════════════════════════════════════════════════
# PALETTE
# ══════════════════════════════════════════════════════════
C_BG      = (8, 6, 5)
C_SOUL    = (140,190,255)
C_LIVING  = (220,200,140)
C_GREEN   = (80, 220,130)
C_GOLD    = (220,170, 40)
C_RED     = (210, 55, 55)
C_WHITE   = (255,255,255)
C_DIM     = (80, 72, 62)
C_ACCENT  = (80,140,255)
C_TORCH   = (255,165, 60)

# ══════════════════════════════════════════════════════════
# LEVEL HELPERS
# ══════════════════════════════════════════════════════════
def hwall(t,tid,x0,x1,y):
    for x in range(x0,x1+1): t.append((tid,x,y))
def vwall(t,tid,x,y0,y1):
    for y in range(y0,y1+1): t.append((tid,x,y))
def plat(t,tid,x0,x1,y):
    for x in range(x0,x1+1): t.append((tid,x,y))
def fill_rect(t,tid,x0,y0,x1,y1):
    for y in range(y0,y1+1):
        for x in range(x0,x1+1): t.append((tid,x,y))

# ══════════════════════════════════════════════════════════
# LEVELS
# ══════════════════════════════════════════════════════════
def build_level_1():
    """
    THE ANTECHAMBER
    Tutorial level. Ghost scouts where box must go. Living pushes it.
    One box, one pressure plate, one gate.
    Layout: left spawn area → push box right onto plate → gate opens → exit.
    """
    S=T_W_SAND; D=T_W_DARK; F=T_FL_ANC; FS=T_FL_SIL
    P=T_PL_STONE; PS=T_PL_SIL; W=T_W_CARVE
    t=[]
    # Outer walls / ceiling / floor
    hwall(t,D,0,COLS-1,0)
    hwall(t,F,0,COLS-1,ROWS-1)
    vwall(t,S,0,1,ROWS-2); vwall(t,S,COLS-1,1,ROWS-2)
    # Main floor
    hwall(t,FS,1,COLS-2,ROWS-2)
    # Ceiling detail
    hwall(t,W,1,COLS-2,1)
    # Left chamber wall
    vwall(t,S,9,2,ROWS-2)
    # Middle chamber wall
    vwall(t,S,19,2,ROWS-2)
    # Platforms in left area
    plat(t,P,2,6,12)
    # Platform in middle
    plat(t,PS,10,14,10)
    # Platform right
    plat(t,P,20,26,8)
    # Ghost barrier above left wall gap
    vwall(t,T_GH_BAR,9,5,8)
    # Stalactites
    for cx in [4,12,16,24]: vwall(t,T_W_ENG,cx,1,3)
    # Torchlight alcoves (decorative dark spots)
    for cx in [3,25]: t.append((T_W_ENG,cx,ROWS-3))

    objs=[
        {'type':'spawn','col':2,'row':16},
        {'type':'pad',  'col':2,'row':15,'id':0},
        # Box starts left chamber
        {'type':'box',  'col':5,'row':15},
        # Plate in middle chamber — box must land here
        {'type':'plate','col':12,'row':9,'id':0,'targets':['gate0']},
        # Gate blocks path to exit area
        {'type':'gate', 'col':19,'row':2,'id':'gate0','open':False},
        # Spikes in gap
        {'type':'spike','col':10,'row':16},
        {'type':'spike','col':11,'row':16},
        # Exit
        {'type':'exit', 'col':25,'row':7},
        {'type':'pad',  'col':21,'row':7,'id':1},
    ]
    return t,objs


def build_level_2():
    """
    THE DESCENT HALLS
    Two boxes, two plates. Ghost reveals which box goes where through
    ghost-only walls. One plate is hidden behind a ghost barrier.
    """
    S=T_W_SAND; D=T_W_DARK; B=T_W_COBB; F=T_FL_ANC
    FS=T_FL_SIL; FD=T_FL_DKSIL; P=T_PL_STONE; PS=T_PL_SIL
    t=[]
    hwall(t,D,0,COLS-1,0);  hwall(t,F,0,COLS-1,ROWS-1)
    vwall(t,S,0,1,ROWS-2);  vwall(t,S,COLS-1,1,ROWS-2)
    hwall(t,FS,1,COLS-2,ROWS-2)
    hwall(t,T_W_CARVE,1,COLS-2,1)
    # Room dividers
    vwall(t,S,8,2,ROWS-2)
    vwall(t,S,16,2,ROWS-2)
    vwall(t,S,24,2,ROWS-2)
    # Floors at different heights
    plat(t,PS,1,7,14)
    plat(t,P,9,15,11)
    plat(t,FS,17,23,8)
    plat(t,PS,25,COLS-2,5)
    # Ghost-only passages
    vwall(t,T_GH_BAR,8,6,10)
    vwall(t,T_GH_BARD,16,4,8)
    # Ceiling arch detail
    for cx in [4,12,20,27]: vwall(t,T_W_ENG,cx,1,2)
    # Stalactites
    for cx in [6,14,22]: vwall(t,T_W_RUIN,cx,1,4)

    objs=[
        {'type':'spawn','col':2,'row':16},
        {'type':'pad',  'col':2,'row':13,'id':0},
        {'type':'pad',  'col':18,'row':7,'id':1},
        # Two boxes
        {'type':'box','col':4,'row':13},
        {'type':'box','col':11,'row':10},
        # Two plates — second one hidden behind ghost barrier
        {'type':'plate','col':6,'row':13,'id':0,'targets':['gate0']},
        {'type':'plate','col':21,'row':7,'id':1,'targets':['gate1']},
        # Two gates
        {'type':'gate','col':16,'row':2,'id':'gate0','open':False},
        {'type':'gate','col':24,'row':2,'id':'gate1','open':False},
        # Spikes
        {'type':'spike','col':9,'row':16},{'type':'spike','col':10,'row':16},
        {'type':'spike','col':17,'row':16},{'type':'spike','col':18,'row':16},
        {'type':'exit','col':27,'row':4},
    ]
    return t,objs


def build_level_3():
    """
    THE INNER SANCTUM
    Three boxes. One plate is accessible only after ghost scouts a
    hidden upper path. Stacked box puzzle needed for one plate.
    Tight ghost timer management required for full scouting run.
    """
    S=T_W_SAND; D=T_W_OBS; B=T_W_ENG; F=T_FL_ANC
    FS=T_FL_SIL; FD=T_FL_DKSIL; LF=T_LAZ_FL
    P=T_PL_STONE; PS=T_PL_SIL; PC=T_PL_CARVE
    t=[]
    hwall(t,D,0,COLS-1,0);  hwall(t,F,0,COLS-1,ROWS-1)
    vwall(t,D,0,1,ROWS-2);  vwall(t,D,COLS-1,1,ROWS-2)
    hwall(t,FS,1,COLS-2,ROWS-2)
    hwall(t,T_W_CARVE,1,COLS-2,1)
    # Complex multi-room
    vwall(t,S,7,3,ROWS-2)
    vwall(t,S,14,3,ROWS-2)
    vwall(t,S,21,3,ROWS-2)
    # Sub-floors
    plat(t,PS,1,6,14)
    plat(t,PC,8,13,11)
    plat(t,P,8,10,8)
    plat(t,PS,15,20,9)
    plat(t,LF,22,COLS-2,6)
    # Upper secret path (ghost scouts it first)
    plat(t,T_PL_DARK,8,13,5)
    plat(t,T_PL_DARK,15,20,5)
    # Ghost-only sealing walls
    vwall(t,T_GH_BAR,7,6,10)
    vwall(t,T_GH_BARD,14,4,8)
    hwall(t,T_GH_BAR,15,20,4)
    # Decorative
    for cx in [3,10,17,25]: vwall(t,B,cx,1,2)
    for cx in [5,12,19,27]: vwall(t,T_W_RUIN,cx,1,3)

    objs=[
        {'type':'spawn','col':2,'row':16},
        {'type':'pad','col':2,'row':13,'id':0},
        {'type':'pad','col':9,'row':7,'id':1},
        {'type':'pad','col':22,'row':5,'id':2},
        # Three boxes
        {'type':'box','col':3,'row':13},
        {'type':'box','col':9,'row':10},
        {'type':'box','col':16,'row':8},
        # Three plates
        {'type':'plate','col':5,'row':13,'id':0,'targets':['gate0']},
        {'type':'plate','col':11,'row':10,'id':1,'targets':['gate1']},
        {'type':'plate','col':18,'row':8,'id':2,'targets':['gate2']},
        # Gates
        {'type':'gate','col':7,'row':3,'id':'gate0','open':False},
        {'type':'gate','col':14,'row':3,'id':'gate1','open':False},
        {'type':'gate','col':21,'row':3,'id':'gate2','open':False},
        # Spikes
        {'type':'spike','col':8,'row':16},{'type':'spike','col':9,'row':16},
        {'type':'spike','col':15,'row':16},{'type':'spike','col':16,'row':16},
        {'type':'spike','col':22,'row':16},
        {'type':'exit','col':26,'row':5},
    ]
    return t,objs

LEVELS=[build_level_1,build_level_2,build_level_3]

# ══════════════════════════════════════════════════════════
# TILESET
# ══════════════════════════════════════════════════════════
class TileSet:
    def __init__(self, path):
        raw=pygame.image.load(path).convert_alpha()
        w,h=raw.get_size()
        self.sheet  =pygame.transform.scale(raw,(w*2,h*2))
        self.tile_px=TILE*2; self._cache={}
    def get(self,col,row,alpha=255):
        k=(col,row,alpha)
        if k not in self._cache:
            src=pygame.Rect(col*self.tile_px,row*self.tile_px,self.tile_px,self.tile_px)
            t=pygame.transform.scale(self.sheet.subsurface(src),(TILE,TILE))
            if alpha<255: t=t.copy(); t.set_alpha(alpha)
            self._cache[k]=t
        return self._cache[k]

# ══════════════════════════════════════════════════════════
# BACKGROUND  — temple underground parallax layers
# ══════════════════════════════════════════════════════════
def make_bg():
    """Near-black with very faint warm gradient — torchlit underground."""
    s=pygame.Surface((COLS*TILE,ROWS*TILE))
    for row in range(ROWS):
        for col in range(COLS):
            v=random.randint(-2,2)
            # Slight warm tint, slightly lighter toward centre rows
            dist=abs(row-ROWS//2)/(ROWS//2)
            lum=12-int(dist*4)
            r=max(4,lum+3+v); g=max(3,lum+2+v); b=max(3,lum+v)
            s.fill((r,g,b),(col*TILE,row*TILE,TILE,TILE))
    return s

def make_far_layer():
    """Distant temple arch silhouettes — very dim."""
    s=pygame.Surface((SW*2,SH),pygame.SRCALPHA)
    rng=random.Random(77)
    col=(30,24,16,28)
    # Arch columns
    for _ in range(8):
        x=rng.randint(0,SW*2); h=rng.randint(80,200); w=rng.randint(12,26)
        pygame.draw.rect(s,col,(x,SH-h,w,h))
        # Arch top
        pygame.draw.ellipse(s,col,(x-w//2,SH-h-w//2,w*2,w))
    # Ground silhouette
    for x in range(0,SW*2,4):
        h=rng.randint(20,55)
        pygame.draw.rect(s,col,(x,SH-h,4,h))
    return s

def make_mid_layer():
    """Mid-distance crumbled wall silhouettes."""
    s=pygame.Surface((SW*2,SH),pygame.SRCALPHA)
    rng=random.Random(88)
    col=(20,16,11,38)
    for _ in range(14):
        x=rng.randint(0,SW*2); h=rng.randint(40,150); w=rng.randint(18,40)
        # Crenellated top
        pygame.draw.rect(s,col,(x,SH-h,w,h))
        for bx in range(x,x+w,8):
            bh=rng.randint(4,14)
            pygame.draw.rect(s,col,(bx,SH-h-bh,6,bh))
    return s

# ══════════════════════════════════════════════════════════
# CAMERA
# ══════════════════════════════════════════════════════════
class Camera:
    def __init__(self): self.x=self.y=0.0; self.shk=0; self.shk_m=0
    def update(self,px,py):
        self.x+=(px-SW//2-self.x)*0.09
        self.y+=(py-SH//2-self.y)*0.09
        self.x=max(0,min(self.x,COLS*TILE-SW))
        self.y=max(0,min(self.y,ROWS*TILE-SH))
        if self.shk>0: self.shk-=1
    def shake(self,m=4,f=8): self.shk_m=m; self.shk=f
    def apply(self,x,y):
        ox=oy=0
        if self.shk>0: ox=random.randint(-self.shk_m,self.shk_m); oy=random.randint(-self.shk_m,self.shk_m)
        return x-int(self.x)+ox,y-int(self.y)+oy

# ══════════════════════════════════════════════════════════
# PARTICLES
# ══════════════════════════════════════════════════════════
class P:
    # FIX: __slots__ must exactly match all attributes assigned in __init__
    __slots__=('x','y','vx','vy','col','life','ml','grav','sz')
    def __init__(self,x,y,vx,vy,col,life,grav=0.14,sz=3):
        self.x=float(x);self.y=float(y);self.vx=vx;self.vy=vy
        self.col=col;self.life=self.ml=life;self.grav=grav;self.sz=sz
    def upd(self):
        self.x+=self.vx;self.y+=self.vy;self.vy+=self.grav;self.vx*=0.93;self.life-=1
    def draw(self,surf,cam):
        if self.life<=0: return
        f=self.life/self.ml; a=int(255*f); sz=max(1,int(self.sz*f))
        sx,sy=cam.apply(int(self.x),int(self.y))
        if not(-sz<sx<SW+sz and -sz<sy<SH+sz): return
        tmp=pygame.Surface((sz*2,sz*2),pygame.SRCALPHA)
        pygame.draw.circle(tmp,(*self.col[:3],a),(sz,sz),sz)
        surf.blit(tmp,(sx-sz,sy-sz))

def burst(ps,x,y,col,n=16,spd=3.0,grav=0.15,life=28,sz=3):
    for _ in range(n):
        a=random.uniform(0,math.pi*2); s=random.uniform(0.3,spd)
        ps.append(P(x,y,math.cos(a)*s,math.sin(a)*s,col,life+random.randint(-5,5),grav,sz))

# ══════════════════════════════════════════════════════════
# TORCH GLOW  (atmospheric point lights drawn each frame)
# ══════════════════════════════════════════════════════════
class TorchLight:
    def __init__(self,x,y,radius=80,color=(255,140,40)):
        self.x=x; self.y=y; self.radius=radius; self.color=color; self.t=random.uniform(0,math.pi*2)
    def draw(self,surf,cam,gt):
        self.t+=0.08
        flicker=0.85+0.15*math.sin(self.t)
        r=int(self.radius*flicker)
        sx,sy=cam.apply(self.x,self.y)
        if not(-r<sx<SW+r and -r<sy<SH+r): return
        glow=pygame.Surface((r*2,r*2),pygame.SRCALPHA)
        for rad,a in [(r,8),(int(r*0.6),18),(int(r*0.3),35),(int(r*0.12),60)]:
            pygame.draw.circle(glow,(*self.color,a),(r,r),rad)
        surf.blit(glow,(sx-r,sy-r))

# ══════════════════════════════════════════════════════════
# SPRITES — improved pixel art style
# ══════════════════════════════════════════════════════════
def draw_living(surf,sx,sy,facing,vx,on_gnd,t,has_box_nearby=False):
    bob=math.sin(t*0.2)*1.5 if on_gnd and abs(vx)>0.3 else 0
    by=sy+int(bob); walk=math.sin(t*0.38)*6 if on_gnd and abs(vx)>0.5 else 0

    # Drop shadow
    shd=pygame.Surface((24,5),pygame.SRCALPHA)
    pygame.draw.ellipse(shd,(0,0,0,45),(0,0,24,5)); surf.blit(shd,(sx-1,sy+31))

    # Legs — dark trousers
    lc=(28,38,95)
    r_leg=int(walk); l_leg=-int(walk)
    pygame.draw.rect(surf,lc,(sx+4, by+20,6,10+r_leg))
    pygame.draw.rect(surf,lc,(sx+12,by+20,6,10+l_leg))
    # Boots
    bc=(18,14,12)
    pygame.draw.rect(surf,bc,(sx+3, by+28+r_leg,8,4))
    pygame.draw.rect(surf,bc,(sx+11,by+28+l_leg,8,4))

    # Coat body
    cc=(195,190,180)
    pygame.draw.rect(surf,cc,(sx+3,by+9,16,13))
    pygame.draw.line(surf,(162,158,148),(sx+11,by+9),(sx+7, by+20),1)
    pygame.draw.line(surf,(162,158,148),(sx+11,by+9),(sx+15,by+20),1)

    # Arms
    sw=math.sin(t*0.38)*5 if on_gnd and abs(vx)>0.5 else 0
    fa=int(sw) if facing>0 else -int(sw)
    pygame.draw.rect(surf,cc,(sx+18,by+10+fa,  5,11))
    pygame.draw.rect(surf,cc,(sx-1, by+10-fa,  5,11))
    pygame.draw.rect(surf,(48,46,42),(sx+18,by+19+fa,  5,4))
    pygame.draw.rect(surf,(48,46,42),(sx-1, by+19-fa,  5,4))

    # Neck + head
    pygame.draw.rect(surf,(180,162,142),(sx+8,by+7,6,4))
    pygame.draw.rect(surf,(180,162,142),(sx+4,by-2,14,10))
    pygame.draw.rect(surf,(180,162,142),(sx+3,by+1,16,8))

    # Helmet
    pygame.draw.rect(surf,(48,48,52),(sx+4,by-4,14,8))
    pygame.draw.rect(surf,(48,48,52),(sx+3,by-2,16,6))
    # Visor
    voff=2 if facing>0 else 1
    vs=pygame.Surface((9,4),pygame.SRCALPHA); vs.fill((75,155,215,190))
    surf.blit(vs,(sx+4+voff,by-2))
    pygame.draw.rect(surf,C_GREEN,(sx+4,by-4,14,2))

    # Interact hint if near box
    if has_box_nearby:
        ht=_fsm.render("PUSH",True,(220,200,140))
        surf.blit(ht,(sx+11-ht.get_width()//2,sy-22))


def draw_ghost(surf,sx,sy,facing,vx,t,gfrac):
    hover=math.sin(t*0.06)*7; rip=t*0.10
    sy_h=sy+int(hover)

    # Warning pulse when almost out
    if gfrac<0.25:
        wa=int(100*abs(math.sin(t*0.28)))
        ws=pygame.Surface((42,42),pygame.SRCALPHA)
        pygame.draw.circle(ws,(255,70,70,wa),(21,21),21)
        surf.blit(ws,(sx-10,sy_h-10))

    # Outer aura
    for rad,a in [(38,12),(26,22),(16,38)]:
        gs=pygame.Surface((rad*2,rad*2),pygame.SRCALPHA)
        pygame.draw.circle(gs,(75,120,255,a),(rad,rad),rad)
        surf.blit(gs,(sx+11-rad,sy_h+12-rad))

    # Spirit chains trailing behind
    cf=-1 if facing>0 else 1
    for i in range(5):
        cx2=sx+11+cf*(7+i*6); cy2=sy_h+14+int(math.sin(rip+i*0.9)*4)
        ca=max(0,90-i*20); cr=max(1,4-i)
        cs=pygame.Surface((cr*2,cr*2),pygame.SRCALPHA)
        pygame.draw.circle(cs,(95,135,255,ca),(cr,cr),cr); surf.blit(cs,(cx2-cr,cy2-cr))

    # Robe polygon — animated tattered hem
    robe=(16,12,25); edge=(48,36,72)
    pts_l=[(sx+4,sy_h+8)]; pts_r=[(sx+18,sy_h+8)]
    for i in range(9):
        fx=i/8.0
        wl=math.sin(rip+fx*math.pi*2.3)*2.8; wr=math.sin(rip+fx*math.pi*2.3+0.7)*2.8
        pts_l.append((sx+3+int(wl)-int(fx*4),sy_h+8+i*3))
        pts_r.append((sx+19-int(wr)+int(fx*4),sy_h+8+i*3))
    pts_r_rev=list(reversed(pts_r))
    pygame.draw.polygon(surf,robe,pts_l+pts_r_rev)
    pygame.draw.lines(surf,edge,False,pts_l,1)
    pygame.draw.lines(surf,edge,False,pts_r,1)
    hem_y=sy_h+8+8*3
    for i in range(6):
        hx=sx+2+i*4; wv=math.sin(rip*1.9+i*1.4)*3.5
        hlen=5+int(abs(math.sin(rip*0.8+i))*8)
        pygame.draw.line(surf,robe,(hx,hem_y),(int(hx+wv),hem_y+hlen),2)
        if i%2==0:
            pygame.draw.line(surf,edge,(hx,hem_y),(int(hx+wv),hem_y+hlen//2),1)

    # Hood
    pygame.draw.ellipse(surf,(13,10,22),(sx+1,sy_h-4,20,16))
    pygame.draw.ellipse(surf,(6,4,12),(sx+4,sy_h+1,14,9))
    pygame.draw.arc(surf,edge,(sx+1,sy_h-4,20,16),math.pi*0.15,math.pi*0.85,2)

    # Eyes — long slit (Hollow Knight style)
    fl=0.55+0.45*math.sin(t*0.29+math.cos(t*0.11))
    ea=int(210*fl); ex_b=sx+6 if facing>0 else sx+4
    for ei in range(2):
        ex=ex_b+ei*6; ey=sy_h+3
        eg=pygame.Surface((12,6),pygame.SRCALPHA)
        pygame.draw.ellipse(eg,(75,175,255,ea//2),(0,0,12,6)); surf.blit(eg,(ex-6,ey-3))
        pygame.draw.line(surf,(155,215,255),(ex-4,ey),(ex+4,ey),2)
        pygame.draw.circle(surf,(215,240,255),(ex,ey),1)

    # Skeletal hands
    hc=(188,182,168); bc2=(218,212,198); hv=math.sin(t*0.09)*4
    pygame.draw.line(surf,(32,26,48),(sx+19,sy_h+11),(sx+23,sy_h+14+int(hv)),2)
    pygame.draw.circle(surf,hc,(sx+23,sy_h+14+int(hv)),4)
    for fi in range(3):
        fa=(-0.4+fi*0.4+math.pi/2)
        fx2=sx+23+int(math.cos(fa)*6); fy2=sy_h+14+int(hv)+int(math.sin(fa)*6)
        pygame.draw.line(surf,bc2,(sx+23,sy_h+14+int(hv)),(fx2,fy2),1)
    pygame.draw.line(surf,(32,26,48),(sx+3,sy_h+11),(sx-1,sy_h+14-int(hv)),2)
    pygame.draw.circle(surf,hc,(sx-1,sy_h+14-int(hv)),4)

    # Scythe
    sc=(68,58,42); bl=(182,196,218); bs=(228,238,255)
    if facing>0:
        pygame.draw.line(surf,sc,(sx+19,sy_h+7),(sx+30,sy_h+32),3)
        bp=[]
        for a in range(-2,13):
            ang=math.pi*0.52+a*0.10
            bp.append((sx+30+int(math.cos(ang)*14),sy_h+4+int(math.sin(ang)*14)))
        if len(bp)>1:
            pygame.draw.lines(surf,bl,False,bp,3)
            pygame.draw.lines(surf,bs,False,bp[:7],1)
        pygame.draw.line(surf,bl,(sx+30,sy_h+4),(sx+32,sy_h+12),2)
    else:
        pygame.draw.line(surf,sc,(sx+3,sy_h+7),(sx-8,sy_h+32),3)
        bp=[]
        for a in range(-2,13):
            ang=math.pi*0.48-a*0.10
            bp.append((sx-8+int(math.cos(ang)*14),sy_h+4+int(math.sin(ang)*14)))
        if len(bp)>1:
            pygame.draw.lines(surf,bl,False,bp,3)
            pygame.draw.lines(surf,bs,False,bp[:7],1)

    # Orbiting soul orbs
    for i in range(3):
        ang=t*0.07+i*(math.pi*2/3); orb_r=15+4*math.sin(t*0.05+i)
        ox2=sx+11+int(math.cos(ang)*orb_r); oy2=sy_h+12+int(math.sin(ang)*orb_r*0.45)
        os=pygame.Surface((8,8),pygame.SRCALPHA)
        oa=90+int(90*math.sin(t*0.10+i))
        pygame.draw.circle(os,(110,155,255,oa),(4,4),4)
        pygame.draw.circle(os,(195,218,255,oa//2),(4,4),2)
        surf.blit(os,(ox2-4,oy2-4))

# ══════════════════════════════════════════════════════════
# BOX  — pushable crate
# ══════════════════════════════════════════════════════════
class Box:
    W=TILE; H=TILE
    def __init__(self,col,row,tileset):
        self.x=float(col*TILE); self.y=float(row*TILE)
        self.vx=0.0; self.vy=0.0; self.on_ground=False
        self.tileset=tileset

    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.W,self.H)

    def update(self,solid_rects,other_boxes):
        self.vy=min(self.vy+0.55,16)
        self.on_ground=False
        # All solids + other boxes
        collidables=solid_rects+[b.rect() for b in other_boxes]

        self.x+=self.vx
        # FIX: clamp x to world bounds so boxes can't escape outer walls
        self.x=max(0.0, min(self.x, (COLS-1)*TILE - self.W))
        r=self.rect()
        for s in collidables:
            if r.colliderect(s):
                self.x=(s.left-self.W) if self.vx>0 else float(s.right)
                self.vx=0
        self.vx*=0.5  # friction

        self.y+=self.vy
        r=self.rect()
        for s in collidables:
            if r.colliderect(s):
                if self.vy>0:
                    self.y=float(s.top-self.H); self.vy=0; self.on_ground=True
                elif self.vy<0:
                    self.y=float(s.bottom); self.vy=0

        # FIX: clamp y — if a box falls off the bottom, reset it to floor
        if self.y > ROWS*TILE + TILE*2:
            self.y = float((ROWS-2)*TILE - self.H)
            self.vy = 0.0

    def draw(self,surf,cam,t):
        sx,sy=cam.apply(int(self.x),int(self.y))
        # Slight bob shadow when falling
        shd=pygame.Surface((TILE,4),pygame.SRCALPHA)
        pygame.draw.ellipse(shd,(0,0,0,40),(0,0,TILE,4)); surf.blit(shd,(sx,sy+TILE))
        surf.blit(self.tileset.get(T_BOX_L[0],T_BOX_L[1]),(sx,sy))
        # Interaction hint glow outline
        glow=pygame.Surface((TILE+4,TILE+4),pygame.SRCALPHA)
        a=int(50+40*math.sin(t*0.08))
        pygame.draw.rect(glow,(200,170,80,a),(0,0,TILE+4,TILE+4),2)
        surf.blit(glow,(sx-2,sy-2))

# ══════════════════════════════════════════════════════════
# PLAYER
# ══════════════════════════════════════════════════════════
class Player:
    W,H=22,30
    # Living
    SPD=3.8; JMP=-11.0; GRAV=0.50; MXFALL=14.0
    PUSH_FORCE=2.8
    # Ghost
    GSPD=5.5; GFLOAT=4.2; GGRAV=0.03; GMXDY=2.5
    GDUR=450

    def __init__(self,x,y):
        self.cycles=4; self.spawn_x=float(x); self.spawn_y=float(y)
        self._init()

    def _init(self):
        self.x=self.spawn_x; self.y=self.spawn_y
        self.vx=self.vy=0.0; self.on_gnd=False
        self.ghost=False; self.gtimer=0; self.dead=False
        self.anim=0; self.facing=1; self.coy=0; self.jbuf=0
        self.trail=[]
        # FIX: inventory belongs in _init so respawn clears it too
        self.inventory=None

    def set_spawn(self,x,y): self.spawn_x=float(x); self.spawn_y=float(y)

    def respawn(self):
        # FIX: guard against going below 0 cycles (e.g. external calls)
        self.cycles=max(0,self.cycles-1)
        self.dead=False
        self._init()

    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.W,self.H)

    def toggle_ghost(self,solid_rects):
        if self.ghost:
            if self._safe(solid_rects): self.ghost=False
        elif self.gtimer<=0:
            self.ghost=True; self.gtimer=self.GDUR

    def _safe(self,solid_rects):
        r=self.rect()
        return not any(r.colliderect(s) for s in solid_rects)

    def update(self,keys,solid_rects,boxes,particles,cam):
        self.anim+=1
        if self.dead: return
        L=keys[pygame.K_LEFT]  or keys[pygame.K_a]
        R=keys[pygame.K_RIGHT] or keys[pygame.K_d]
        U=keys[pygame.K_UP]    or keys[pygame.K_w] or keys[pygame.K_SPACE]
        D=keys[pygame.K_DOWN]  or keys[pygame.K_s]

        # ── GHOST ──────────────────────────────────────────
        if self.ghost:
            self.gtimer-=1
            if self.gtimer<=0:
                self.ghost=False; self.gtimer=0
                if not self._safe(solid_rects):
                    self.dead=True; cam.shake(7,14)
                    burst(particles,self.x+self.W//2,self.y+self.H//2,C_RED,24,4.5,life=40)
                    return
            if R: self.vx=min(self.vx+1.3, self.GSPD);  self.facing=1
            elif L: self.vx=max(self.vx-1.3,-self.GSPD); self.facing=-1
            else:   self.vx*=0.78
            if U:   self.vy=max(self.vy-1.4,-self.GFLOAT)
            elif D: self.vy=min(self.vy+1.4, self.GFLOAT)
            else:
                self.vy+=self.GGRAV
                self.vy=max(-self.GMXDY,min(self.GMXDY,self.vy))*0.91
            self.x+=self.vx; self.y+=self.vy
            self.x=max(0,min(self.x,COLS*TILE-self.W))
            self.y=max(-TILE*3,min(self.y,ROWS*TILE+TILE))
            self.trail.append((self.x+self.W//2,self.y+self.H//2))
            if len(self.trail)>24: self.trail.pop(0)
            if self.anim%3==0:
                # FIX: use 'grav' keyword (matching P.__init__ parameter name),
                # NOT 'gravity' — P uses __slots__ so wrong kwargs crash immediately
                particles.append(P(self.x+self.W//2+random.uniform(-8,8),
                                   self.y+self.H+random.uniform(-6,0),
                                   random.uniform(-0.4,0.4),random.uniform(-1.8,-0.2),
                                   (65,105,235),38,grav=-0.04,sz=2))
            return

        # ── LIVING ─────────────────────────────────────────
        self.trail.clear()
        if R: self.vx=min(self.vx+1.1, self.SPD);  self.facing=1
        elif L: self.vx=max(self.vx-1.1,-self.SPD); self.facing=-1
        else:   self.vx*=0.70

        if U:   self.jbuf=8
        else:   self.jbuf=max(0,self.jbuf-1)
        if self.on_gnd: self.coy=10
        else:           self.coy=max(0,self.coy-1)
        if self.jbuf>0 and self.coy>0:
            self.vy=self.JMP; self.coy=0; self.jbuf=0
            burst(particles,self.x+self.W//2,self.y+self.H,
                  C_GREEN,8,2.0,grav=0.2,life=16,sz=2)

        self.vy=min(self.vy+self.GRAV,self.MXFALL)
        self.on_gnd=False

        # All collidable rects: tiles + boxes
        all_solid=solid_rects+[b.rect() for b in boxes]

        self.x+=self.vx
        r=self.rect()
        for s in all_solid:
            if r.colliderect(s):
                self.x=(s.left-self.W) if self.vx>0 else float(s.right)
                self.vx=0
                # Box pushing
                for b in boxes:
                    if r.colliderect(b.rect()):
                        b.vx=self.PUSH_FORCE*(1 if self.facing>0 else -1)

        self.y+=self.vy
        r=self.rect()
        for s in all_solid:
            if r.colliderect(s):
                if self.vy>0:
                    self.y=float(s.top-self.H); self.vy=0; self.on_gnd=True
                elif self.vy<0:
                    self.y=float(s.bottom); self.vy=0

        if self.y>ROWS*TILE+80: self.dead=True

    def draw(self,surf,cam,boxes):
        sx,sy=cam.apply(int(self.x),int(self.y))
        if self.ghost:
            for i,(tx,ty) in enumerate(self.trail):
                tsx,tsy=cam.apply(int(tx),int(ty))
                f=i/max(1,len(self.trail)); a=int(80*f*f); r2=max(1,int(7*f))
                ts=pygame.Surface((r2*2,r2*2),pygame.SRCALPHA)
                pygame.draw.circle(ts,(65,95,245,a),(r2,r2),r2); surf.blit(ts,(tsx-r2,tsy-r2))
            draw_ghost(surf,sx,sy,self.facing,self.vx,self.anim,self.gtimer/self.GDUR)
        else:
            near_box=any(self.rect().inflate(8,4).colliderect(b.rect()) for b in boxes)
            draw_living(surf,sx,sy,self.facing,self.vx,self.on_gnd,self.anim,near_box)

        # Soul pips
        for i in range(4):
            cx=sx+3+i*6; cy=sy-9
            c=C_GREEN if i<self.cycles else (26,26,36)
            b=(68,188,98) if i<self.cycles else (40,40,52)
            pygame.draw.circle(surf,c,(cx,cy),3)
            pygame.draw.circle(surf,b,(cx,cy),3,1)

        # Ghost bar
        if self.ghost or self.gtimer>0:
            bw=self.W+10; bx=sx-5; by=sy-16
            f=self.gtimer/self.GDUR
            pygame.draw.rect(surf,(10,10,28),(bx,by,bw,4))
            bc=(75,135,255) if f>0.3 else (215,55,55)
            pygame.draw.rect(surf,bc,(bx,by,int(bw*f),4))
            pygame.draw.rect(surf,(125,155,228),(bx,by,int(bw*f),4),1)

        # Rematerialise danger indicator
        if self.ghost:
            r=self.rect(); danger=any(r.colliderect(s) for s in _current_solids)
            if danger:
                da=int(160*abs(math.sin(self.anim*0.32)))
                ds=pygame.Surface((self.W+8,5),pygame.SRCALPHA)
                ds.fill((255,55,55,da)); surf.blit(ds,(sx-4,sy+self.H+2))

# ══════════════════════════════════════════════════════════
# PRESSURE PLATE
# ══════════════════════════════════════════════════════════
class Plate:
    W=TILE; H=TILE//2
    def __init__(self,col,row,pid,targets,tileset):
        self.col=col; self.row=row
        self.x=col*TILE; self.y=row*TILE+TILE//2
        self.id=pid; self.targets=targets
        self.active=False; self.tileset=tileset
    def rect(self): return pygame.Rect(self.x,self.y,self.W,self.H)
    def draw(self,surf,cam,t):
        sx,sy=cam.apply(self.x,self.y)
        tid=T_PLATE_ON if self.active else T_PLATE_OFF
        surf.blit(self.tileset.get(tid[0],tid[1]),(sx,sy+TILE//2-8))
        if not self.active:
            pt=_fsm.render("▼",True,(160,140,80))
            surf.blit(pt,(sx+TILE//2-pt.get_width()//2,sy-14))

# ══════════════════════════════════════════════════════════
# GATE  — slides open when plate activated
# ══════════════════════════════════════════════════════════
class Gate:
    def __init__(self,col,row,gid,tileset,start_open=False):
        self.col=col; self.row=row
        self.x=col*TILE; self.base_y=row*TILE
        # FIX: respect start_open so object dicts with 'open':True work correctly
        self.open=start_open
        self.y=float(self.base_y - TILE*4) if start_open else float(self.base_y)
        self.id=gid; self.tileset=tileset

    def rect(self):
        # FIX: return off-screen rect when open rather than Rect(0,0,0,0)
        # which could cause phantom collisions at the world origin
        if self.open and self.y <= self.base_y - TILE*4:
            return pygame.Rect(-TILE*2, -TILE*2, 0, 0)
        return pygame.Rect(self.x, int(self.y), TILE, TILE*4)

    def update(self):
        if self.open:
            # FIX: stop sliding once fully raised to avoid useless per-frame math
            if self.y > self.base_y - TILE*4:
                self.y = max(float(self.base_y - TILE*4), self.y - 4)

    def draw(self,surf,cam,t):
        sx,sy=cam.apply(self.x,int(self.y))
        # FIX: don't draw at all once fully raised and open
        if self.open and self.y <= self.base_y - TILE*4:
            return
        for i in range(4):
            dy=i*TILE
            surf.blit(self.tileset.get(T_W_IRON[0],T_W_IRON[1]),(sx,sy+dy))
        # Gate bar accent
        pygame.draw.rect(surf,(80,72,62),(sx+2,sy,TILE-4,TILE*4),2)
        # Indicator
        gc=(80,210,100) if self.open else (80,80,80)
        pygame.draw.circle(surf,gc,(sx+TILE//2,sy+TILE*2),5)

# ══════════════════════════════════════════════════════════
# LEVEL RUNTIME
# ══════════════════════════════════════════════════════════
_current_solids=[]   # global ref so Player.draw can check

class Level:
    def __init__(self,tile_data,objects,tileset):
        self.tileset=tileset; self.tile_map={}
        self.solid_rects=[]; self.particles=[]; self.t=0
        self.reached_exit=False

        for (tid,col,row) in tile_data:
            self.tile_map[(col,row)]=tid
            if tid in SOLID_TILES:
                self.solid_rects.append(pygame.Rect(col*TILE,row*TILE,TILE,TILE))

        self.boxes=[]; self.plates=[]; self.gates={}
        self.pads=[]; self.spikes=[]; self.exit_rect=None
        self.spawn_pos=(2*TILE,15*TILE)
        self.torches=[]

        # FIX: removed dead 'gate_map={}' variable that was created but never used
        for obj in objects:
            ot=obj['type']; ox=obj['col']*TILE; oy=obj['row']*TILE
            if ot=='spawn':
                self.spawn_pos=(ox,oy)
            elif ot=='box':
                self.boxes.append(Box(obj['col'],obj['row'],tileset))
            elif ot=='plate':
                self.plates.append(Plate(obj['col'],obj['row'],obj['id'],obj['targets'],tileset))
            elif ot=='gate':
                # FIX: pass 'open' field from object dict so gates can start open if spec'd
                start_open=obj.get('open',False)
                g=Gate(obj['col'],obj['row'],obj['id'],tileset,start_open)
                self.gates[obj['id']]=g
            elif ot=='spike':
                self.spikes.append(pygame.Rect(ox,oy+20,TILE,12))
            elif ot=='pad':
                self.pads.append({'rect':pygame.Rect(ox,oy,TILE,TILE),'id':obj['id'],'touched':False})
            elif ot=='exit':
                self.exit_rect=pygame.Rect(ox,oy,TILE,TILE)

        # Place torches near walls automatically
        rng = random.Random(sum(col + row for (_, col, row) in tile_data[:50]))
        for (col,row),tid in self.tile_map.items():
            if tid in SOLID_TILES and row<ROWS-2:
                if rng.random()<0.04:
                    self.torches.append(TorchLight(col*TILE+TILE//2,row*TILE+TILE,
                                                   radius=rng.randint(60,100),color=(255,rng.randint(120,160),30)))

        self._rebuild_gates()

    def _rebuild_gates(self):
        # Only include closed/partially-open gates as solid geometry
        self.gate_solid=[g.rect() for g in self.gates.values()
                         if not (g.open and g.y <= g.base_y - TILE*4)]

    def all_solids(self):
        return self.solid_rects+self.gate_solid

    def update(self,player,cam):
        global _current_solids
        self.t+=1; self.reached_exit=False
        all_s=self.all_solids()
        _current_solids=all_s

        # Update gates
        for g in self.gates.values():
            g.update()
        self._rebuild_gates()

        # Update boxes (pass other boxes for stacking)
        for i,b in enumerate(self.boxes):
            others=[bx for j,bx in enumerate(self.boxes) if j!=i]
            b.update(all_s,others)

        # Pressure plates — check if any box is on them
        for plate in self.plates:
            was=plate.active
            plate.active=any(plate.rect().colliderect(b.rect()) for b in self.boxes)
            if plate.active and not was:
                burst(self.particles,plate.x+TILE//2,plate.y+TILE//2,C_GREEN,14,2.5,life=30)
                for tid in plate.targets:
                    if tid in self.gates:
                        self.gates[tid].open=True
                        burst(self.particles,self.gates[tid].x+TILE//2,
                              self.gates[tid].base_y,C_GOLD,20,3.5,life=35)
            elif not plate.active and was:
                # Box removed — close gate again only if no other plate targets it
                for tid in plate.targets:
                    if tid in self.gates and not any(
                            p.active for p in self.plates if tid in p.targets):
                        self.gates[tid].open=False
                        # Reset gate y so it slides back down
                        self.gates[tid].y=float(self.gates[tid].base_y)

        if not player.dead and not player.ghost:
            # Spikes
            for s in self.spikes:
                if player.rect().colliderect(s):
                    player.dead=True; cam.shake(5,10)
                    burst(self.particles,player.rect().centerx,player.rect().centery,
                          C_RED,22,4.0,life=38)
            # Pads
            for pad in self.pads:
                if player.rect().colliderect(pad['rect']):
                    player.set_spawn(pad['rect'].x,pad['rect'].y-player.H)
                    if not pad['touched']:
                        pad['touched']=True
                        burst(self.particles,pad['rect'].centerx,pad['rect'].top,
                              C_GREEN,12,2.0,life=28,sz=2)
            # Exit
            if self.exit_rect and player.rect().colliderect(self.exit_rect):
                self.reached_exit=True

        for p in self.particles: p.upd()
        self.particles=[p for p in self.particles if p.life>0]

    # ── DRAW ─────────────────────────────────────────────
    def draw(self,surf,cam,bg,far_layer,mid_layer,player,gt):
        # Far parallax
        px=int(cam.x*0.08)%SW
        surf.blit(far_layer,(-px,0)); surf.blit(far_layer,(SW-px,0))
        # Mid parallax
        px2=int(cam.x*0.18)%SW
        surf.blit(mid_layer,(-px2,0)); surf.blit(mid_layer,(SW-px2,0))
        # BG tile
        bx,by=cam.apply(0,0); surf.blit(bg,(bx,by))

        # Torch lights (draw before tiles for additive feel)
        for tc in self.torches: tc.draw(surf,cam,gt)

        # Ghost-only tiles
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
            # Top-edge highlight
            pygame.draw.line(surf,(110,95,72),(sx,sy),(sx+TILE-1,sy),1)
            pygame.draw.line(surf,(22,18,14),(sx,sy+TILE-1),(sx+TILE-1,sy+TILE-1),1)

        # Gates
        for g in self.gates.values(): g.draw(surf,cam,gt)

        # Pressure plates
        for plate in self.plates: plate.draw(surf,cam,gt)

        # Boxes
        for b in self.boxes: b.draw(surf,cam,gt)

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
            pulse=abs(math.sin(gt*0.06))
            act=pad['touched']
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
            et=_fsm.render("EXIT",True,(175,222,255))
            surf.blit(et,(sx+TILE//2-et.get_width()//2,sy-16))

        # Particles
        for p in self.particles: p.draw(surf,cam)

        # Ghost world overlay
        if player.ghost:
            ov=pygame.Surface((SW,SH),pygame.SRCALPHA)
            ov.fill((15,25,70,40)); surf.blit(ov,(0,0))

# ══════════════════════════════════════════════════════════
# HUD
# ══════════════════════════════════════════════════════════
def draw_hud(surf,player,lnum,hint_t,gt):
    # Dark panel
    pan=pygame.Surface((280,52),pygame.SRCALPHA); pan.fill((6,4,3,200))
    surf.blit(pan,(10,10))

    # Soul vessels
    for i in range(4):
        cx=22+i*28; cy=28
        alive=i<player.cycles
        c=C_GREEN if alive else (20,20,30)
        e=(65,185,95) if alive else (32,32,44)
        pygame.draw.circle(surf,c,(cx,cy),10)
        pygame.draw.circle(surf,e,(cx,cy),10,2)
        if alive:
            inner=pygame.Surface((8,8),pygame.SRCALPHA)
            pygame.draw.circle(inner,(195,255,205,180),(4,4),4)
            surf.blit(inner,(cx-4,cy-4))

    # Form label
    if player.ghost:
        ft=_fsm.render("◈  GHOST",True,C_SOUL)
    else:
        ft=_fsm.render("◆  LIVING",True,C_LIVING)
    surf.blit(ft,(145,20))

    # Ghost bar
    if player.ghost or player.gtimer>0:
        bw=150; bx=14; by2=66
        f=player.gtimer/player.GDUR
        bg2=pygame.Surface((bw,6),pygame.SRCALPHA); bg2.fill((8,8,24,200))
        surf.blit(bg2,(bx,by2))
        bc=(72,130,255) if f>0.3 else (215,55,55)
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

    # Level name
    names=["I · THE ANTECHAMBER","II · THE DESCENT HALLS","III · THE INNER SANCTUM"]
    ln=_fsm.render(names[min(lnum-1,2)],True,C_DIM)
    surf.blit(ln,(SW-ln.get_width()-14,14))

    # Hint
    if hint_t>0:
        a=min(255,hint_t*3)
        lines=["Q — Ghost Form: fly through walls to scout the puzzle",
               "Push boxes onto pressure plates to open gates  •  No levers!"]
        for i,line in enumerate(lines):
            ht=_fsm.render(line,True,(138,125,105))
            hs=pygame.Surface(ht.get_size(),pygame.SRCALPHA)
            hs.blit(ht,(0,0)); hs.set_alpha(a)
            surf.blit(hs,(SW//2-ht.get_width()//2,SH-44+i*18))


def draw_overlay(surf,title,sub='',col=C_WHITE,sub2=''):
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
    global _fsm,_fmed,_fbig,_current_solids
    pygame.init()
    screen=pygame.display.set_mode((SW,SH))
    pygame.display.set_caption("THE LAZARUS PROJECT")
    clock=pygame.time.Clock()

    _fsm =pygame.font.SysFont("consolas",13)
    _fmed=pygame.font.SysFont("consolas",20,bold=True)
    _fbig=pygame.font.SysFont("consolas",40,bold=True)
    _current_solids=[]

    sd=os.path.dirname(os.path.abspath(__file__))
    ts_path=os.path.join(sd,"lazarus_tileset.png")
    if not os.path.exists(ts_path):
        print(f"ERROR: lazarus_tileset.png not found at:\n  {ts_path}"); sys.exit(1)

    tileset=TileSet(ts_path)
    far_layer=make_far_layer()
    mid_layer=make_mid_layer()

    cur=0; hint_t=520; gt=0

    def load(idx,cycles=4):
        td,obs=LEVELS[idx]()
        lvl=Level(td,obs,tileset)
        sx,sy=lvl.spawn_pos
        p=Player(sx,sy-Player.H); p.cycles=cycles
        lvl.bg=make_bg()
        return lvl,p

    level,player=load(cur)
    cam=Camera(); state='title'; state_t=0

    running=True
    while running:
        clock.tick(FPS); gt+=1; state_t+=1

        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: running=False
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_ESCAPE: running=False
                if state=='title': state='play'; state_t=0
                elif state=='play':
                    if ev.key==pygame.K_q:
                        player.toggle_ghost(level.all_solids())
                    if ev.key==pygame.K_r:
                        level,player=load(cur,player.cycles)
                        state='play'; state_t=0; hint_t=200
                elif state in('dead','gameover','win'):
                    if ev.key==pygame.K_r:
                        if state=='gameover': cur=0; level,player=load(0,4)
                        elif state=='win':    cur=0; level,player=load(0,4)
                        else:                level,player=load(cur,player.cycles)
                        state='play'; state_t=0; hint_t=200

        if state=='play':
            hint_t=max(0,hint_t-1)
            keys=pygame.key.get_pressed()
            player.update(keys,level.all_solids(),level.boxes,level.particles,cam)
            level.update(player,cam)
            cam.update(player.x+Player.W//2,player.y+Player.H//2)

            if player.dead:
                state='gameover' if player.cycles<=0 else 'dead'; state_t=0
            if level.reached_exit:
                cur+=1
                if cur>=len(LEVELS): state='win'; state_t=0
                else: level,player=load(cur,player.cycles); state='play'; state_t=0

        elif state=='dead' and state_t>85:
            player.respawn(); state='play'; state_t=0

        # ── RENDER ──
        screen.fill(C_BG)
        if state=='title':
            screen.blit(far_layer,(0,0)); screen.blit(mid_layer,(0,0))
            ov=pygame.Surface((SW,SH),pygame.SRCALPHA); ov.fill((0,0,0,140)); screen.blit(ov,(0,0))
            t1=_fbig.render("THE LAZARUS PROJECT",True,C_ACCENT)
            screen.blit(t1,(SW//2-t1.get_width()//2,SH//2-90))
            t2=_fmed.render("An underground temple escape",True,(120,105,80))
            screen.blit(t2,(SW//2-t2.get_width()//2,SH//2-38))
            lines=[
                "A lab deep underground. The Lazarus Project has failed. You must escape.",
                "As a GHOST: scout the temple, fly through walls, read the puzzle.",
                "As LIVING: push boxes onto pressure plates to open gates. Reach the exit.",
                "Ghost timer drains — plan where to rematerialise or you die inside a wall.",
            ]
            for i,line in enumerate(lines):
                lt=_fsm.render(line,True,(90,80,62))
                screen.blit(lt,(SW//2-lt.get_width()//2,SH//2+10+i*20))
            pt=_fmed.render("Press any key",True,(70,62,48))
            screen.blit(pt,(SW//2-pt.get_width()//2,SH//2+108))
        else:
            level.draw(screen,cam,level.bg,far_layer,mid_layer,player,gt)
            player.draw(screen,cam,level.boxes)
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