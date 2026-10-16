# video_07.py  -  "LEFT ON READ" sketch
import bpy, os, aud
T = bpy.data.texts["stickman_tools.py"]
st = T.as_module()                        # Sticky
S = bpy.context.scene
A = "//video_07_audio/"
X = 0.15                                  # Sticky xonada turadigan joy
HEAD = 2.78
PH = 40.0                                 # telefon markazi
FACE = (X + 0.08, 2.75, 2.6)              # yuz yaqin plani
PHONE_CAM = (PH, 2.45, 6.0)               # telefon ekrani to'liq

st.clear_animation()
st.POSES["ph_rage"] = {"upper_arm.L": -62, "forearm.L": 58, "upper_arm.R": 150, "forearm.R": 85}
st.backdrop("room")
S.frame_end = 1400                        # oxirida aniq qiymat qo'yiladi
S.render.filepath = "//video_07_"

# ---------- yordamchi buyruqlar ----------
EST = {"S01": 96, "S02": 16, "S03": 38, "S04": 44, "S05": 46, "S06": 64, "S07": 54, "S08": 30, "S09": 70, "S10": 40}
def L(key):
    """Gap uzunligi kadrlarda."""
    p = bpy.path.abspath(A + key + ".wav")
    if os.path.exists(p):
        s = aud.Sound.file(p)
        return int(round(s.length / s.specs[0] * 30))
    return EST[key]
def say(key, f, **kw):
    p = bpy.path.abspath(A + key + ".wav")
    if os.path.exists(p):
        return st.say(A + key + ".wav", f, **kw)
    st.talk(f, f + EST[key], end=kw.get("end", "smile"), closed=kw.get("closed", "neutral"))
    return f + EST[key]
def on(name, f, x=None, z=None): st.place(name, f, x=x, z=z, scale=1.0, step=True)
def off(name, f): st.place(name, f, scale=0.0, step=True)
def pulse(ob, f0, f1, lo=1.0, hi=1.22, step=4):
    """Yozuvni chaqnatadi (kattalashib-kichrayadi)."""
    k = 0
    for f in range(f0, f1, step):
        s = hi if k % 2 == 0 else lo
        ob.scale = (s, s, s); ob.keyframe_insert("scale", frame=f); k += 1
PHONE = bpy.data.objects["Prop_phone"]
def plate(name, f_on, f_off, y):
    """Yozuv ostidagi och rangli taxtacha (kameraga yopishgan): HUD_Plate1 - bir qator, HUD_Plate2 - ikki qator."""
    ob = bpy.data.objects[name]
    ob.location = (0.0, y, -5.06); ob.keyframe_insert("location", frame=f_on - 1)
    for f, sc in ((f_on - 1, 0.0), (f_on + 3, 1.08), (f_on + 6, 1.0), (f_off, 1.0), (f_off + 3, 0.0)):
        ob.scale = (sc, sc, sc); ob.keyframe_insert("scale", frame=f)
def front(ob):
    """Yozuvni oldinga chiqaradi (kartochka ustidagi yozuvlar uchun)."""
    ob.location.y = -0.42
    return ob
def phone(f, x, z, step=False):
    if step: PHONE.keyframe_insert("location", frame=f - 1)
    PHONE.location = (x, 0.0, z); PHONE.keyframe_insert("location", frame=f)
def walk(f0, f1, x0, x1, step):
    """Xona bo'ylab u yoqdan bu yoqqa yuradi: oyoqlar almashadi, tana harakat tomonga egiladi."""
    d = 1 if x1 > x0 else -1
    arms = {"upper_arm.L": -62, "forearm.L": 58, "upper_arm.R": 140, "forearm.R": 75, "head": 86, "front": "R"}
    st.POSES["wA"] = dict(arms, **{"thigh.L": -58, "shin.L": -82, "thigh.R": -100, "shin.R": -118, "root": 90 - 5 * d})
    st.POSES["wB"] = dict(arms, **{"thigh.L": -80, "shin.L": -62, "thigh.R": -122, "shin.R": -98, "root": 90 - 5 * d})
    k = 0; f = f0
    while f < f1:
        st.move_to(x0 + (x1 - x0) * (f - f0) / float(f1 - f0), 0.0, f)
        st.apply_pose("wA" if k % 2 == 0 else "wB", f, face=False)
        st.hop(f, 0.07, step)
        k += 1; f += step
    st.move_to(x1, 0.0, f1)
    st.apply_pose("wA" if k % 2 == 0 else "wB", f1, face=False)

