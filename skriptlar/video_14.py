# video_14.py  -  "Who Really Got Rich in the Gold Rush?" (hikoyachi: Fenrir, Kokoro TTS)
import bpy, os, math, random, aud
T = bpy.data.texts["stickman_tools.py"]
st = T.as_module()                        # Sticky - xazina xaritasi
bn = T.as_module(); bn.use("T_")          # Ben - sariq kaska, oltin qazadi
ly = T.as_module(); ly.use("L_")          # Lily - firuza bant, belkurak sotadi
mx = T.as_module(); mx.use("R_")          # Max - ko'k kepka, suv va gazak sotadi
gp = T.as_module(); gp.use("G_")          # Bobo - kaskali xaridor (konchi)
ALL = (st, bn, ly, mx, gp)
S = bpy.context.scene
O = bpy.data.objects
A = "//video_14_audio/"
LX = (-1.42, -0.47, 0.47, 1.42)           # qatorda: Sticky, Ben, Lily, Max
WIDE = (0.0, 2.3, 7.0)
CHART = (70.0, 2.3, 7.0)
GAIN = 1.3

st.clear_animation()
for m in (bn, ly, mx, gp):
    m.clear_animation(); m.show()
st.backdrop("room")
S.frame_end = 1800
S.render.filepath = "//Who Really Got Rich in the Gold Rush.mp4"

EST = {"S01": 142, "S02": 38, "S03": 52, "S04": 115, "S05": 113, "S06": 64, "S07": 65, "S08": 78, "S09": 176, "S10": 138, "S11": 80}
VOL = {}
def N(key, f, vol=0.9):
    p = bpy.path.abspath(A + key + ".wav")
    if os.path.exists(p):
        st.voice(A + key + ".wav", f, volume=vol * VOL.get(key, 1.0), channel=1)
        s = aud.Sound.file(p); return f + int(round(s.length / s.specs[0] * 30))
    return f + EST[key]
def on(name, f, x=None, z=None, s=1.0): st.place(name, f, x=x, z=z, scale=s, step=True)
def off(name, f): st.place(name, f, scale=0.0, step=True)
def popin(name, f, x=None, z=None, s=1.0):
    st.place(name, f, x=x, z=z, scale=s * 0.6, step=True); st.place(name, f + 3, scale=s * 1.12); st.place(name, f + 6, scale=s)
def keyall(ob, f):
    for p in ("location", "rotation_euler", "scale"): ob.keyframe_insert(p, frame=f)
def put(ob, f, x, z, rot=0.0, s=1.0, y=None, step=False):
    if isinstance(ob, str): ob = O[ob]
    if step: keyall(ob, f - 1)
    ob.location = (x, ob.location.y if y is None else y, z); ob.rotation_euler = (0.0, rot, 0.0)
    ob.scale = (s, s, s) if isinstance(s, (int, float)) else tuple(s)
    keyall(ob, f)
def skey(ob, pairs):
    if isinstance(ob, str): ob = O[ob]
    for f, s in pairs:
        ob.scale = (s, s, s) if isinstance(s, (int, float)) else tuple(s); ob.keyframe_insert("scale", frame=f)
def P(m, name, f):
    m.apply_pose(name, f, face=False)
def go(m, f, x, z=0.0):
    """Personajni shu kadrda boshqa joyga o'tkazadi (oldingi joy ushlab turiladi)."""
    pb = m._rig().pose.bones["root"]; pb.keyframe_insert("location", frame=f - 1); m.move_to(x, z, f)
class Face:
    def __init__(self, m): self.m = m; self.b = [0.0, 0.0, 0.0]; self.l = [0.0, 0.0]
    def brow(self, f, tilt, lift=0.0, cock=0.0):
        self.m.brows(self.b[0], self.b[1], f - 1, self.b[2]); self.m.brows(tilt, lift, f, cock); self.b[:] = [tilt, lift, cock]
    def look(self, f, dx, dz):
        self.m.look(self.l[0], self.l[1], f - 1); self.m.look(dx, dz, f); self.l[:] = [dx, dz]
FS, FB, FL, FM, FG = Face(st), Face(bn), Face(ly), Face(mx), Face(gp)
ARM = 0.55
def reach(side, tx, tz, sx=0.0, sz=2.3):
    d = min(math.hypot(tx - sx, tz - sz), 2 * ARM - 1e-4)
    phi = math.degrees(math.atan2(tz - sz, tx - sx)); al = math.degrees(math.acos(d / 2.0 / ARM))
    best = None
    for sg in (1, -1):
        ua = phi + sg * al
        ex = sx + ARM * math.cos(math.radians(ua)); ez = sz + ARM * math.sin(math.radians(ua))
        fa = math.degrees(math.atan2(tz - ez, tx - ex))
        if best is None or ez < best[0]: best = (ez, ua, fa)
    return {"upper_arm." + side: best[1], "forearm." + side: best[2]}
