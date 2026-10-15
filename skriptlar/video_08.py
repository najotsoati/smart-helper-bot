# video_08.py  -  "MY PHONE IS MY BOSS" sketch
import bpy, os, math, aud
T = bpy.data.texts["stickman_tools.py"]
st = T.as_module()                        # Sticky
S = bpy.context.scene
O = bpy.data.objects
A = "//video_08_audio/"
X = 0.15                                  # Sticky xonada turadigan joy
HEAD = 2.78
PH = 40.0                                 # telefon markazi
FACE = (X + 0.08, 2.75, 2.6)              # yuz yaqin plani
MED = (X - 0.01, 2.6, 2.8)                # bel-bosh plani
WIDE = (0.0, 2.3, 7.0)
PHONE_CAM = (PH, 2.45, 6.0)               # telefon ekrani to'liq
BZ = 2.3                                  # ... va uning balandligi
BIG = 1.5                                 # telefon yuzining katta holati
PV = 0.75                                 # telefon ovozi balandligi (George baland o'qiydi)
SOFA_X = -1.1                             # telefon divanda yotadigan joy

st.clear_animation()
st.backdrop("room")
st.COLORS["blue"] = "Stk_Blue"
S.frame_end = 1500                        # oxirida aniq qiymat qo'yiladi
S.render.filepath = "//My Phone Is My Boss.mp4"

# ---------- yordamchi buyruqlar ----------
def L(key):
    s = aud.Sound.file(bpy.path.abspath(A + key + ".wav")); return int(round(s.length / s.specs[0] * 30))
def say(key, f, **kw): return st.say(A + key + ".wav", f, **kw)
def on(name, f, x=None, z=None, s=1.0): st.place(name, f, x=x, z=z, scale=s, step=True)
def off(name, f): st.place(name, f, scale=0.0, step=True)
def popin(name, f, x=None, z=None, s=1.0):
    st.place(name, f, x=x, z=z, scale=0.6 * s, step=True); st.place(name, f + 3, scale=1.1 * s); st.place(name, f + 6, scale=s)
def flash(text, f0, f1, **kw):
    """Yozuv f0 da birdan chiqadi, f1 da birdan yo'qoladi."""
    ob = st.caption(text, f0, f1, **kw)
    ob.animation_data_clear()
    for f, s in ((f0 - 1, 0.0), (f0, 1.0), (f1 - 1, 1.0), (f1, 0.0)):
        ob.scale = (s, s, s); ob.keyframe_insert("scale", frame=f)
    return ob
def warp(x, z, f):
    pb = st._rig().pose.bones["root"]; pb.keyframe_insert("location", frame=f - 1); st.move_to(x, z, f)
_B = [0.0, 0.0, 0.0]
def brow(f, tilt, lift=0.0, cock=0.0):
    """Qoshlar shu kadrda keskin o'zgaradi (oldingi holat ushlab turiladi)."""
    st.brows(_B[0], _B[1], f - 1, _B[2]); st.brows(tilt, lift, f, cock); _B[:] = [tilt, lift, cock]
_LK = [0.0, 0.0]
def look(f, dx, dz):
    st.look(_LK[0], _LK[1], f - 1); st.look(dx, dz, f); _LK[:] = [dx, dz]
def squint(f, v):
    """Ko'zni qisadi: 1 = ochiq, 0.55 = shubhali, 0.1 = yumuq."""
    for n in st.EYE_BASE:
        ob = st._o(n); ob.keyframe_insert("scale", frame=f - 1)
        ob.scale = (1.0, 1.0, v); ob.keyframe_insert("scale", frame=f)

# --- qo'ldagi telefon (yongan ekrani bilan) ---
PHONE = O["Prop_phone"]; PHON = O["Prop_phoneon"]
def hand_phone(f, x, z, s=0.6, lit=True, step=True):
    for ob, vis in ((PHONE, True), (PHON, lit)):
        if step:
            ob.keyframe_insert("location", frame=f - 1); ob.keyframe_insert("scale", frame=f - 1)
        v = s if vis else 0.0
        ob.location = (x, 0.0, z); ob.scale = (v, v, v)
        ob.keyframe_insert("location", frame=f); ob.keyframe_insert("scale", frame=f)

