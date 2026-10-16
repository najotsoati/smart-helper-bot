# video_09.py  -  "THE TIME-TRAVEL MISTAKE" sketch
import bpy, os, math, random, aud
T = bpy.data.texts["stickman_tools.py"]
st = T.as_module()                        # Sticky
S = bpy.context.scene
O = bpy.data.objects
A = "//video_09_audio/"
X = 0.08                                  # Sticky turadigan joy
FRX = 0.62                                # muzlatgich oldidagi joy
HEAD = 2.78
PZS = 0.74                                # qo'ldagi pitsa kattaligi
PZH = 0.58                                # qo'ldagi pitsa Stickydan qancha o'ngda
WIDE = (0.0, 2.3, 7.0)
MEDP = (X + 0.22, 2.65, 2.5)              # Sticky va qo'lidagi pitsa
FRIDGE_CAM = (1.1, 2.5, 3.6)              # muzlatgich oldi
FLOOR_CAM = (-0.35, 0.55, 2.2)            # poldagi banan
BTN1_CAM = (-0.4, 2.05, 1.6)              # tugma juda yaqin
BTN2_CAM = (-0.18, 2.5, 2.4)              # tugma va Sticky yuzi
RAGE_CAM = (X + 0.17, 2.8, 2.3)
MACH_CAM = (-1.565, 1.7, 4.2)             # vaqt mashinasi to'liq
PIZZA_CAM = (1.4, 0.95, 3.0)              # yerdagi pitsa va dinozavr tumshug'i
CASE_CAM = (1.45, 2.2, 3.0)               # muzey vitrinasi va yozuv
DUO_CAM = (0.83, 2.7, 4.3)                # Sticky va vitrina
BTN = (-0.61, 2.08)                       # qizil tugma ustki nuqtasi
PZX, PZG = 1.45, 0.32                     # pitsa yerda yotadigan joy

st.clear_animation()
st.backdrop("room")
S.frame_end = 1700                        # oxirida aniq qiymat qo'yiladi
S.render.filepath = "//The Time-Travel Mistake.mp4"

# ---------- yordamchi buyruqlar ----------
EST = {"S01": 40}
def say(key, f, **kw):
    p = bpy.path.abspath(A + key + ".wav")
    if os.path.exists(p): return st.say(A + key + ".wav", f, **kw)
    st.talk(f, f + EST[key], end=kw.get("end", "smile")); return f + EST[key]
def on(name, f, x=None, z=None, s=1.0): st.place(name, f, x=x, z=z, scale=s, step=True)
def off(name, f): st.place(name, f, scale=0.0, step=True)
_B = [0.0, 0.0, 0.0]
def brow(f, tilt, lift=0.0, cock=0.0):
    st.brows(_B[0], _B[1], f - 1, _B[2]); st.brows(tilt, lift, f, cock); _B[:] = [tilt, lift, cock]
_LK = [0.0, 0.0]
def look(f, dx, dz):
    st.look(_LK[0], _LK[1], f - 1); st.look(dx, dz, f); _LK[:] = [dx, dz]
def keyall(ob, f):
    for p in ("location", "rotation_euler", "scale"): ob.keyframe_insert(p, frame=f)
def put(ob, f, x, z, rot=0.0, s=1.0, y=None, step=False):
    """Istalgan obyektni joyi, burilishi va kattaligi bilan birga kalitlaydi."""
    if step: keyall(ob, f - 1)
    ob.location = (x, ob.location.y if y is None else y, z); ob.rotation_euler = (0.0, rot, 0.0)
    ob.scale = (s, s, s) if isinstance(s, (int, float)) else tuple(s)
    keyall(ob, f)
def kid(ob, f, s, step=True):
    if step: ob.keyframe_insert("scale", frame=f - 1)
    ob.scale = (s, s, s); ob.keyframe_insert("scale", frame=f)
def title_off(f0, f1):
    """Sarlavhani yaqin plan paytida yashiradi."""
    for f, s in ((f0 - 1, 1.0), (f0, 0.0), (f1 - 1, 0.0), (f1, 1.0)):
        TITLE.scale = (s, s, s); TITLE.keyframe_insert("scale", frame=f)

PZ = O["FX_Pizza"]; FROST = O["FX_PizzaFrost"]; STEAM = O["FX_PizzaSteam"]
def pizza(f, x, z, rot=0.0, s=0.8, y=-0.15, step=False): put(PZ, f, x, z, rot, s, y, step)
def steam(f0, f1):
    k = 0
    for f in range(f0, f1, 4):
        STEAM.scale = (1.0, 1.0, 1.18 if k % 2 == 0 else 0.95); STEAM.keyframe_insert("scale", frame=f); k += 1
ARM = 0.55
def reach(side, tx, tz, rx):
    """Tik turgan Sticky (oyog'i rx da) qo'lini (tx, tz) nuqtaga cho'zadi - tirsak pastda."""
    sx, sz = rx, 2.3
    d = min(math.hypot(tx - sx, tz - sz), 2 * ARM - 1e-4)
    phi = math.degrees(math.atan2(tz - sz, tx - sx)); al = math.degrees(math.acos(d / 2.0 / ARM))
    best = None
    for sg in (1, -1):
        ua = phi + sg * al
        ex = sx + ARM * math.cos(math.radians(ua)); ez = sz + ARM * math.sin(math.radians(ua))
        fa = math.degrees(math.atan2(tz - ez, tx - ex))
        if best is None or ez < best[0]: best = (ez, ua, fa)
    return {"upper_arm." + side: best[1], "forearm." + side: best[2]}