def pose(*parts, **kw):
    d = {}
    for p in parts: d.update(p)
    d.update(kw); return d

# ---------- belkurak: tepa (dasta) nuqtasi va burchagi bo'yicha ----------
SH_TOP, SH_TIP = 0.62, 0.98               # dasta uchi va tig' uchi (obyekt markazidan)
def shovel_at(top, ang):
    ux, uz = math.sin(ang), math.cos(ang)
    org = (top[0] - SH_TOP * ux, top[1] - SH_TOP * uz)
    tip = (top[0] - (SH_TOP + SH_TIP) * ux, top[1] - (SH_TOP + SH_TIP) * uz)
    return org, tip
def grip(top, ang, t):
    L = SH_TOP + SH_TIP
    return (top[0] - t * L * math.sin(ang), top[1] - t * L * math.cos(ang))
DIG = {"dig_up": ((-0.08, 2.4), math.radians(-32)), "dig_down": ((0.1, 1.85), math.radians(-18))}
for m in ALL:
    m.POSES["sell"] = pose(reach("L", 0.45, 1.75), reach("R", -0.45, 1.25))
    m.POSES["give"] = pose(reach("R", -0.45, 1.35), reach("L", 0.75, 2.2))
    m.POSES["hold"] = pose(reach("L", 0.45, 1.85))
    m.POSES["holdmap"] = pose(reach("L", 0.32, 1.62), reach("R", -0.32, 1.62))
    m.POSES["buy"] = pose(reach("R", -0.62, 1.95))
    m.POSES["holdL"] = pose(reach("R", -0.45, 1.85))
    m.POSES["holdbig"] = pose(reach("L", 0.8, 2.5), reach("R", -0.8, 2.5))
    m.POSES["cup"] = pose(reach("R", -0.15, 2.45), head=96)
    for k, (top, ang) in DIG.items():
        h1 = grip(top, ang, 0.06); h2 = grip(top, ang, 0.36)
        m.POSES[k] = pose(reach("R", h1[0], h1[1]), reach("L", h2[0], h2[1]))
SHV = O["FX_Shovel"]
def shovel_pose(f, bx, k, step=False):
    top, ang = DIG[k]
    org, tip = shovel_at((bx + top[0], top[1]), ang)
    put(SHV, f, org[0], org[1], rot=ang, s=1.0, y=-0.3, step=step)
    return tip

# ---------- sahna ----------
off("Set_Calendar", 1)
for n in ("Set_Floor", "Set_Door", "Set_DoorFrame"): off(n, 1)
on("Gold_Back", 1); on("Chart_BoardPlain", 1)
for n in ("R_Hat", "R_Bowtie"): off(n, 1)
on("R_Cap", 1); on("T_Helmet", 1); on("G_Helmet", 1); off("T_Beanie", 1)
TITLE = st.title("WHO REALLY GOT RICH?", f_on=-8, size=0.38)
def title_off(f0, f1):
    skey(TITLE, ((f0 - 1, 1.0), (f0, 0.0), (f1 - 1, 0.0), (f1, 1.0)))
for m, x in zip((st, bn, ly, mx), LX):
    m.move_to(x, 0.0, 1); P(m, "stand", 1); m.mouth("smile", 1)
gp.move_to(-8.0, 0.0, 1); P(gp, "stand", 1); gp.mouth("smile", 1)
PL = O["HUD_Plate1"]
def board(f0, f1):
    PL.location = (0.0, -2.75, -5.06); PL.keyframe_insert("location", frame=f0 - 1)
    skey(PL, ((f0 - 1, 0.0), (f0 + 3, 1.08), (f0 + 6, 1.0), (f1 - 1, 1.0), (f1, 0.0)))
def shimmer(f, xs=((-0.1, 4.0), (0.42, 3.45), (-0.62, 3.1), (0.95, 2.8)), s=0.5):
    for i, (x, z) in enumerate(xs):
        g = "FX_Gold_%d" % (i + 1)
        O[g].location.y = 0.6
        st.place(g, f + i * 3, x=x, z=z, scale=0.0, step=True); st.place(g, f + i * 3 + 4, scale=s * 1.2)
        st.place(g, f + i * 3 + 8, scale=s * 0.8); st.place(g, f + i * 3 + 14, scale=0.0)
    st.sfx("shimmer", f, 0.5)