# --- divanda yotadigan telefon ---
LP = O["FX_PhoneLoose"]
def lp_key(f, x, z, rot, s=0.9):
    LP.location = (x, 0.3, z); LP.rotation_euler = (0.0, rot, 0.0); LP.scale = (s, s, s)
    for p in ("location", "rotation_euler", "scale"): LP.keyframe_insert(p, frame=f)

# --- telefonning yuzi ---
def pmood(f, lid=0.7, tilt=10.0, lift=0.0, cock=0.0):
    """Telefon yuzi: lid = qovoq (0 ochiq, 0.7 mensimaydigan), tilt > 0 = xo'jayin qoshi, cock = bitta qoshni ko'tarish."""
    for side, sg in (("L", 1.0), ("R", -1.0)):
        ld = O["PFace_Lid" + side]; br = O["PFace_Brow" + side]
        ld.keyframe_insert("scale", frame=f - 1); br.keyframe_insert("rotation_euler", frame=f - 1); br.keyframe_insert("location", frame=f - 1)
        ld.scale = (1.0, 1.0, lid) if lid > 0.01 else (0.0, 0.0, 0.0); ld.keyframe_insert("scale", frame=f)
        br.rotation_euler = (0.0, sg * math.radians(tilt), 0.0); br.keyframe_insert("rotation_euler", frame=f)
        br.location.z = 0.66 + lift + (cock if side == "R" else 0.0); br.keyframe_insert("location", frame=f)
def pblink(f):
    for side in "LR":
        e = O["PFace_Eye" + side]
        for ff, s in ((f - 2, 1.0), (f, 0.1), (f + 3, 1.0)):
            e.scale = (1.0, 1.0, s); e.keyframe_insert("scale", frame=ff)
def psay(key, f, volume=PV):
    """Telefon gapiradi: ovoz qo'shiladi, og'zi ovoz balandligiga qarab ochiladi. Tugash kadrini qaytaradi."""
    path = A + key + ".wav"
    s = st.voice(path, f, volume, channel=4)
    n = st._length(s); lv = st._levels(path)
    mo = O["PFace_Mouth"]
    mo.scale = (1.0, 1.0, 0.1); mo.keyframe_insert("scale", frame=f - 1)
    for i in range(0, len(lv), 2):
        v = max(lv[i:i + 2])
        mo.scale = (1.0, 1.0, 0.1) if v < 0.1 else (0.9, 1.0, min(1.0, 0.3 + v))
        mo.keyframe_insert("scale", frame=f + i)
    mo.scale = (1.0, 1.0, 0.1); mo.keyframe_insert("scale", frame=f + n + 1)
    return f + n

# --- otjimaniya: tana yotiq, qo'llar polga tiraladi (ikki bo'g'inli qo'l hisobi) ---
ROOTX, ROOTZ = -1.7, 0.27
HAND = (0.46, -0.03)
ARM, SH = 0.55, 2.3
def plank_pose(th, zr, head):
    sx = ROOTX + SH * math.cos(math.radians(th)); sz = zr + SH * math.sin(math.radians(th))
    def ik(tx, tz):
        dx, dz = tx - sx, tz - sz
        d = min(math.hypot(dx, dz), 2 * ARM - 1e-4)
        phi = math.degrees(math.atan2(dz, dx)); al = math.degrees(math.acos(d / 2.0 / ARM))
        ua = phi - al
        ex = sx + ARM * math.cos(math.radians(ua)); ez = sz + ARM * math.sin(math.radians(ua))
        return ua, math.degrees(math.atan2(tz - ez, tx - ex))
    uaL, faL = ik(HAND[0] + 0.05, HAND[1]); uaR, faR = ik(HAND[0] - 0.06, HAND[1])
    return {"root": th, "head": head, "upper_arm.L": uaL, "forearm.L": faL, "upper_arm.R": uaR, "forearm.R": faR,
            "thigh.L": th + 180, "shin.L": th + 180, "foot.L": -80, "thigh.R": th + 178, "shin.R": th + 178, "foot.R": -84}
def plank(f, th, head=62):
    st.POSES["_pl"] = plank_pose(th, ROOTZ, head)
    st.move_to(ROOTX, ROOTZ, f); st.apply_pose("_pl", f, face=False)
