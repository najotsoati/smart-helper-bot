# video_13.py  -  "She Invested for 10 Years. He Started Later." (hikoyachi: Fenrir, Kokoro TTS)
import bpy, os, math, random, aud
T = bpy.data.texts["stickman_tools.py"]
st = T.as_module()                        # Sticky
ly = T.as_module(); ly.use("L_")          # Lily
S = bpy.context.scene
O = bpy.data.objects
A = "//video_13_audio/"
LXP, SXP = -1.2, 1.2                      # Lily va Sticky joyi
LJ, SJ = -0.45, 0.45                      # ularning bankalari
WIDE = (0.0, 2.3, 7.0)
CHART = (70.0, 2.3, 7.0)
GAIN = 1.3

st.clear_animation()
ly.clear_animation(); ly.show()
st.backdrop("room")
S.frame_end = 1800
S.render.filepath = "//She Invested for 10 Years. He Started Later.mp4"

EST = {"K1": 150, "K2": 92, "K3": 196, "K4": 265, "K5": 150, "K6": 81, "K7": 150, "K8": 92}
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
def P(m, name, f):
    m.apply_pose(name, f, face=False)
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
for m in (st, ly):
    m.POSES["dropL"] = pose(reach("L", 0.62, 1.95))          # o'ng tomondagi bankaga tanga
    m.POSES["dropR"] = pose(reach("R", -0.62, 1.95))         # chap tomondagi bankaga tanga
    m.POSES["sign"] = pose(reach("L", 0.38, 1.45), reach("R", -0.2, 1.5))
    m.POSES["watch"] = pose(reach("R", -0.15, 2.45), reach("L", 0.2, 2.35))
    m.POSES["plant"] = pose(reach("R", -0.55, 1.35))
JL = (O["FX_JarBack"], O["FX_JarFill"], O["FX_JarFront"])
JS = (O["FX_Jar2Back"], O["FX_Jar2Fill"], O["FX_Jar2Front"])
def jar(J, f, x, fill, step=False, s=1.0):
    put(J[0], f, x, 0.0, s=s, step=step); put(J[2], f, x, 0.0, s=s, step=step)
    put(J[1], f, x, 0.03 * s, s=(s, s, max(fill, 0.001) * 0.75 * s), step=step)
def fill_to(J, f, x, fill):
    put(J[1], f, x, 0.03, s=(1.0, 1.0, max(fill, 0.001) * 0.75))
PL = O["HUD_Plate1"]
def board(f0, f1):
    PL.location = (0.0, -2.75, -5.06); PL.keyframe_insert("location", frame=f0 - 1)
    skey(PL, ((f0 - 1, 0.0), (f0 + 3, 1.08), (f0 + 6, 1.0), (f1 - 1, 1.0), (f1, 0.0)))
coin_i = [0]
def coin(f, x0, z0, x1, z1):
    coin_i[0] = coin_i[0] % 10 + 1; n = "Coin_%d" % coin_i[0]
    st.place(n, f, x=x0, z=z0, scale=0.55, step=True); st.place(n, f + 6, x=x1, z=z1); st.place(n, f + 7, scale=0.0, step=True)

