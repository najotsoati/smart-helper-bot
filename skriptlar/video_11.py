# video_11.py  -  "How a $2,000 TV Cost $4,064" (hikoyachi: Fenrir, Kokoro TTS)
import bpy, os, math, random, aud
T = bpy.data.texts["stickman_tools.py"]
st = T.as_module()                        # Sticky
rk = T.as_module(); rk.use("R_")          # Rick: do'konda sotuvchi (shlyapa), uyda Max (kepka)
S = bpy.context.scene
O = bpy.data.objects
A = "//video_11_audio/"
SX, RX = -1.0, 1.3                        # do'konda Sticky va sotuvchi
WIDE = (0.0, 2.3, 7.0)
CHART = (70.0, 2.3, 7.0)
GAIN = 1.3

st.clear_animation()
rk.clear_animation(); rk.show()
st.backdrop("room")
S.frame_end = 1800
S.render.filepath = "//How a $2,000 TV Cost $4,064.mp4"

# ---------- yordamchilar ----------
EST = {"V1": 70, "V2": 196, "V3": 207, "V4": 185, "V5": 185, "V6": 138, "V7": 80, "V8": 104}
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
    if step: keyall(ob, f - 1)
    ob.location = (x, ob.location.y if y is None else y, z); ob.rotation_euler = (0.0, rot, 0.0)
    ob.scale = (s, s, s) if isinstance(s, (int, float)) else tuple(s)
    keyall(ob, f)
def skey(ob, pairs):
    for f, s in pairs:
        ob.scale = (s, s, s) if isinstance(s, (int, float)) else tuple(s); ob.keyframe_insert("scale", frame=f)
class Face:
    def __init__(self, m): self.m = m; self.b = [0.0, 0.0, 0.0]; self.l = [0.0, 0.0]
    def brow(self, f, tilt, lift=0.0, cock=0.0):
        self.m.brows(self.b[0], self.b[1], f - 1, self.b[2]); self.m.brows(tilt, lift, f, cock); self.b[:] = [tilt, lift, cock]
    def look(self, f, dx, dz):
        self.m.look(self.l[0], self.l[1], f - 1); self.m.look(dx, dz, f); self.l[:] = [dx, dz]
FS, FR = Face(st), Face(rk)
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
def P(m, name, f):
    m.apply_pose(name, f, face=False)
for m in (st, rk):
    m.POSES["sign"] = pose(reach("L", 0.42, 1.95), reach("R", 0.2, 2.0), front="R")
    m.POSES["sign2"] = pose(reach("L", 0.42, 1.95), reach("R", 0.3, 1.92), front="R")
    m.POSES["card_up"] = pose(reach("R", -0.78, 2.75))
    m.POSES["hug"] = pose(reach("L", 0.55, 1.75), reach("R", -0.55, 1.75))
    m.POSES["drop"] = pose(reach("R", -0.5, 2.15))
    m.POSES["hold_card"] = pose(reach("L", 0.5, 2.3))

TV = O["Set_TV"]; TAG = O["FX_PriceTag"]; CARD = O["FX_Card"]; CON = O["FX_Contract"]; PEN = O["FX_Pen"]
JB, JF, JFR = O["FX_JarBack"], O["FX_JarFill"], O["FX_JarFront"]
PL = O["HUD_Plate1"]
def jar(f, x, z, fill=None, step=False, s=1.0):
    for ob, dz in ((JB, 0.0), (JFR, 0.0)):
        put(ob, f, x, z + dz, s=s, step=step)
    if fill is not None:
        put(JF, f, x, z + 0.03 * s, s=(s, s, max(fill, 0.0) * s * 0.75), step=step)
ROOM = ("Set_Floor", "Set_Door", "Set_DoorFrame")
def to_shop(f):
    for n in ROOM: off(n, f)
    on("Shop_Back", f)
def to_room(f):
    for n in ROOM: on(n, f)
    off("Shop_Back", f)
def as_max(f):
    off("R_Hat", f); off("R_Bowtie", f); on("R_Cap", f)
