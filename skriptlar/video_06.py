# video_06.py  -  "HOW TO BECOME A MILLIONAIRE" sketch (47 soniya)
import bpy
T = bpy.data.texts["stickman_tools.py"]
st = T.as_module()                        # Sticky (Sam)
rk = T.as_module(); rk.use("R_")          # kurs sotuvchisi (Rick)
S = bpy.context.scene
A = "//video_06_audio/"
X = 0.15                                  # Sticky xonada turadigan joy
HEAD = 2.78
PX = 39.6                                 # telefon ekrani ichida personaj turadigan joy
PH = 40.0                                 # telefon markazi

st.clear_animation()
rk.clear_animation(); rk.show()
st.backdrop("room")
S.frame_end = 1415
S.render.filepath = "//video_06_"

# ---------- yordamchi buyruqlar ----------
def on(name, f):  st.place(name, f, scale=1.0, step=True)
def off(name, f): st.place(name, f, scale=0.0, step=True)
def warp(mod, x, z, f):
    """Personajni shu kadrda boshqa joyga ko'chiradi (silliq emas, birdan)."""
    pb = mod._rig().pose.bones["root"]
    pb.keyframe_insert("location", frame=f - 1)
    mod.move_to(x, z, f)
PHONE = bpy.data.objects["Prop_phone"]
def phone(f, x, z, step=False):
    """Qo'ldagi telefon joyi (personajga nisbatan)."""
    if step:
        PHONE.keyframe_insert("location", frame=f - 1)
    PHONE.location = (x, 0.0, z)
    PHONE.keyframe_insert("location", frame=f)
def phone_show(f, visible):
    p = 0.0 if visible else 0.6
    PHONE.scale = (p, p, p)
    PHONE.keyframe_insert("scale", frame=f - 1)
    s = 0.6 if visible else 0.0
    PHONE.scale = (s, s, s)
    PHONE.keyframe_insert("scale", frame=f)
_SP = [0]
def sparkle(f, x, z, s=1.0):
    """Oltin uchqun."""
    _SP[0] += 1
    n = "FX_Gold_%d" % ((_SP[0] - 1) % 4 + 1)
    st.place(n, f, x=x, z=z, scale=0.0, step=True)
    st.place(n, f + 3, scale=1.2 * s)
    st.place(n, f + 6, scale=s)
    st.place(n, f + 11, scale=0.0)
def banner(name, f_in, f_out=None):
    """Telefon tepasidan tushadigan xabar."""
    st.place(name, f_in, z=5.2, scale=1.0, step=True)
    st.place(name, f_in + 6, z=3.75)
    if f_out:
        st.place(name, f_out, z=3.75)
        st.place(name, f_out + 4, z=5.2)
        off(name, f_out + 5)
def card(label, lines, f0, f1, sizes=(0.28,), label_color="gold"):
    """Telefon ekrani pastidagi qora taxtacha ustidagi yozuv."""
    if label:
        st.caption(label, f0, f1, z=0.95, size=0.16, x=PH, color=label_color)
    zs = (0.47,) if len(lines) == 1 else (0.6, 0.3)
    for i, tx in enumerate(lines):
        st.caption(tx, f0, f1, z=zs[i], size=sizes[min(i, len(sizes) - 1)], x=PH, color="white", max_width=2.45)

st.POSES["sit"] = {"upper_arm.L": -62, "forearm.L": 58, "upper_arm.R": -100, "forearm.R": -94, "head": 86,
                   "thigh.L": 0, "shin.L": 0, "foot.L": 90, "thigh.R": 0, "shin.R": 0, "foot.R": 90}
st.POSES["ph_tap"] = {"upper_arm.L": -62, "forearm.L": 58, "upper_arm.R": -30, "forearm.R": 75, "head": 86, "front": "R"}
st.POSES["ph_rage"] = {"upper_arm.L": -62, "forearm.L": 58, "upper_arm.R": 150, "forearm.R": 85}
st.POSES["idea_R"] = {"upper_arm.L": -62, "forearm.L": 58, "upper_arm.R": 152, "forearm.R": 94}