# ---------- sahna, sarlavha ----------
off("Set_Calendar", 1)
on("Set_Bed", 1); on("Set_Blanket", 1)
bpy.data.objects["Set_Blanket"].location.y = 0.25                     # ko'rpa personaj orqasida
bpy.data.objects["Set_Blanket"].keyframe_insert("location", frame=1)
st.title("LEFT ON READ", f_on=-8)
st.move_to(X, 0.0, 1)
st.apply_pose("phone", 1, face=False)
st.prop("phone", -8, 5000, x=0.62, z=2.55, size=0.6)

# chat ekranining doimiy qismi
on("Chat_Header", 1)
st.caption("EMMA", -10, 5000, z=3.98, size=0.2, x=39.78)
on("Chat_Me1", 1, x=40.3, z=3.05)
st.caption("Wanna get coffee?", -10, 5000, z=3.05, size=0.15, x=40.3, color="white", max_width=1.8)

# ==== A) HOOK: telefon ekrani, "Read 2 min ago"
st.cut(1, *PHONE_CAM)
st.zoom(2, 30, z=2.66, scale=5.4)                                  # sarlavha telefon ustida qolishi uchun z ham ko'tariladi
rd = st.caption("Read 2 min ago", -10, 5000, z=2.72, size=0.15, x=40.62, color="red")
pulse(rd, 4, 28, 1.0, 1.25, 5)
rd.scale = (1.0, 1.0, 1.0); rd.keyframe_insert("scale", frame=30)
hb = st.sfx("heart", 1, 0.45)
e1 = say("S01", 10, end="sad", closed="neutral")

# ==== B) STICKY dahshatda
b0 = 30
st.cut(b0, *FACE)
st.zoom(b0, e1 + 4, z=2.8, scale=2.35)
st.eyes("wide", 1); st.brows(12, 0.07, 1); st.look(0.04, -0.03, 1)
st.prop("sweat", b0 + 2, e1)
st.shiver(b0, e1 - 20, 0.012)
st.fx("lines", b0, X, HEAD, 1.0, length=22)
st.look(0.04, -0.03, 76); st.look(0.0, -0.02, 82); st.brows(14, 0.0, 82)   # "It's over." 82-kadrda

# ==== C) TELEFON: "Hey" deb yozadi
c0 = e1 + 6
st._set_end(hb, c0)
st.cut(c0, *PHONE_CAM)
on("Chat_Input", c0); on("Chat_Keys", c0)
t = st.caption("Hey", c0 - 6, c0 + 31, z=1.72, size=0.19, x=39.2)
bpy.context.view_layer.update()
xs = [v[0] for v in t.bound_box]; left, right = 39.2 + min(xs), 39.2 + max(xs)
st.place("Phone_Mask", c0, x=40.64, z=1.72, scale=(40.64 - left + 0.03, 1.0, 0.34), step=True)
st.place("Phone_Cursor", c0, x=left - 0.02, z=1.72, scale=1.0, step=True)
for i, f in enumerate((c0 + 8, c0 + 12, c0 + 16), 1):
    rx = left + (right - left) * i / 3.0
    st.place("Phone_Mask", f, scale=(max(40.64 - rx - 0.02, 0.001), 1.0, 0.34), step=True)
    st.place("Phone_Cursor", f, x=rx + 0.03, step=True)