FLAT = {"root": 0, "head": 40, "upper_arm.L": 4, "forearm.L": -4, "upper_arm.R": 200, "forearm.R": 176,
        "thigh.L": 180, "shin.L": 180, "foot.L": -80, "thigh.R": 178, "shin.R": 178, "foot.R": -84}
def flat(f, head=40):
    st.POSES["_fl"] = dict(FLAT, head=head)
    st.move_to(ROOTX, 0.15, f); st.apply_pose("_fl", f, face=False)

st.POSES["ph_hip"] = {"upper_arm.L": -62, "forearm.L": 58, "upper_arm.R": -135, "forearm.R": -49, "head": 86}
st.POSES["ph_rage"] = {"upper_arm.L": -62, "forearm.L": 58, "upper_arm.R": 150, "forearm.R": 85}
st.POSES["wind"] = {"upper_arm.L": 35, "forearm.L": 95, "upper_arm.R": -120, "forearm.R": -60, "root": 86}
st.POSES["threw"] = {"upper_arm.L": 150, "forearm.L": 175, "upper_arm.R": -110, "forearm.R": -80, "root": 97, "front": "L"}
st.POSES["grab"] = {"root": 97, "head": 96, "upper_arm.R": 232, "forearm.R": 216, "upper_arm.L": -60, "forearm.L": -100}
st.POSES["tapA"] = {"upper_arm.L": -62, "forearm.L": 58, "upper_arm.R": -30, "forearm.R": 75, "head": 80, "front": "R"}
st.POSES["tapB"] = {"upper_arm.L": -62, "forearm.L": 58, "upper_arm.R": -30, "forearm.R": 66, "head": 80, "front": "R"}

# ---------- sahna ----------
off("Set_Calendar", 1)
on("Set_Sofa", 1)
on("Phone_ScreenOff", 1)
lo = O["FX_PhoneLooseOn"]; lo.scale = (1.0, 1.0, 1.0); lo.keyframe_insert("scale", frame=1)
st.move_to(X, 0.0, 1)
st.apply_pose("phone", 1, face=False)
hand_phone(1, 0.62, 2.55, lit=False, step=False)
st.mouth("neutral", 1)
TITLE = st.title("MY PHONE IS MY BOSS", f_on=-8)

# ==== A) HOOK: shubha bilan telefonga qaraydi, yuzga tez yaqinlashish
st.cut(1, X, 2.5, 5.2)
st.zoom(4, 11, x=FACE[0], z=FACE[1], scale=FACE[2])
st.sfx("whoosh", 3, 0.5)
squint(1, 0.55); st.brows(-8, 0.0, 1, 0.05); _B[:] = [-8, 0.0, 0.05]; st.look(0.04, -0.03, 1); _LK[:] = [0.04, -0.03]
e1 = say("S01", 8, volume=1.2, end="neutral")
st.zoom(11, e1 + 2, x=X + 0.12, z=2.8, scale=2.42)
look(8 + 46, 0.0, 0.0)                                             # "...replace me" - kameraga qaraydi

# ==== B) TELEFON EKRANI YONADI: "Finally. You noticed."
b0 = e1 + 3
st.cut(b0, *PHONE_CAM)
LIT = b0 + 9
off("Phone_ScreenOff", LIT); on("Phone_ScreenOn", LIT)
st.place("PFace", LIT, z=BZ, scale=1.0, step=True); st.place("PFace", LIT + 3, scale=1.62); st.place("PFace", LIT + 6, scale=BIG)
pmood(LIT, lid=0.0, tilt=0.0, lift=0.06)                           # ko'zlar katta ochiladi
pmood(LIT + 16, lid=0.7, tilt=10.0)                                # keyin mensimay qaraydi
hand_phone(LIT, 0.62, 2.55)                                        # qo'ldagi telefon ham yonadi
st.sfx("boom", LIT, 0.42); st.sfx("ding", LIT + 2, 0.35)
st.shake(LIT, LIT + 8, 0.07)
p1 = psay("P01", LIT + 8)
st.zoom(LIT + 8, p1 + 2, z=2.7, scale=5.3)

