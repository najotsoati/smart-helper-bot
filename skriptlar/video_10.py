# video_10.py  -  "$1,000,000 or One Penny That Doubles?" (hikoyachi: Fenrir, Kokoro TTS)
import bpy, os, math, random, aud
T = bpy.data.texts["stickman_tools.py"]
st = T.as_module()                        # Sticky
mx = T.as_module(); mx.use("R_")          # Max (Rick qo'g'irchog'i: ko'k kepka, shlyapasiz)
S = bpy.context.scene
O = bpy.data.objects
A = "//video_10_audio/"
SX, MX = -0.85, 0.85                      # Sticky va Max turadigan joy
WIDE = (0.0, 2.3, 7.0)
TWO = (-0.12, 2.45, 6.3)                    # ikkalasi, biroz yaqin
MAXM = (MX - 0.02, 2.55, 4.4)             # Max o'rta plan
STKM = (SX + 0.1, 2.45, 4.4)              # Sticky o'rta plan (taxtda)
ECU = (SX, 2.72, 2.2)                     # Sticky yuzi juda yaqin (taxtda)
CHART = (70.0, 2.3, 7.0)
GAIN = 1.3

st.clear_animation()
mx.clear_animation(); mx.show()
st.backdrop("room")
S.frame_end = 1700
S.render.filepath = "//$1,000,000 or One Penny That Doubles.mp4"

# ---------- yordamchilar ----------
EST = {"N01": 196, "N02": 46, "N03": 46, "N04": 115, "N05": 58, "N06": 104, "N07": 69, "N08": 50,
       "N09": 58, "N10": 127, "N11": 69, "N12": 104, "N13": 138}
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
    """Qosh va nigohni oldingi qiymatni ushlab o'zgartiradi."""
    def __init__(self, m): self.m = m; self.b = [0.0, 0.0, 0.0]; self.l = [0.0, 0.0]
    def brow(self, f, tilt, lift=0.0, cock=0.0):
        self.m.brows(self.b[0], self.b[1], f - 1, self.b[2]); self.m.brows(tilt, lift, f, cock); self.b[:] = [tilt, lift, cock]
    def look(self, f, dx, dz):
        self.m.look(self.l[0], self.l[1], f - 1); self.m.look(dx, dz, f); self.l[:] = [dx, dz]
FS, FM = Face(st), Face(mx)
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

SIT_LEGS = {"thigh.L": -48, "shin.L": -88, "thigh.R": -132, "shin.R": -92}
GROUND_LEGS = {"thigh.L": -35, "shin.L": -82, "thigh.R": -145, "shin.R": -98}
for m in (st, mx):
    m.POSES["hug"] = pose(reach("L", 0.5, 1.72), reach("R", -0.5, 1.72))
    m.POSES["laugh"] = pose(reach("L", 0.17, 1.78), reach("R", -0.17, 1.78), head=102)
    m.POSES["throne"] = pose(reach("L", 0.8, 1.82), reach("R", -0.8, 1.82), SIT_LEGS)
    m.POSES["throne_cup"] = pose(reach("L", 0.98, 2.38), reach("R", -0.8, 1.82), SIT_LEGS)
    m.POSES["throne_point"] = pose({"upper_arm.L": 18, "forearm.L": 12}, reach("R", -0.8, 1.82), SIT_LEGS)
    m.POSES["throne_scared"] = pose(reach("L", 0.32, 2.75), reach("R", -0.32, 2.75), SIT_LEGS)
    m.POSES["ground"] = pose(reach("L", 0.62, 1.42), reach("R", -0.62, 1.42), GROUND_LEGS)
    m.POSES["ground_laugh"] = pose(reach("L", 0.17, 1.78), reach("R", -0.17, 1.78), GROUND_LEGS, head=100)
    m.POSES["fry"] = pose(reach("L", 0.62, 2.55), reach("R", -0.62, 1.42), GROUND_LEGS)
    m.POSES["hold"] = pose(reach("R", -0.42, 2.55))
    m.POSES["lean"] = pose(reach("L", 0.3, 1.9), reach("R", -0.3, 1.9), head=104, root=104)