coin_i = [0]
def coin(f, x0, z0, x1, z1):
    coin_i[0] = coin_i[0] % 10 + 1; n = "Coin_%d" % coin_i[0]
    st.place(n, f, x=x0, z=z0, scale=0.55, step=True); st.place(n, f + 6, x=x1, z=z1); st.place(n, f + 7, scale=0.0, step=True)

# ---------- ovoz kursori ----------
H0 = 12
e1 = N("S01", H0); GOLD = H0 + 72
c2 = e1 + 4
e2 = N("S02", c2 + 4)
c3 = e2 + 4
e3 = N("S03", c3 + 8); XPOP = c3 + 8 + 12; TOI = c3 + 8 + 36
c3b = e3 + 4
c4 = c3b + 30
e4 = N("S04", c4 + 4); FOOD = c4 + 4 + 40; GEAR = c4 + 4 + 58; ATE = c4 + 4 + 74
c5 = e4 + 6
e5 = N("S05", c5 + 4); NOTICED = c5 + 4 + 8; TOOLS = c5 + 4 + 58; SOLD = c5 + 4 + 92
c6 = e5 + 6
e6 = N("S06", c6 + 4)
c7 = e6 + 28
e7 = N("S07", c7 + 8)
c8 = max(e7, c7 + 90) + 6
e8 = N("S08", c8 + 4); NOT = c8 + 4 + 42
c9 = e8 + 6
e9 = N("S09", c9 + 4); NEEDS = [c9 + 4 + t for t in (74, 92, 114, 137, 155)]
c10 = e9 + 6
e10 = N("S10", c10 + 4); SERVE = c10 + 4 + 44; CHASE = c10 + 4 + 88
c11 = e10 + 6
e11 = N("S11", c11 + 4); SELLW = c11 + 4 + 35
GAG = e11 + 6
END = GAG + 84
S.frame_end = END

# ---------- kamera (vaqt tartibida) ----------
st.cut(1, *WIDE); st.zoom(1, c2 - 1, x=0.0, z=2.3, scale=6.85)
st.cut(c2, 0.0, 2.45, 4.8)
st.cut(c3, 0.0, 2.6, 3.9); st.zoom(TOI, TOI + 8, x=-0.05, z=2.45, scale=1.9)
st.cut(c3b, 0.0, 2.75, 2.3)
st.cut(c4, 0.05, 2.2, 6.2)
st.cut(c5, 0.0, 2.3, 6.4)
st.cut(c6, 0.4, 2.3, 6.6)
st.cut(c7, *CHART)
st.cut(c8, 0.0, 2.3, 6.4)
st.cut(c9, *CHART)
st.cut(c10, *WIDE); st.zoom(SERVE - 14, SERVE - 2, x=-0.9, z=1.85, scale=4.8)
st.cut(CHASE, *WIDE)
st.cut(c11, *WIDE)
st.cut(GAG, -1.42, 2.4, 4.0)
title_off(c3, c4); title_off(SERVE - 10, CHASE)

# ================= A. Hook: to'rt do'st, har birida $100 =================
for x in LX:
    st.caption("$100", -8, c2, z=3.93, x=x, size=0.3, color="green")
wh = st.caption("WHO WINS?", -8, H0 + 48, z=4.5, x=0.0, size=0.5, color="red")
st.sfx("ding", 1, 0.4); st.sfx("pop", 2, 0.35)
shimmer(GOLD); rb = st.sfx("rumble", GOLD - 4, 0.25); st._set_end(rb, GOLD + 30)
for F_, m, dx in ((FS, st, 0.04), (FB, bn, 0.03), (FL, ly, -0.03), (FM, mx, -0.04)):
    F_.look(GOLD + 2, dx, 0.05); m.mouth("grin", GOLD + 4)
for m in (st, bn, ly, mx): m.eyes("money", GOLD + 8); m.eyes("normal", c2)

# ================= B. Sticky xarita sotib oladi =================
for m in (st, bn, ly, mx): P(m, "stand", c2 - 1)
for m in (bn, ly, mx): go(m, c2, -8.0)
go(st, c2, 0.0); P(st, "hold", c2); FS.look(c2, 0.0, 0.0); st.mouth("grin", c2); P(st, "hold", c3 - 1); P(st, "holdbig", c3)
st.flash("-$100", c2 + 4, c3, z=3.85, x=-0.62, size=0.36, color="red")
st.sfx("chaching", c2 + 4, 0.5)
ROLL = O["FX_MapRoll"]
put(ROLL, c2 + 9, 0.45, 1.85, rot=0.35, s=0.0, y=-0.3, step=True); put(ROLL, c2 + 12, 0.45, 1.85, rot=0.35, s=1.15); put(ROLL, c2 + 15, 0.45, 1.85, rot=0.35, s=1.0)
st.sfx("pop", c2 + 10, 0.45); st.eyes("wide", c2 + 12); st.eyes("normal", c3)
st.caption("TREASURE MAP!", c2 + 14, c3, z=0.62, x=0.2, size=0.26, color="black")