# ---------- sahna, sarlavha, musiqa ----------
off("Set_Calendar", 1)
on("Set_Bed", 1); on("Set_Blanket", 1)
st.title("HOW TO BECOME", f_on=-8, f_off=1334, y=3.17, size=0.36)
st.title("A MILLIONAIRE", f_on=-8, f_off=1334, y=2.83, size=0.36)
m = st.music("//musiqa_02_epic.wav", volume=0.06, fade=1, end=1170)     # "Refund" kelganda birdan o'chadi
for f, v in ((1, 0.30), (8, 0.30), (16, 0.10), (86, 0.10), (92, 0.06), (1100, 0.06), (1108, 0.26), (1169, 0.26)):
    m.volume = v
    m.keyframe_insert("volume", frame=f)
rk.move_to(80.0, 0.0, 1)                                              # Rick hozircha kadrdan tashqarida
st.prop("phone", -8, 2000, x=0.62, z=2.55, size=0.6)
st.alive(1, 1415, blink_skip=[(1, 150), (318, 412), (612, 652), (860, 884), (1104, 1240)])

# ==== 1) HOOK: karavotdan sakrab turadi                         1-51
st.move_to(-0.95, -0.37, 1)
st.apply_pose("sit", 1, face=False)
st.eyes("wide", 1); st.brows(0, 0.08, 1); st.mouth("grin", 1); st.look(0.04, -0.02, 1)
st.move_to(-0.95, -0.37, 5); st.apply_pose("sit", 5, face=False); phone(5, 0.62, 2.55)
st.move_to(-0.35, 1.1, 10); st.apply_pose("cheer", 10, face=False); phone(10, 0.62, 3.28)
st.move_to(X, 0.0, 15)
bl = bpy.data.objects["Set_Blanket"]                                  # sakragach ko'rpa personaj orqasiga o'tadi
bl.keyframe_insert("location", frame=9); bl.location.y = 0.25; bl.keyframe_insert("location", frame=10)
st.punch(15, 0.16, 4)
st.fx("dust", 15, X - 0.32, 0.14, 0.9); st.fx("dust", 15, X + 0.32, 0.14, 0.9)
st.sfx("jump", 5, 0.5); st.sfx("land", 14, 0.6)
st.say(A + "S01.wav", 8, end="grin", closed="grin")
st.bounce(26, 0.3, 12, sound=0.45)
st.bounce(40, 0.3, 12, sound=0.45)
st.drift(16, 50)

# ==== 2) YAQIN PLAN: ko'zlarida dollar                          52-89
st.cut(52, X + 0.05, 2.9, 2.7)
st.zoom(52, 88, z=2.95, scale=2.45)
st.eyes("money", 52); st.brows(0, 0.06, 52); st.look(0.0, 0.0, 52)
st.fx("lines", 52, X, HEAD, 1.0, length=20)
st.sfx("chaching", 53, 0.5)
sparkle(54, X - 0.5, 3.5, 0.4); sparkle(60, X + 0.38, 2.1, 0.35); sparkle(68, X - 0.5, 2.25, 0.35); sparkle(76, X + 0.55, 3.85, 0.3)

# ==== 3) TELEFON: qidiruv yoziladi                              90-147
st.cut(90, PH, 2.45, 6.0)
on("Phone_Search", 90)
t = st.caption("how to get rich overnight", 88, 147, z=3.55, size=0.185, x=PH + 0.12, max_width=2.05)
bpy.context.view_layer.update()
xs = [v[0] for v in t.bound_box]
left, right = PH + 0.12 + min(xs), PH + 0.12 + max(xs)
st.place("Phone_Mask", 90, scale=(41.15 - left + 0.03, 1.0, 0.36), step=True)
st.place("Phone_Cursor", 90, x=left - 0.02, scale=1.0, step=True)
s = st.sfx("type", 94, 0.7); st._set_end(s, 141)
for f, c in ((94, 4), (98, 8), (105, 11), (113, 15), (117, 18), (124, 22), (135, 25)):
    rx = left + (right - left) * c / 25.0
    st.place("Phone_Mask", f, scale=(max(41.15 - rx - 0.02, 0.001), 1.0, 0.36), step=True)
    st.place("Phone_Cursor", f, x=rx + 0.03, step=True)
st.sfx("pop", 140, 0.6)
off("Phone_Search", 148); off("Phone_Mask", 148); off("Phone_Cursor", 148)
st.drift(92, 146)

