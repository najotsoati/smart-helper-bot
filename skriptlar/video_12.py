# video_12.py  -  "Grandpa Gave 4 Kids $100. Who Used It Best?" (hikoyachi: Fenrir, Kokoro TTS)
import bpy, os, math, random, aud
T = bpy.data.texts["stickman_tools.py"]
st = T.as_module()                        # Sticky (1)
tm = T.as_module(); tm.use("T_")          # Tom (2) - to'q sariq shapka
ly = T.as_module(); ly.use("L_")          # Lily (3) - firuza bant
mx = T.as_module(); mx.use("R_")          # Max (4) - ko'k kepka
gp = T.as_module(); gp.use("G_")          # Bobo - ko'zoynak, soqol
ALL = (st, tm, ly, mx, gp)
S = bpy.context.scene
O = bpy.data.objects
A = "//video_12_audio/"
LX = (-1.42, -0.47, 0.47, 1.42)           # qatorda turish joylari (1..4)
WIDE = (0.0, 2.3, 7.0)
CHART = (70.0, 2.3, 7.0)
STAND = (0.0, 2.6, 5.8)                   # bitta stol va sotuvchi
GAIN = 1.3

st.clear_animation()
for m in (tm, ly, mx, gp):
    m.clear_animation(); m.show()
st.backdrop("room")
S.frame_end = 1800
S.render.filepath = "//Grandpa Gave 4 Kids $100. Who Used It Best.mp4"

EST = {"L01": 162, "L02": 150, "L03": 104, "L04": 46, "L05": 173, "L06": 127, "L07": 138, "L08": 92, "L09": 140, "L10": 69}
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
def go(m, f, x, z=0.0):
    """Personajni shu kadrda boshqa joyga o'tkazadi (oldingi joy ushlab turiladi)."""
    pb = m._rig().pose.bones["root"]; pb.keyframe_insert("location", frame=f - 1); m.move_to(x, z, f)
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
for m in ALL:
    m.POSES["sell"] = pose(reach("L", 0.45, 1.75), reach("R", -0.45, 1.25))
    m.POSES["pour"] = pose(reach("L", 0.4, 1.95), reach("R", -0.4, 1.6))
    m.POSES["cane"] = pose(reach("R", -0.45, 1.35), reach("L", 0.5, 2.45))
    m.POSES["give"] = pose(reach("R", -0.45, 1.35), reach("L", 0.75, 2.2))
    m.POSES["cool"] = pose(reach("L", 0.15, 1.5), reach("R", -0.15, 1.5))

off("Set_Calendar", 1)
for n in ("Set_Floor", "Set_Door", "Set_DoorFrame"): off(n, 1)
on("Hill_Back", 1); on("Chart_BoardPlain", 1)
for n in ("R_Hat", "R_Bowtie"): off(n, 1)
on("R_Cap", 1)
TITLE = st.title("THE $100 LEMONADE CHALLENGE", f_on=-8, size=0.36)
def title_off(f0, f1):
    skey(TITLE, ((f0 - 1, 1.0), (f0, 0.0), (f1 - 1, 0.0), (f1, 1.0)))
for m, x in zip((st, tm, ly, mx), LX):
    m.move_to(x, 0.0, 1); P(m, "stand", 1); m.mouth("smile", 1)
gp.move_to(-6.0, 0.0, 1); P(gp, "cane", 1); gp.mouth("smile", 1)

# ---------- ovoz kursori ----------
H0 = 40                                   # hook: birinchi 40 kadr faqat yozuvlar
e1 = N("L01", H0)
c2 = e1 + 6
e2 = N("L02", c2 + 4)
c3 = e2 + 6
e3 = N("L03", c3 + 4)
e4 = N("L04", e3 + 6)
c5 = e4 + 14
e5 = N("L05", c5 + 4)
c6 = e5 + 6
e6 = N("L06", c6 + 4)
c7 = e6 + 6
e7 = N("L07", c7 + 4)
e8 = N("L08", e7 + 6)
c9 = e8 + 8
e9 = N("L09", c9 + 4)
c10 = e9 + 6
e10 = N("L10", c10 + 4)
END = e10 + 50
S.frame_end = END