SIT_Z, GROUND_Z = -0.2, -0.85

CASE = O["FX_Suitcase"]; PEN = O["FX_Penny"]; BILL = O["FX_BigBill"]; THR = O["Set_Throne"]
PILE = O["FX_CoinPile"]; CF1, CF2 = O["FX_Confetti"], O["FX_Confetti2"]
BARS, BARM = O["Chart_BarS"], O["Chart_BarM"]
MASK, DOT = O["Chart_Mask"], O["Chart_Dot"]
PL = O["HUD_Plate1"]

# ---------- sahna: tepalik, xona yashirin ----------
for n in ("Set_Floor", "Set_Door", "Set_DoorFrame", "Set_Calendar"): off(n, 1)
on("Hill_Back", 1); on("Chart_Board", 1)
for n in ("R_Hat", "R_Bowtie"): off(n, 1)
on("R_Cap", 1)
TITLE = st.title("$1,000,000 OR 1¢?", f_on=-8)
def title_off(f0, f1):
    skey(TITLE, ((f0 - 1, 1.0), (f0, 0.0), (f1 - 1, 0.0), (f1, 1.0)))

st.move_to(-3.3, 0.0, 1); mx.move_to(3.3, 0.0, 1)
P(st, "stand", 1); P(mx, "stand", 1)
st.mouth("neutral", 1); mx.mouth("neutral", 1)

# ---------- ovoz kursori: barcha kadr belgilarini oldindan hisoblaymiz ----------
e1 = N("N01", 8)
DBL = 8 + int((e1 - 8) * 0.55)                     # "doubles" so'zi taxminan
D30 = 8 + int((e1 - 8) * 0.85)                     # "thirty days"
c2 = e1 + 12
e2 = N("N02", c2 + 4)
c3 = max(e2, c2 + 30) + 4
e3 = N("N03", c3 + 4)
PK = max(e3, c3 + 26) + 2
L0 = PK + 8
c4 = L0 + 58
T10 = c4 + 27
e4 = N("N04", c4 + 20)
c5 = e4 + 6
e5 = N("N05", c5 + 4)
J = max(e5, c5 + 40) + 2
c6 = J + 32
T20 = c6 + 27
e6 = N("N06", c6 + 14)
c7 = e6 + 4
e7 = N("N07", c7 + 2)
c8 = e7 + 6
T28 = c8 + 42
e8 = N("N08", c8 + 4)
c9 = max(e8, T28 + 8) + 2
PASS = c9 + 22
e9 = N("N09", c9 + 4)
JAW = max(e9, PASS + 20) + 4
c10 = JAW + 30
T30 = c10 + 20
e10 = N("N10", c10 + 4)
c11 = e10 + 4
e11 = N("N11", c11 + 2)
IMP = c11 + 26
c12 = max(e11, IMP + 36) + 8
e12 = N("N12", c12 + 4)
R0, R1 = c12 + 4, max(e12, c12 + 90)
HUGE = R0 + int((R1 - R0) * 0.9)
c13 = R1 + 12
c14 = c13 + 70
e13 = N("N13", c14 + 4)
END = e13 + 45
S.frame_end = END

# ---------- kamera (vaqt tartibida) ----------
st.cut(1, 0.0, 2.0, 6.0); st.zoom(1, e1, x=0.0, z=2.0, scale=5.7)
st.cut(c2, *WIDE)
st.cut(c4, *MAXM)
st.cut(c5, *WIDE)
st.cut(c6, -0.12, 2.45, 6.6); st.zoom(c6, c7 - 1, x=-0.12, z=2.45, scale=6.3)
st.cut(c7, *WIDE)
st.cut(c8, *STKM); st.zoom(c8, c8 + 50, x=SX, z=2.65, scale=3.6)
st.cut(c9, *CHART)
st.cut(JAW, *ECU); st.shake(JAW, JAW + 6, 0.025)
st.cut(c10, *WIDE)
st.cut(c11, *TWO); st.cut(IMP + 2, SX + 0.05, 1.35, 4.1); st.shake(IMP + 2, IMP + 10, 0.06)
st.cut(c12, *CHART)
st.cut(c13, SX + 0.36, 1.95, 3.6)
st.cut(c14, *WIDE)
title_off(JAW, c10); title_off(IMP + 2, c12)