# ================= C. Xarita: qizil X ... unitazda =================
MAP = O["FX_Map"]
put(MAP, c3, 0.0, 2.6, s=(0.06, 1.0, 1.0), y=-0.6, step=True)
put(MAP, c3 + 5, 0.0, 2.6, s=(1.05, 1.0, 1.0), y=-0.6); put(MAP, c3 + 8, 0.0, 2.6, s=1.0, y=-0.6)
st.sfx("drop", c3, 0.7); st.sfx("whoosh", c3 + 1, 0.4); off("FX_MapRoll", c3)
mt = st.caption("STICKY'S HOUSE", c3 + 6, c3b, z=3.13, x=0.0, size=0.14, color="black")
mt.location.y = -0.7
skey("FX_MapX", ((XPOP - 1, 0.0), (XPOP + 3, 1.3), (XPOP + 6, 1.0)))
st.sfx("pop", XPOP, 0.55); st.sfx("ding", XPOP + 1, 0.3)
st.sfx("flush", TOI, 0.75)
skey("FX_MapX", ((TOI + 8, 1.0), (TOI + 11, 1.2), (TOI + 14, 1.0)))
off("FX_Map", c3b); skey("FX_MapX", ((c3b - 1, 1.0), (c3b, 0.0)))
# ---- Sticky yuzi: jim ----
P(st, "hold", c3b); st.mouth("neutral", c3b); st.squint(c3b, 0.6); FS.brow(c3b, 0.0, -0.02)
st.blink(c3b + 16); st.prop("sweat", c3b + 6, c4 - 2, x=-0.45, z=3.05, size=0.8)
off("FX_MapRoll", c4)

# ================= D. Ben oltin qazadi =================
BX = 0.15
go(st, c4, -8.0)
on("Gold_Mine", c4); off("Gold_Mine", c5)
go(bn, c4, BX); bn.mouth("grin", c4); FB.look(c4, 0.04, -0.04); FB.brow(c4, -0.1, 0.0)
PILE = O["FX_CoinPile"]
PX = BX + 1.05
put(PILE, c4, PX, 0.0, s=(0.42, 1.0, 0.0), y=-0.2, step=True)
f = c4 + 2; k = 0; h = 0.0
while f + 6 < ATE:
    P(bn, "dig_up", f); shovel_pose(f, BX, "dig_up", step=(k == 0))
    P(bn, "dig_down", f + 5); tip = shovel_pose(f + 5, BX, "dig_down")
    st.sfx("pickaxe" if k % 3 == 1 else "dig", f + 5, 0.55)
    st.fx("dust", f + 5, tip[0], 0.25, 0.5)
    if f + 5 < FOOD:
        h = min(h + 0.16, 0.8); put(PILE, f + 7, PX, 0.0, s=(0.42, 1.0, h), y=-0.2)
        if k % 2 == 0: st.sfx("chaching", f + 7, 0.3)
    f += 12; k += 1
P(bn, "dig_down", f); P(bn, "stand", f + 4); shovel_pose(f, BX, "dig_down")
put(SHV, f + 4, BX + 0.6, 0.98, rot=0.15, s=1.0, y=-0.3)
board(c4 + 8, c5)
st.flash("GOLD +$700", c4 + 8, FOOD, z=-2.75, size=0.4, color="green", hud=True)
st.flash("FOOD -$350", FOOD, GEAR, z=-2.75, size=0.4, color="red", hud=True)
st.flash("GEAR -$200", GEAR, ATE + 8, z=-2.75, size=0.4, color="red", hud=True)
st.flash("NET +$150", ATE + 8, c5, z=-2.75, size=0.4, color="green", hud=True)
for fx_ in (c4 + 8, FOOD, GEAR, ATE + 8): st.sfx("tick", fx_, 0.8)
popin("FX_Cupcake", FOOD, x=PX - 0.05, z=1.15, s=0.7); st.sfx("pop", FOOD, 0.45)
put(PILE, FOOD + 1, PX, 0.0, s=(0.42, 1.0, h), y=-0.2); put(PILE, FOOD + 6, PX, 0.0, s=(0.42, 1.0, 0.42), y=-0.2)
off("FX_Cupcake", GEAR)
SH2 = O["FX_Shovel_2"]
put(SH2, GEAR, PX - 0.12, 1.3, rot=0.9, s=0.0, y=-0.32, step=True); put(SH2, GEAR + 3, PX - 0.12, 1.3, rot=0.9, s=0.62); put(SH2, GEAR + 6, PX - 0.12, 1.3, rot=0.9, s=0.52)
st.sfx("pop", GEAR, 0.45)
put(PILE, GEAR + 1, PX, 0.0, s=(0.42, 1.0, 0.42), y=-0.2); put(PILE, GEAR + 6, PX, 0.0, s=(0.42, 1.0, 0.16), y=-0.2)
off("FX_Shovel_2", ATE + 8)
bn.mouth("sad", ATE); FB.look(ATE, 0.05, -0.05); FB.brow(ATE, 0.2, 0.0); st.sfx("trombone", ATE + 6, 0.35)
bn.prop("sweat", ATE + 2, c5 - 2, x=-0.45, z=3.05, size=0.8)
off("FX_CoinPile", c5); off("FX_Shovel", c5)
go(bn, c5, -8.0)

