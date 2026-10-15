# video_05.py  -  "PAYDAY" sketch, haqiqiy ovoz effektlari bilan (17 soniya)
import bpy
st = bpy.data.texts["stickman_tools.py"].as_module()      # Sam
S = bpy.context.scene
A = "//video_03_audio/"                   # ovozlar video_03 dan (o'zgarmagan)
X = -0.55                                 # Sam turgan joy
HEAD = 2.78                               # bosh markazi balandligi

st.clear_animation()
st.backdrop("room")
S.frame_end = 512
S.render.filepath = "//video_05_"
st.music("//musiqa_01.wav", volume=0.12, fade=3, end=150)   # eshik taqillaganda musiqa birdan to'xtaydi
st.title("PAYDAY")
st.move_to(X, 0.0)
st.alive(1, 512, blink_skip=[(14, 100), (150, 300), (430, 500)])   # nafas oladi, ko'z qisadi

# ---- 1) UZOQ PLAN: telefonga maosh tushdi                     1-35
st.apply_pose("phone", 1)
st.prop("phone", -8, 96, x=0.62, z=2.55, size=0.6)
st.look(0.04, -0.03, 1)
st.sfx("ding", 6, 0.8)
st.caption("+$2,000", 6, 32, z=3.2, size=0.34, x=0.25, color="green")
st.eyes("wide", 18); st.brows(0, 0.09, 18); st.mouth("open", 18)
st.punch(18, 0.07)
st.fx("lines", 18, X, HEAD, 1.0, length=16)
st.sfx("pop", 18, 0.7)
st.drift(2, 34)

# ---- 2) YAQIN PLAN: ko'zlarida dollar                         36-97
st.cut(36, x=X, z=2.75, scale=2.4)
st.zoom(36, 96, scale=2.15)
st.eyes("money", 36); st.brows(0, 0.05, 36); st.look(0.0, 0.0, 36)
st.sfx("chaching", 37, 0.6)
st.fx("star", 37, X - 0.47, 3.3, 0.42)
st.fx("star", 44, X + 0.5, 2.3, 0.36)
st.say(A + "S01.wav", 40, end="grin", closed="grin")

# ---- 3) UZOQ PLAN: sakrab xursand bo'ladi, pullar uchadi      98-149
st.cut(98, x=0.0, z=2.3, scale=7.0)
st.eyes("normal", 98)
st.snap("cheer", 100)
for f in (100, 116, 132):
    st.bounce(f, 0.35, 12, sound=0.5)
    st.fx("dust", f + 12, X + (-0.32 if f == 116 else 0.32), 0.14, 0.8)
for n, f, x0, x1, z1 in (("Note_1", 100, -0.88, -2.35, 3.45), ("Note_2", 106, 0.9, 2.35, 4.3), ("Note_3", 112, 1.35, 2.35, 3.3)):
    st.place(n, f, x=x0, z=1.5, scale=1.0, step=True)
    st.place(n, f + 34, x=x1, z=z1)
    st.place(n, f + 36, scale=0.0, step=True)
st.caption("$2,000", 102, 214, z=4.55, size=0.55, color="green")
st.drift(100, 148)

# ---- 4) TAQ-TAQ: musiqa to'xtaydi, Sam qotib qoladi           150-195
st.sfx("knock3", 150, 1.0)
for f, dx in ((150, 0.0), (151, 0.05), (153, 0.0), (155, 0.0), (156, 0.05), (158, 0.0), (161, 0.0), (162, 0.05), (164, 0.0)):
    st.place("Set_Door", f, x=1.92 + dx)
st.punch(150, 0.06)
st.mouth("neutral", 152); st.brows(0, 0.06, 152); st.eyes("wide", 152); st.look(0.05, 0.0, 152)
st.fx("lines", 152, X, HEAD, 1.0, length=14)
st.zoom(150, 192, x=0.15, z=2.5, scale=6.6)
st.say(A + "S02.wav", 172, end="neutral")