# ================= A. Hook: chamadon yoki bitta tanga =================
put(CASE, 1, -0.8, 0.5, s=0.85, y=-0.18, step=True)
put(PEN, 1, 0.85, 2.0, s=1.3, y=-0.2, step=True)
st.sfx("boom", 1, 0.35); st.sfx("ding", 1, 0.5)
st.caption("$1,000,000", -8, c2 + 14, z=2.0, x=-0.8, size=0.34, color="green", max_width=1.4)
st.caption("OR", -8, c2 + 2, z=1.15, x=0.08, size=0.45, color="red")
st.caption("× 2 EVERY DAY", DBL, c3 + 12, z=3.02, x=0.72, size=0.27, color="red", max_width=1.32)
st.caption("FOR 30 DAYS", D30, c3 + 12, z=2.7, x=0.72, size=0.24, color="black", max_width=1.32)
skey(PEN, ((DBL - 1, 1.3), (DBL + 3, 1.55), (DBL + 7, 1.3)))
st.sfx("pop", DBL, 0.5); st.sfx("tick", D30, 0.9)

# ================= B. Sticky millionni oldi =================
P(st, "stand", c2)
st.move_to(-3.3, 0.0, c2); st.move_to(-2.0, 0.55, c2 + 5); st.move_to(SX, 0.0, c2 + 10)
P(st, "cheer", c2 + 2); st.punch(c2 + 10); st.sfx("whoosh", c2, 0.6); st.sfx("land", c2 + 10, 0.3)
st.fx("dust", c2 + 10, SX, 0.1, 0.7)
P(st, "cheer", c2 + 11); P(st, "hug", c2 + 15)
put(CASE, c2 + 12, -0.8, 0.5, s=0.85); put(CASE, c2 + 16, SX, 1.3, s=0.75, y=-0.2)
st.eyes("money", c2 + 16); st.mouth("grin", c2 + 16)
popin("Prop_Crown", c2 + 20); st.sfx("chaching", c2 + 20, 0.6); st.sfx("ding", c2 + 21, 0.35)
for i, (dx, dz) in enumerate(((-0.45, 3.7), (0.45, 3.9))):
    gn = "FX_Gold_%d" % (i + 1)
    st.place(gn, c2 + 20 + i * 3, x=SX + dx, z=dz, scale=0.0, step=True); st.place(gn, c2 + 23 + i * 3, scale=0.55)
    st.place(gn, c2 + 26 + i * 3, scale=0.4); st.place(gn, c2 + 31 + i * 3, scale=0.0)

# ================= C. Max tangani oldi =================
P(mx, "stand", c3)
mx.move_to(3.3, 0.0, c3); mx.move_to(2.1, 0.5, c3 + 5); mx.move_to(MX, 0.0, c3 + 10)
mx.punch(c3 + 10); st.sfx("whoosh", c3, 0.5); st.sfx("land", c3 + 10, 0.25)
st.fx("dust", c3 + 10, MX, 0.1, 0.6)
P(mx, "stand", c3 + 11); P(mx, "hold", c3 + 15)
put(PEN, c3 + 12, 0.85, 2.0, s=1.3); put(PEN, c3 + 17, MX - 0.42, 2.6, s=0.55)
st.sfx("pop", c3 + 17, 0.5); mx.mouth("smile", c3 + 17); FM.look(c3 + 17, -0.04, -0.01)
P(mx, "hold", PK); P(mx, "shrug", PK + 6); P(mx, "shrug", PK + 18); P(mx, "stand", PK + 24)
put(PEN, PK, MX - 0.42, 2.6, s=0.55); put(PEN, PK + 5, MX - 0.15, 1.45, s=0.3); put(PEN, PK + 7, MX - 0.15, 1.45, s=0.0)
st.sfx("drop", PK + 5, 0.6); FM.look(PK + 6, 0.0, 0.0)