# ==== 4) STICKY: "Perfect! Finally an easy life."                148-229
st.cut(148, X + 0.01, 2.6, 2.9)
st.zoom(148, 228, scale=2.7)
st.snap("phone", 148, lead=2, face=False); phone(148, 0.62, 2.55, step=True)
st.eyes("normal", 148); st.brows(0, 0.05, 148); st.look(0.04, -0.03, 148)
st.say(A + "S02.wav", 152, end="grin", closed="smile")
st.look(0.04, -0.03, 172); st.look(0.0, 0.0, 178); st.punch(178, 0.05)

# ==== 5) TELEFON: kurs reklamasi, $99                            230-319
st.cut(230, PH, 2.45, 6.0)
warp(rk, PX, 0.1, 230)
rk.snap("present", 230, lead=2, face=False); rk.mouth("smile", 230); rk.brows(0, 0.03, 230)
rk.alive(230, 906)
on("Phone_Card", 230)
card(None, ["BUY MY COURSE"], 231, 319, sizes=(0.3,))
rk.say(A + "P01.wav", 234, end="grin", closed="smile")
st.place("Phone_Burst", 272, x=40.78, scale=0.0, step=True); st.place("Phone_Burst", 275, scale=1.2); st.place("Phone_Burst", 278, scale=0.95)
st.caption("$99", 273, 319, z=3.3, size=0.36, x=40.78)
st.sfx("pop", 272, 0.7)
rk.snap("idea", 272, face=False)
off("Phone_Burst", 320)
st.drift(232, 318)

# ==== 6) STICKY: "Only ninety-nine dollars? That's practically free!"   320-409
st.cut(320, X + 0.08, 2.7, 2.6)
st.eyes("wide", 320); st.brows(0, 0.09, 320); st.look(0.04, -0.03, 320)
st.say(A + "S03.wav", 323, end="grin", closed="neutral")
st.eyes("money", 373); st.brows(0, 0.05, 373); st.look(0.0, 0.0, 373); st.punch(373, 0.07)
sparkle(374, X - 0.5, 3.45, 0.4); sparkle(382, X + 0.5, 2.0, 0.35)
st.snap("ph_tap", 402, face=False)                                 # "sotib olish" tugmasini bosadi
st.sfx("pop", 404, 0.6)

# ==== 7) TELEFON: to'lov ketdi, 1-dars                           410-513
st.cut(410, PH, 2.45, 6.0)
rk.snap("cheer", 410, lead=2, face=False); rk.mouth("grin", 410); rk.tip_hat(418)
card(None, ["THANK YOU!"], 411, 437, sizes=(0.3,))
banner("Phone_BannerBad", 411, 436)
st.caption("PAYMENT SENT", 415, 435, z=3.88, size=0.17, x=40.22)
st.caption("-$99", 415, 435, z=3.63, size=0.24, x=40.22, color="red")
st.sfx("drop", 411, 0.6); st.sfx("chaching", 414, 0.7)
rk.snap("present", 442, face=False)
card("LESSON 1", ["WAKE UP EARLY"], 442, 513)
st.sfx("pop", 442, 0.5)
rk.say(A + "P02.wav", 445, end="smile", closed="smile")

# ==== 8) STICKY: "Disgusting."                                   514-547
st.cut(514, X + 0.08, 2.75, 2.6)
st.snap("phone", 514, lead=2, face=False)
st.eyes("normal", 514); st.brows(-10, -0.01, 514); st.look(0.04, -0.03, 514); st.mouth("sad", 514)
st.say(A + "S04.wav", 517, end="sad", closed="sad")
st.look(0.04, -0.03, 532); st.look(-0.04, 0.0, 538)

# ==== 9) TELEFON: 2-dars                                         548-613
st.cut(548, PH, 2.45, 6.0)
rk.snap("hips", 548, lead=2, face=False)
card("LESSON 2", ["WORK HARD"], 549, 613)
st.sfx("pop", 549, 0.5)
rk.say(A + "P03.wav", 551, end="smile", closed="smile")

# ==== 10) STICKY: "SCAM!" - ekran silkinadi                      614-649
st.cut(614, X + 0.08, 2.75, 2.6)
st.snap("ph_rage", 615, lead=2, face=False)
st.eyes("wide", 614); st.brows(-16, 0.04, 614); st.look(0.0, 0.0, 614)
st.say(A + "S05.wav", 616, end="open", closed="open", opened="scream")
st.shake(616, 640, 0.07)
st.fx("lines", 616, X, HEAD, 1.0, length=26)
st.caption("SCAM!", 617, 648, z=1.74, size=0.42, x=X + 0.08, color="red")
st.sfx("boom", 616, 0.6)