on("Chat_Smiley", c0 + 22, x=right + 0.2, z=1.72)
st.place("Phone_Mask", c0 + 22, scale=(max(40.64 - right - 0.36, 0.001), 1.0, 0.34), step=True)
st.place("Phone_Cursor", c0 + 22, x=right + 0.37, step=True)
s = st.sfx("type", c0 + 8, 0.7); st._set_end(s, c0 + 28)
say("S02", c0 + 8, end="neutral")
SEND = c0 + 32                                                    # yuborildi
off("Phone_Mask", SEND); off("Phone_Cursor", SEND)
on("Chat_Me2", SEND, x=40.8, z=2.3)
st.place("Chat_Me2", SEND, scale=0.6); st.place("Chat_Me2", SEND + 3, scale=1.1); st.place("Chat_Me2", SEND + 6, scale=1.0)
st.place("Chat_Smiley", SEND, x=41.05, z=2.3, step=True)
st.caption("Hey", SEND, 5000, z=2.3, size=0.17, x=40.66, color="white")
st.sfx("whoosh", SEND - 2, 0.6)
c1 = SEND + 24

# ==== D) STICKY kutadi ("1 SECOND LATER"), keyin: "Maybe she's busy."
st.cut(c1, X + 0.01, 2.6, 2.9)
st.eyes("wide", c1); st.brows(8, 0.05, c1); st.look(0.04, -0.03, c1); st.mouth("neutral", c1)
plate("HUD_Plate1", c1 + 1, c1 + 44, -2.2)
st.caption("1 SECOND LATER", c1 + 2, c1 + 44, z=-2.2, size=0.34, hud=True)
st.sfx("pop", c1 + 2, 0.5)
for k, f in enumerate(range(c1 + 8, c1 + 44, 6)):                  # sabrsizlik: ko'zlari telefon bilan kamera orasida yuguradi
    st.look(0.04 if k % 2 == 0 else -0.03, -0.03 if k % 2 == 0 else 0.0, f)
D = c1 + 50
st.eyes("normal", D); st.brows(0, 0.05, D); st.look(0.04, -0.03, D)
d1 = say("S03", D, volume=2.2, end="smile", closed="smile")
st.look(0.04, -0.03, D + 14); st.look(0.0, 0.0, D + 20)

# ==== E) TELEFON: holati - ONLINE (qizil chaqnaydi)
e0 = d1 + 6
off("Chat_Input", e0); off("Chat_Keys", e0)
st.cut(e0, *PHONE_CAM)
st.caption("online", -10, e0 + 5, z=3.75, size=0.13, x=39.78, color="green")
big = st.caption("ONLINE", e0 + 8, 5000, z=3.73, size=0.3, x=40.2, color="red")
pulse(big, e0 + 16, e0 + 40, 1.0, 1.2, 4)
big.scale = (0.55, 0.55, 0.55); big.keyframe_insert("scale", frame=e0 + 46)
st.zoom(e0 + 8, e0 + 40, z=2.85, scale=4.9)
st.sfx("boom", e0 + 8, 0.6)
f0 = e0 + 46

# ==== F) STICKY: "BUSY DOING WHAT?!"
st.cut(f0, *FACE)
st.snap("ph_rage", f0 + 1, lead=2, face=False)
st.eyes("wide", f0); st.brows(-16, 0.04, f0); st.look(0.0, 0.0, f0)
f1 = say("S04", f0 + 3, end="open", closed="open", opened="scream")
st.shake(f1 - 22, f1, 0.06)
st.fx("lines", f0 + 3, X, HEAD, 1.0, length=30)
st.punch(f1 - 22, 0.08)

# ==== G) XONADA U YOQDAN BU YOQQA YURADI - tezlashib boradi
g0 = f1 + 12
st.cut(g0, 0.0, 2.3, 7.0)
st.eyes("wide", g0); st.brows(12, 0.07, g0); st.look(0.0, 0.0, g0)
p1 = g0 + 4 + L("S05") + 10
p2 = p1 + L("S06") + 10
p3 = p2 + L("S07") + 6
walk(g0, p1, X, -1.3, 7)
walk(p1, p2, -1.3, 1.25, 5)
walk(p2, p3, 1.25, X, 4)
say("S05", g0 + 4, volume=1.4, end="open", closed="neutral")
say("S06", p1 + 2, volume=1.3, end="open", closed="neutral")
say("S07", p2 + 2, volume=1.1, end="scream", closed="open", opened="scream")
st.caption("PHONE DIED?", g0 + 6, p1 - 2, z=4.4, size=0.36)
st.caption("NEW COUNTRY?", p1 + 4, p2 - 2, z=4.4, size=0.42)
st.caption("KIDNAPPED?!", p2 + 4, p3 + 2, z=4.42, size=0.55, color="red")
st.prop("sweat", p1, p3)
hf = st.sfx("heart_fast", g0, 0.3)
rs = st.sfx("riser", g0, 0.18)
st.zoom(g0, p3, z=2.6, scale=6.4)