# ---------- yillik balans (oyiga $200, yiliga 8%) ----------
r = 0.08 / 12; Lb = Sb = 0.0; BAL = {}
for mth in range(1, 481):
    Lb = Lb * (1 + r) + (200 if mth <= 120 else 0); Sb = Sb * (1 + r) + (200 if mth > 120 else 0)
    if mth % 12 == 0: BAL[25 + mth // 12] = (Lb, Sb)
BAL[25] = (0.0, 0.0)

off("Set_Calendar", 1)
for n in ("Set_Floor", "Set_Door", "Set_DoorFrame"): off(n, 1)
on("Hill_Back", 1); on("Chart_BoardPlain", 1)
TITLE = st.title("WHO HAS MORE AT 65?", f_on=-8, size=0.42)
ly.move_to(LXP, 0.0, 1); st.move_to(SXP, 0.0, 1)
P(ly, "stand", 1); P(st, "stand", 1); ly.mouth("smile", 1); st.mouth("smile", 1)
jar(JL, 1, LJ, 0.0, step=True); jar(JS, 1, SJ, 0.0, step=True)

# ---------- ovoz kursori ----------
H0 = 45
e1 = N("K1", H0)
c2 = e1 + 4
e2 = N("K2", c2 + 4)
c3 = e2 + 6
e3 = N("K3", c3 + 4)
c4 = e3 + 6
e4 = N("K4", c4 + 4)
e5 = N("K5", e4 + 6)
c6 = e5 + 8
e6 = N("K6", c6 + 4)
c7 = e6 + 6
e7 = N("K7", c7 + 4)
c8 = max(e7, c7 + 120) + 6
e8 = N("K8", c8 + 4)
END = e8 + 45
S.frame_end = END

# ---------- kamera ----------
st.cut(1, *WIDE)
st.cut(c4, *CHART)
st.cut(c6, *WIDE)
st.cut(c7, 1.05, 2.1, 4.6)
st.cut(c8, *WIDE)
skey(TITLE, ((c7 - 1, 1.0), (c7, 0.0), (c8 - 1, 0.0), (c8, 1.0)))

# ================= A. Hook =================
st.caption("LILY: 10 YEARS", -8, H0 + 30, z=3.85, x=LXP + 0.1, size=0.24, color="green", max_width=1.5)
st.caption("STICKY: 30 YEARS", -8, H0 + 30, z=3.85, x=SXP - 0.1, size=0.24, color="black", max_width=1.5)
st.caption("WHY DID SHE WIN?", 8, H0 + 30, z=4.35, x=0.0, size=0.36, color="red")
st.sfx("ding", 1, 0.4); st.sfx("pop", 8, 0.45)

# ================= B. Lily 25 yoshda boshlaydi, Sticky "keyin" =================
board(H0, c4)
st.flash("AGE 25", H0, c2 + 4, z=-2.75, x=-0.95, size=0.34, color="black", hud=True)
st.flash("$200 / MONTH", H0, c2 + 4, z=-2.75, x=0.8, size=0.3, color="green", hud=True, max_width=1.8)
P(st, "stand", H0 - 1); P(st, "sign", H0 + 2); popin("FX_Sign", H0 + 2, x=SXP + 0.38, z=0.75, s=0.8)
st.mouth("grin", H0 + 2); st.sfx("pop", H0 + 2, 0.4)
for k in range(5):
    f = H0 + 10 + k * 24
    P(ly, "stand", f - 1); P(ly, "dropL", f + 2); P(ly, "stand", f + 9)
    coin(f + 2, LXP + 0.62, 1.95, LJ, 0.9); st.sfx("chaching", f + 8, 0.3)
    fill_to(JL, f + 8, LJ, 0.04 * (k + 1))

# ================= C. 35 yoshda to'xtaydi =================
for i, age in enumerate(range(26, 36)):
    f0 = c2 + 4 + i * 3; f1 = c2 + 4 + (i + 1) * 3 if age < 35 else c3
    st.flash("AGE %d" % age, f0, f1, z=-2.75, x=-0.95, size=0.34, color="black", hud=True)
    st.sfx("tick", f0, 0.7)
st.flash("LILY PUT IN $24,000", c2 + 34, c3, z=-2.75, x=0.65, size=0.24, color="green", hud=True, max_width=2.0)
fill_to(JL, c2 + 34, LJ, 0.35)
st.caption("STOPPED", c2 + 36, c3 + 20, z=3.85, x=LXP + 0.1, size=0.3, color="red")
st.sfx("pop", c2 + 36, 0.45)
P(ly, "stand", c2 + 34); P(ly, "hips", c2 + 38); ly.mouth("smile", c2 + 38); P(ly, "hips", c3 + 6); P(ly, "stand", c3 + 12)

# ================= D. Sticky 35 dan 65 gacha =================
off("FX_Sign", c3); P(st, "sign", c3 - 1); P(st, "stand", c3 + 1); st.mouth("smile", c3 + 1)
for i, age in enumerate(range(36, 66)):
    f0 = c3 + 8 + int(i * 4.5); f1 = c3 + 8 + int((i + 1) * 4.5) if age < 65 else c4
    st.flash("AGE %d" % age, f0, f1, z=-2.75, x=-0.95, size=0.34, color="black", hud=True)
    if age % 2 == 0: st.sfx("tick", f0, 0.6)
for k in range(6):
    f = c3 + 14 + k * 24
    P(st, "stand", f - 1); P(st, "dropR", f + 2); P(st, "stand", f + 9)
    coin(f + 2, SXP - 0.62, 1.95, SJ, 0.9); st.sfx("chaching", f + 8, 0.3)
    fill_to(JS, f + 8, SJ, 0.12 * (k + 1) * 0.9)
st.flash("STICKY PUT IN $72,000", c3 + 142, c4, z=-2.75, x=0.65, size=0.24, color="black", hud=True, max_width=2.0)
ly.squint(c3 + 40, 0.55); ly.mouth("smile", c3 + 40)

# ================= E. Grafik: 25 dan 65 gacha =================
BL, BS = O["Chart_B3"], O["Chart_B1"]
XL, XS = 69.35, 70.65
TOPV = 400130.0; HMAX = 3.5
R0 = c4 + 10; R1 = c4 + 4 + int((e4 - c4 - 4) * 0.9)
for ob, x in ((BL, XL), (BS, XS)):
    put(ob, c4, x, -0.38, s=(1.3, 1.0, 0.001), step=True)
ages = list(range(25, 66))
for i, age in enumerate(ages):
    f = R0 + int((R1 - R0) * i / 40.0)
    lv, sv = BAL[age]
    put(BL, f, XL, -0.38, s=(1.3, 1.0, max(lv / TOPV * HMAX, 0.001)))
    put(BS, f, XS, -0.38, s=(1.3, 1.0, max(sv / TOPV * HMAX, 0.001)))
    if age % 5 == 0 or age == 65:
        st.flash("AGE %d" % age, f, (R0 + int((R1 - R0) * (i + 5) / 40.0)) if age < 65 else c6, z=4.25, x=70.0, size=0.4, color="black")
        st.sfx("tick", f, 0.7)
for ob, x in ((BL, XL), (BS, XS)):
    put(ob, c6 - 1, x, -0.38, s=(1.3, 1.0, ob.scale.z)); put(ob, c6, x, -0.38, s=0.0)
st.caption("LILY", c4 + 4, c6, z=-0.62, x=XL, size=0.26, color="green")
st.caption("STICKY", c4 + 4, c6, z=-0.62, x=XS, size=0.24, color="black")
st.caption("≈ $400,000", e4 + 6, c6, z=-0.38 + HMAX + 0.25, x=XL, size=0.22, color="green", max_width=1.3)
st.caption("≈ $298,000", e4 + 20, c6, z=-0.38 + 298072 / TOPV * HMAX + 0.25, x=XS, size=0.22, color="black", max_width=1.3)
st.caption("8% A YEAR - EXAMPLE, NOT A PROMISE", c4 + 30, c6, z=-0.85, x=70.0, size=0.13, color="black", max_width=3.0)
st.sfx("pop", e4 + 6, 0.5); st.sfx("pop", e4 + 20, 0.45); st.sfx("ding", e4 + 7, 0.35)

# ================= F. Vaqt pulni o'stiradi =================
off("FX_Sign", c6)
fill_to(JL, c6, LJ, 0.35); fill_to(JL, c6 + 20, LJ, 1.25)
PILE = O["FX_CoinPile"]
put(PILE, c6 + 14, LJ, 0.0, s=(0.35, 1.0, 0.0), y=0.3, step=True); put(PILE, c6 + 34, LJ, 0.0, s=(0.35, 1.0, 0.75), y=0.3)
popin("FX_StampBox", c6 + 30, x=0.0, z=4.0, s=1.0)
sb = st.caption("TIME > MONEY", c6 + 30, c7, z=4.0, x=0.0, size=0.27, color="red", max_width=1.8)
O["FX_StampBox"].rotation_euler.y = math.radians(-5); sb.rotation_euler.y = math.radians(-5); sb.location.y = -0.42
st.sfx("chaching", c6 + 20, 0.5); st.sfx("boom", c6 + 30, 0.3)
P(ly, "stand", c6); P(ly, "cheer", c6 + 22); ly.mouth("grin", c6 + 22); ly.squint(c6, 1.0)
st.mouth("sad", c6 + 22); st.eyes("wide", c6 + 22)
off("FX_StampBox", c7)

# ================= G. Sticky tangani tuvakka ekadi =================
st.eyes("normal", c7); st.mouth("smile", c7)
on("FX_Pot", c7, x=SXP - 0.6, z=0.0)
for ob in JS: put(ob, c7, SJ, ob.location.z, s=0.0, step=True)
P(st, "stand", c7); P(st, "plant", c7 + 6)
coin(c7 + 8, SXP - 0.55, 1.4, SXP - 0.6, 0.55); st.sfx("drop", c7 + 14, 0.5)
P(st, "plant", c7 + 20); P(st, "stand", c7 + 26)
FS_t = c7 + 40
st.caption("1 SECOND LATER...", FS_t, FS_t + 30, z=3.75, x=SXP - 0.2, size=0.24, color="black")
P(st, "stand", FS_t + 30); P(st, "watch", FS_t + 34); st.prop("clock", FS_t + 36, FS_t + 70, x=-0.55, z=3.0, size=0.6)
st.look(0.0, 0.0, FS_t + 33); st.look(0.0, -0.04, FS_t + 34); st.mouth("think", FS_t + 34)
st.sfx("tick", FS_t + 36, 0.8); st.sfx("tick", FS_t + 46, 0.8); st.sfx("tick", FS_t + 56, 0.8)
st.caption("NOTHING.", FS_t + 64, c8, z=3.75, x=SXP - 0.2, size=0.3, color="red")
st.sfx("trombone", FS_t + 64, 0.4); st.mouth("sad", FS_t + 64)
off("FX_Pot", c8)

# ================= H. Savol =================
P(st, "watch", c8 - 1); P(st, "sign", c8); popin("FX_Sign", c8, x=SXP + 0.38, z=0.75, s=0.8)
st.look(0.0, -0.04, c8 - 1); st.look(0.0, 0.0, c8)
st.mouth("sad", c8); ly.mouth("smile", c8); P(ly, "cheer", c8 - 1); P(ly, "stand", c8)
st.plate(c8 + 6, 100000, -2.72, lines=2)
st.caption("START NOW", c8 + 6, 100000, z=-2.52, size=0.34, color="green", hud=True, max_width=3.2)
st.caption("OR START LATER?", c8 + 12, 100000, z=-2.95, size=0.34, color="red", hud=True, max_width=3.2)
st.sfx("ding", c8 + 6, 0.4); st.sfx("pop", c8 + 12, 0.4)

# ---------- musiqa ----------
m_ = st.music("//musiqa_01.wav", volume=0.16, fade=25, end=END + 1)
for f, v in ((1, 0.22), (H0, 0.13), (END - 24, 0.13), (END + 1, 0.0)):
    m_.volume = v * GAIN; m_.keyframe_insert("volume", frame=f)
for s_ in st._strips():
    if s_.type == 'SOUND' and not s_.name.startswith("Music"): s_.volume *= GAIN
st.alive(1, END); ly.alive(1, END)
bpy.app.driver_namespace["v13_marks"] = dict(H0=H0, e1=e1, c2=c2, e2=e2, c3=c3, e3=e3, c4=c4, e4=e4, e5=e5, c6=c6, e6=e6, c7=c7, e7=e7, c8=c8, e8=e8, END=END)
S.frame_set(1)