# ==== C) STICKY: "Wait... you can TALK?!"
c0 = p1 + 4
st.cut(c0, *FACE)
st.eyes("wide", c0); brow(c0, 0, 0.1); look(c0, 0.04, -0.03)
st.punch(c0 + 1, 0.1); st.fx("lines", c0 + 1, X, HEAD, 1.0, length=20)
ce = say("S02", c0 + 3, volume=1.3, end="open", closed="open", opened="scream")
TALK = c0 + 3 + 43
st.zoom(c0, TALK - 2, x=X + 0.10, z=2.8, scale=2.42)
st.shake(TALK, TALK + 12, 0.03); st.punch(TALK, 0.08)
st.fx("lines", TALK, X, HEAD, 1.0, length=16)

# ==== D) TELEFON: "...calculate how many hours you wasted today." -> 9 HOURS
d0 = ce + 5
st.cut(d0, *PHONE_CAM)
P2 = d0 + 3
d1 = psay("P02", P2)
d_end = d1 + 6
EX = P2 + 57                                                       # "For example,"
K = P2 + 84                                                        # "calculate..."
NINE = K + 48                                                      # "...today"
pblink(P2 + 30)
st.place("PFace", EX - 4, z=BZ, scale=BIG); st.place("PFace", EX + 4, z=3.2, scale=1.15)      # yuz tepaga suriladi
pmood(EX, lid=0.45, tilt=2.0, lift=0.03, cock=0.1)
popin("Phone_Panel", EX + 2); st.sfx("pop", EX + 2, 0.5)
st.caption("SCREEN TIME TODAY", EX + 4, d_end, z=1.48, size=0.15, x=PH, max_width=1.9)
for i in range(1, 9):
    f = K + (i - 1) * 6
    flash("%d HOUR%s" % (i, "" if i == 1 else "S"), f, f + 6, z=0.85, size=0.4, x=PH, max_width=2.0)
    st.sfx("tick", f, 1.0)
nine = st.caption("9 HOURS", NINE, d_end, z=0.85, size=0.62, x=PH, max_width=2.05, color="red")
for dx, dz, col in ((0.09, 0.03, "blue"), (-0.08, -0.03, "black")):      # glitch: rangli soyalar
    g = flash("9 HOURS", NINE, NINE + 7, z=0.85 + dz, size=0.62, x=PH + dx, max_width=2.05, color=col); g.location.y = -0.28
for k, dx in enumerate((0.0, 0.1, -0.08, 0.06, -0.1, 0.04, 0.0)):
    nine.location.x = PH + dx; nine.keyframe_insert("location", frame=NINE + k)
st.place("Phone_Glitch", NINE, z=0.95, scale=1.0, step=True); st.place("Phone_Glitch", NINE + 2, z=1.25, step=True)
st.place("Phone_Glitch", NINE + 4, z=0.6, step=True); st.place("Phone_Glitch", NINE + 6, scale=0.0, step=True)
st.sfx("glitch", NINE, 0.35); st.sfx("boom", NINE, 0.38)
pmood(NINE + 2, lid=0.85, tilt=14.0)
st.zoom(d0, NINE - 2, z=2.7, scale=5.3)
st.shake(NINE, NINE + 7, 0.05)

# ==== E) STICKY: "That number is fake."
e0 = d_end
st.cut(e0, *MED)
st.snap("ph_hip", e0, lead=2, face=False)
st.eyes("normal", e0); brow(e0, -12, 0.0); look(e0, 0.04, -0.03)
ee = say("S03", e0 + 4, volume=1.6, end="neutral")

# ==== F) TELEFON: "You watched videos of people cleaning carpets for three hours."
f0 = ee + 5
st.cut(f0, *PHONE_CAM)
off("Phone_Panel", f0)
on("Phone_Thumb", f0); on("Phone_Carpet", f0)
pmood(f0, lid=0.55, tilt=6.0, cock=0.1)
fe = psay("P03", f0 + 3)
F2 = f0 + 3 + 52                                                   # gap davom etadi, kadrda aybdor Sticky
st.caption("CARPET", f0 - 8, F2 + 2, z=1.42, size=0.19, x=PH + 0.38, color="white", max_width=1.35)
st.caption("CLEANING", f0 - 8, F2 + 2, z=1.17, size=0.19, x=PH + 0.38, color="white", max_width=1.35)
st.caption("3 HOURS", f0 + 20, F2 + 2, z=0.75, size=0.27, x=PH + 0.38, color="gold", max_width=1.35)
st.sfx("pop", f0 + 20, 0.5)
pblink(f0 + 34)
st.zoom(f0, F2 - 1, z=2.62, scale=5.5)
st.cut(F2, *FACE)
off("Phone_Thumb", F2 + 2); off("Phone_Carpet", F2 + 2)
st.snap("phone", F2, lead=2, face=False)
brow(F2, 10, 0.03); look(F2, 0.04, -0.03); st.mouth("neutral", F2)
look(F2 + 18, -0.05, 0.01)                                         # ko'zini olib qochadi
st.prop("sweat", F2 + 16, fe + 20)
# noqulay sukut
look(fe + 5, 0.05, 0.0); look(fe + 13, -0.05, 0.01)
st.mouth("think", fe + 2)
g0 = fe + 20

