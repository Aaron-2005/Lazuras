# levels.py — level builder helpers and all 6 levels

from tileset import *
from constants import COLS, ROWS

# ── Layout helpers ───────────────────────────────────────
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
def build_level_1():
    """THE ANTECHAMBER — tutorial. One box, one plate, one gate."""
    S=T_W_SAND; D=T_W_DARK; F=T_FL_ANC; FS=T_FL_SIL
    P=T_PL_STONE; PS=T_PL_SIL; W=T_W_CARVE
    t=[]
    hwall(t,D,0,COLS-1,0);   hwall(t,F,0,COLS-1,ROWS-1)
    vwall(t,S,0,1,ROWS-2);   vwall(t,S,COLS-1,1,ROWS-2)
    hwall(t,FS,1,COLS-2,ROWS-2)
    hwall(t,W,1,COLS-2,1)
    vwall(t,S,9,2,ROWS-2);   vwall(t,S,19,2,ROWS-2)
    plat(t,P,2,6,12);         plat(t,PS,10,14,10);  plat(t,P,20,26,8)
    vwall(t,T_GH_BAR,9,5,8)
    for cx in [4,12,16,24]: vwall(t,T_W_ENG,cx,1,3)
    for cx in [3,25]: t.append((T_W_ENG,cx,ROWS-3))
    objs=[
        {'type':'spawn','col':2,'row':16},
        {'type':'pad','col':2,'row':15,'id':0},
        {'type':'box','col':5,'row':15},
        {'type':'plate','col':12,'row':9,'id':0,'targets':['gate0']},
        {'type':'gate','col':19,'row':2,'id':'gate0','open':False},
        {'type':'spike','col':10,'row':16},{'type':'spike','col':11,'row':16},
        {'type':'exit','col':25,'row':7},
        {'type':'pad','col':21,'row':7,'id':1},
    ]
    return t, objs


# ══════════════════════════════════════════════════════════
def build_level_2():
    """THE DESCENT HALLS — two boxes, two plates, ghost barriers."""
    S=T_W_SAND; D=T_W_DARK; F=T_FL_ANC; FS=T_FL_SIL
    P=T_PL_STONE; PS=T_PL_SIL
    t=[]
    hwall(t,D,0,COLS-1,0);   hwall(t,F,0,COLS-1,ROWS-1)
    vwall(t,S,0,1,ROWS-2);   vwall(t,S,COLS-1,1,ROWS-2)
    hwall(t,FS,1,COLS-2,ROWS-2)
    hwall(t,T_W_CARVE,1,COLS-2,1)
    vwall(t,S,8,2,ROWS-2);   vwall(t,S,16,2,ROWS-2);  vwall(t,S,24,2,ROWS-2)
    plat(t,PS,1,7,14);        plat(t,P,9,15,11);
    plat(t,FS,17,23,8);       plat(t,PS,25,COLS-2,5)
    vwall(t,T_GH_BAR,8,6,10); vwall(t,T_GH_BARD,16,4,8)
    for cx in [4,12,20,27]: vwall(t,T_W_ENG,cx,1,2)
    for cx in [6,14,22]: vwall(t,T_W_RUIN,cx,1,4)
    objs=[
        {'type':'spawn','col':2,'row':16},
        {'type':'pad','col':2,'row':13,'id':0},
        {'type':'pad','col':18,'row':7,'id':1},
        {'type':'box','col':4,'row':13},
        {'type':'box','col':11,'row':10},
        {'type':'plate','col':6,'row':13,'id':0,'targets':['gate0']},
        {'type':'plate','col':21,'row':7,'id':1,'targets':['gate1']},
        {'type':'gate','col':16,'row':2,'id':'gate0','open':False},
        {'type':'gate','col':24,'row':2,'id':'gate1','open':False},
        {'type':'spike','col':9,'row':16},{'type':'spike','col':10,'row':16},
        {'type':'spike','col':17,'row':16},{'type':'spike','col':18,'row':16},
        {'type':'enemy','col':12,'row':10,'patrol':3},
        {'type':'exit','col':27,'row':4},
    ]
    return t, objs