# ---- 5) ESHIK OCHILADI: uchta to'lov yugurib kelib pulni olib ketadi   196-299
st.cut(196, x=0.0, z=2.3, scale=7.0)
st.sfx("slam", 196, 1.0)
st.place("Set_Door", 196, scale=(0.12, 1.0, 1.0), step=True)
st.fx("star", 196, 1.45, 2.2, 1.5)
st.shake(196, 204, 0.08)
st.snap("shock", 198)
for i, (f, amount, col) in enumerate(((198, "$900", "black"), (222, "$250", "black"), (246, "$3", "red")), 1):
    b = "Bill_%d" % i; n = "Note_%d" % i
    st.place(b, f, x=1.45, z=1.43, scale=0.05, step=True)      # eshikdan chiqadi
    st.place(b, f + 4, scale=1.5)
    st.sfx("whoosh", f + 2, 0.9)
    st.run(b, f + 4, f + 16, 0.45)                             # Sam yoniga yuguradi
    st.place(n, f + 16, x=X + 0.1, z=2.0, scale=1.0, step=True)  # pul Sam'dan chiqadi
    st.place(n, f + 20, x=-0.39, z=1.64)                       # to'lov qo'liga o'tadi
    st.sfx("drop", f + 18, 0.8)
    st.run(b, f + 20, f + 34, -3.4)                            # Sam ustidan yugurib chiqib ketadi
    st.place(n, f + 34, x=-4.24, z=1.64)
    st.fx("star", f + 23, X + 0.15, 2.0, 1.0)                  # zarba
    if i < 3:
        st.spin(f + 23, 2, 16)                                 # Sam pirildoqdek aylanadi
        st.sfx("whirl", f + 23, 0.7)
    else:
        up = st.flatten(f + 23, 16)                            # uchinchisi uni yapaloq qilib ketadi
        st.sfx("splat", f + 23, 0.9)
        st.sfx("pop", up, 0.8)
    st.caption(amount, f + 19, (f + 42) if i < 3 else 298, z=4.55, size=0.55, color=col)
st.say(A + "S03.wav", 220, end="open")
st.drift(206, 296)

# ---- 6) YAQIN PLAN: ko'z yoshi, bo'sh hamyondan pashsha uchadi         300-365
st.cut(300, x=X, z=2.75, scale=2.4)
st.zoom(300, 364, scale=2.15)
st.snap("slump", 296, lead=2)
st.eyes("normal", 300); st.look(0.0, -0.03, 300)
st.tears(306, 364)
st.sfx("trombone", 302, 0.75)
st.place("FX_Wallet", 304, x=X + 0.36, z=2.02, scale=0.0, step=True)
st.place("FX_Wallet", 307, scale=1.05)
st.place("FX_Wallet", 310, scale=0.9)
st.place("FX_Wallet", 364, scale=0.9)
st.place("FX_Wallet", 365, scale=0.0, step=True)
st.flutter("FX_Fly", 314, 346, X + 0.36, 2.12, X + 0.75, 3.7)
st.sfx("buzz", 314, 0.5)
st.caption("$3", 308, 364, z=1.76, size=0.22, x=X + 0.36, color="red")

# ---- 7) KALENDAR: keyingi maoshgacha 29 kun                    366-437
st.cut(366, x=-1.35, z=4.57, scale=1.9)
st.zoom(366, 373, scale=1.5)
st.sfx("boom", 366, 0.8)
st.place("Set_Calendar", 366, scale=1.18, step=True)
st.place("Set_Calendar", 372, scale=1.0)
st.voice(A + "S04.wav", 372, 1.0, channel=2)
st.drift(376, 436)

# ---- 8) QICHQIRIQ                                             438-469
st.cut(438, x=X, z=2.65, scale=2.3)
st.snap("shock", 436, lead=2)
st.mouth("scream", 438); st.eyes("wide", 438); st.brows(0, 0.1, 438); st.look(0.0, 0.0, 438)
st.voice(A + "S05.wav", 440, 1.0, channel=2)
st.sfx("rumble", 440, 0.6)
st.fx("lines", 438, X, HEAD, 1.0, length=30)
st.zoom(440, 469, scale=2.6)
st.shake(440, 469, 0.05)
st.shiver(440, 468, 0.03)

# ---- 9) TASHQARIDAN: butun uy silkinadi                       470-497
st.cut(470, x=20.0, z=2.3, scale=7.0)
for f in range(470, 498, 2):
    st.place("Ext_House", f, x=20.0 + (0.07 if (f // 2) % 2 else -0.07))
st.place("Ext_House", 498, x=20.0)
st.shake(470, 496, 0.04)
st.caption("NOOOOO!", 472, 600, z=4.25, size=0.6, x=20.0)

# ---- 10) AYLANMA YAKUN: oxirgi kadr birinchi kadr bilan bir xil   498-512
st.cut(498, x=0.0, z=2.3, scale=7.0)
st.place("Set_Door", 498, scale=(1.0, 1.0, 1.0), step=True)
st.apply_pose("shock", 497, face=False)
st.apply_pose("phone", 498)
st.eyes("normal", 498); st.look(0.04, -0.03, 498)
st.prop("phone", 488, 600, x=0.62, z=2.55, size=0.6)

S.frame_set(1)