# ================= E. Lily belkurak sotadi =================
on("Shop_Stand", c5, x=0.0, z=0.0)
SHX = (-1.18, -1.36, -1.54, -1.72)
for i, x in enumerate(SHX):
    put("FX_Shovel_%d" % (i + 3), c5, x, 0.98, rot=(0.07 if i % 2 else -0.06), s=1.0, y=-0.32, step=True)
go(ly, c5, 0.0); P(ly, "sell", c5); ly.mouth("smile", c5); FL.look(c5, 0.0, 0.0)
ly.prop("bulb", NOTICED, NOTICED + 34, x=0.62, z=4.22, size=0.8); st.sfx("ding", NOTICED + 2, 0.4)
ly.mouth("grin", NOTICED + 2)
GX = 1.25
go(gp, c5 + 24, 3.2); gp.move_to(GX, 0.0, c5 + 34); P(gp, "stand", c5 + 24)
st.sfx("shopbell", c5 + 34, 0.6); gp.hop(c5 + 34, 0.12, 8)
P(gp, "buy", c5 + 40); FG.look(c5 + 40, -0.05, 0.0); gp.mouth("smile", c5 + 40)
coin(c5 + 42, GX - 0.62, 1.95, 0.45, 1.75); st.sfx("chaching", c5 + 48, 0.45)
SH6 = O["FX_Shovel_6"]
put(SH6, TOOLS - 1, SHX[3], 0.98, rot=0.07, s=1.0, y=-0.32)
put(SH6, TOOLS + 6, GX - 0.55, 1.6, rot=-0.25, s=1.0, y=-0.32)
st.sfx("whoosh", TOOLS, 0.4); st.sfx("shopbell", TOOLS + 6, 0.5)
P(gp, "buy", TOOLS + 5); P(gp, "hold", TOOLS + 8)
put(SH6, TOOLS + 8, GX + 0.45, 1.25, rot=0.12, s=1.0, y=-0.32)
P(ly, "sell", TOOLS - 1); P(ly, "give", TOOLS + 2); P(ly, "sell", TOOLS + 12)
board(c5 + 40, c6)
st.flash("COST $10", c5 + 40, SOLD, z=-2.75, x=-0.85, size=0.34, color="red", hud=True, max_width=1.6)
st.flash("SELLS $30", c5 + 40, SOLD, z=-2.75, x=0.85, size=0.34, color="green", hud=True, max_width=1.7)
st.flash("+$20 EACH", SOLD, c6, z=-2.75, size=0.42, color="green", hud=True)
st.flash("BEFORE OTHER COSTS", SOLD, c6, z=-2.32, size=0.13, color="black", hud=True)
st.sfx("tick", c5 + 40, 0.8); st.sfx("chaching", SOLD, 0.5)
ly.eyes("money", SOLD); ly.eyes("normal", c6)

# ================= F. Max: suv va gazak, navbat o'sadi =================
off("Shop_Stand", c6)
for i in range(4): off("FX_Shovel_%d" % (i + 3), c6)
off("FX_Shovel_6", c6)
go(ly, c6, -8.0); go(gp, c6, -8.0); FB.brow(c6, 0.0); FG.look(c6, 0.0, 0.0)
MXX = -0.45
on("Snack_Stand", c6, x=MXX, z=0.0)
go(mx, c6, MXX); P(mx, "sell", c6); mx.mouth("grin", c6); FM.look(c6, 0.04, 0.0)
put("FX_Barrel", c6, MXX - 0.62, 0.97, s=0.62, y=-0.34, step=True)
put("FX_Cup", c6, MXX + 0.2, 1.12, s=0.8, y=-0.34, step=True)
put("FX_Cupcake", c6, MXX + 0.62, 1.12, s=0.55, y=-0.34, step=True)
st.caption("WATER $2  •  SNACKS $3", c6 + 6, e6 + 4, z=4.3, x=MXX + 0.35, size=0.26, color="black", max_width=2.6)
st.sfx("pop", c6 + 6, 0.4)
LINE = ((bn, FB, 0.85), (st, FS, 1.6), (gp, FG, 2.35))
for i, (m, F_, x) in enumerate(LINE):
    f0 = c6 + 8 + i * 9
    go(m, f0, x); P(m, "stand", f0); m.hop(f0, 0.18, 8); F_.look(f0, -0.05, 0.0); m.mouth("smile", f0)
    st.sfx("pop", f0, 0.35); st.sfx("land", f0 + 8, 0.2)