# ================= D. Sticky kulib yiqiladi =================
P(st, "hug", L0 - 1); P(st, "laugh", L0 + 2)
st.eyes("normal", L0 + 2); st.squint(L0 + 2, 0.15); st.mouth("wide", L0 + 2); FS.brow(L0 + 2, -0.1, 0.05)
put(CASE, L0, SX, 1.3, s=0.75); put(CASE, L0 + 4, SX + 0.75, 0.0, rot=0.2, s=0.7); put(CASE, L0 + 6, SX + 0.75, 0.0, rot=0.0, s=0.7)
st.sfx("drop", L0 + 4, 0.6)
st.shiver(L0 + 4, L0 + 28, 0.03)
for k, (hx, hz) in enumerate(((SX - 0.6, 3.7), (SX + 0.6, 3.95), (SX - 0.1, 4.35))):
    st.caption("HA!", L0 + 4 + k * 8, L0 + 50, z=hz, x=hx, size=0.32, color="black")
    st.sfx("pop", L0 + 4 + k * 8, 0.35)
P(st, "laugh", L0 + 28); P(st, "lean", L0 + 32)
st.move_to(SX, 0.0, L0 + 30); st.move_to(SX, GROUND_Z, L0 + 36)
P(st, "ground_laugh", L0 + 36); st.punch(L0 + 36, 0.1)
st.sfx("whoosh", L0 + 30, 0.45); st.sfx("land", L0 + 36, 0.32); st.fx("dust", L0 + 36, SX, 0.15, 0.8)
st.shiver(L0 + 38, L0 + 56, 0.025)
mx.squint(L0 + 10, 0.6); mx.mouth("neutral", L0 + 10)

# ================= E..K kunlar hisoblagichi (pastki taxta) =================
VALS = [0.01 * 2 ** (d - 1) for d in range(1, 31)]
def money(d):
    v = VALS[d - 1]
    return ("$%.2f" % v) if v < 1000 else "$" + format(v, ",.2f")
def tick(d, f0, f1):
    st.flash("DAY %d" % d, f0, f1, z=-2.75, x=-0.95, size=0.34, color="red", hud=True, max_width=1.4)
    st.flash(money(d), f0, f1, z=-2.75, x=0.72, size=0.36, color="green", hud=True, max_width=1.9)
    st.sfx("tick", f0, 0.9)
st.plate(c4, 100000, -2.75)
skey(PL, ((c9 - 1, 1.0), (c9, 0.0), (c10 - 1, 0.0), (c10, 1.0), (c11 - 1, 1.0), (c11, 0.0)))
for fdel in (100000, 100003):
    try: PL.keyframe_delete("scale", frame=fdel)
    except Exception: pass
for d in range(1, 10): tick(d, c4 + 3 * (d - 1), c4 + 3 * d)
tick(10, T10, c6)
for d in range(11, 20): tick(d, c6 + 3 * (d - 11), c6 + 3 * (d - 10))
tick(20, T20, c8)
for d in range(21, 28): tick(d, c8 + 6 * (d - 21), c8 + 6 * (d - 20))
tick(28, T28, c9)
tick(29, c10 + 2, T30)
tick(30, T30, c11)

# ================= E. 10-kun: $5.12 =================
P(st, "ground_laugh", c4 - 3); P(st, "ground", c4 - 1); st.squint(c4, 1.0); st.mouth("grin", c4); FS.brow(c4, 0.0)
mx.squint(c4, 1.0); FM.look(c4 + 2, 0.0, -0.05); mx.mouth("smile", T10)