# ==== G) "I'm taking my life back!" va telefonni divanga otadi
st.cut(g0, *MED)
st.snap("ph_rage", g0 + 1, lead=2, face=False)
brow(g0, -14, 0.02); look(g0, 0.0, 0.0)
ge = say("S04", g0 + 3, volume=1.0, end="grin")
st.punch(g0 + 3, 0.06)
TH = ge + 3
st.cut(TH, *WIDE)
st.snap("wind", TH, lead=2, over=0.0, settle=1, face=False)
st.snap("threw", TH + 5, lead=3, face=False)
hand_phone(TH, 0.42, 3.3)
REL = TH + 4                                                       # telefon qo'ldan chiqadi
hand_phone(REL, 0.42, 3.3, s=0.0)
LP.keyframe_insert("scale", frame=REL - 1)
lp_key(REL, X - 0.05, 3.35, 0.0)
lp_key(REL + 5, -0.5, 3.75, -4.2)
lp_key(REL + 10, -0.95, 2.6, -9.0)
lp_key(REL + 13, SOFA_X, 1.36, -12.45)
lp_key(REL + 16, SOFA_X, 1.52, -12.45)
lp_key(REL + 19, SOFA_X, 1.34, -12.45)
st.sfx("whoosh", REL - 1, 0.7); st.sfx("pop", REL + 13, 0.5)
st.mouth("neutral", TH + 8)

# ==== H) OTJIMANIYA: "One! Two! Three!" va yiqiladi
DROP = REL + 12
st.move_to(X, 0.0, DROP); st.apply_pose("threw", DROP, face=False)
plank(DROP + 7, 20)
st.sfx("jump", DROP, 0.4); st.sfx("land", DROP + 7, 0.32)
st.fx("dust", DROP + 7, 0.5, 0.1, 0.9); st.punch(DROP + 7, 0.06)
brow(DROP + 7, -10, 0.0)
R1 = DROP + 11
for f, th in ((R1, 20), (R1 + 3, 12), (R1 + 6, 5), (R1 + 9, 12), (R1 + 12, 20)): plank(f, th)
say("S05", R1 + 9, volume=0.9, end="neutral")
R2 = R1 + 24
st.caption("1", R1 + 10, R2 + 10, z=4.3, size=0.7)
st.sfx("pop", R1 + 10, 0.4)
for f, th in ((R2, 20), (R2 + 4, 12), (R2 + 8, 5), (R2 + 13, 12), (R2 + 18, 20)): plank(f, th)
say("S06", R2 + 13, volume=1.0, end="neutral")
R3 = R2 + 27
st.caption("2", R2 + 14, R3 + 16, z=4.3, size=0.7)
st.sfx("pop", R2 + 14, 0.4)
for f, th in ((R3, 20), (R3 + 5, 12), (R3 + 10, 5), (R3 + 18, 8), (R3 + 26, 11), (R3 + 34, 12)): plank(f, th)
FALL = R3 + 38                                                     # qo'llari ko'tara olmaydi
plank(FALL - 1, 12)
st.shiver(R3 + 12, R3 + 36, 0.02)
brow(R3 + 10, 14, 0.03); squint(R3 + 10, 0.5); st.prop("sweat", R3 + 12, FALL - 2, x=-0.59, z=2.61)
say("S07", R3 + 20, volume=1.1, end="open", closed="open")
st.caption("3", R3 + 21, FALL + 1, z=4.3, size=0.7, color="red")
st.sfx("pop", R3 + 21, 0.4)
flat(FALL + 3)
squint(FALL + 3, 0.1); brow(FALL + 3, 8, 0.0)
st.sfx("fall", FALL - 10, 0.3); st.sfx("splat", FALL + 3, 0.35); st.sfx("land", FALL + 3, 0.22)
st.fx("star", FALL + 3, 1.0, 1.32, 0.8); st.fx("dust", FALL + 3, 0.2, 0.1, 1.0)
st.zoom(DROP, FALL, x=-0.03, z=2.25, scale=6.85)
st.shake(FALL + 3, FALL + 9, 0.06)
PH4 = FALL + 3 + 22
for k, f in enumerate(range(FALL + 6, PH4 + 84, 7)):               # hansiraydi
    st.mouth("wide" if k % 2 == 0 else "open", f)