def as_seller(f):
    on("R_Hat", f); on("R_Bowtie", f); off("R_Cap", f)

off("Set_Calendar", 1)
to_shop(1); on("Chart_BoardPlain", 1)
as_seller(1)
T1 = st.title("HOW A $2,000 TV", f_on=-8, y=3.17, size=0.36)
T2 = st.title("COST $4,064", f_on=-8, y=2.8, size=0.44, color="red")
def title_off(f0, f1):
    for t in (T1, T2): skey(t, ((f0 - 1, 1.0), (f0, 0.0), (f1 - 1, 0.0), (f1, 1.0)))

st.move_to(SX, 0.0, 1); rk.move_to(3.4, 0.0, 1)
P(st, "stand", 1); P(rk, "stand", 1)
st.mouth("neutral", 1); rk.mouth("smile", 1)

# ---------- ovoz kursori ----------
e1 = N("V1", 8)
FLIP = e1 + 2
c2 = FLIP + 24
e2 = N("V2", c2 + 4)
c3 = e2 + 6
e3 = N("V3", c3 + 4)
c4 = e3 + 6
e4 = N("V4", c4 + 4)
c5 = e4 + 8
BRK = c5 + 50
c6 = BRK + 40
e5 = N("V5", c6 + 4)
c7 = e5 + 6
e6 = N("V6", c7 + 4)
c8 = e6 + 6
FALL = c8 + 38
e7 = N("V7", c8 + 8)
c9 = max(e7, FALL + 24) + 6
e8 = N("V8", c9 + 4)
END = e8 + 45
S.frame_end = END

# ---------- kamera (vaqt tartibida) ----------
HOOK = (-0.22, 2.5, 4.9)
st.cut(1, *HOOK); st.zoom(1, FLIP, x=-0.22, z=2.5, scale=4.65)
st.shake(FLIP + 3, FLIP + 9, 0.04)
st.cut(c2, *WIDE)
st.cut(c3, *CHART)
st.cut(c4, *WIDE)
st.cut(c5, -0.3, 2.4, 5.2); st.zoom(c5, BRK, x=-0.3, z=2.5, scale=4.4)
st.shake(BRK, BRK + 8, 0.05)
st.cut(c6, *CHART)
st.cut(c7, *WIDE)
st.cut(c8, -0.3, 2.35, 5.2)
st.shake(FALL, FALL + 8, 0.05)
st.cut(c9, *WIDE)

# ================= A. Hook: $2,000 -> $4,064 =================
TVX = 0.25
put(TV, 1, TVX, 0.0, s=1.0, y=0.3, step=True); on("TV_ScreenOn", 1, x=TVX, z=0.0)
put(TAG, 1, 0.55, 2.72, rot=0.12, s=1.0, y=-0.12, step=True)
st.caption("$2,000", -8, FLIP, z=2.73, x=0.55, size=0.2, color="black")
skey(TAG, ((FLIP - 1, (1.0, 1.0, 1.0)), (FLIP + 2, (0.0, 1.0, 1.0)), (FLIP + 5, (1.15, 1.0, 1.15)), (FLIP + 9, (1.1, 1.0, 1.1))))
st.caption("$4,064?!", FLIP + 4, c2, z=2.73, x=0.55, size=0.2, color="red")
skey(TAG, ((c2 - 1, 1.1), (c2, 0.0)))
st.sfx("drop", FLIP, 0.7); st.sfx("boom", FLIP + 3, 0.35)
st.eyes("wide", FLIP + 3); st.mouth("scream", FLIP + 3); st.punch(FLIP + 3, 0.08); FS.brow(FLIP + 3, 0.1, 0.1)
FS.look(4, 0.05, -0.02)
st.prop("exclaim", FLIP + 4, c2 - 2, x=0.55, z=3.55, size=0.65)