# ================= F. Taxt =================
popin("Set_Throne", c5 + 2); st.sfx("pop", c5 + 2, 0.6); st.sfx("chaching", c5 + 3, 0.6)
put(CASE, c5 + 1, SX + 0.75, 0.0, s=0.7); put(CASE, c5 + 4, SX + 0.75, 0.2, s=0.0); st.fx("dust", c5 + 3, SX + 0.75, 0.3, 0.8)
st.move_to(SX, GROUND_Z, c5 + 2); st.move_to(SX, 0.45, c5 + 7); st.move_to(SX, SIT_Z, c5 + 11)
P(st, "ground", c5 + 2); P(st, "cheer", c5 + 6); P(st, "throne", c5 + 11)
st.punch(c5 + 11, 0.06); st.sfx("jump", c5 + 3, 0.4); st.sfx("land", c5 + 11, 0.3)
st.mouth("grin", c5 + 11)
FM.look(c5 + 4, -0.05, 0.0); mx.mouth("neutral", c5 + 6)
P(st, "throne", J - 1); P(st, "throne_point", J + 2); st.mouth("wide", J + 6)
popin("R_Prop_Crown", J + 6, s=0.45); st.sfx("pop", J + 6, 0.5); st.sfx("ding", J + 7, 0.3)
mx.squint(J + 10, 0.55); FM.look(J + 10, 0.0, 0.05); mx.mouth("sad", J + 10)
P(st, "throne", J + 26); st.mouth("grin", J + 26)

# ================= G. 20-kun: $5,242.88 =================
mx.squint(c6 + 2, 1.0); mx.mouth("smile", T20); FM.look(c6 + 2, 0.0, -0.05)

# ================= H. "Achinish ziyofati" =================
P(st, "throne", c7 - 1); P(st, "throne_cup", c7 + 4)
popin("FX_Cupcake", c7 + 5, x=SX + 0.98, z=2.12, s=0.9)
st.sfx("pop", c7 + 8, 0.7); st.sfx("whoosh", c7 + 8, 0.35)
for ob, f0 in ((CF1, c7 + 8), (CF2, c7 + 14)):
    put(ob, f0, MX - 0.05, 3.4, rot=0.0, s=0.4, y=ob.location.y, step=True)
    put(ob, f0 + 4, MX - 0.02, 3.3, rot=0.05, s=1.05)
    put(ob, f0 + 22, MX + 0.05, 2.0, rot=0.12, s=1.0); put(ob, f0 + 44, MX - 0.05, -0.6, rot=-0.08, s=1.0)
    put(ob, f0 + 45, MX - 0.05, -0.6, s=0.0)
st.mouth("smile", c7 + 4); FS.brow(c7 + 4, 0.2, 0.03)
mx.squint(c7 + 10, 0.5); mx.mouth("neutral", c7 + 10); FM.look(c7 + 10, -0.04, 0.0)

# ================= I. 28-kun keldi =================
off("FX_Cupcake", c8)
P(st, "throne_cup", c8 - 1); P(st, "throne", c8 + 2)
st.sfx("riser2", T28 - 50, 0.6)
st.mouth("smile", c8 + 12); st.mouth("neutral", c8 + 26); st.mouth("sad", T28)
FS.brow(c8 + 26, 0.25, 0.04); st.prop("sweat", T28 - 6, c10 + 40, x=-0.45, z=3.05, size=0.8)
FS.look(c8 + 6, 0.05, 0.0)
mx.squint(c8, 1.0); mx.mouth("grin", c8)