# --- vaqt mashinasi ---
TB = O["TM_Button"]; TH = O["TM_Hand"]; BULB = O["TM_Bulb"]
def press(f):
    for ff, s in ((f - 1, 1.0), (f, 0.4), (f + 4, 0.4), (f + 7, 1.0)):
        TB.scale = (1.0, 1.0, s); TB.keyframe_insert("scale", frame=ff)
def dial(f0, f1, turns):
    """Soat mili aylanadi: turns < 0 - orqaga."""
    TH.keyframe_insert("rotation_euler", frame=f0)
    TH.rotation_euler.y += turns * 2 * math.pi
    TH.keyframe_insert("rotation_euler", frame=f1)
def bulb_pulse(f0, f1):
    k = 0
    for f in range(f0, f1, 5):
        s = 1.25 if k % 2 == 0 else 1.0
        BULB.scale = (s, s, s); BULB.keyframe_insert("scale", frame=f); k += 1
STREAK = O["HUD_Streaks"]; FLASH = O["HUD_Flash"]
def streaks(f0, f1):
    rnd = random.Random(f0)
    STREAK.keyframe_insert("scale", frame=f0 - 1)
    for f in range(f0, f1):
        STREAK.scale = (1.0, 1.0, 1.0); STREAK.location = (rnd.uniform(-0.3, 0.3), rnd.uniform(-0.9, 0.9), -4.85)
        STREAK.keyframe_insert("scale", frame=f); STREAK.keyframe_insert("location", frame=f)
    STREAK.scale = (0.0, 0.0, 0.0); STREAK.keyframe_insert("scale", frame=f1)
def wflash(f, n=2):
    FLASH.keyframe_insert("scale", frame=f - 1)
    FLASH.scale = (1.0, 1.0, 1.0); FLASH.keyframe_insert("scale", frame=f); FLASH.keyframe_insert("scale", frame=f + n - 1)
    FLASH.scale = (0.0, 0.0, 0.0); FLASH.keyframe_insert("scale", frame=f + n)
def time_fx(f0, f1, label):
    """Vaqt sakrashi: ekran bo'ylab chiziqlar, tepada yozuv, kamera titraydi."""
    streaks(f0, f1)
    st.plate(f0 + 1, f1 - 3, 2.14)
    st.caption(label, f0 + 2, f1 - 3, z=2.14, size=0.36, color="red", hud=True, max_width=3.1)
    st.shake(f0, f1, 0.03)
FD = O["Set_FreezerDoor"]
def door(f, sx):
    FD.keyframe_insert("scale", frame=f - 1); FD.scale = (sx, 1.0, 1.0); FD.keyframe_insert("scale", frame=f)
def pupil(name, f, dx, dz):
    ob = O[name + "_Pupil"]; bx, bz = (0.0, 0.55) if name == "Dino_Peek" else (-0.5, 0.26)
    ob.keyframe_insert("location", frame=f - 1)
    ob.location = (bx + dx, -0.06, bz + dz); ob.keyframe_insert("location", frame=f)
def sparkle(n, f, x, z, s=0.6):
    gn = "FX_Gold_%d" % n
    st.place(gn, f, x=x, z=z, scale=0.0, step=True); st.place(gn, f + 3, scale=s); st.place(gn, f + 6, scale=s * 0.75); st.place(gn, f + 11, scale=0.0)

# --- yiqilishlar ---
UP = {"upper_arm.L": 60, "forearm.L": 80, "upper_arm.R": 120, "forearm.R": 100}
LYING = {"root": 0, "head": 38, "upper_arm.L": 20, "forearm.L": 50, "upper_arm.R": 160, "forearm.R": 200,
         "thigh.L": 165, "shin.L": 195, "thigh.R": 178, "shin.R": 178, "foot.L": 80, "foot.R": 85}
def fall_keys(x0, x1=-1.55):
    """Orqasiga yiqilish: oyoqlar chapga sirpanadi, tana o'ng tomonga yotadi."""
    return [(0, x0, 0.0, dict(UP, root=90, head=88)),
            (2, x0 + (x1 - x0) * 0.35, 0.3, dict(UP, root=58, head=70, **{"thigh.L": -140, "shin.L": -150, "thigh.R": -165, "shin.R": -170})),
            (5, x0 + (x1 - x0) * 0.8, 0.7, dict(UP, root=18, head=50, **{"thigh.L": 150, "shin.L": 140, "thigh.R": 170, "shin.R": 165})),
            (8, x1, 0.15, LYING)]
def play(keys, f0, reverse=False, k=1.0):
    tt = keys[-1][0]
    for dt, x, z, pose in (list(reversed(keys)) if reverse else keys):
        f = f0 + int(round(((tt - dt) if reverse else dt) * k))
        st.POSES["_k"] = pose; st.move_to(x, z, f); st.apply_pose("_k", f, face=False)
    return f0 + int(round(tt * k))