P(gp, "hold", c6 + 26)
put(SH6, c6 + 26, 2.35 + 0.45, 1.25, rot=0.12, s=1.0, y=-0.32, step=True)
put(ROLL, c6 + 17, 1.6, 1.62, rot=0.0, s=1.0, y=-0.3, step=True); P(st, "holdmap", c6 + 17)
FS.brow(c6 + 17, 0.0); st.squint(c6 + 17, 1.0); st.mouth("smile", c6 + 17)
crowd = st.sfx("crowd", c6 + 8, 0.22); st._set_end(crowd, c7)
st.sfx("clink", c6 + 14, 0.5)
P(mx, "sell", c6 + 30); P(mx, "give", c6 + 34); st.sfx("clink", c6 + 36, 0.5); st.sfx("chaching", c6 + 40, 0.4)
P(mx, "sell", c6 + 46)
P(bn, "stand", c6 + 36); P(bn, "cup", c6 + 40)
put("FX_Cup", c6 + 36, MXX + 0.2, 1.12, s=0.8)
put("FX_Cup", c6 + 40, 0.85 - 0.15, 2.45, s=0.6)
put("FX_Cup", e6 + 2, 0.85 - 0.15, 2.45, s=0.6); put("FX_Cup", e6 + 4, MXX + 0.2, 1.12, s=0.8)
P(bn, "cup", e6 + 1); P(bn, "stand", e6 + 4); bn.mouth("grin", e6 + 4)
# ---- qayta to'ldirish ----
st.flash("RESTOCK!", e6 + 4, c7, z=4.3, x=MXX + 0.35, size=0.44, color="green")
skey("FX_Barrel", ((e6 + 4, 0.62), (e6 + 7, 0.75), (e6 + 10, 0.62)))
skey("FX_Cupcake", ((e6 + 6, 0.55), (e6 + 9, 0.7), (e6 + 12, 0.55)))
st.sfx("pop", e6 + 4, 0.45); st.sfx("chaching", e6 + 10, 0.45); st.sfx("chaching", e6 + 20, 0.35)
mx.eyes("money", e6 + 10)
for n in ("Snack_Stand", "FX_Barrel", "FX_Cup", "FX_Cupcake", "FX_Shovel_6", "FX_MapRoll"): off(n, c7)
for m in ALL: go(m, c7, -8.0)
mx.eyes("normal", c7)

# ================= G. Grafik: sof natija =================
BASE, HMAX, TOPV = 0.55, 3.0, 2400.0
VALS = (-100.0, 150.0, 2400.0, 2000.0)
NAMES = ("STICKY", "BEN", "LILY", "MAX")
LBL = ("-$100", "+$150", "+$2,400", "+$2,000")
for i, v in enumerate(VALS):
    ob = O["Chart_B%d" % (i + 1)]
    hh = v / TOPV * HMAX
    if abs(hh) < 0.12: hh = 0.12 if hh > 0 else -0.12
    f0 = c7 + 6 + i * 12
    put(ob, f0, ob.location.x, BASE, s=(1.0, 1.0, 0.0), step=True)
    put(ob, f0 + 8, ob.location.x, BASE, s=(1.0, 1.0, hh))
    put(ob, c8 - 1, ob.location.x, BASE, s=(1.0, 1.0, hh)); put(ob, c8, ob.location.x, BASE, s=0.0)
    zl = BASE + hh + 0.24 if hh > 0 else BASE + hh - 0.24
    st.caption(LBL[i], f0 + 8, c8, z=zl, x=ob.location.x, size=0.17, color="red" if v < 0 else "green", max_width=0.78)
    st.caption(NAMES[i], f0, c8, z=-0.12, x=ob.location.x, size=0.17, color="black", max_width=0.78)
    st.sfx("pop", f0 + 8, 0.45)