# ================= B. Do'konda: karta, 24%, $50/oy =================
rk.move_to(3.4, 0.0, c2); rk.move_to(RX, 0.0, c2 + 10)
P(rk, "stand", c2); P(rk, "present", c2 + 10); rk.punch(c2 + 10, 0.05)
st.sfx("whoosh", c2, 0.55); st.sfx("land", c2 + 10, 0.25)
st.eyes("normal", c2 + 2); st.mouth("smile", c2 + 2); FS.brow(c2 + 2, 0.0); FS.look(c2 + 2, 0.05, 0.0)
CK = c2 + 26
P(rk, "present", CK - 1); P(rk, "card_up", CK + 2)
popin("FX_Card", CK + 2, x=RX - 0.78, z=2.78, s=1.0); st.sfx("pop", CK + 2, 0.5)
APR = c2 + 4 + int((e2 - c2 - 4) * 0.45)
FIFTY = c2 + 4 + int((e2 - c2 - 4) * 0.8)
st.caption("24% APR", APR, c3, z=4.4, x=-0.15, size=0.46, color="red")
st.sfx("pop", APR, 0.5)
st.caption("$50/MONTH", FIFTY, c3, z=3.85, x=-0.15, size=0.34, color="green", max_width=1.75)
st.sfx("ding", FIFTY, 0.4)
SG = FIFTY + 6
popin("FX_Contract", SG, x=SX + 0.42, z=1.95, s=1.0)
on("FX_Pen", SG, x=SX + 0.2, z=1.98)
P(st, "stand", SG - 1)
for k in range(8):
    f = SG + 2 + k * 3
    P(st, "sign" if k % 2 == 0 else "sign2", f)
    st.place("FX_Pen", f, x=SX + (0.2 if k % 2 == 0 else 0.3), z=1.98 - 0.02 * (k % 2))
s_ = st.sfx("type", SG + 2, 0.6); st._set_end(s_, SG + 26)
st.eyes("money", SG + 8); st.mouth("grin", SG + 8)
popin("Prop_Crown", SG + 14, s=0.9); st.sfx("chaching", SG + 14, 0.5)
P(st, "sign2", e2 + 2); P(st, "stand", e2 + 5); P(rk, "card_up", e2 + 2); P(rk, "present", e2 + 6)
off("FX_Contract", e2 + 5); off("FX_Pen", e2 + 5); off("FX_Card", e2 + 5)
off("Prop_Crown", c3)
rk.mouth("grin", SG + 8)

# ================= C. Birinchi oy: $40 foiz, $10 televizor =================
popin("Chart_Pie", c3 + 4, s=1.0); st.sfx("pop", c3 + 4, 0.5); st.sfx("chaching", c3 + 6, 0.4)
st.caption("YOUR $50 PAYMENT", c3 + 2, c4, z=4.05, x=70.0, size=0.3, color="black", max_width=3.0)
st.caption("MONTH 1", c3 + 2, c4, z=3.6, x=70.0, size=0.24, color="black")
INT = c3 + 4 + int((e3 - c3 - 4) * 0.35)
st.caption("$40", INT, c4, z=1.85, x=69.75, size=0.5, color="white")
st.caption("INTEREST", INT + 3, c4, z=1.4, x=69.75, size=0.24, color="white")
TVP = c3 + 4 + int((e3 - c3 - 4) * 0.62)
st.caption("$10", TVP, c4, z=3.05, x=70.38, size=0.22, color="white")
st.caption("ONLY $10 PAYS FOR THE TV", TVP + 4, c4, z=0.45, x=70.0, size=0.24, color="green", max_width=3.1)
st.sfx("error", INT, 0.35); st.sfx("pop", TVP, 0.4)
off("Chart_Pie", c4)

# ================= D. Max yig'adi (uyda) =================
MX = 0.6
to_room(c4); as_max(c4)
off("TV_ScreenOn", c4); put(TV, c4, -0.75, 0.0, s=0.0, step=True)
rk.move_to(RX, 0.0, c4 - 1); rk.move_to(MX, 0.0, c4); P(rk, "stand", c4); rk.mouth("smile", c4); FR.look(c4, -0.04, -0.03)
st.move_to(SX, 0.0, c4 - 1); st.move_to(-5.0, 0.0, c4)
jar(c4, MX - 0.85, 0.0, fill=0.02, step=True)
st.plate(c4, 100000, -2.75)
for fdel in (100000, 100003):
    try: PL.keyframe_delete("scale", frame=fdel)
    except Exception: pass