# ================= J. Grafik: tanga milliondan o'tdi =================
on("Chart_Line", c9)
put(BARS, c9, 69.3, -0.38, s=(1.0, 1.0, 2.2), step=True); put(BARS, c9 + 40, 69.3, -0.38, s=(1.0, 1.0, 1.5))
put(BARM, c9, 70.7, -0.38, s=(1.0, 1.0, 1.48), step=True)
put(BARM, PASS - 6, 70.7, -0.38, s=(1.0, 1.0, 1.48)); put(BARM, PASS + 2, 70.7, -0.38, s=(1.0, 1.0, 3.15)); put(BARM, PASS + 6, 70.7, -0.38, s=(1.0, 1.0, 2.95))
st.caption("STICKY", c9 + 2, c10, z=-0.66, x=69.3, size=0.24, color="black")
st.caption("MAX", c9 + 2, c10, z=-0.66, x=70.7, size=0.26, color="black")
st.caption("$1,000,000", c9 + 2, c10, z=2.05, x=69.3, size=0.19, color="red", max_width=1.2)
st.caption("DAY 28", c9 + 2, c10, z=4.22, x=69.25, size=0.26, color="black")
st.caption("$1,342,177", PASS + 2, c10, z=2.85, x=70.7, size=0.2, color="green", max_width=1.25)
pz = st.caption("PASSED!", PASS + 3, c10, z=3.45, x=70.55, size=0.4, color="red")
pz.rotation_euler.y = math.radians(8)
st.sfx("pop", c9 + 2, 0.5); st.sfx("whoosh", PASS - 4, 0.5); st.sfx("boom", PASS + 2, 0.35); st.sfx("pop", PASS + 3, 0.5)
# ---- Sticky jag'i tushadi (musiqa to'xtaydi) ----
P(st, "throne", JAW - 1); P(st, "throne_scared", JAW)
st.mouth("scream", JAW); st.eyes("wide", JAW); FS.brow(JAW, 0.15, 0.1); FS.look(JAW, 0.0, 0.0)
st.punch(JAW, 0.05); st.sfx("scratch", JAW, 0.8)

# ================= K. 30-kun: $5,368,709.12 =================
off("Chart_Line", c10); off("Chart_BarS", c10); off("Chart_BarM", c10)
P(mx, "stand", T30 - 1); P(mx, "cheer", T30 + 3); mx.eyes("money", T30); mx.mouth("grin", T30)
mx.bounce(T30 + 3, height=0.25, length=12, sound=0.4)
PILE.location = (MX, -0.25, 0.0)
PILE.keyframe_insert("location", frame=T30 - 1)
skey(PILE, ((T30 - 1, (0.85, 1.0, 0.0)), (T30 + 8, (0.85, 1.0, 0.0)), (T30 + 30, (0.85, 1.0, 1.05)), (T30 + 36, (0.85, 1.0, 1.0))))
rnd = random.Random(30)
for i in range(1, 11):
    f0 = T30 + 2 + (i - 1) * 3; x = MX + rnd.uniform(-0.75, 0.75)
    st.place("Coin_%d" % i, f0, x=x, z=6.1, scale=0.8, step=True)
    st.place("Coin_%d" % i, f0 + 20, x=x, z=1.2 + rnd.uniform(0.0, 0.6))
    st.place("Coin_%d" % i, f0 + 21, scale=0.0, step=True)
for i in range(1, 4):
    f0 = T30 + 6 + i * 5; x = MX + rnd.uniform(-0.6, 0.6)
    st.place("Note_%d" % i, f0, x=x, z=6.0, scale=0.9, step=True)
    st.place("Note_%d" % i, f0 + 26, x=x + 0.2, z=1.6)
    st.place("Note_%d" % i, f0 + 27, scale=0.0, step=True)
for k in range(3): st.sfx("chaching", T30 + 4 + k * 12, 0.55)
st.sfx("ding", T30, 0.4)
P(st, "throne_scared", c10 + 2); FS.look(T30, 0.05, 0.0)