st.flash("NET RESULT", c7 + 2, e7 - 26, z=4.25, x=70.0, size=0.42, color="black")
st.caption("FICTIONAL EXAMPLE, AFTER BASIC COSTS", c7 + 30, c8, z=-0.62, x=70.0, size=0.13, color="black", max_width=3.0)
sw = st.caption("SUPPLIERS WIN", e7 - 26, c8, z=4.25, x=70.0, size=0.42, color="green", max_width=3.2)
st.sfx("ding", e7 - 26, 0.4)

# ================= H. Har doim ham emas =================
on("Shop_Stand", c8, x=0.0, z=0.0)
for i, x in enumerate(SHX):
    put("FX_Shovel_%d" % (i + 3), c8, x, 0.98, rot=(0.07 if i % 2 else -0.06), s=1.0, y=-0.32, step=True)
go(ly, c8, 0.0); P(ly, "sell", c8); ly.mouth("smile", c8); FL.look(c8, 0.0, 0.0)
P(ly, "sell", NOT - 2); P(ly, "shrug", NOT + 2); ly.mouth("neutral", NOT + 2); FL.brow(NOT + 2, 0.15, 0.05)
st.caption("NOT ALWAYS!", NOT, c9, z=4.4, x=0.0, size=0.42, color="red")
st.sfx("pop", NOT, 0.5); st.sfx("boing", NOT + 2, 0.3)
for i in range(4): off("FX_Shovel_%d" % (i + 3), c9)
off("Shop_Stand", c9)
go(ly, c9, -8.0)

# ================= I. Oltin shov-shuvi nimalarga ehtiyoj tug'diradi =================
st.caption("A GOLD RUSH NEEDS:", c9 + 4, c10, z=4.25, x=70.0, size=0.34, color="black", max_width=3.0)
ITEMS = ("FOOD", "TRANSPORT", "TOOLS", "REPAIRS", "INFORMATION")
for i, (w, f0) in enumerate(zip(ITEMS, NEEDS)):
    z = 3.35 - i * 0.78
    c = st.caption(w, f0, c10, z=z, x=69.75, size=0.36, color="green" if i % 2 == 0 else "black", max_width=2.2)
    st.sfx("pop", f0, 0.45)
popin("FX_Cupcake", NEEDS[0], x=71.25, z=3.2, s=0.6)
put(SHV, NEEDS[2], 71.3, 1.82, rot=0.8, s=0.0, y=-0.3, step=True); put(SHV, NEEDS[2] + 3, 71.3, 1.82, rot=0.8, s=0.55); put(SHV, NEEDS[2] + 6, 71.3, 1.82, rot=0.8, s=0.45)
off("FX_Cupcake", c10); off("FX_Shovel", c10)

# ================= J. Hamma tog'ga qaraydi, Lily yozuvni o'giradi =================
SHOPX = -0.92
on("Shop_Stand", c10, x=SHOPX, z=0.0)
go(ly, c10, SHOPX); P(ly, "sell", c10); ly.mouth("smile", c10); FL.brow(c10, 0.0)
ROW = ((bn, FB, 0.42), (st, FS, 1.42))
for m, F_, x in ROW:
    go(m, c10, x); P(m, "stand", c10); m.mouth("smile", c10); F_.look(c10 + 2, -0.04, 0.05)
FL.look(c10 + 2, 0.04, 0.05)
PEAK = ((-0.1, 4.08), (0.25, 4.3), (-0.42, 3.88), (0.52, 3.85))
shimmer(c10 + 6, PEAK)
T1, T2 = O["Shop_Stand_Txt1"], O["Shop_Stand_Txt2"]
skey(T1, ((SERVE - 1, 1.0), (SERVE + 3, (0.05, 1.0, 1.0)), (SERVE + 4, 0.0)))
skey(T2, ((SERVE + 3, 0.0), (SERVE + 4, (0.05, 1.0, 1.0)), (SERVE + 8, (1.08, 1.0, 1.0)), (SERVE + 11, 1.0)))
P(ly, "sell", SERVE - 4); P(ly, "give", SERVE); P(ly, "sell", SERVE + 10)
FL.look(SERVE - 2, 0.0, -0.03); ly.mouth("grin", SERVE + 6)
st.sfx("whoosh", SERVE, 0.5); st.sfx("pop", SERVE + 4, 0.5); st.sfx("ding", SERVE + 8, 0.4)
shimmer(CHASE + 2, PEAK)
for m, F_, x in ROW: F_.look(CHASE, -0.04, 0.05)
bn.mouth("grin", CHASE); st.eyes("money", CHASE + 4); st.eyes("normal", c11)
off("Shop_Stand", c11); skey(T2, ((c11 - 1, 1.0), (c11, 1.0)))