# ══════════════════════════════════════════════════════════
def build_level_3():
    """THE INNER SANCTUM — three boxes, tight ghost timer."""
    S=T_W_SAND; D=T_W_OBS; B=T_W_ENG; F=T_FL_ANC
    FS=T_FL_SIL; LF=T_LAZ_FL; P=T_PL_STONE; PS=T_PL_SIL; PC=T_PL_CARVE
    t=[]
    hwall(t,D,0,COLS-1,0);   hwall(t,F,0,COLS-1,ROWS-1)
    vwall(t,D,0,1,ROWS-2);   vwall(t,D,COLS-1,1,ROWS-2)
    hwall(t,FS,1,COLS-2,ROWS-2)
    hwall(t,T_W_CARVE,1,COLS-2,1)
    vwall(t,S,7,3,ROWS-2);   vwall(t,S,14,3,ROWS-2);  vwall(t,S,21,3,ROWS-2)
    plat(t,PS,1,6,14);        plat(t,PC,8,13,11)
    plat(t,P,8,10,8);         plat(t,PS,15,20,9);      plat(t,LF,22,COLS-2,6)
    plat(t,T_PL_DARK,8,13,5); plat(t,T_PL_DARK,15,20,5)
    vwall(t,T_GH_BAR,7,6,10); vwall(t,T_GH_BARD,14,4,8)
    hwall(t,T_GH_BAR,15,20,4)
    for cx in [3,10,17,25]: vwall(t,B,cx,1,2)
    for cx in [5,12,19,27]: vwall(t,T_W_RUIN,cx,1,3)
    objs=[
        {'type':'spawn','col':2,'row':16},
        {'type':'pad','col':2,'row':13,'id':0},
        {'type':'pad','col':9,'row':7,'id':1},
        {'type':'pad','col':22,'row':5,'id':2},
        {'type':'box','col':3,'row':13},
        {'type':'box','col':9,'row':10},
        {'type':'box','col':16,'row':8},
        {'type':'plate','col':5,'row':13,'id':0,'targets':['gate0']},
        {'type':'plate','col':11,'row':10,'id':1,'targets':['gate1']},
        {'type':'plate','col':18,'row':8,'id':2,'targets':['gate2']},
        {'type':'gate','col':7,'row':3,'id':'gate0','open':False},
        {'type':'gate','col':14,'row':3,'id':'gate1','open':False},
        {'type':'gate','col':21,'row':3,'id':'gate2','open':False},
        {'type':'spike','col':8,'row':16},{'type':'spike','col':9,'row':16},
        {'type':'spike','col':15,'row':16},{'type':'spike','col':16,'row':16},
        {'type':'spike','col':22,'row':16},
        {'type':'enemy','col':10,'row':11,'patrol':3},
        {'type':'enemy','col':17,'row':9,'patrol':2},
        {'type':'exit','col':26,'row':5},
    ]
    return t, objs


# ══════════════════════════════════════════════════════════
def build_level_4():
    """
    THE CLOCKWORK VAULT
    Introduces moving platforms. Ghost must scout platform timing.
    One lever opens a shortcut gate, plates still needed for main gate.
    """
    S=T_W_COBB; D=T_W_ENG; F=T_FL_MIX; FS=T_FL_DKSIL
    P=T_PL_STONE; PC=T_PL_CARVE; PH=T_PL_HAZ
    t=[]
    hwall(t,D,0,COLS-1,0);    hwall(t,F,0,COLS-1,ROWS-1)
    vwall(t,S,0,1,ROWS-2);    vwall(t,S,COLS-1,1,ROWS-2)
    hwall(t,FS,1,COLS-2,ROWS-2)
    hwall(t,T_W_CARVE,1,COLS-2,1)
    # Dividers
    vwall(t,S,10,2,12);       vwall(t,S,20,2,14)
    # Floors
    plat(t,P,1,9,14);         plat(t,PC,11,19,11)
    plat(t,FS,21,COLS-2,7)
    # Ceiling ledges
    plat(t,T_PL_DARK,3,6,6);  plat(t,T_PL_DARK,13,17,5)
    # Hazard floor strip
    plat(t,PH,11,19,ROWS-2)
    # Ghost barriers
    vwall(t,T_GH_BAR,10,5,10); hwall(t,T_GH_BARD,13,17,4)
    # Decoration
    for cx in [2,7,14,22,28]: vwall(t,D,cx,1,2)
    objs=[
        {'type':'spawn','col':2,'row':16},
        {'type':'pad','col':2,'row':13,'id':0},
        {'type':'box','col':4,'row':13},
        {'type':'box','col':6,'row':13},
        # Two plates in middle room
        {'type':'plate','col':13,'row':10,'id':0,'targets':['gate0']},
        {'type':'plate','col':16,'row':10,'id':1,'targets':['gate0']},
        # Lever opens shortcut
        {'type':'lever','col':8,'row':13,'id':'lev0','targets':['gate1']},
        {'type':'gate','col':20,'row':2,'id':'gate0','open':False},
        {'type':'gate','col':10,'row':8,'id':'gate1','open':False},
        # Moving platforms
        {'type':'mplat','col':11,'row':9,'axis':'h','dist':4,'speed':1.2},
        {'type':'mplat','col':21,'row':5,'axis':'v','dist':3,'speed':1.0},
        # Enemies
        {'type':'enemy','col':14,'row':10,'patrol':3},
        {'type':'enemy','col':23,'row':6,'patrol':2},
        # Spikes on hazard floor
        {'type':'spike','col':12,'row':16},{'type':'spike','col':13,'row':16},
        {'type':'spike','col':17,'row':16},{'type':'spike','col':18,'row':16},
        {'type':'exit','col':26,'row':6},
        {'type':'pad','col':22,'row':6,'id':1},
    ]
    return t, objs