def getup(f, x_from, x_to, pose, z_from=0.15, n=8):
    """Yotgan joyidan sakrab turadi."""
    st.POSES["_h"] = pose; st.move_to(x_from, z_from, f); st.apply_pose("_h", f, face=False)
    st.POSES["_m"] = {"root": 48, "head": 70, "upper_arm.L": -30, "forearm.L": -70, "upper_arm.R": -120, "forearm.R": -100, "thigh.L": -150, "shin.L": -100, "thigh.R": -160, "shin.R": -110}
    st.move_to((x_from + x_to) / 2.0, 0.2, f + n // 2); st.apply_pose("_m", f + n // 2, face=False)
    st.move_to(x_to, 0.0, f + n); st.apply_pose("stand", f + n, face=False)
    return f + n

HOLD = {"upper_arm.L": -62, "forearm.L": 58, "upper_arm.R": -100, "forearm.R": -94, "head": 84}
NEUT = {"upper_arm.L": -78, "forearm.L": -92, "upper_arm.R": -102, "forearm.R": -88, "head": 88}
FISTL = {"upper_arm.L": 30, "forearm.L": 95}
st.POSES["hold"] = HOLD
st.POSES["hold_idea"] = dict(HOLD, **{"upper_arm.R": 152, "forearm.R": 94})
st.POSES["hold_press"] = dict(HOLD, **reach("R", BTN[0] + 0.02, BTN[1], X))
st.POSES["put"] = dict(HOLD, **reach("L", 1.3, 2.62, FRX))
st.POSES["point_dl"] = {"upper_arm.R": 230, "forearm.R": 240, "upper_arm.L": -45, "forearm.L": -131, "head": 97}
st.POSES["wipe"] = {"upper_arm.R": 128, "forearm.R": 52, "upper_arm.L": -80, "forearm.L": -86, "front": "R"}
st.POSES["tangle"] = {"thigh.L": -112, "shin.L": -124, "thigh.R": -66, "shin.R": -58, "upper_arm.L": 30, "forearm.L": 70, "upper_arm.R": 150, "forearm.R": 110, "root": 80}
st.POSES["rage"] = {"upper_arm.L": 45, "forearm.L": 100, "upper_arm.R": 135, "forearm.R": 80}
st.POSES["ready"] = dict(FISTL, **reach("R", BTN[0] + 0.06, BTN[1] + 0.5, X))
st.POSES["slam"] = dict(FISTL, **reach("R", BTN[0] + 0.02, BTN[1] - 0.03, X))
st.POSES["lunge"] = dict(reach("R", BTN[0] + 0.24, BTN[1] + 0.32, 0.0), **{"upper_arm.L": -40, "forearm.L": -70, "head": 92})
st.POSES["point_r"] = {"upper_arm.L": 4, "forearm.L": 10, "upper_arm.R": -100, "forearm.R": -94, "head": 86}
st.POSES["pay"] = dict(reach("R", -0.2, 2.35, X), **{"upper_arm.L": -80, "forearm.L": -86, "head": 94})
st.POSES["ticket"] = {"upper_arm.L": -62, "forearm.L": 58, "upper_arm.R": -100, "forearm.R": -94, "head": 90}

# ---------- sahna ----------
for n in ("Set_Door", "Set_DoorFrame", "Set_Calendar"): off(n, 1)
on("Set_TimeMachine", 1); on("Set_Fridge", 1)
BAN = O["FX_Banana"]; TOY = O["FX_Toy"]; HND = O["FX_Hand"]
put(BAN, 1, -0.5, 0.02, s=0.65, y=-0.2, step=True)
put(TOY, 1, -1.2, 0.0, s=0.9, y=-0.2, step=True)
TITLE = st.title("THE TIME-TRAVEL MISTAKE", f_on=-8)
st.move_to(X, 0.0, 1); st.apply_pose("hold", 1, face=False); st.mouth("sad", 1)
pizza(1, X + PZH, 2.5, s=PZS)
kid(FROST, 1, 1.0, step=False); kid(STEAM, 1, 0.0, step=False)

# ==== A) HOOK: sovuq pitsa -> "I can fix this!" -> vaqt mashinasi yonadi
st.cut(1, *MEDP)
st.brows(12, 0.02, 1); _B[:] = [12, 0.02, 0.0]; st.look(0.05, -0.02, 1); _LK[:] = [0.05, -0.02]
st.shiver(2, 32, 0.012)
a0 = 34
st.cut(a0, *WIDE)
st.snap("hold_idea", a0 + 2, lead=2, face=False)
brow(a0, -8, 0.04); look(a0, 0.0, 0.0)
e1 = say("S01", a0 + 2, volume=0.7, end="grin")       # bu gap baland o'qilgan (cho'qqi 0.87)
PRESS = e1 + 6
st.snap("hold_press", PRESS, lead=3, over=0.1, face=False)
look(PRESS - 3, -0.05, -0.02)
press(PRESS + 1); st.sfx("pop", PRESS + 1, 0.7); st.sfx("boom", PRESS + 1, 0.3)
kid(BULB, PRESS + 2, 1.0)
st.fx("star", PRESS + 1, BTN[0] + 0.05, BTN[1] + 0.45, 0.6)

# ==== B) VAQT ORQAGA: muz eriydi, pitsa issiq bo'ladi
r0 = PRESS + 7; r1 = r0 + 54
time_fx(r0, r1, "<< REWIND")
dial(r0, r1, -5)
s = st.sfx("rewind", r0, 0.6); st._set_end(s, r1 + 2)
bulb_pulse(r0, r1)
st.snap("hold", r0 + 2, lead=3, face=False); look(r0 + 2, 0.05, -0.02); brow(r0 + 2, 0, 0.08); st.mouth("open", r0 + 2)
FROST.keyframe_insert("scale", frame=r0 + 8); FROST.scale = (0.0, 0.0, 0.0); FROST.keyframe_insert("scale", frame=r0 + 28)
kid(STEAM, r0 + 28, 1.0)
wflash(r1, 2); st.sfx("ding", r1, 0.5)

# ==== C) ISSIQ PITSA: xursand
c0 = r1 + 2
st.cut(c0, *MEDP)
st.mouth("grin", c0); brow(c0, 0, 0.09); look(c0, 0.05, -0.02)
st.punch(c0 + 10, 0.04); st.punch(c0 + 20, 0.04); st.punch(c0 + 30, 0.04)                  # hidlaydi
c1 = c0 + 40

# ==== D) ...va uni yana muzlatgichga solib qo'yadi
st.cut(c1, *WIDE)
w1 = c1 + 24
st.apply_pose("hold", c1 - 1, face=False)
st.walk(c1, w1, X, FRX, step=6, arms=HOLD)
for f in list(range(c1, w1, 6)) + [w1]:
    pizza(f, X + (FRX - X) * (f - c1) / float(w1 - c1) + PZH, 2.5, s=PZS)
steam(r0 + 28, w1 + 8)
st.mouth("smile", c1); look(c1, 0.05, 0.0)
st.cut(w1 - 6, *FRIDGE_CAM)
st.apply_pose("hold", w1 + 2, face=False)
DO = w1 + 4                                                       # eshikcha ochiladi
door(DO, 0.12); st.sfx("pop", DO, 0.5)
st.snap("put", DO + 7, lead=3, face=False)
pizza(DO + 4, FRX + PZH, 2.5, s=PZS)
pizza(DO + 9, 1.47, 2.72, s=0.72, y=0.34)
STEAM.scale = (1.0, 1.0, 1.0); kid(STEAM, DO + 9, 0.0)
DC = DO + 16                                                      # eshikcha yopiladi
door(DC, 1.0); st.sfx("slam", DC, 0.3)
kid(FROST, DC, 1.0)
st.snap("hips", DC + 3, lead=3, face=False); st.mouth("grin", DC + 3); brow(DC + 3, 0, 0.05); look(DC + 3, 0.0, 0.0)
st.sfx("ding", DC + 4, 0.6)
st.fx("dust", DC + 1, 1.2, 2.3, 0.8)
q0 = DC + 30                                                      # "shoshma..."
st.prop("question", q0, q0 + 18, x=0.45, z=3.2, size=0.6)
st.mouth("neutral", q0); brow(q0, 6, 0.03, 0.05); look(q0, 0.05, 0.02); st.sfx("pop", q0, 0.4)
st.snap("shrug", q0 + 20, lead=3, face=False); st.mouth("smile", q0 + 20); brow(q0 + 20, 0, 0.04); look(q0 + 20, 0.0, 0.0)
d1 = q0 + 40

# ==== E) BANAN PO'STI: sirpanib yiqiladi
st.cut(d1, *WIDE)
SL = d1 + 30
st.apply_pose("shrug", d1 - 1, face=False)
st.walk(d1, SL, FRX, -0.3, step=6, arms=NEUT)
look(d1, -0.04, 0.0)
st.cut(SL - 12, *FLOOR_CAM); title_off(SL - 12, SL + 2)             # banan yaqin planda
st.cut(SL + 2, *WIDE)
SLIP = fall_keys(-0.3)
land1 = play(SLIP, SL)
st.eyes("wide", SL); st.mouth("scream", SL); brow(SL, 0, 0.1)
st.sfx("jump", SL, 0.5); st.sfx("splat", land1, 0.4); st.sfx("land", land1, 0.3)
st.fx("star", land1, 1.15, 1.05, 0.7); st.fx("dust", land1, 0.2, 0.1, 1.0); st.shake(land1, land1 + 6, 0.06)
st.eyes("normal", land1 + 2); st.squint(land1 + 2, 0.1); st.mouth("open", land1 + 2)
b0 = land1 + 24

# ==== F) TUGMA: vaqtni orqaga qaytaradi
HZ = BTN[1] + 0.04
st.cut(b0, *BTN1_CAM); title_off(b0, b0 + 14)
put(HND, b0, 0.25, 1.2, y=-0.5, step=True); put(HND, b0 + 5, BTN[0], HZ, y=-0.5)
press(b0 + 5); st.sfx("hit", b0 + 5, 0.5); st.sfx("pop", b0 + 5, 0.5); st.fx("star", b0 + 5, BTN[0] + 0.3, BTN[1] + 0.3, 0.5)
put(HND, b0 + 9, BTN[0], HZ, y=-0.5); put(HND, b0 + 13, 0.25, 1.2, y=-0.5); put(HND, b0 + 14, 0.25, 1.2, s=0.0, y=-0.5, step=True)
b1 = b0 + 14

# ==== G) REWIND: yiqilish teskari o'ynaydi
g0 = b1; g1 = g0 + 38
st.cut(g0, *WIDE)
time_fx(g0, g1, "<< REWIND")
dial(g0, g1, -4)
s = st.sfx("rewind", g0, 0.6); st._set_end(s, g1 + 1)
up1 = play(SLIP, g0 + 2, reverse=True, k=1.25)
st.squint(g0 + 6, 1.0); st.mouth("neutral", g0 + 6)
st.walk(up1, g1 - 2, -0.3, FRX, step=4, arms=NEUT)
wflash(g1, 2)

# ==== H) BANANDAN O'TADI... va o'yinchoq mashinaga tushadi
h0 = g1 + 2
STOPX = 0.35
st.walk(h0, h0 + 12, FRX, STOPX, step=6, arms=NEUT)
st.apply_pose("stand", h0 + 14, face=False)
brow(h0 + 14, -6, 0.02); look(h0 + 14, -0.05, -0.05)
st.snap("point_dl", h0 + 19, lead=3, face=False); st.mouth("grin", h0 + 19)
st.sfx("pop", h0 + 19, 0.4)
HP = h0 + 48
st.snap("cheer", HP + 2, lead=2, face=False); look(HP, 0.0, 0.0); brow(HP, 0, 0.06)
st.move_to(STOPX, 0.0, HP); st.move_to(-1.0, 0.0, HP + 12)
st.bounce(HP, 0.6, 12, sound=0.5)
LAND = HP + 12
put(TOY, LAND, -1.2, 0.0, s=0.9, y=-0.2); put(TOY, LAND + 3, -0.6, 0.25, rot=-0.5, s=0.9, y=-0.2); put(TOY, LAND + 12, 3.2, 0.9, rot=-6.0, s=0.9, y=-0.2)
put(TOY, LAND + 13, 3.2, 0.9, s=0.0, y=-0.2, step=True)
st.sfx("spring", LAND, 0.45); st.sfx("whoosh", LAND + 1, 0.6)
SLIP2 = fall_keys(-1.0)
land2 = play(SLIP2, LAND + 1)
st.eyes("wide", LAND); st.mouth("scream", LAND); brow(LAND, 0, 0.1)
st.sfx("splat", land2, 0.4); st.sfx("land", land2, 0.3)
st.fx("star", land2, 1.15, 1.05, 0.7); st.fx("dust", land2, 0.2, 0.1, 1.0); st.shake(land2, land2 + 6, 0.06)
st.eyes("normal", land2 + 2); st.squint(land2 + 2, 0.1); st.mouth("sad", land2 + 2); brow(land2 + 2, 10, 0.0)
i0 = land2 + 26

# ==== I) O'Z OYOG'IGA QOQILADI
UPX = -1.62
up2 = getup(i0, -1.55, UPX, LYING)
st.squint(i0 + 4, 1.0); look(i0 + 6, -0.05, 0.0)
look(up2 + 5, 0.05, 0.0); look(up2 + 10, 0.0, -0.04)                  # atrofga, keyin yerga qaraydi: toza
st.snap("wipe", up2 + 14, lead=3, face=False); st.mouth("smile", up2 + 14); brow(up2 + 14, 0, 0.07); look(up2 + 14, 0.0, 0.0)
st.prop("sweat", up2 + 14, up2 + 26)
TR = up2 + 30
st.snap("tangle", TR + 3, lead=3, over=0.0, settle=1, face=False)
st.eyes("wide", TR + 2); st.mouth("open", TR + 2)
st.sfx("fall", TR - 4, 0.3)
st.move_to(UPX, 0.0, TR + 4)
st.flat(TR + 10, x=UPX)
thud = TR + 10
st.sfx("land", thud, 0.6); st.sfx("splat", thud, 0.3)
st.fx("dust", thud, 0.3, 0.1, 1.1); st.fx("star", thud, 0.95, 1.05, 0.7); st.shake(thud, thud + 7, 0.07)
st.eyes("normal", thud + 1); st.squint(thud + 1, 0.1); st.mouth("neutral", thud + 1)
put(BAN, thud, -0.5, 0.02, s=0.65, y=-0.2); put(BAN, thud + 10, 2.9, 3.2, rot=7.0, s=0.65, y=-0.2); put(BAN, thud + 11, 2.9, 3.2, s=0.0, y=-0.2, step=True)   # banan uchib ketadi
j0 = thud + 32

# ==== J) JAHL
up3 = getup(j0, UPX, X, st.POSES["_flat"])
st.cut(up3 + 1, *RAGE_CAM)
st.sfx("whoosh", j0 + 2, 0.6)
st.squint(j0 + 6, 1.0)
st.snap("rage", up3 + 2, lead=2, face=False)
brow(up3, -18, 0.02); st.mouth("scream", up3 + 2); look(up3, 0.0, 0.0)
st.shake(up3 + 2, up3 + 28, 0.03); st.fx("lines", up3 + 2, X, HEAD, 1.0, length=26)
st.sfx("rumble", up3 + 2, 0.38)
k0 = up3 + 32

# ==== K) MASHINA: 100 MILLION YIL ORQAGA
st.cut(k0, *MACH_CAM)
st.snap("ready", k0, lead=2, face=False); st.mouth("neutral", k0)
vals = ("TODAY", "-100", "-10,000", "-1,000,000", "-100,000,000")
l0 = k0 + 4 + len(vals) * 7 + 8
for i, v in enumerate(vals):
    f = k0 + 4 + i * 7
    last = (i == len(vals) - 1)
    st.flash(v, f, l0 + 8 if last else f + 7, z=0.48, size=0.14, x=-1.35, max_width=0.84, color="red" if last else "gold")
    st.sfx("tick", f, 1.0)
dial(k0 + 4, l0, -6)
bulb_pulse(k0, l0 + 8)
st.snap("slam", l0, lead=2, over=0.0, face=False)
press(l0); st.sfx("hit", l0, 0.45); st.sfx("boom", l0, 0.3); st.fx("star", l0, BTN[0] - 0.02, BTN[1] + 0.52, 0.5); st.shake(l0, l0 + 7, 0.06)

# ==== M) O'TMISHGA SAKRASH
m0 = l0 + 8; m1 = m0 + 40; SW = m0 + 20
st.cut(m0, *WIDE)
st.snap("stand", m0, lead=2, face=False); brow(m0, 0, 0.08); st.mouth("open", m0); st.eyes("wide", m0)
time_fx(m0, m1, "<< 100,000,000 YEARS")
dial(m0, m1, -12)
st.sfx("rewind", m0, 0.6)
wflash(SW, 3)
for n in ("Set_Floor", "Set_Fridge"): off(n, SW)
on("Past_Back", SW)
pizza(SW, 1.47, 2.72, s=0.72, y=0.3, step=True)
look(m1, -0.05, 0.0); look(m1 + 8, 0.05, 0.0)
st.eyes("normal", m1 + 8)
PD = m1 + 16                                                      # muzlatgich yo'q - pitsa havoda qolib, keyin tushadi
pizza(PD, 1.47, 2.72, s=0.72, y=0.3); pizza(PD + 3, 1.47, 2.8, s=0.72, y=0.3)
pizza(PD + 10, PZX, PZG, rot=1.4, s=0.8, y=0.3); pizza(PD + 12, PZX, PZG + 0.12, rot=1.4, s=0.8, y=0.3); pizza(PD + 14, PZX, PZG, rot=1.4, s=0.8, y=0.3)
st.sfx("pop", PD + 10, 0.5)
look(PD + 2, 0.05, 0.02); look(PD + 10, 0.05, -0.05)
WK = PD + 24                                                      # "pitsam!" - unga qarab yuradi
st.mouth("grin", WK); brow(WK, 0, 0.07)
st.apply_pose("stand", WK - 1, face=False)
st.walk(WK, WK + 18, X, 0.5, step=6, arms=NEUT)

# ==== N) DINOZAVRLAR
DA = O["Dino_A"]; DB = O["Dino_B"]; DP = O["Dino_Peek"]
n0 = WK + 18
put(DA, n0, 4.4, 1.35, y=0.55, step=True); put(DA, n0 + 6, 2.02, 1.35, y=0.55); put(DA, n0 + 9, 2.15, 1.35, y=0.55)
pupil("Dino_A", n0, -0.05, 0.0)
st.sfx("roar", n0, 0.68); st.shake(n0 + 4, n0 + 16, 0.06)
st.move_to(0.5, 0.0, n0 + 4); st.move_to(X, 0.0, n0 + 9); st.hop(n0 + 4, 0.3, 6)       # orqaga sakraydi
st.snap("shock", n0 + 6, lead=2, face=False); st.eyes("wide", n0 + 5); st.mouth("scream", n0 + 5); brow(n0 + 5, 0, 0.1); look(n0 + 5, 0.05, -0.03)
st.fx("lines", n0 + 9, X, HEAD, 1.0, length=16)
n1 = n0 + 36
put(DB, n1, -4.4, 3.55, s=(-1, 1, 1), y=0.55, step=True); put(DB, n1 + 6, -2.02, 3.55, s=(-1, 1, 1), y=0.55); put(DB, n1 + 9, -2.15, 3.55, s=(-1, 1, 1), y=0.55)
pupil("Dino_B", n1, -0.045, -0.035)
st.sfx("roar_small", n1, 0.3); st.shake(n1 + 4, n1 + 14, 0.05)
look(n1 + 6, -0.05, 0.04)
n2 = n1 + 32
put(DP, n2, 0.7, -2.5, y=-0.6, step=True); put(DP, n2 + 6, 0.7, -0.9, y=-0.6); put(DP, n2 + 9, 0.7, -1.0, y=-0.6)
pupil("Dino_Peek", n2, -0.04, 0.04)
st.sfx("pop", n2 + 5, 0.6)
look(n2 + 8, 0.02, -0.06)
st.prop("sweat", n0 + 12, n2 + 40)
st.shiver(n0 + 18, n2 + 14, 0.014)

# ==== O) HAMMASI PITSAGA TIKILADI
o0 = n2 + 30
st.caption("100,000,000 YEARS AGO", m1 - 2, o0 + 15, z=2.28, size=0.26, color="red", hud=True)
pupil("Dino_A", o0, -0.01, -0.055); st.sfx("tick", o0, 1.0)
pupil("Dino_B", o0 + 6, -0.05, -0.03); st.sfx("tick", o0 + 6, 1.0)
pupil("Dino_Peek", o0 + 12, 0.05, 0.04); st.sfx("tick", o0 + 12, 1.0)
look(o0 + 14, 0.05, -0.05)                                         # Sticky ham pitsaga qaraydi
st.cut(o0 + 18, *PIZZA_CAM)
put(DP, o0 + 18, 0.95, -0.78, y=-0.6, step=True)                  # yaqin planda pastdagi dinozavrning ikki ko'zi ham ko'rinsin
hb = st.sfx("heart", o0 + 14, 0.45)
DR = O["FX_Drool"]
for dk in (o0 + 24, o0 + 42, o0 + 60):                                     # so'lak
    put(DR, dk, 1.02, 1.12, s=0.5, y=0.3, step=True); put(DR, dk + 5, 1.02, 1.05, s=1.0, y=0.3); put(DR, dk + 13, 1.02, 0.5, s=1.0, y=0.3); put(DR, dk + 14, 1.02, 0.5, s=0.0, y=0.3, step=True)
    st.sfx("pop", dk + 13, 0.3)
sparkle(1, o0 + 30, 1.75, 0.62, 0.55); sparkle(2, o0 + 42, 1.2, 0.56, 0.55)
st.zoom(o0 + 18, o0 + 76, z=0.97, scale=2.85)
p0 = o0 + 78

# ==== P) MASHINAGA TASHLANADI - DINOZAVR TUGMANI BIRINCHI BOSADI
st._set_end(hb, p0)
st.cut(p0, *WIDE)
put(DP, p0, 0.7, -1.0, y=-0.6, step=True)
look(p0, -0.05, 0.0); brow(p0, -6, 0.08)
RUN = p0 + 8
st.apply_pose("shock", RUN, face=False); st.move_to(X, 0.0, RUN)
st.move_to(0.0, 0.0, RUN + 4); st.apply_pose("lunge", RUN + 4, face=False)
st.sfx("whoosh", RUN, 0.7); st.fx("dust", RUN + 1, 0.4, 0.1, 0.9)
E2 = RUN + 4
st.cut(E2, *BTN2_CAM); title_off(E2, E2 + 28)
DARM = O["Dino_Arm"]
put(DARM, E2, -1.05, 3.1, rot=-0.42, y=0.6, step=True); put(DARM, E2 + 4, BTN[0], BTN[1] - 0.08, rot=-0.42, y=0.6)
press(E2 + 4); st.sfx("pop", E2 + 4, 0.7); st.sfx("boom", E2 + 4, 0.35); st.fx("star", E2 + 4, BTN[0] - 0.02, BTN[1] + 0.55, 0.45)
st.eyes("wide", E2 + 4); st.mouth("open", E2 + 4); brow(E2 + 4, 8, 0.1); look(E2 + 4, -0.05, -0.03)
st.punch(E2 + 5, 0.07)
q0 = E2 + 28

# ==== Q) KELAJAKKA
q1 = q0 + 36; SW2 = q0 + 18
st.cut(q0, *WIDE)
time_fx(q0, q1, ">> FAST FORWARD")
dial(q0, q1, 12)
st.sfx("ffwd", q0, 0.6)
wflash(SW2, 3)
for ob in (DA, DB, DP, DARM):
    keyall(ob, SW2 - 1); ob.scale = (0.0, 0.0, 0.0); ob.keyframe_insert("scale", frame=SW2)
off("Past_Back", SW2)
for n in ("Mus_Back", "Mus_Case", "Mus_Shine", "Mus_Sign", "Mus_Tickets"): on(n, SW2)
RB = O["Robo_Dino"]; RARM = O["Robo_Arm"]
put(RB, SW2, -2.15, 3.55, s=(-1, 1, 1), y=0.55, step=True)
pupil("Robo_Dino", SW2, -0.03, -0.05)
pizza(SW2, PZX, 1.78, rot=0.0, s=0.8, y=0.34, step=True)
kid(FROST, SW2, 0.0)
kid(BULB, SW2, 0.0)                                               # kelajakda chiroq o'chadi (TICKETS yozuvini to'smasin)
st.move_to(0.0, 0.0, SW2 - 1); st.move_to(X, 0.0, SW2); st.apply_pose("lunge", SW2 - 1, face=False); st.apply_pose("stand", SW2, face=False)
st.eyes("normal", SW2); st.mouth("neutral", SW2); brow(SW2, 0, 0.06); look(SW2, 0.0, 0.0)

# ==== R) MUZEY
st.plate(q1 + 1, q1 + 46, 2.14); st.caption("THE FUTURE", q1 + 2, q1 + 46, z=2.14, size=0.4, hud=True)
st.sfx("ding", q1 + 1, 0.6)
look(q1 + 8, -0.05, 0.04); look(q1 + 20, 0.05, 0.0)
RP = O["Robo_Dino_Pupil"]
for k, f in enumerate(range(q1, q1 + 420, 6)):                     # robot ko'zi miltillaydi
    sc = 1.35 if k % 2 == 0 else 0.9
    RP.scale = (sc, sc, sc); RP.keyframe_insert("scale", frame=f)
st.sfx("glitch", q1 + 8, 0.3)
r_0 = q1 + 48
st.cut(r_0, *CASE_CAM)
SH = O["Mus_Shine"]
put(SH, r_0, 1.33, 0.0, y=0.26); put(SH, r_0 + 44, 1.6, 0.0, y=0.26)
sparkle(3, r_0 + 6, 1.0, 2.5, 0.5); sparkle(4, r_0 + 18, 1.92, 1.6, 0.5)
st.sfx("ding", r_0 + 2, 0.5)
st.zoom(r_0, r_0 + 48, z=2.25, scale=2.8)
s_0 = r_0 + 50

# ==== S) "BU MENING PITSAM-KU"
st.cut(s_0, *DUO_CAM)
st.snap("point_r", s_0 + 2, lead=2, face=False)
st.eyes("wide", s_0); st.mouth("open", s_0); brow(s_0, 6, 0.1); look(s_0, 0.05, -0.02)
st.punch(s_0 + 2, 0.06)
look(s_0 + 20, 0.0, 0.0); st.eyes("normal", s_0 + 20); st.mouth("neutral", s_0 + 20); brow(s_0 + 20, 0, 0.0)
t0 = s_0 + 42

# ==== T) CHIPTA SOTIB OLADI: robot pulni yutadi, chipta beradi
TK = O["FX_Ticket"]; NOTE = O["Note_1"]
st.cut(t0, *WIDE)
CL = (-0.5, 2.72)                                                 # robot panjasi to'xtaydigan joy
put(RARM, t0 + 2, -1.1, 3.4, rot=-0.5, y=0.6, step=True); put(RARM, t0 + 9, CL[0], CL[1], rot=-0.5, y=0.6)
put(TK, t0 + 2, -1.04, 3.3, rot=0.25, y=-0.16, step=True); put(TK, t0 + 9, CL[0] + 0.05, CL[1] - 0.1, rot=0.25, y=-0.16)
st.sfx("glitch", t0 + 2, 0.3); st.sfx("pop", t0 + 9, 0.5)
st.apply_pose("point_r", t0, face=False); st.snap("stand", t0 + 4, lead=3, face=False)
look(t0 + 6, -0.05, 0.03); brow(t0 + 6, 8, 0.02)
st.snap("slump", t0 + 20, lead=4, face=False); st.mouth("sad", t0 + 20)          # xo'rsinadi
PAY = t0 + 40
st.snap("pay", PAY, lead=3, face=False)
put(NOTE, PAY, -0.2, 2.35, s=0.8, y=-0.16, step=True); put(NOTE, PAY + 8, -0.2, 2.35, s=0.8, y=-0.16)
put(NOTE, PAY + 16, -0.95, 3.42, rot=0.6, s=0.45, y=-0.16); put(NOTE, PAY + 17, -0.95, 3.42, s=0.0, y=-0.16, step=True)
st.sfx("whoosh", PAY + 8, 0.4); st.sfx("chaching", PAY + 16, 0.55)
put(TK, PAY + 20, CL[0] + 0.05, CL[1] - 0.1, rot=0.25, y=-0.16); put(TK, PAY + 27, -0.18, 2.38, rot=0.1, y=-0.16)
st.sfx("pop", PAY + 27, 0.5)
put(RARM, PAY + 27, CL[0], CL[1], rot=-0.5, y=0.6); put(RARM, PAY + 34, -1.1, 3.4, rot=-0.5, y=0.6); put(RARM, PAY + 35, -1.1, 3.4, rot=-0.5, s=0.0, y=0.6, step=True)
u0 = PAY + 40

# ==== U) YAKUN: o'z pitsasini ko'rish uchun chipta ushlab turibdi
st.cut(u0, 0.82, 2.55, 4.4)
st.apply_pose("pay", u0 - 1, face=False); st.apply_pose("ticket", u0, face=False)
put(TK, u0 - 1, -0.18, 2.38, rot=0.1, y=-0.16); put(TK, u0, X + 0.63, 2.52, rot=-0.15, y=-0.16)
st.mouth("neutral", u0); brow(u0, 0, 0.0); look(u0, 0.05, -0.02)
look(u0 + 16, 0.0, 0.0)                                            # kameraga qaraydi
st.blink(u0 + 34)
st.plate(u0 + 20, 5000, -2.7, lines=2)
st.caption("PAID $20 TO SEE", u0 + 21, 5000, z=-2.45, size=0.3, hud=True)
st.caption("HIS OWN PIZZA", u0 + 27, 5000, z=-2.98, size=0.5, color="red", hud=True)
st.sfx("ding", u0 + 21, 0.6); st.sfx("trombone", u0 + 27, 0.45)
st.zoom(u0, u0 + 122, z=2.57, scale=4.3)
END = u0 + 124
S.frame_end = END

# ---------- musiqa ----------
GAIN = 1.3
m = st.music("//musiqa_03_sneaky.wav", volume=0.1, fade=20, end=END + 1)
MV = ((1, 0.2), (a0, 0.2), (a0 + 4, 0.1), (e1 + 2, 0.1), (e1 + 8, 0.2), (o0 + 12, 0.2), (o0 + 14, 0.0), (p0 - 1, 0.0), (p0 + 2, 0.22),
      (u0 + 18, 0.2), (u0 + 24, 0.12), (END - 19, 0.12), (END + 1, 0.0))
for f, v in MV:
    m.volume = v * GAIN; m.keyframe_insert("volume", frame=f)
st.sfx("scratch", o0 + 13, 0.7)
for s_ in st._strips():
    if s_.type == 'SOUND' and not s_.name.startswith("Music"): s_.volume *= GAIN
st.alive(1, END, blink_skip=[(SL - 2, g0 + 8), (LAND - 2, i0 + 8), (TR - 2, up3 + 4), (m0, m1 + 10), (n0, q1), (s_0, s_0 + 22), (u0, END)])
S.frame_set(1)
MARKS = dict(a0=a0, e1=e1, PRESS=PRESS, r0=r0, r1=r1, c0=c0, c1=c1, w1=w1, DO=DO, DC=DC, d1=d1, SL=SL, land1=land1, b0=b0, g0=g0, g1=g1, h0=h0,
             HP=HP, LAND=LAND, land2=land2, i0=i0, TR=TR, thud=thud, j0=j0, up3=up3, k0=k0, l0=l0, m0=m0, SW=SW, m1=m1, PD=PD, WK=WK, n0=n0, n1=n1, n2=n2, o0=o0, p0=p0,
             RUN=RUN, E2=E2, q0=q0, SW2=SW2, q1=q1, r_0=r_0, s_0=s_0, t0=t0, PAY=PAY, u0=u0, END=END)
bpy.app.driver_namespace["v09_marks"] = MARKS