# ==== 11) TELEFON: 3-dars                                        650-775
st.cut(650, PH, 2.45, 6.0)
rk.snap("point", 650, lead=2, face=False)
card("LESSON 3", ["STOP BUYING COURSES", "AND ACTUALLY DO SOMETHING"], 651, 775, sizes=(0.2, 0.2))
st.sfx("pop", 651, 0.5)
rk.say(A + "P04.wav", 653, end="smile", closed="smile")
rk.snap("shrug", 724, face=False)
st.drift(652, 772)

# ==== 12) STICKY sekin ekranga qaraydi: "I paid ninety-nine dollars to learn THAT?!"   776-881
st.cut(776, X + 0.08, 2.75, 2.6)
st.zoom(776, 878, z=2.8, scale=2.3)
st.snap("phone", 776, lead=2, face=False)
st.eyes("normal", 776); st.brows(0, 0.0, 776); st.mouth("neutral", 776); st.look(0.04, -0.03, 776)
st.look(0.04, -0.03, 792); st.look(0.0, 0.0, 803); st.blink(808); st.brows(8, 0.03, 806)
st.say(A + "S06.wav", 814, end="sad", closed="neutral")
st.eyes("wide", 864); st.brows(0, 0.1, 864); st.punch(864, 0.08); st.shake(864, 880, 0.04)

# ==== 13) G'OYA!                                                 882-907
st.cut(882, X, 2.5, 5.2)
st.eyes("normal", 882); st.brows(0, 0.0, 882); st.mouth("neutral", 882)
st.snap("idea_R", 886, lead=2, face=False)
st.mouth("grin", 886); st.brows(0, 0.08, 886)
st.prop("bulb", 886, 904, x=-0.62, z=3.75, size=0.9)
st.fx("lines", 886, X, HEAD, 1.0, length=18)
st.sfx("ding", 886, 0.7)

# ==== 14) TELEFON: Sticky o'z kursini sotadi, $199               908-1055
st.cut(908, PH, 2.45, 6.0)
warp(rk, 80.0, 0.0, 908)
warp(st, PX, 0.1, 908); phone_show(908, False)
st.snap("present", 908, lead=2, face=False); st.brows(0, 0.05, 908)
card("NEW COURSE", ["MILLIONAIRE", "IN 30 SECONDS"], 909, 1055, sizes=(0.27, 0.22))
st.say(A + "S07.wav", 912, end="grin", closed="smile")
st.place("Phone_Burst", 997, x=40.78, scale=0.0, step=True); st.place("Phone_Burst", 1000, scale=1.2); st.place("Phone_Burst", 1003, scale=0.95)
st.caption("$199", 998, 1055, z=3.3, size=0.3, x=40.78)
st.sfx("pop", 997, 0.7)
st.snap("idea", 997, face=False)
st.bounce(1034, 0.22, 12)
st.drift(910, 1052)

# ==== 15) TELEFON: birinchi sotuv!                                1056-1107
off("Phone_Card", 1056); off("Phone_Burst", 1056)
warp(st, X, 0.0, 1056); phone_show(1056, True)
st.caption("COURSE SALES", 1056, 1107, z=2.85, size=0.2, x=PH)
st.caption("$0", 1056, 1065, z=2.05, size=0.8, x=PH)
st.caption("0 STUDENTS", 1056, 1065, z=1.3, size=0.2, x=PH)
st.caption("1 STUDENT", 1069, 1107, z=1.3, size=0.2, x=PH, color="green")
banner("Phone_BannerOK", 1058)
st.sfx("ding", 1058, 0.6)
st.caption("YOU MADE YOUR", 1061, 1107, z=3.88, size=0.17, x=40.22)
st.caption("FIRST SALE!", 1061, 1107, z=3.63, size=0.2, x=40.22, color="green")
st.voice(A + "P05.wav", 1062, 1.0, channel=3)
st.caption("$199", 1069, 1107, z=2.05, size=0.8, x=PH, color="green")
st.sfx("chaching", 1068, 0.5)
sparkle(1070, PH - 1.05, 2.5); sparkle(1076, PH + 1.05, 1.6); sparkle(1084, PH + 0.95, 2.6, 0.8); sparkle(1094, PH - 0.95, 1.5, 0.8)