# ---------- kamera ----------
st.cut(1, *WIDE)
st.cut(H0, 0.0, 2.6, 4.6)
st.cut(c2, *CHART)
st.cut(c3, *STAND)
st.cut(c5, *STAND)
st.cut(c6, *STAND)
st.cut(c7, 0.0, 2.6, 7.6)
st.cut(c9, *CHART)
st.cut(c10, *WIDE)

# ================= A. Hook: to'rtala bola, $100 =================
for i, x in enumerate(LX):
    st.caption(str(i + 1), -8, H0, z=-0.45, x=x, size=0.45, color="black")
st.caption("$100 EACH", -8, H0, z=4.35, x=0.0, size=0.42, color="green")
st.caption("ONE MADE $0.", 6, H0, z=3.98, x=-0.95, size=0.26, color="red", max_width=1.75)
st.caption("ONE MADE $20,750.", 14, H0, z=3.98, x=0.95, size=0.26, color="green", max_width=1.85)
st.sfx("ding", 1, 0.45); st.sfx("pop", 6, 0.4); st.sfx("chaching", 14, 0.5)
st.mouth("neutral", 6); mx.mouth("grin", 14)
for m in (st, tm, ly, mx): go(m, H0, -8.0)

# ================= B. Bobo konvertlar beradi =================
go(gp, H0, 0.0); P(gp, "cane", H0); popin("FX_Cane", H0, x=-0.45, z=0.0, s=1.0)
for k in range(4):
    f0 = H0 + 30 + k * 18; side = -1 if k % 2 == 0 else 1
    P(gp, "cane", f0 - 1); P(gp, "give", f0 + 2)
    put(O["FX_Envelope"], f0, 0.75, 2.2, s=0.8, step=True)
    put(O["FX_Envelope"], f0 + 8, 0.75 + side * 2.2, 2.6 + 0.3 * k, rot=side * 0.6, s=0.8)
    put(O["FX_Envelope"], f0 + 9, 0.75 + side * 2.2, 2.6, s=0.0)
    st.sfx("whoosh", f0, 0.4)
P(gp, "cane", H0 + 30 + 4 * 18)
st.caption("90 DAYS", H0 + 110, c2, z=3.72, x=0.0, size=0.4, color="red")
go(gp, c2, -8.0); off("FX_Cane", c2)
st.sfx("tick", H0 + 110, 0.9)

# ================= C. Bitta stakan: $0.25 -> $1 =================
popin("FX_Cup", c2 + 4, x=70.0, z=1.3, s=2.6)
st.caption("COST $0.25", c2 + 14, c3, z=3.7, x=70.0, size=0.38, color="red")
st.caption("SELLS FOR $1", c2 + 50, c3, z=0.7, x=70.0, size=0.38, color="green")
st.caption("+$0.75 A CUP", c2 + 80, c3, z=0.2, x=70.0, size=0.28, color="black")
st.sfx("pop", c2 + 4, 0.5); st.sfx("pop", c2 + 14, 0.4); st.sfx("chaching", c2 + 50, 0.5)
off("FX_Cup", c3)

# ================= D. Sticky: neon va ko'zoynak, limon yo'q =================
def board(f0, f1):
    """Pastki natija taxtasi (HUD)."""
    PL = O["HUD_Plate1"]
    PL.location = (0.0, -2.75, -5.06); PL.keyframe_insert("location", frame=f0 - 1)
    skey(PL, ((f0 - 1, 0.0), (f0 + 3, 1.08), (f0 + 6, 1.0), (f1 - 1, 1.0), (f1, 0.0)))
SX = 0.0
go(st, c3, SX); P(st, "cool", c3); st.mouth("grin", c3)
on("FX_Stand", c3, x=SX, z=0.0)
popin("FX_Neon", c3 + 6, x=SX - 0.08, z=0.88, s=1.0); O["FX_Neon"].location.y = -0.42; O["FX_Neon"].keyframe_insert("location", frame=c3 + 6)
st.sfx("pop", c3 + 6, 0.4)
popin("Prop_Shades", c3 + 18, s=1.0); st.sfx("whoosh", c3 + 18, 0.4)
board(c3 + 30, c5)
st.flash("$100 SPENT", c3 + 30, e3 + 12, z=-2.75, size=0.34, color="red", hud=True)
st.sfx("chaching", c3 + 30, 0.5)
st.caption("NO LEMONS", e3 + 6, c5, z=4.3, x=0.0, size=0.34, color="red")
st.flash("$0", e3 + 12, c5, z=-2.75, size=0.5, color="red", hud=True)
st.mouth("sad", e3 + 8); st.sfx("trombone", e3 + 10, 0.4)
go(st, c5, -8.0); off("FX_Neon", c5); off("Prop_Shades", c5)