# ================= L. Taxt qulaydi =================
FS.look(IMP - 12, 0.0, 0.06); st.mouth("scream", IMP - 8)
put(BILL, IMP - 10, SX, 7.6, rot=0.1, s=1.0, y=-0.3, step=True)
put(BILL, IMP, SX, 2.2, rot=0.06, s=1.0); put(BILL, IMP + 2, SX - 0.05, 0.9, rot=0.02, s=(1.0, 1.0, 0.6)); put(BILL, IMP + 3, SX - 0.05, 0.9, rot=0.02, s=(1.0, 1.0, 0.3), y=0.3)
st.sfx("fall", IMP - 10, 0.3); st.sfx("whoosh", IMP - 6, 0.5)
st.sfx("boom", IMP, 0.4); st.sfx("hit", IMP, 0.45); st.sfx("splat", IMP + 1, 0.35)
FLAT = st.flatten(IMP + 1, hold=26)
st.move_to(SX, SIT_Z, IMP); st.move_to(SX, 0.0, IMP + 1); st.move_to(SX, 0.0, FLAT - 3); st.move_to(SX, GROUND_Z, FLAT)
P(st, "throne_scared", IMP); P(st, "stand", IMP + 1); P(st, "stand", FLAT - 3); P(st, "ground", FLAT)
THR.keyframe_insert("scale", frame=IMP)
THR.scale = (1.1, 1.0, 0.3); THR.keyframe_insert("scale", frame=IMP + 3)
st.fx("dust", IMP + 3, SX - 0.4, 0.2, 1.0); st.fx("dust", IMP + 4, SX + 0.4, 0.2, 0.9)
st.sfx("trombone", IMP + 16, 0.5)
st.eyes("normal", FLAT); st.squint(FLAT, 0.5); st.mouth("sad", FLAT); FS.look(FLAT, 0.0, 0.0); FS.brow(FLAT, 0.2, 0.0)
st.fx("star", FLAT + 2, SX + 0.42, 2.75, 1.0); st.sfx("pop", FLAT, 0.3)
mx.mouth("open", IMP + 2); FM.look(IMP + 2, -0.05, -0.03)

# ================= M. Eksponensial o'sish grafigi =================
on("Chart_Curve", c12); on("Chart_Dot", c12)
MASK.location = (71.62, 0.36, 0.0)
MASK.keyframe_insert("location", frame=c12 - 1)
on("Chart_Mask", c12)
def curve_z(x):
    t = min(max((x - 68.62) / 2.9, 0.0), 1.0)
    return -0.36 + 4.45 * (2 ** (29 * t) - 1) / (2 ** 29 - 1)
for f in range(R0, R1 + 1, 2):
    p = (f - R0) / float(R1 - R0)
    sx_ = max(1.0 - p, 0.0)
    MASK.scale = (sx_, 1.0, 1.0); MASK.keyframe_insert("scale", frame=f)
    xe = max(min(71.62 - 3.0 * sx_, 71.52), 68.62)
    DOT.location = (xe, 0.34, curve_z(xe)); DOT.keyframe_insert("location", frame=f)
st.caption("DAY 1", c12 + 2, c13, z=-0.66, x=68.85, size=0.2, color="black")
st.caption("DAY 30", c12 + 2, c13, z=-0.66, x=71.3, size=0.2, color="black")
st.caption("SLOW...", c12 + 20, c13, z=0.3, x=69.6, size=0.32, color="black")
st.caption("...THEN HUGE!", HUGE, c13, z=3.35, x=70.25, size=0.34, color="red", max_width=1.75)
st.caption("ILLUSTRATION ONLY\nREAL INVESTMENTS DON'T DOUBLE DAILY", c12 + 30, c13, z=2.2, x=70.0, size=0.16, color="black", max_width=2.75)
st.sfx("riser2", HUGE - 45, 0.5); st.sfx("whoosh", HUGE - 2, 0.6); st.sfx("pop", HUGE, 0.5)