# ==== H) TELEFON JIRINGLADI: "SHE REPLIED?!"
h0 = p3 + 5
st._set_end(hf, h0); st._set_end(rs, h0)                          # yurak urishi va taranglik shu kadrda uziladi
st.snap("phone", h0, lead=2, face=False)
st.cut(h0 + 1, *FACE)
st.sfx("ding", h0, 0.8)
st.punch(h0 + 1, 0.1)
st.fx("lines", h0 + 1, X, HEAD, 1.0, length=18)
st.eyes("wide", h0); st.brows(0, 0.1, h0); st.look(0.04, -0.03, h0)
h1 = say("S08", h0 + 8, end="grin", closed="grin", opened="wide")

# ==== I) TELEFON: "lol"
i0 = h1 + 5
st.cut(i0, *PHONE_CAM)
st.caption("Delivered", SEND + 8, i0 - 8, z=2.0, size=0.1, x=41.0)
rd2 = st.caption("Read", i0 - 6, 5000, z=2.0, size=0.1, x=41.1)
LOL = i0 + 20
st.sfx("riser2", LOL - 50, 0.6)
on("Chat_Her", LOL, x=39.33, z=1.45)
st.place("Chat_Her", LOL, scale=0.6); st.place("Chat_Her", LOL + 3, scale=1.6); st.place("Chat_Her", LOL + 6, scale=1.4)
st.caption("lol", LOL + 1, 5000, z=1.45, size=0.28, x=39.33)
st.sfx("pop", LOL, 0.8)
st.zoom(LOL + 2, LOL + 30, z=2.79, scale=5.0)
j0 = LOL + 24

# ==== J) SUKUT 1,5 soniya, keyin: "I nearly died for an LOL."
st.cut(j0, *FACE)
st.zoom(j0, j0 + 34, z=2.8, scale=2.3)
st.mouth("grin", j0); st.eyes("normal", j0); st.brows(0, 0.08, j0); st.look(0.04, -0.03, j0)
st.mouth("smile", j0 + 8); st.brows(0, 0.03, j0 + 8)
st.mouth("neutral", j0 + 16); st.brows(0, 0.0, j0 + 16); st.look(0.0, 0.0, j0 + 18)
st.blink(j0 + 25)
st.brows(-8, -0.01, j0 + 30)
j1 = say("S09", j0 + 34, end="sad", closed="neutral")

# ==== K) DO'STIDAN XABAR
k0 = j1 + 8
st.cut(k0, *PHONE_CAM)
st.place("Chat_Notif", k0 + 2, z=5.6, scale=1.0, step=True)
st.place("Chat_Notif", k0 + 8, z=2.7); st.place("Chat_Notif", k0 + 11, z=2.75)
st.sfx("ding", k0 + 2, 0.8)
st.sfx("scratch", k0, 0.7)
rd2.scale = (1.0, 1.0, 1.0); rd2.keyframe_insert("scale", frame=k0 + 5)
rd2.scale = (0.0, 0.0, 0.0); rd2.keyframe_insert("scale", frame=k0 + 6)
NT = k0 + 9
l0 = k0 + 88
m0 = l0 + 32
GONE = m0 + 20                                                   # kartochka shu kadrda uchib ketadi
front(st.caption("MIKE", NT, GONE, z=3.17, size=0.2, x=39.62))
front(st.caption("Bro, why haven't you", NT + 2, GONE, z=2.8, size=0.17, x=PH))
front(st.caption("replied to me in", NT + 4, GONE, z=2.54, size=0.17, x=PH))
front(st.caption("THREE DAYS?", NT + 8, GONE, z=2.24, size=0.24, x=PH, color="red"))