M0 = c4 + 6
MSTEP = max(2, int((e4 - c4 - 40) / 40))
for mth in range(1, 41):
    f0 = M0 + (mth - 1) * MSTEP; f1 = M0 + mth * MSTEP if mth < 40 else c5
    st.flash("MONTH %d" % mth, f0, f1, z=-2.75, x=-0.85, size=0.32, color="black", hud=True, max_width=1.6)
    st.flash("$%s SAVED" % format(50 * mth, ","), f0, f1, z=-2.75, x=0.85, size=0.3, color="green", hud=True, max_width=1.6)
    if mth % 2 == 1: st.sfx("tick", f0, 0.8)
    put(JF, f0, MX - 0.85, 0.03, s=(1.0, 1.0, 0.75 * min(mth / 40.0, 1.0)))
for k in range(6):
    f = M0 + k * MSTEP * 6
    P(rk, "drop", f); P(rk, "stand", f + 4)
    st.place("Coin_%d" % (k + 1), f, x=MX - 0.5, z=2.15, scale=0.6, step=True)
    st.place("Coin_%d" % (k + 1), f + 5, x=MX - 0.85, z=0.9)
    st.place("Coin_%d" % (k + 1), f + 6, scale=0.0, step=True)
    st.sfx("chaching", f + 5, 0.3)
BUY = M0 + 40 * MSTEP + 4
put(JF, BUY, MX - 0.85, 0.03, s=(1.0, 1.0, 0.75)); put(JF, BUY + 5, MX - 0.85, 0.03, s=(1.0, 1.0, 0.02))
popin("Set_TV", BUY + 2, x=-0.75, z=0.0); on("TV_ScreenOn", BUY + 8, x=-0.75, z=0.0)
st.sfx("chaching", BUY + 2, 0.6); st.sfx("ding", BUY + 8, 0.35)
popin("FX_StampBox", BUY + 12, x=0.0, z=3.9, s=1.0)
sb = st.caption("NO INTEREST", BUY + 12, c5, z=3.9, x=0.0, size=0.34, color="red")
O["FX_StampBox"].rotation_euler.y = math.radians(-6); sb.rotation_euler.y = math.radians(-6); sb.location.y = -0.42
st.sfx("boom", BUY + 12, 0.3); st.shake(BUY + 12, BUY + 18, 0.03)
P(rk, "stand", BUY); P(rk, "cheer", BUY + 4); rk.mouth("grin", BUY + 4)
off("FX_StampBox", c5)

# ================= E. Yillar o'tadi: Stickyning televizori buziladi =================
as_seller(c5)            # Rick bu sahnada yo'q
rk.move_to(MX, 0.0, c5 - 1); rk.move_to(6.0, 0.0, c5)
jar(c5, 6.0, 0.0, fill=0.0, step=True)
SH = 0.05
st.move_to(-5.0, 0.0, c5 - 1); st.move_to(SH, 0.0, c5)
P(st, "hold_card", c5); popin("FX_Card", c5, x=SH + 0.5, z=2.3, s=0.8)
st.mouth("smile", c5); FS.look(c5, -0.05, 0.0); st.eyes("normal", c5)
skey(PL, ((BRK + 29, 1.0), (BRK + 30, 0.0)))
for yr in range(1, 6):
    f0 = c5 + 4 + (yr - 1) * 8; f1 = c5 + 4 + yr * 8 if yr < 5 else BRK + 30
    st.flash("YEAR %d" % yr, f0, f1, z=-2.75, x=-0.85, size=0.32, color="black", hud=True)
    st.flash("PAYMENT %d/82" % min(yr * 12, 82), f0, f1, z=-2.75, x=0.85, size=0.28, color="red", hud=True, max_width=1.7)
    st.sfx("tick", f0, 0.8)
    st.caption("-$50", f0 + 2, f0 + 7, z=2.75, x=SH + 0.5 + 0.08 * (yr % 2), size=0.18, color="red")