# ==== I) DIVANDAGI TELEFON: "Want to watch a video about getting six-pack abs in seven days?"
i0 = PH4
st.sfx("ding", i0 - 8, 0.6)
for f, s in ((i0 - 9, 0.9), (i0 - 6, 1.15), (i0 - 3, 0.9)):
    LP.scale = (s, s, s); LP.keyframe_insert("scale", frame=f)
st.cut(i0, *PHONE_CAM)
st.place("PFace", i0, z=BZ, scale=BIG, step=True)
pmood(i0, lid=0.4, tilt=-4.0, lift=0.04, cock=0.1)
ie = psay("P04", i0 + 3)
TP = i0 + 3 + 50                                                   # "six-pack abs"
I2 = i0 + 3 + 84                                                   # kadrda polda yotgan Sticky
st.place("PFace", TP - 4, z=BZ, scale=BIG); st.place("PFace", TP + 4, z=3.2, scale=1.15)
popin("Phone_Thumb", TP); popin("Phone_Abs", TP + 2); st.sfx("pop", TP, 0.5)
st.caption("SIX-PACK ABS", TP + 2, I2 + 2, z=1.37, size=0.17, x=PH + 0.38, color="white", max_width=1.35)
st.caption("IN 7 DAYS", TP + 6, I2 + 2, z=1.02, size=0.26, x=PH + 0.38, color="gold", max_width=1.35)
pblink(i0 + 30)
st.cut(I2, 0.62, 1.78, 4.7)
flat(I2 - 1); flat(I2 + 7, head=72)                                # boshini ko'taradi
squint(I2 + 4, 1.0); st.eyes("wide", I2 + 7); brow(I2 + 7, 0, 0.09); look(I2 + 7, -0.05, 0.02)
st.mouth("smile", I2 + 8); st.mouth("grin", I2 + 16)

# ==== J) "YES!" - telefonni bir zumda oladi
j0 = max(ie + 3, I2 + 20)
say("S08", j0, volume=1.2, end="grin", closed="grin", opened="wide")
ZIP = j0 + 9
st.cut(ZIP, *WIDE)
off("Phone_Thumb", ZIP); off("Phone_Abs", ZIP)
flat(ZIP - 1, head=72)
st.move_to(-0.25, 0.0, ZIP + 4); st.apply_pose("grab", ZIP + 4, face=False)
st.sfx("whoosh", ZIP - 1, 0.8); st.fx("dust", ZIP, 0.3, 0.12, 1.0)
GRAB = ZIP + 6
LP.keyframe_insert("scale", frame=GRAB - 1); LP.scale = (0.0, 0.0, 0.0); LP.keyframe_insert("scale", frame=GRAB)
hand_phone(GRAB, -0.80, 1.60)
st.snap("cheer", GRAB + 3, lead=3, face=False)
hand_phone(GRAB + 3, -0.62, 3.28, step=False)
st.eyes("normal", GRAB); brow(GRAB, 0, 0.06); look(GRAB, 0.0, 0.0)
st.bounce(GRAB + 6, 0.3, 12, sound=0.5)
for i, (gx, gz) in enumerate(((-1.25, 3.75), (-0.78, 4.28), (-1.2, 3.1))):       # telefon atrofida uchqunlar
    gf = GRAB + 6 + i * 3; gn = "FX_Gold_%d" % (i + 1)
    st.place(gn, gf, x=gx, z=gz, scale=0.0, step=True); st.place(gn, gf + 3, scale=0.7); st.place(gn, gf + 6, scale=0.55); st.place(gn, gf + 11, scale=0.0)