# ==== 16) XONA: "I'M RICH!" - oltin tangalar yog'adi              1108-1169
st.cut(1108, 0.0, 2.3, 7.0)
off("Phone_BannerOK", 1108)
st.snap("cheer", 1108, lead=2, face=False); phone(1108, 0.62, 3.28, step=True)
st.eyes("money", 1108); st.brows(0, 0.08, 1108); st.look(0.0, 0.0, 1108)
st.say(A + "S08.wav", 1110, end="grin", closed="grin", opened="wide")
for f in (1110, 1126, 1142):
    st.bounce(f, 0.35, 12, sound=0.5)
    st.fx("dust", f + 12, X + (-0.32 if f == 1126 else 0.32), 0.14, 0.8)
for i, (cx, cx2) in enumerate(((-1.6, 1.25), (1.5, -1.0), (-0.9, 1.75), (1.05, -1.7), (-1.75, 0.9), (1.8, -0.55), (-1.2, 1.45), (1.3, -1.4), (-0.5, 1.1), (1.6, -0.8)), 1):
    n = "Coin_%d" % i
    for f0, x in ((1105 + i * 3, cx), (1136 + i * 3, cx2)):       # ikki to'lqin tanga
        st.place(n, f0, x=x, z=6.1, scale=1.0, step=True)
        st.place(n, f0 + 22, z=-0.7)
        st.place(n, f0 + 23, scale=0.0, step=True)
sh = st.caption("+$199", 1110, 1169, z=4.52, size=0.55, x=0.03, color="black")   # soya: oltin yozuv yaxshi o'qilsin
sh.location.y = -0.27
st.caption("+$199", 1110, 1169, z=4.55, size=0.55, color="gold")
st.sfx("chaching", 1112, 0.6); st.sfx("chaching", 1136, 0.5)
sparkle(1112, X - 0.85, 3.3); sparkle(1120, X + 0.95, 2.6); sparkle(1132, X - 0.8, 2.0); sparkle(1146, X - 1.3, 3.9)
st.drift(1110, 1168)

# ==== 17) TELEFON: "Refund requested" - musiqa birdan o'chadi     1170-1223
st.cut(1170, PH, 2.45, 6.0)
st.caption("COURSE SALES", 1160, 1223, z=2.85, size=0.2, x=PH)
st.caption("$199", 1160, 1182, z=2.05, size=0.8, x=PH, color="green")
st.caption("1 STUDENT", 1160, 1182, z=1.3, size=0.2, x=PH, color="green")
st.caption("0 STUDENTS", 1186, 1223, z=1.3, size=0.2, x=PH, color="red")
st.sfx("scratch", 1170, 0.9)
banner("Phone_BannerBad", 1171)
st.sfx("error", 1175, 0.45)
st.caption("REFUND REQUESTED", 1175, 1223, z=3.75, size=0.17, x=40.22, color="red", max_width=1.85)
st.voice(A + "P06.wav", 1184, 1.0, channel=3)
st.caption("$0", 1186, 1223, z=2.05, size=0.8, x=PH, color="red")
st.sfx("pop", 1186, 0.6)

# ==== 18) STICKY: tabassum so'nadi - "I hate business."           1224-1335
st.cut(1224, X + 0.08, 2.75, 2.6)
st.zoom(1224, 1330, z=2.8, scale=2.25)
st.mouth("grin", 1224)
st.eyes("normal", 1238); st.look(0.04, 0.02, 1238)
st.mouth("neutral", 1246); st.brows(10, 0.0, 1250); st.mouth("sad", 1256)
st.snap("slump", 1262, lead=4, over=0.1, face=False); phone(1258, 0.62, 3.28); phone(1264, 0.2, 1.1)
st.look(0.0, -0.03, 1264)
st.say(A + "S09.wav", 1272, volume=1.5, end="sad", closed="sad")

# ==== 19) YAKUN YOZUVI                                            1336-1415
st.cut(1336, 60.0, 2.3, 7.0)
st.caption("PART 2", 1340, 1500, z=3.35, size=0.62, x=60.0, color="gold")
st.caption("THE MILLIONAIRE'S", 1348, 1500, z=2.4, size=0.36, x=60.0, color="white")
st.caption("DOWNFALL", 1354, 1500, z=1.9, size=0.52, x=60.0, color="white")
st.sfx("trombone", 1338, 0.7)

S.frame_set(1)