# ================= K. Savol =================
P(st, "stand", c11 - 1); P(bn, "stand", c11 - 1); P(ly, "sell", c11 - 1)
for m, x in zip((st, bn, ly, mx), LX):
    go(m, c11, x); P(m, "stand", c11); m.mouth("smile", c11)
for F_ in (FS, FB, FL, FM): F_.look(c11, 0.0, 0.0)
P(st, "hold", c11); put(ROLL, c11, LX[0] + 0.45, 1.85, rot=0.35, s=1.0, y=-0.3, step=True)
P(bn, "hold", c11); put(SHV, c11, LX[1] + 0.45, 1.45, rot=0.05, s=1.0, y=-0.3, step=True)
P(ly, "hold", c11); put(SH6, c11, LX[2] + 0.45, 1.45, rot=0.05, s=1.0, y=-0.3, step=True)
P(mx, "holdL", c11); put("FX_Cup", c11, LX[3] - 0.45, 1.95, s=0.8, y=-0.3, step=True)
st.caption("DIG", c11 + 6, GAG, z=4.02, x=(LX[0] + LX[1]) / 2, size=0.42, color="black")
st.caption("SELL", SELLW, GAG, z=4.02, x=(LX[2] + LX[3]) / 2, size=0.42, color="green")
st.sfx("pop", c11 + 6, 0.4); st.sfx("pop", SELLW, 0.45)
st.plate(c11 + 10, 100000, -2.72, lines=2)
st.caption("DIG for GOLD", c11 + 10, 100000, z=-2.52, size=0.32, color="black", hud=True, max_width=3.2)
st.caption("or SELL the SHOVELS?", c11 + 16, 100000, z=-2.95, size=0.32, color="red", hud=True, max_width=3.2)
st.sfx("ding", c11 + 10, 0.4)

# ================= L. Yakuniy hazil: X yana yonadi =================
for n in ("FX_Shovel", "FX_Shovel_6", "FX_Cup"): off(n, GAG)
for m in (bn, ly, mx): go(m, GAG, -8.0)
off("FX_MapRoll", GAG)
P(st, "hold", GAG - 1); P(st, "holdmap", GAG); st.mouth("smile", GAG); FS.look(GAG, 0.0, -0.05)
put(MAP, GAG, LX[0], 1.88, s=0.62, y=-0.45, step=True)
skey("FX_MapX", ((GAG - 1, 0.0), (GAG, 1.0)))
GL = O["FX_MapGlow"]
skey(GL, ((GAG + 5, 0.0), (GAG + 9, 1.15), (GAG + 13, 0.9), (GAG + 17, 1.15), (GAG + 21, 0.9), (GAG + 25, 1.15), (GAG + 29, 0.95)))
st.sfx("shimmer", GAG + 5, 0.55); st.sfx("riser", GAG + 6, 0.25)
FS.look(GAG + 22, 0.0, 0.0); st.mouth("neutral", GAG + 22)
st.eyes("wide", GAG + 30); st.mouth("think", GAG + 30); FS.brow(GAG + 30, 0.15, 0.1)
st.sfx("scratch", GAG + 30, 0.8)
st.sfx("flush", GAG + 40, 0.8)
st.prop("sweat", GAG + 44, END, x=-0.45, z=3.05, size=0.8)
st.mouth("sad", GAG + 58)

# ---------- musiqa ----------
m_ = st.music("//musiqa_03_sneaky.wav", volume=0.14, fade=20, end=END + 1)
for f_, v in ((1, 0.2), (H0, 0.12), (c3b - 1, 0.12), (c3b, 0.0), (c4 - 1, 0.0), (c4 + 2, 0.12), (GAG + 29, 0.12), (GAG + 30, 0.0), (END + 1, 0.0)):
    m_.volume = v * GAIN; m_.keyframe_insert("volume", frame=f_)
for s_ in st._strips():
    if s_.type == 'SOUND' and not s_.name.startswith("Music"): s_.volume *= GAIN
for m in ALL: m.alive(1, END)
bpy.app.driver_namespace["v14_marks"] = dict(H0=H0, e1=e1, GOLD=GOLD, c2=c2, e2=e2, c3=c3, XPOP=XPOP, TOI=TOI, e3=e3, c3b=c3b, c4=c4, FOOD=FOOD, GEAR=GEAR,
    ATE=ATE, e4=e4, c5=c5, NOTICED=NOTICED, TOOLS=TOOLS, SOLD=SOLD, e5=e5, c6=c6, e6=e6, c7=c7, e7=e7, c8=c8, NOT=NOT, e8=e8, c9=c9, e9=e9,
    c10=c10, SERVE=SERVE, CHASE=CHASE, e10=e10, c11=c11, SELLW=SELLW, e11=e11, GAG=GAG, END=END)
S.frame_set(1)