# ================= E. Tom: jimjit ko'cha, kuniga 20 stakan =================
go(tm, c5, 0.0); P(tm, "sell", c5); tm.mouth("smile", c5)
popin("FX_Cup", c5 + 20, x=0.45, z=1.14, s=0.8)
CUPS = [3, 5, 8, 10, 13, 15, 18, 20]
tick_f = [c5 + 24 + k * 6 for k in range(8)]
for k, f in enumerate(tick_f):
    st.flash("%d CUPS" % CUPS[k], f, tick_f[k + 1] if k < 7 else c5 + 74, z=4.3, x=0.0, size=0.34, color="black")
    st.sfx("tick", f, 0.7)
st.caption("20 CUPS A DAY", c5 + 74, c6, z=4.3, x=0.0, size=0.34, color="black")
FB = c5 + 4 + int((e5 - c5 - 4) * 0.55)
board(FB, c6)
st.flash("20 × $0.75 × 90 DAYS", FB, FB + 40, z=-2.75, size=0.3, color="black", hud=True, max_width=3.1)
st.flash("$1,350", FB + 40, c6, z=-2.75, size=0.5, color="green", hud=True)
st.sfx("chaching", FB + 40, 0.5)
go(tm, c6, -8.0); off("FX_Cup", c6)

# ================= F. Lily: plyaj, kuniga 100 stakan =================
on("Beach_Back", c6); off("Hill_Back", c6)
go(ly, c6, 0.0); P(ly, "pour", c6); ly.mouth("grin", c6)
popin("FX_Cup", c6 + 10, x=0.45, z=1.14, s=0.8)
st.caption("BUSY BEACH", c6 + 6, c6 + 50, z=4.3, x=0.0, size=0.36, color="black")
st.caption("100 CUPS A DAY", c6 + 50, c7, z=4.3, x=0.0, size=0.34, color="black")
FB2 = c6 + 4 + int((e6 - c6 - 4) * 0.5)
board(FB2, c7)
st.flash("100 × $0.75 × 90 DAYS", FB2, FB2 + 30, z=-2.75, size=0.3, color="black", hud=True, max_width=3.1)
st.flash("$6,750", FB2 + 30, c7, z=-2.75, size=0.5, color="green", hud=True)
st.sfx("pop", c6 + 50, 0.4); st.sfx("chaching", FB2 + 30, 0.5)
for k in range(6):
    P(ly, "pour" if k % 2 == 0 else "sell", c6 + 12 + k * 12)
go(ly, c7, -8.0); off("FX_Cup", c7)

# ================= G. Max: bitta stol -> beshta stol =================
go(mx, c7, -1.05); P(mx, "sell", c7); mx.mouth("grin", c7)
st.place("FX_Stand", c7, x=-1.05, z=0.0, step=True)
st.caption("10 DAYS = $750", c7 + 10, c7 + 66, z=4.6, x=0.0, size=0.36, color="black")
for k, x in enumerate((0.0, 0.52, 1.04, 1.56)):
    ob = O["FX_Stand_%d" % (k + 2)]
    put(ob, c7 + 60 + k * 10, x, 0.95, s=0.3, y=0.3, step=True); put(ob, c7 + 63 + k * 10, x, 0.95, s=0.56, y=0.3); put(ob, c7 + 66 + k * 10, x, 0.95, s=0.5, y=0.3)
    st.sfx("pop", c7 + 60 + k * 10, 0.45)