on("TV_Crack", BRK, x=-0.75, z=0.0); off("TV_ScreenOn", BRK)
st.fx("star", BRK + 1, -0.6, 2.3, 0.9); st.fx("star", BRK + 4, -1.0, 1.85, 0.7)
st.sfx("hit", BRK, 0.45); st.sfx("glitch", BRK, 0.35); st.sfx("trombone", BRK + 10, 0.5)
st.eyes("wide", BRK + 2); st.mouth("scream", BRK + 2); FS.brow(BRK + 2, 0.2, 0.08); st.punch(BRK + 2, 0.06)
st.caption("STILL PAYING...", BRK + 14, c6, z=3.68, x=-0.3, size=0.3, color="red")
off("FX_Card", c6)

# ================= F. 82 ta to'lov =================
on("Chart_Grid", c6)
st.caption("82 PAYMENTS", c6 + 2, c7, z=4.25, x=70.0, size=0.36, color="black")
R0 = c6 + 8; RST = max(6, int((e5 - c6 - 30) / 12))
for r in range(12):
    ob = O["Chart_Row_%02d" % (r + 1)]
    f = R0 + r * RST
    ob.scale = (0.0, 1.0, 1.0); ob.keyframe_insert("scale", frame=f - 1)
    ob.scale = (1.0, 1.0, 1.0); ob.keyframe_insert("scale", frame=f + 4)
    ob.keyframe_insert("scale", frame=c7 - 1); ob.scale = (0.0, 0.0, 0.0); ob.keyframe_insert("scale", frame=c7)
    st.sfx("tick", f, 0.8)
    paid = min(50.0 * 7 * (r + 1), 4063.80)
    st.flash("PAID $%s" % format(paid, ",.2f") if r == 11 else "PAID $%s" % format(int(paid), ","), f + 2,
             (R0 + (r + 1) * RST + 2) if r < 11 else c7, z=-0.35, x=70.0, size=0.3, color="red", max_width=3.0)
DONE = R0 + 12 * RST
st.caption("INTEREST: $2,063.80", DONE + 4, c7, z=-0.68, x=70.0, size=0.24, color="black", max_width=3.0)
st.sfx("boom", DONE + 4, 0.3)
off("Chart_Grid", c7)

# ================= G. Max: televizor ishlaydi, yana yig'adi =================
as_max(c7)
st.move_to(SH, 0.0, c7 - 1); st.move_to(-5.0, 0.0, c7)
off("TV_Crack", c7); on("TV_ScreenOn", c7, x=-0.75, z=0.0)
rk.move_to(6.0, 0.0, c7 - 1); rk.move_to(MX, 0.0, c7); P(rk, "present", c7); rk.mouth("smile", c7); rk.eyes("normal", c7); FR.look(c7, 0.0, 0.0)
jar(c7, MX - 0.85, 0.0, fill=0.05, step=True)
put(JF, c7 + 10, MX - 0.85, 0.03, s=(1.0, 1.0, 0.05)); put(JF, e6 - 10, MX - 0.85, 0.03, s=(1.0, 1.0, 0.62))
st.caption("+$2,100 SAVED", c7 + 30, c8, z=4.2, x=0.2, size=0.4, color="green")
st.sfx("chaching", c7 + 30, 0.5); st.sfx("ding", c7 + 31, 0.3)