# ══════════════════════════════════════════════════════════
def build_level_5():
    """
    THE HAUNTED AQUEDUCT
    Water-channel theme. Multiple enemies guard lever positions.
    Moving platforms over spike pits. Ghost essential for lever routing.
    """
    S=T_W_BSLT; D=T_W_OBS; F=T_FL_GRATE; FS=T_FL_MOSS
    P=T_PL_MOSS; PB=T_PL_BONE; PD=T_PL_DARK
    t=[]
    hwall(t,D,0,COLS-1,0);    hwall(t,F,0,COLS-1,ROWS-1)
    vwall(t,S,0,1,ROWS-2);    vwall(t,S,COLS-1,1,ROWS-2)
    hwall(t,FS,1,COLS-2,ROWS-2)
    hwall(t,T_W_MOSS,1,COLS-2,1)
    # Main floor sections separated by spike pits
    plat(t,P,1,6,14);         plat(t,P,10,14,14);  plat(t,P,18,22,14)
    plat(t,FS,25,COLS-2,14)
    # Upper ledges
    plat(t,PB,2,5,10);        plat(t,PB,11,15,8);
    plat(t,PD,19,23,6);       plat(t,PD,25,COLS-2,4)
    # Mid walls
    vwall(t,S,8,4,14);        vwall(t,S,17,4,14);   vwall(t,S,24,4,14)
    # Ghost passages
    vwall(t,T_GH_BAR,8,7,12); vwall(t,T_GH_BARD,17,6,12)
    hwall(t,T_GH_BAR,19,23,5)
    # Stalactites
    for cx in [3,12,20,27]: vwall(t,T_W_RUIN,cx,1,3)
    objs=[
        {'type':'spawn','col':2,'row':16},
        {'type':'pad','col':2,'row':13,'id':0},
        {'type':'pad','col':11,'row':7,'id':1},
        # Boxes
        {'type':'box','col':4,'row':13},
        {'type':'box','col':12,'row':13},
        # Plates
        {'type':'plate','col':3,'row':9,'id':0,'targets':['gate0']},
        {'type':'plate','col':13,'row':7,'id':1,'targets':['gate1']},
        # Levers
        {'type':'lever','col':6,'row':13,'id':'lev0','targets':['gate2']},
        {'type':'lever','col':20,'row':5,'id':'lev1','targets':['gate3']},
        # Gates
        {'type':'gate','col':8,'row':2,'id':'gate0','open':False},
        {'type':'gate','col':17,'row':2,'id':'gate1','open':False},
        {'type':'gate','col':24,'row':9,'id':'gate2','open':False},
        {'type':'gate','col':24,'row':2,'id':'gate3','open':False},
        # Moving platforms over spike pits
        {'type':'mplat','col':7,'row':13,'axis':'h','dist':2,'speed':1.5},
        {'type':'mplat','col':15,'row':13,'axis':'h','dist':2,'speed':1.3},
        {'type':'mplat','col':23,'row':10,'axis':'v','dist':4,'speed':1.0},
        # Enemies
        {'type':'enemy','col':3,'row':9,'patrol':2},
        {'type':'enemy','col':12,'row':7,'patrol':2},
        {'type':'enemy','col':20,'row':13,'patrol':2},
        {'type':'enemy','col':26,'row':3,'patrol':2},
        # Spike pits
        {'type':'spike','col':7,'row':16},{'type':'spike','col':8,'row':16},
        {'type':'spike','col':15,'row':16},{'type':'spike','col':16,'row':16},
        {'type':'spike','col':17,'row':16},
        {'type':'exit','col':27,'row':3},
    ]
    return t, objs