st.caption("5 STANDS", c7 + 68, e8, z=4.6, x=0.0, size=0.4, color="black")
st.caption("+$0.50 A CUP EACH", c7 + 90, e8, z=4.15, x=0.0, size=0.26, color="black", max_width=2.6)
board(e7 + 4, c9)
st.flash("$20,750", e7 + 8, c9, z=-2.75, size=0.5, color="green", hud=True)
st.sfx("chaching", e7 + 8, 0.6); st.sfx("ding", e7 + 9, 0.35)
mx.eyes("money", e7 + 8)
for k in range(2, 6): off("FX_Stand_%d" % k, c9)
off("FX_Stand", c9); off("Beach_Back", c9); on("Hill_Back", c9)
go(mx, c9, -8.0)

# ================= H. Grafik: 4 ustun =================
VAL = (0.0, 1350.0, 6750.0, 20750.0)
for i, v in enumerate(VAL):
    ob = O["Chart_B%d" % (i + 1)]
    h = max(v / 20750.0 * 3.6, 0.03)
    f0 = c9 + 8 + i * 14
    put(ob, f0, ob.location.x, -0.38, s=(1.0, 1.0, 0.0), step=True)
    put(ob, f0 + 10, ob.location.x, -0.38, s=(1.0, 1.0, h))
    put(ob, c10 - 1, ob.location.x, -0.38, s=(1.0, 1.0, h)); put(ob, c10, ob.location.x, -0.38, s=0.0)
    lbl = ("$0", "$1,350", "$6,750", "$20,750")[i]
    st.caption(lbl, f0 + 10, c10, z=-0.38 + h + 0.22, x=ob.location.x, size=0.17, color="black", max_width=0.72)
    st.caption(str(i + 1), f0, c10, z=-0.62, x=ob.location.x, size=0.26, color="black")
    st.sfx("pop", f0 + 10, 0.4)
WORDS = ("SPENDING", "SELLING", "LOCATION", "SYSTEM")
WF = [c9 + 4 + int((e9 - c9 - 4) * (0.42 + 0.14 * i)) for i in range(4)]
for i, w in enumerate(WORDS):
    st.flash(w, WF[i], WF[i + 1] if i < 3 else c10, z=4.25, x=70.0, size=0.42, color=("red", "black", "black", "green")[i])
    st.sfx("tick", WF[i], 0.8)

# ================= I. Savol: qatorda 1-2-3-4 =================
for m, x in zip((st, tm, ly, mx), LX): go(m, c10, x); P(m, "stand", c10)
st.mouth("sad", c10); tm.mouth("smile", c10); ly.mouth("smile", c10); mx.mouth("grin", c10); mx.eyes("normal", c10)
for i, x in enumerate(LX):
    st.caption(str(i + 1), c10 + 2 + i * 4, 100000, z=4.0, x=x, size=0.42, color="black")
    st.sfx("pop", c10 + 2 + i * 4, 0.35)
st.plate(c10 + 20, 100000, -2.72, lines=2)
st.caption("1, 2, 3 OR 4?", c10 + 20, 100000, z=-2.52, size=0.32, color="black", hud=True, max_width=3.2)
st.caption("WHO USED $100 BEST?", c10 + 26, 100000, z=-2.95, size=0.3, color="red", hud=True, max_width=3.2)
st.caption("EXAMPLE NUMBERS, BEFORE OTHER COSTS", c10 + 30, 100000, z=2.32, size=0.13, color="black", hud=True, max_width=3.0)
st.sfx("ding", c10 + 20, 0.4)

# ---------- musiqa ----------
m_ = st.music("//musiqa_01.wav", volume=0.16, fade=25, end=END + 1)
for f, v in ((1, 0.22), (H0, 0.13), (END - 24, 0.13), (END + 1, 0.0)):
    m_.volume = v * GAIN; m_.keyframe_insert("volume", frame=f)
for s_ in st._strips():
    if s_.type == 'SOUND' and not s_.name.startswith("Music"): s_.volume *= GAIN
for m in ALL: m.alive(1, END)
bpy.app.driver_namespace["v12_marks"] = dict(H0=H0, e1=e1, c2=c2, e2=e2, c3=c3, e3=e3, e4=e4, c5=c5, e5=e5, c6=c6, e6=e6, c7=c7, e7=e7,
                                              e8=e8, c9=c9, e9=e9, c10=c10, e10=e10, END=END)
S.frame_set(1)