j1 = GRAB + 22
st.apply_pose("cheer", j1, face=False)

# ==== K) TELEFON: "Good. Now subscribe to my channel."
k0 = j1
st.cut(k0, *PHONE_CAM)
st.place("PFace", k0, z=2.75, scale=1.45, step=True)
pmood(k0, lid=0.8, tilt=12.0)
ke = psay("P05", k0 + 3, volume=PV * 1.15)
SB = k0 + 3 + 34
popin("Phone_SubBtn", SB); st.sfx("pop", SB, 0.7)
sb = st.caption("SUBSCRIBE", SB + 1, ke + 6, z=0.95, size=0.24, x=PH, color="white", max_width=1.6)
for k, f in enumerate(range(SB + 10, ke + 4, 5)):
    st.place("Phone_SubBtn", f, scale=1.08 if k % 2 == 0 else 1.0)
st.pulse(sb, SB + 10, ke + 4, 1.0, 1.1, 5)

# ==== L) STICKY: "Wait... YOU have a channel?"
l0 = ke + 5
warp(X, 0.0, l0); st.apply_pose("phone", l0, face=False)
hand_phone(l0, 0.62, 2.55)
st.cut(l0, *FACE)
brow(l0, 0, 0.02, 0.07); look(l0, 0.04, -0.03); st.mouth("neutral", l0)
le = say("S09", l0 + 3, volume=1.2, end="open", closed="neutral")
look(l0 + 3 + 30, 0.0, 0.0)
st.zoom(l0, le, x=X + 0.12, z=2.8, scale=2.42)

# ==== M) TELEFON: "Three million subscribers." - musiqa uziladi
m0 = le + 4
st.cut(m0, *PHONE_CAM)
off("Phone_SubBtn", m0)
st.place("PFace", m0, z=3.2, scale=1.15, step=True)
pmood(m0, lid=0.9, tilt=14.0)
on("Phone_Panel", m0)
MIL = m0 + 5
me_ = psay("P06", MIL)
n0 = me_ + 8
st.caption("3,000,000", MIL + 2, n0 + 2, z=1.15, size=0.5, x=PH, max_width=2.0)
st.caption("SUBSCRIBERS", MIL + 8, n0 + 2, z=0.6, size=0.22, x=PH, color="red", max_width=2.0)
st.sfx("scratch", m0, 0.8); st.sfx("ding", MIL + 2, 0.5)

# ==== N) STICKY kameraga 1 soniya tikiladi: "I have twelve followers."
st.cut(n0, X + 0.16, 2.84, 2.36)
brow(n0, 0, 0.0); look(n0, 0.0, 0.0); st.mouth("neutral", n0)
st.blink(n0 + 17)
ne = say("S10", n0 + 28, volume=1.3, end="sad", closed="neutral")
st.zoom(n0, ne + 6, scale=2.3)
brow(ne + 2, 10, 0.0)

# ==== O) TELEFON: skaner -> "UNEMPLOYED HUMAN DETECTED"
o0 = ne + 8
st.apply_pose("phone", o0, face=False)
st.cut(o0, *PHONE_CAM)
off("Phone_Panel", o0)
pmood(o0, lid=0.25, tilt=0.0, lift=0.04)
ALERT = o0 + 20
q0 = ALERT + 46
st.place("Phone_Scan", o0 + 2, z=4.3, scale=1.0, step=True); st.place("Phone_Scan", o0 + 18, z=0.0); st.place("Phone_Scan", o0 + 19, scale=0.0, step=True)
st.caption("SCANNING HUMAN...", o0 - 8, ALERT - 3, z=0.95, size=0.2, x=PH, max_width=2.3)
for f in range(o0 + 2, o0 + 18, 3): st.sfx("tick", f, 1.0)
popin("Phone_Alert", ALERT)
st.caption("UNEMPLOYED HUMAN", ALERT + 1, q0 + 2, z=0.98, size=0.2, x=PH, color="white", max_width=2.1)
det = st.caption("DETECTED", ALERT + 4, q0 + 2, z=0.52, size=0.38, x=PH, color="white", max_width=2.1)
st.pulse(det, ALERT + 14, q0 - 2, 1.0, 1.1, 5)
st.sfx("error", ALERT, 0.36); st.sfx("boom", ALERT, 0.3)
mo = O["PFace_Mouth"]; gr = O["PFace_Grin"]
mo.keyframe_insert("scale", frame=ALERT - 1); mo.scale = (0.0, 0.0, 0.0); mo.keyframe_insert("scale", frame=ALERT)
gr.keyframe_insert("scale", frame=ALERT - 1); gr.scale = (1.0, 1.0, 1.0); gr.keyframe_insert("scale", frame=ALERT)
for k, f in enumerate(range(ALERT + 4, q0, 4)):                    # kuladi
    gr.scale = (1.0, 1.0, 0.8 if k % 2 == 0 else 1.0); gr.keyframe_insert("scale", frame=f)