# ==== L) STICKY ko'zini olib qochadi
st.cut(l0, *FACE)
st.eyes("normal", l0); st.brows(0, 0.06, l0); st.mouth("neutral", l0); st.look(0.04, -0.03, l0)
st.look(0.04, -0.03, l0 + 8); st.look(-0.05, 0.0, l0 + 12); st.look(-0.05, 0.0, l0 + 20); st.look(0.05, 0.0, l0 + 24)
st.prop("sweat", l0 + 4, l0 + 28)

# ==== M) TELEFON: bildirishnomalarni o'chiradi
st.cut(m0, *PHONE_CAM)
on("Chat_ToggleOn", m0, z=1.45)
front(st.caption("NOTIFICATIONS", m0 - 4, 5000, z=1.45, size=0.15, x=39.72))
st.place("Chat_ToggleOn", m0 + 14, scale=0.0, step=True)
on("Chat_ToggleOff", m0 + 14, z=1.45)
st.sfx("pop", m0 + 14, 0.8)
st.place("Chat_Notif", m0 + 20, z=2.75); st.place("Chat_Notif", m0 + 27, z=5.8)
st.sfx("whoosh", m0 + 20, 0.6)
n0 = m0 + 40

# ==== N) "I'm a busy man." - kameraga tik qaraydi
st.cut(n0, X + 0.01, 2.6, 2.9)
st.snap("hips", n0, lead=2, face=False)
PHONE.scale = (0.6, 0.6, 0.6); PHONE.keyframe_insert("scale", frame=n0 - 1)      # telefonni cho'ntakka soldi
PHONE.scale = (0.0, 0.0, 0.0); PHONE.keyframe_insert("scale", frame=n0)
st.eyes("normal", n0); st.brows(0, 0.0, n0, 0.04); st.look(0.05, 0.03, n0)
n1 = say("S10", n0 + 6, end="smile", closed="smile")
st.look(0.05, 0.03, n1 + 2); st.look(0.0, 0.0, n1 + 8)
z0 = n1 + 10
st.cut(z0, X, 2.84, 2.1)
st.zoom(z0, z0 + 106, scale=1.85)
st.mouth("neutral", z0); st.brows(0, 0.0, z0)
st.blink(z0 + 26)
plate("HUD_Plate2", z0 + 7, 5000, -2.3)
st.caption("THE DOUBLE STANDARDS", z0 + 8, 5000, z=-2.03, size=0.3, hud=True)
st.caption("ARE CRAZY", z0 + 14, 5000, z=-2.58, size=0.52, color="red", hud=True)
st.sfx("boom", z0 + 8, 0.6)
END = z0 + 112
S.frame_end = END

# ---------- musiqa: yozishdan telefon jiringlaguncha, keyin do'stining xabaridan oxirigacha ("lol" dan keyin sukut) ----------
m = st.music("//musiqa_01.wav", volume=0.2, fade=20, end=END + 1)
for f, v in ((1, 0.0), (c0 - 1, 0.0), (c0 + 6, 0.2), (h0 - 1, 0.2), (h0, 0.0), (k0, 0.0), (k0 + 10, 0.13), (END - 20, 0.13)):
    m.volume = v; m.keyframe_insert("volume", frame=f)
st.alive(1, END, blink_skip=[(1, c1 + 50), (f0, h1 + 4), (j0, j0 + 36), (z0, END)])
S.frame_set(1)
MARKS = dict(b0=b0, e1=e1, c0=c0, SEND=SEND, c1=c1, d1=d1, e0=e0, f0=f0, f1=f1, g0=g0, p1=p1, p2=p2, p3=p3, h0=h0, h1=h1, i0=i0, LOL=LOL, j0=j0, j1=j1, k0=k0, l0=l0, m0=m0, n0=n0, n1=n1, z0=z0, END=END)
bpy.app.driver_namespace["v07_marks"] = MARKS