# ================= N. Kartoshka fri (hazil) =================
P(st, "ground", c13 - 1); P(st, "fry", c13)
st.squint(c13, 1.0); st.mouth("neutral", c13); FS.brow(c13, 0.1, 0.0)
on("FX_Fry", c13, x=SX + 0.62, z=1.67); off("FX_BigBill", c13)
FS.look(c13 + 4, 0.04, -0.02)
st.caption("×2?", c13 + 14, c13 + 44, z=2.5, x=SX + 0.9, size=0.3, color="red")
st.sfx("pop", c13 + 14, 0.35); st.sfx("pop", c13 + 44, 0.2)
st.blink(c13 + 50); st.mouth("sad", c13 + 52)

# ================= O. Savol =================
off("FX_Fry", c14)
st.move_to(SX, GROUND_Z, c14 - 1); st.move_to(SX, 0.0, c14)
P(st, "fry", c14 - 1); P(st, "hug", c14); st.mouth("smile", c14); FS.brow(c14, 0.0); FS.look(c14, 0.0, 0.0)
put(CASE, c14, SX, 1.3, s=0.75, y=-0.2, step=True)
skey(THR, ((c14 - 1, (1.1, 1.0, 0.3)), (c14, 0.0)))
P(mx, "cheer", c14 - 1); P(mx, "hold", c14); mx.eyes("normal", c14); mx.mouth("smile", c14); FM.look(c14, 0.0, 0.0)
PILE.keyframe_insert("location", frame=c14 - 1); PILE.location = (MX, 0.3, 0.0); PILE.keyframe_insert("location", frame=c14)
put(PEN, c14, MX - 0.42, 2.6, s=0.55, step=True)
skey(PEN, ((e13 - 30, 0.55), (e13 - 26, 0.7), (e13 - 22, 0.55)))
st.plate(c14 + 6, 100000, -2.72, lines=2)
st.caption("ONE MILLION or THE PENNY?", c14 + 6, 100000, z=-2.52, size=0.26, color="black", hud=True, max_width=3.2)
st.caption("TELL ME WHY", c14 + 12, 100000, z=-2.95, size=0.34, color="red", hud=True)
st.sfx("ding", c14 + 6, 0.4); st.sfx("pop", c14 + 12, 0.4)

# ---------- musiqa ----------
m = st.music("//musiqa_01.wav", volume=0.18, fade=25, end=END + 1)
for f, v in ((1, 0.2), (12, 0.13), (c2 - 2, 0.13), (c2 + 4, 0.15), (c4, 0.14), (JAW - 1, 0.14), (JAW, 0.0), (c10 - 1, 0.0), (c10 + 2, 0.2),
             (c10 + 10, 0.14), (c13, 0.14), (c13 + 4, 0.2), (c14 + 2, 0.14), (END - 24, 0.14), (END + 1, 0.0)):
    m.volume = v * GAIN; m.keyframe_insert("volume", frame=f)
for s_ in st._strips():
    if s_.type == 'SOUND' and not s_.name.startswith("Music"): s_.volume *= GAIN

st.alive(1, END, blink_skip=[(L0, c4 + 5), (JAW - 5, c10 + 5), (IMP - 15, FLAT + 30), (c13 + 40, c13 + 60)])
mx.alive(c3, END, blink_skip=[(J + 8, c6 + 5), (c7 + 8, c8 + 2), (T30, T30 + 40)])
bpy.app.driver_namespace["v10_marks"] = dict(e1=e1, c2=c2, e2=e2, c3=c3, e3=e3, PK=PK, L0=L0, c4=c4, T10=T10, e4=e4, c5=c5, e5=e5, J=J,
    c6=c6, T20=T20, e6=e6, c7=c7, e7=e7, c8=c8, T28=T28, e8=e8, c9=c9, PASS=PASS, e9=e9, JAW=JAW, c10=c10, T30=T30, e10=e10,
    c11=c11, IMP=IMP, FLAT=FLAT, e11=e11, c12=c12, HUGE=HUGE, e12=e12, R1=R1, c13=c13, c14=c14, e13=e13, END=END)
S.frame_set(1)