pmood(ALERT, lid=0.75, tilt=16.0)
st.shake(ALERT, ALERT + 6, 0.05)
st.zoom(ALERT + 6, q0, z=2.7, scale=5.3)

# ==== Q) YAKUN: yana telefon titkilaydi, tepada savol
st.cut(q0, *WIDE)
k = 0
for f in range(q0, q0 + 76, 5):
    st.apply_pose("tapA" if k % 2 == 0 else "tapB", f, face=False); k += 1
squint(q0, 0.6); brow(q0, 6, -0.01); look(q0, 0.04, -0.03); st.mouth("neutral", q0)
END = q0 + 66
st.zoom(q0, END, x=-0.08, z=2.45, scale=6.7)
st.title("WHO REALLY OWNS", f_on=q0 + 3, y=2.9, size=0.36)
st.title("YOUR PHONE?", f_on=q0 + 10, y=2.47, size=0.48, color="red")
st.sfx("pop", q0 + 3, 0.5); st.sfx("boom", q0 + 10, 0.45)
TITLE.keyframe_delete("scale", frame=100000); TITLE.keyframe_delete("scale", frame=100003)
TITLE.scale = (1.0, 1.0, 1.0); TITLE.keyframe_insert("scale", frame=q0 - 1)
TITLE.scale = (0.0, 0.0, 0.0); TITLE.keyframe_insert("scale", frame=q0)
S.frame_end = END

# ---------- musiqa: "uch million"da uziladi, ogohlantirishda qaytadi ----------
m = st.music("//musiqa_03_sneaky.wav", volume=0.1, fade=20, end=END + 1)
MV = ((1, 0.22), (7, 0.22), (12, 0.10), (LIT - 2, 0.10), (LIT, 0.0), (LIT + 8, 0.0), (LIT + 14, 0.10),
      (fe, 0.10), (fe + 4, 0.0), (g0 - 2, 0.0), (g0 + 2, 0.12), (DROP, 0.12), (DROP + 8, 0.17), (i0 - 2, 0.17), (i0 + 4, 0.10),
      (m0 - 1, 0.10), (m0, 0.0), (ALERT - 1, 0.0), (ALERT + 2, 0.16), (END - 19, 0.16), (END + 1, 0.0))
GAIN = 1.3                                # umumiy balandlik: hamma tovush bir xil nisbatda ko'tariladi
for f, v in MV:
    m.volume = v * GAIN; m.keyframe_insert("volume", frame=f)
for s_ in st._strips():
    if s_.type == 'SOUND' and not s_.name.startswith("Music"): s_.volume *= GAIN
st.alive(1, END, blink_skip=[(1, d0), (R3, GRAB + 12), (n0, o0), (q0, END)])
S.frame_set(1)
MARKS = dict(e1=e1, b0=b0, LIT=LIT, p1=p1, c0=c0, TALK=TALK, ce=ce, d0=d0, EX=EX, K=K, NINE=NINE, d_end=d_end, e0=e0, ee=ee, f0=f0, F2=F2, fe=fe, g0=g0, ge=ge,
             TH=TH, REL=REL, DROP=DROP, R1=R1, R2=R2, R3=R3, FALL=FALL, i0=i0, TP=TP, I2=I2, ie=ie, j0=j0, ZIP=ZIP, GRAB=GRAB, k0=k0, SB=SB, ke=ke,
             l0=l0, le=le, m0=m0, MIL=MIL, n0=n0, ne=ne, o0=o0, ALERT=ALERT, q0=q0, END=END)
bpy.app.driver_namespace["v08_marks"] = MARKS