# ================= H. "To'lov rejasi" - televizor qo'lida parchalanadi =================
as_seller(c8)
rk.move_to(MX, 0.0, c8 - 1); rk.move_to(6.0, 0.0, c8)
jar(c8, 6.0, 0.0, fill=0.0, step=True)
st.move_to(-5.0, 0.0, c8 - 1); st.move_to(-0.3, 0.0, c8)
P(st, "hug", c8); st.mouth("sad", c8); st.eyes("normal", c8); FS.brow(c8, 0.2, 0.0); FS.look(c8, 0.0, 0.0)
off("TV_ScreenOn", c8)
put(TV, c8, -0.3, 0.45, s=0.75, y=-0.2, step=True); put(O["TV_Crack"], c8, -0.3, 0.45, s=0.75, y=-0.24, step=True)
st.caption("PAYMENT PLAN?", c8 + 6, FALL, z=3.78, x=-0.3, size=0.34, color="black")
st.mouth("smile", c8 + 10)
put(TV, FALL - 1, -0.3, 0.45, s=0.75); put(TV, FALL + 2, -0.3, 0.3, s=(0.85, 0.75, 0.2)); put(TV, FALL + 3, -0.3, 0.3, s=0.0)
off("TV_Crack", FALL + 1)
put(O["FX_Debris"], FALL, -0.3, 1.3, s=1.0, step=True); put(O["FX_Debris"], FALL + 10, -0.3, 0.05, rot=0.3, s=1.0)
st.fx("dust", FALL + 3, -0.6, 0.2, 1.0); st.fx("dust", FALL + 4, 0.0, 0.2, 0.9)
st.sfx("boom", FALL, 0.35); st.sfx("hit", FALL, 0.4); st.sfx("splat", FALL + 2, 0.3); st.sfx("trombone", FALL + 12, 0.45)
P(st, "hug", FALL - 1); P(st, "shock", FALL + 2); st.mouth("scream", FALL + 2); st.eyes("wide", FALL + 2)

# ================= I. Savol =================
as_max(c9)
put(O["FX_Debris"], c9, -0.9, 0.0, s=1.0, step=True)
st.move_to(-0.3, 0.0, c9 - 1); st.move_to(-0.95, 0.0, c9); P(st, "slump", c9); st.mouth("sad", c9); st.eyes("normal", c9)
rk.move_to(6.0, 0.0, c9 - 1); rk.move_to(0.95, 0.0, c9); P(rk, "present", c9); rk.mouth("smile", c9)
jar(c9, 0.2, 0.0, fill=0.62, step=True)
st.plate(c9 + 6, 100000, -2.72, lines=2)
st.caption("WAIT AND SAVE,", c9 + 6, 100000, z=-2.52, size=0.3, color="green", hud=True, max_width=3.2)
st.caption("OR PAY INTEREST?", c9 + 12, 100000, z=-2.95, size=0.36, color="red", hud=True, max_width=3.2)
st.sfx("ding", c9 + 6, 0.4); st.sfx("pop", c9 + 12, 0.4)

# ---------- musiqa ----------
m = st.music("//musiqa_03_sneaky.wav", volume=0.16, fade=25, end=END + 1)
for f, v in ((1, 0.2), (12, 0.1), (FLIP, 0.1), (FLIP + 1, 0.0), (FLIP + 14, 0.0), (FLIP + 18, 0.12), (BRK - 1, 0.12), (BRK, 0.0), (BRK + 30, 0.0),
             (c6, 0.12), (FALL - 1, 0.12), (FALL, 0.0), (FALL + 20, 0.0), (c9, 0.12), (END - 24, 0.12), (END + 1, 0.0)):
    m.volume = v * GAIN; m.keyframe_insert("volume", frame=f)
for s_ in st._strips():
    if s_.type == 'SOUND' and not s_.name.startswith("Music"): s_.volume *= GAIN

st.alive(1, END, blink_skip=[(FLIP, c2 + 4), (SG + 6, e2 + 8), (BRK - 5, c6 + 5), (FALL - 5, c9 + 5)])
rk.alive(c2, END, blink_skip=[(BUY, c5)])
bpy.app.driver_namespace["v11_marks"] = dict(e1=e1, FLIP=FLIP, c2=c2, e2=e2, c3=c3, e3=e3, c4=c4, e4=e4, c5=c5, BRK=BRK, c6=c6, e5=e5,
                                              c7=c7, e6=e6, c8=c8, FALL=FALL, e7=e7, c9=c9, e8=e8, END=END)
S.frame_set(1)