# ══════════════════════════════════════════════════════════
def build_level_6():
    """
    THE LAZARUS CHAMBER
    Final level. All mechanics combined: moving platforms, levers,
    pressure plates, boxes, multiple enemies. Ghost timer is tight.
    Three-stage unlock: lever → plate → plate → exit.
    """
    S=T_W_IRON; D=T_W_OBS; F=T_LAZ_FL; FS=T_FL_DKSIL
    P=T_PL_CARVE; PL=T_LAZ_WL; PD=T_PL_DARK
    t=[]
    hwall(t,D,0,COLS-1,0);    hwall(t,F,0,COLS-1,ROWS-1)
    vwall(t,S,0,1,ROWS-2);    vwall(t,S,COLS-1,1,ROWS-2)
    hwall(t,FS,1,COLS-2,ROWS-2)
    hwall(t,T_W_CARVE,1,COLS-2,1)
    # Complex layout
    vwall(t,S,6,3,ROWS-2);    vwall(t,S,12,3,16);
    vwall(t,S,18,3,ROWS-2);   vwall(t,S,24,3,12)
    # Floors
    plat(t,P,1,5,14);         plat(t,P,7,11,12);
    plat(t,PD,13,17,10);      plat(t,P,19,23,8)
    plat(t,FS,25,COLS-2,5)
    # Upper paths
    plat(t,PL,1,5,8);         plat(t,PL,7,11,6);
    plat(t,PD,13,17,4);       plat(t,PD,19,23,3)
    # Ghost-only areas
    vwall(t,T_GH_BAR,6,5,10); vwall(t,T_GH_BARD,12,4,9)
    vwall(t,T_GH_BAR,18,4,8); hwall(t,T_GH_BARD,19,23,2)
    # Lava floor (spikes) in gaps
    for cx in [6,7,12,13,18,19]: t.append((T_PL_HAZ,cx,ROWS-2))
    # Decoration
    for cx in [3,9,15,21,27]: vwall(t,T_W_ENG,cx,1,2)
    objs=[
        {'type':'spawn','col':2,'row':16},
        {'type':'pad','col':2,'row':13,'id':0},
        {'type':'pad','col':8,'row':11,'id':1},
        {'type':'pad','col':20,'row':7,'id':2},
        # Boxes
        {'type':'box','col':3,'row':13},
        {'type':'box','col':8,'row':11},
        {'type':'box','col':14,'row':9},
        # Plates
        {'type':'plate','col':4,'row':7,'id':0,'targets':['gate1']},
        {'type':'plate','col':10,'row':5,'id':1,'targets':['gate2']},
        {'type':'plate','col':15,'row':9,'id':2,'targets':['gate3']},
        # Levers — must be activated by ghost scouting first
        {'type':'lever','col':5,'row':13,'id':'lev0','targets':['gate0']},
        {'type':'lever','col':22,'row':7,'id':'lev1','targets':['gate4']},
        # Gates — chained unlock
        {'type':'gate','col':6,'row':3,'id':'gate0','open':False},
        {'type':'gate','col':12,'row':3,'id':'gate1','open':False},
        {'type':'gate','col':18,'row':3,'id':'gate2','open':False},
        {'type':'gate','col':24,'row':3,'id':'gate3','open':False},
        {'type':'gate','col':24,'row':8,'id':'gate4','open':False},
        # Moving platforms
        {'type':'mplat','col':7,'row':11,'axis':'h','dist':3,'speed':1.4},
        {'type':'mplat','col':13,'row':9,'axis':'v','dist':3,'speed':1.2},
        {'type':'mplat','col':19,'row':7,'axis':'h','dist':3,'speed':1.6},
        {'type':'mplat','col':25,'row':4,'axis':'v','dist':2,'speed':0.9},
        # Enemies — heavy guard
        {'type':'enemy','col':9,'row':11,'patrol':2},
        {'type':'enemy','col':14,'row':9,'patrol':2},
        {'type':'enemy','col':20,'row':7,'patrol':2},
        {'type':'enemy','col':26,'row':4,'patrol':2},
        {'type':'enemy','col':3,'row':7,'patrol':2},
        # Spike pits in floor gaps
        {'type':'spike','col':6,'row':16},{'type':'spike','col':7,'row':16},
        {'type':'spike','col':12,'row':16},{'type':'spike','col':13,'row':16},
        {'type':'spike','col':18,'row':16},{'type':'spike','col':19,'row':16},
        {'type':'exit','col':27,'row':4},
    ]
    return t, objs


LEVELS = [
    build_level_1, build_level_2, build_level_3,
    build_level_4, build_level_5, build_level_6,
]
