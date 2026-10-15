# stickman_tools.py (v8)  -  personajlar, kamera, rangli sahna, tovush effektlari, gapiradigan telefon
# Burchaklar ekran bo'yicha gradusda: 0 = o'ngga, 90 = tepaga, -90 = pastga, 180 = chapga
# .L = ekranda O'NG tomondagi qo'l/oyoq, .R = ekranda CHAP tomondagi
#
# Sam:  st = bpy.data.texts["stickman_tools.py"].as_module()
# Rick: rk = bpy.data.texts["stickman_tools.py"].as_module(); rk.use("R_"); rk.show()
import bpy, math, random

PREFIX = ""
RIG_NAME = "Stickman_Rig"
MOUTHS = ("neutral", "smile", "grin", "open", "wide", "sad", "think", "scream")
PROPS = ("question", "exclaim", "bulb", "phone", "clock", "house", "money", "sweat")
EYE_BASE = {"Eye.L": (0.085, 2.90), "Eye.R": (-0.085, 2.90)}
BROW_BASE = {"Brow.L": (0.095, 3.015), "Brow.R": (-0.095, 3.015)}
ARM_PARTS = {"L": ("UpperArm.L", "Forearm.L"), "R": ("UpperArm.R", "Forearm.R")}
COLORS = {"black": "Stk_Black", "white": "Stk_White", "red": "Stk_Red", "green": "Stk_Green", "gold": "Stk_Gold", "cream": "Stk_Cream", "grey": "Stk_Grey", "blue": "Stk_Blue"}

POSES = {
    "rest":    {},
    "stand":   {"upper_arm.L": -80, "forearm.L": -86, "upper_arm.R": -100, "forearm.R": -94},
    "hips":    {"upper_arm.L": -45, "forearm.L": -131, "upper_arm.R": -135, "forearm.R": -49},
    "think":   {"upper_arm.L": -50, "forearm.L": 108, "upper_arm.R": -135, "forearm.R": -49, "head": 92, "front": "L"},
    "point":   {"upper_arm.L": 8, "forearm.L": 14, "upper_arm.R": -100, "forearm.R": -94, "head": 88},
    "point_left": {"upper_arm.R": 172, "forearm.R": 166, "upper_arm.L": -80, "forearm.L": -86, "head": 92},
    "idea":    {"upper_arm.L": 28, "forearm.L": 86, "upper_arm.R": -135, "forearm.R": -49},
    "cheer":   {"upper_arm.L": 25, "forearm.L": 80, "upper_arm.R": 155, "forearm.R": 100},
    "wave":    {"upper_arm.L": 18, "forearm.L": 78, "upper_arm.R": -100, "forearm.R": -94, "head": 93},
    "wave2":   {"upper_arm.L": 18, "forearm.L": 48, "upper_arm.R": -100, "forearm.R": -94, "head": 93},
    "shrug":   {"upper_arm.L": -42, "forearm.L": 8, "upper_arm.R": -138, "forearm.R": 172},
    "present": {"upper_arm.L": -32, "forearm.L": -8, "upper_arm.R": -148, "forearm.R": -172},
    "shock":   {"upper_arm.L": 20, "forearm.L": 95, "upper_arm.R": 160, "forearm.R": 85},
    "slump":   {"upper_arm.L": -78, "forearm.L": -84, "upper_arm.R": -102, "forearm.R": -96, "head": 80},
    "tip":     {"upper_arm.L": 40, "forearm.L": 105, "upper_arm.R": -100, "forearm.R": -94},
    "phone":   {"upper_arm.L": -62, "forearm.L": 58, "upper_arm.R": -100, "forearm.R": -94, "head": 86},
}
# poza bilan birga keladigan yuz: (og'iz, qosh qiyaligi, qosh ko'tarilishi, bitta qoshni ko'tarish)
POSE_FACE = {
    "rest": ("neutral", 0, 0.0, 0.0), "stand": ("neutral", 0, 0.0, 0.0), "hips": ("smile", 0, 0.0, 0.0),
    "think": ("think", 6, 0.0, 0.035), "point": ("smile", 0, 0.015, 0.0), "point_left": ("smile", 0, 0.015, 0.0),
    "idea": ("grin", 0, 0.04, 0.0), "cheer": ("grin", 0, 0.04, 0.0), "wave": ("smile", 0, 0.02, 0.0),
    "wave2": ("smile", 0, 0.02, 0.0), "shrug": ("sad", 12, 0.02, 0.0), "present": ("smile", 0, 0.01, 0.0),
    "shock": ("open", 0, 0.06, 0.0), "slump": ("sad", 14, 0.0, 0.0), "tip": ("smile", 0, 0.02, 0.0),
    "phone": ("neutral", 0, 0.0, 0.0),
}

# ---------------- personajni tanlash ----------------
def use(prefix):
    """Qaysi personaj boshqarilishini tanlaydi: "" = Sam, "R_" = Rick."""
    global PREFIX, RIG_NAME
    PREFIX = prefix
    RIG_NAME = prefix + "Stickman_Rig"

def show(visible=True):
    """Personajni ko'rsatadi yoki yashiradi."""
    c = bpy.data.collections[PREFIX + "Stickman"]
    c.hide_viewport = c.hide_render = not visible

def _o(name):
    return bpy.data.objects[PREFIX + name]

def _rig():
    return bpy.data.objects[RIG_NAME]

def _ordered(rig):
    out = []
    def walk(b):
        out.append(b)
        for c in b.children:
            walk(c)
    for b in rig.data.bones:
        if b.parent is None:
            walk(b)
    return out

def _rest_angle(b):
    v = b.tail_local - b.head_local
    return math.degrees(math.atan2(v.z, v.x))

def _nearest(target, current):
    return current + ((target - current + 180.0) % 360.0 - 180.0)

def _step(ob, path, frame, value):
    """Qiymatni aynan shu kadrda keskin o'zgartiradi."""
    ob.keyframe_insert(path, frame=frame - 1)
    setattr(ob, path, value)
    ob.keyframe_insert(path, frame=frame)

def _restore(ob):
    ob.animation_data_clear()
    if "rest_loc" in ob:
        ob.location = tuple(ob["rest_loc"])
        ob.rotation_euler = tuple(ob["rest_rot"])
        ob.scale = tuple(ob["rest_scale"])
        ob.hide_viewport = ob.hide_render = bool(ob["rest_hide"])

# ---------------- yuz ----------------
def mouth(name, frame=None):
    """Og'iz: neutral, smile, grin, open, sad, think, scream"""
    for m in MOUTHS:
        ob = _o("Mouth_" + m)
        ob.hide_viewport = ob.hide_render = (m != name)
        if frame is not None:
            ob.keyframe_insert("hide_viewport", frame=frame)
            ob.keyframe_insert("hide_render", frame=frame)

def brows(tilt=0.0, lift=0.0, frame=None, cock=0.0):
    """Qoshlar: tilt > 0 xavotirli, tilt < 0 jahldor; lift = ko'tarish; cock = bitta qoshni ko'tarish"""
    for n, (bx, bz) in BROW_BASE.items():
        ob = _o(n)
        s = 1.0 if n.endswith("L") else -1.0
        ob.location = (bx, 0.0, bz + lift + (cock if s > 0 else 0.0))
        ob.rotation_euler = (0.0, s * math.radians(tilt), 0.0)
        if frame is not None:
            ob.keyframe_insert("location", frame=frame)
            ob.keyframe_insert("rotation_euler", frame=frame)

def eyes(mode="normal", frame=1):
    """Ko'z turi shu kadrdan boshlab: normal, wide (katta hayratli ko'z), money ($ belgili ko'z)."""
    for side in ("L", "R"):
        _step(_o("EyeWhite." + side), "scale", frame, (1.0, 1.0, 1.0) if mode == "wide" else (0.0, 0.0, 0.0))
        _step(_o("EyeDollar." + side), "scale", frame, (1.0, 1.0, 1.0) if mode == "money" else (0.0, 0.0, 0.0))
        _step(_o("Eye." + side), "scale", frame, (0.0, 0.0, 0.0) if mode == "money" else (1.0, 1.0, 1.0))

def look(dx=0.0, dz=0.0, frame=None):
    """Ko'zlarni suradi (taxminan -0.05 .. 0.05)."""
    for n, (bx, bz) in EYE_BASE.items():
        ob = _o(n)
        ob.location = (bx + dx, 0.0, bz + dz)
        if frame is not None:
            ob.keyframe_insert("location", frame=frame)

def blink(frame):
    """Ko'z qisish."""
    for n in EYE_BASE:
        ob = _o(n)
        for f, s in ((frame - 2, 1.0), (frame, 0.1), (frame + 3, 1.0)):
            ob.scale = (1.0, 1.0, s)
            ob.keyframe_insert("scale", frame=f)

def talk(f0, f1, step=4, end="smile", closed="neutral", opened="open"):
    """f0 dan f1 gacha gapirayotgandek og'zini ochib-yopadi."""
    f = f0
    op = True
    while f < f1:
        mouth(opened if op else closed, f)
        op = not op
        f += step
    mouth(end, f1)

# ---------------- pozalar va harakat ----------------
def apply_pose(name, frame=None, face=True):
    """Pozani qo'yadi. frame berilsa, o'sha kadrga kalit yozadi. Pozada "root": 100 kabi qiymat butun tanani og'diradi."""
    rig = _rig()
    pose = POSES[name]
    total = {}
    for b in _ordered(rig):
        pb = rig.pose.bones[b.name]
        ptot = total[b.parent.name] if b.parent else 0.0
        local = (pose[b.name] - _rest_angle(b)) - ptot if b.name in pose else 0.0
        local = _nearest(local, math.degrees(pb.rotation_euler.z))
        pb.rotation_euler = (0.0, 0.0, math.radians(local))
        total[b.name] = ptot + local
        if frame is not None:
            pb.keyframe_insert("rotation_euler", index=2, frame=frame)
    front = pose.get("front", "")
    for side, names in ARM_PARTS.items():
        for n in names:
            ob = _o(n)
            ob.location.y = -0.10 if side in front else 0.0
            if frame is not None:
                ob.keyframe_insert("location", index=1, frame=frame)
    if face and name in POSE_FACE:
        m, tilt, lift, cock = POSE_FACE[name]
        mouth(m, frame)
        brows(tilt, lift, frame, cock)
    bpy.context.view_layer.update()

def hold(name, f0, f1, face=True):
    """Pozani f0 kadrdan f1 kadrgacha ushlab turadi."""
    apply_pose(name, f0, face)
    apply_pose(name, f1, face)

def move_to(x=0.0, z=0.0, frame=None):
    """Butun personajni suradi (x = o'ng/chap, z = tepa/past)."""
    pb = _rig().pose.bones["root"]
    pb.location = (x, z, 0.0)
    if frame is not None:
        pb.keyframe_insert("location", frame=frame)

def hop(frame, height=0.25, length=10):
    """Kichik sakrash."""
    pb = _rig().pose.bones["hips"]
    for f, h in ((frame, 0.0), (frame + length // 2, height), (frame + length, 0.0)):
        pb.location = (0.0, h, 0.0)
        pb.keyframe_insert("location", frame=f)

def bounce(frame, height=0.3, length=12, sound=None):
    """Cho'zilib-siqilib sakrash (multfilmdagidek). sound=0.5 - sakrash shuvillashi va yerga tushish ovozi shu balandlikda qo'shiladi."""
    if sound:
        sfx("jump", frame, sound)
        sfx("land", frame + length - 1, sound * 1.1)
    rig = _rig()
    hips = rig.pose.bones["hips"]
    root = rig.pose.bones["root"]
    for f, h, sx, sy in ((frame - 3, 0.0, 1.0, 1.0), (frame, 0.0, 1.14, 0.84), (frame + length // 2, height, 0.9, 1.12),
                         (frame + length, 0.0, 1.16, 0.82), (frame + length + 3, 0.0, 1.0, 1.0)):
        hips.location = (0.0, h, 0.0)
        hips.keyframe_insert("location", frame=f)
        root.scale = (sx, sy, 1.0)
        root.keyframe_insert("scale", frame=f)

def shiver(f0, f1, amp=0.025):
    """Titrash: f0 dan f1 gacha."""
    pb = _rig().pose.bones["root"]
    base = tuple(pb.location)
    rnd = random.Random(f0)
    for f in range(f0, f1):
        pb.location = (base[0] + rnd.uniform(-amp, amp), base[1], base[2])
        pb.keyframe_insert("location", frame=f)
    pb.location = base
    pb.keyframe_insert("location", frame=f1)

def tip_hat(frame, lift=0.2, length=18):
    """Shlyapani ko'tarib qo'yadi (faqat shlyapasi bor personaj uchun)."""
    ob = _o("Hat")
    loc = tuple(ob["rest_loc"])
    rot = tuple(ob["rest_rot"])
    for f, dz, r in ((frame, 0.0, 0.0), (frame + length // 3, lift, 14.0), (frame + 2 * length // 3, lift, 14.0), (frame + length, 0.0, 0.0)):
        ob.location = (loc[0] + dz * 0.5, loc[1], loc[2] + dz)
        ob.rotation_euler = (rot[0], rot[1] + math.radians(r), rot[2])
        ob.keyframe_insert("location", frame=f)
        ob.keyframe_insert("rotation_euler", frame=f)

# ---------------- rasmlar (rekvizit) va boshqa obyektlar ----------------
def prop(name, f_on, f_off, x=None, z=None, size=1.0):
    """Rasm chiqaradi: question, exclaim, bulb, phone, clock, house, money, sweat.
    x, z berilsa, personajga nisbatan o'sha joyda chiqadi (x manfiy = chap tomonda). size = kattaligi."""
    ob = _o("Prop_" + name)
    if x is not None and z is not None:
        ob.location = (x, 0.0, z)
        ob.keyframe_insert("location", frame=f_on - 1)
        ob.keyframe_insert("location", frame=f_off + 4)
    for f, s in ((f_on - 1, 0.0), (f_on + 4, 1.2), (f_on + 7, 1.0), (f_off, 1.0), (f_off + 4, 0.0)):
        ob.scale = (s * size, s * size, s * size)
        ob.keyframe_insert("scale", frame=f)

def fly(name, f0, f1, x0, z0, x1, z1):
    """Rasmni (x0, z0) nuqtadan (x1, z1) nuqtaga uchirib o'tkazadi va yo'qotadi."""
    ob = _o("Prop_" + name)
    for f, s in ((f0 - 1, 0.0), (f0 + 3, 1.0), (f1 - 2, 1.0), (f1 + 2, 0.0)):
        ob.scale = (s, s, s)
        ob.keyframe_insert("scale", frame=f)
    ob.location = (x0, 0.0, z0)
    ob.keyframe_insert("location", frame=f0 - 1)
    ob.location = (x1, 0.0, z1)
    ob.keyframe_insert("location", frame=f1 + 2)

def place(name, frame, x=None, z=None, scale=None, step=False):
    """Istalgan obyektni (qo'shimcha personaj, pul, eshik) shu kadrda joylaydi. step=True - keskin o'zgarish.
    scale: bitta son yoki (x, y, z)."""
    ob = bpy.data.objects[name]
    if step:
        ob.keyframe_insert("location", frame=frame - 1)
        ob.keyframe_insert("scale", frame=frame - 1)
    if x is not None:
        ob.location.x = x
    if z is not None:
        ob.location.z = z
    if scale is not None:
        ob.scale = (scale, scale, scale) if isinstance(scale, (int, float)) else tuple(scale)
    ob.keyframe_insert("location", frame=frame)
    ob.keyframe_insert("scale", frame=frame)

# ---------------- kamera ----------------
_CAM = [0.0, 2.3, 7.0]          # x, z, masshtab (7 = to'liq kadr, 2.6 = yuz yaqin plani)

def _cam_key(frame, x, z, scale):
    cam = bpy.context.scene.camera
    cam.location = (x, -10.0, z)
    cam.keyframe_insert("location", frame=frame)
    cam.data.ortho_scale = scale
    cam.data.keyframe_insert("ortho_scale", frame=frame)
    hud = bpy.data.objects.get("HUD")
    if hud:
        s = scale / 7.0
        hud.scale = (s, s, s)
        hud.keyframe_insert("scale", frame=frame)

def cut(frame, x=0.0, z=2.3, scale=7.0):
    """Keskin kadr almashishi: shu kadrdan kamera (x, z) markazga va scale masshtabga o'tadi."""
    _cam_key(frame - 1, _CAM[0], _CAM[1], _CAM[2])
    _cam_key(frame, x, z, scale)
    _CAM[:] = [x, z, scale]

def zoom(f0, f1, x=None, z=None, scale=None):
    """f0 dan f1 gacha silliq surish yoki yaqinlashish."""
    x = _CAM[0] if x is None else x
    z = _CAM[1] if z is None else z
    scale = _CAM[2] if scale is None else scale
    _cam_key(f0, _CAM[0], _CAM[1], _CAM[2])
    _cam_key(f1, x, z, scale)
    _CAM[:] = [x, z, scale]

def shake(f0, f1, amp=0.06):
    """Kamerani f0 dan f1 gacha silkitadi."""
    cam = bpy.context.scene.camera
    rnd = random.Random(f0)
    for f in range(f0, f1):
        cam.location = (_CAM[0] + rnd.uniform(-amp, amp), -10.0, _CAM[1] + rnd.uniform(-amp, amp))
        cam.keyframe_insert("location", frame=f)
    cam.location = (_CAM[0], -10.0, _CAM[1])
    cam.keyframe_insert("location", frame=f1)

def reset_camera():
    cam = bpy.context.scene.camera
    cam.animation_data_clear()
    cam.data.animation_data_clear()
    cam.location = (0.0, -10.0, 2.3)
    cam.data.ortho_scale = 7.0
    hud = bpy.data.objects.get("HUD")
    if hud:
        hud.animation_data_clear()
        hud.scale = (1.0, 1.0, 1.0)
    _CAM[:] = [0.0, 2.3, 7.0]

def backdrop(name="white"):
    """Fon: "white" = oq (oddiy uslub), "room" = rangli xona (eshik va kalendar bilan)."""
    S = bpy.context.scene
    c = bpy.data.collections.get("Stickman_Set")
    if name == "white":
        S.world.color = (1.0, 1.0, 1.0)
        if c:
            c.hide_viewport = c.hide_render = True
    else:
        wm = bpy.data.materials.get("Stk_Wall")          # ishlatilmagan material fayl qayta ochilganda yo'qoladi
        S.world.color = tuple(wm.diffuse_color)[:3] if wm else (0.485, 0.539, 0.392)
        if c:
            c.hide_viewport = c.hide_render = False

# ---------------- tozalash ----------------
def clear_animation():
    """Shu personajni boshlang'ich holatga qaytaradi.
    Sam uchun chaqirilsa: yozuvlar, ovozlar, kamera, fon va qo'shimcha obyektlarni ham tozalaydi, boshqa personajlarni yashiradi."""
    rig = _rig()
    rig.animation_data_clear()
    for pb in rig.pose.bones:
        pb.rotation_euler = (0.0, 0.0, 0.0)
        pb.location = (0.0, 0.0, 0.0)
        pb.scale = (1.0, 1.0, 1.0)
    for cn in ("Stickman_Parts", "Stickman_Props"):
        for ob in bpy.data.collections[PREFIX + cn].objects:
            _restore(ob)
    if PREFIX == "":
        clear_captions()
        clear_audio()
        reset_camera()
        for k in _FX:
            _FX[k] = 0
        for cn in ("Stickman_Extras", "Stickman_Set"):
            c = bpy.data.collections.get(cn)
            if c:
                for ob in c.objects:
                    _restore(ob)
        backdrop("white")
        for c in bpy.data.collections:
            if c.name.endswith("_Stickman"):
                c.hide_viewport = c.hide_render = True

def clear_captions():
    c = bpy.data.collections.get("Stickman_Captions")
    if c:
        for ob in list(c.objects):
            cu = ob.data
            bpy.data.objects.remove(ob, do_unlink=True)
            if cu.users == 0:
                bpy.data.curves.remove(cu)

# ---------------- yozuvlar ----------------
CAPTION_FONTS = (r"C:\Windows\Fonts\ariblk.ttf", r"C:\Windows\Fonts\arialbd.ttf")

def _font():
    import os
    for p in CAPTION_FONTS:
        if os.path.exists(p):
            try:
                return bpy.data.fonts.load(p, check_existing=True)
            except Exception:
                pass
    return None

def caption(text, f_on, f_off, z=4.75, size=0.42, x=0.0, max_width=3.4, color="black", hud=False):
    """Sahnadagi yozuv: f_on kadrda paydo bo'ladi, f_off kadrda yo'qoladi. color: black, white, red, green, gold, cream, grey.
    z = balandlik, size = harf kattaligi. Keng yozuv o'zi kichrayadi. hud=True bo'lsa kameraga yopishadi."""
    c = bpy.data.collections.get("Stickman_Captions")
    if c is None:
        c = bpy.data.collections.new("Stickman_Captions")
        bpy.context.scene.collection.children.link(c)
        c.hide_select = True
    cu = bpy.data.curves.new("Caption", 'FONT')
    cu.body = text
    cu.size = size
    cu.align_x = 'CENTER'
    cu.align_y = 'CENTER'
    cu.space_line = 0.95
    f = _font()
    if f:
        cu.font = f
    cu.materials.append(bpy.data.materials.get(COLORS.get(color, "Stk_Black")) or bpy.data.materials["Stk_Black"])
    ob = bpy.data.objects.new("Caption", cu)
    c.objects.link(ob)
    if hud and bpy.data.objects.get("HUD"):
        ob.parent = bpy.data.objects["HUD"]
        ob.location = (x, z, -5.0)
        ob.rotation_euler = (0.0, 0.0, 0.0)
    else:
        ob.location = (x, -0.3, z)
        ob.rotation_euler = (math.pi / 2, 0.0, 0.0)
    bpy.context.view_layer.update()
    w = ob.dimensions.x
    if hud and ob.parent is not None and ob.parent.scale.x > 1e-6:
        w = w / ob.parent.scale.x          # HUD kamera bilan kichrayadi - haqiqiy enini olamiz
    if w > max_width:
        cu.size = size * max_width / w
    for fr, s in ((f_on - 1, 0.0), (f_on + 4, 1.12), (f_on + 7, 1.0), (f_off, 1.0), (f_off + 3, 0.0)):
        ob.scale = (s, s, s)
        ob.keyframe_insert("scale", frame=fr)
    return ob

def title(text, f_on=1, f_off=100000, y=2.75, size=0.5, color="black"):
    """Ekran tepasidagi sarlavha: kamera yaqinlashsa ham joyida turadi."""
    return caption(text, f_on, f_off, z=y, size=size, color=color, hud=True)

# ---------------- ovoz, musiqa, tovush effektlari ----------------
AUDIO_NAMES = ("Voice", "Music", "Sfx")

def _strips():
    S = bpy.context.scene
    se = S.sequence_editor or S.sequence_editor_create()
    return se.strips if hasattr(se, "strips") else se.sequences

def _audio_setup():
    S = bpy.context.scene
    try:
        S.render.ffmpeg.audio_codec = 'AAC'
        S.render.ffmpeg.audio_bitrate = 192
    except Exception:
        pass
    try:
        S.sync_mode = 'AUDIO_SYNC'
    except Exception:
        pass

def _set_end(strip, frame):
    for attr in ("right_handle", "frame_final_end"):
        if hasattr(strip, attr):
            try:
                setattr(strip, attr, frame)
                return
            except Exception:
                pass

def _length(strip):
    for attr in ("duration", "frame_final_duration"):
        if hasattr(strip, attr):
            return int(getattr(strip, attr))
    return 0

def voice(path, frame=1, volume=1.0, channel=1):
    """Ovoz faylini qo'shadi (hikoyachi). path = fayl ("//nom.mp3" = shu papkadagi fayl), frame = boshlanish kadri."""
    _audio_setup()
    s = _strips().new_sound("Voice", path, channel, frame)
    s.volume = volume
    return s

def _levels(path, fps=30):
    """Ovoz faylining har kadrdagi balandligi (0..1)."""
    import aud
    import numpy as np
    snd = aud.Sound.file(bpy.path.abspath(path))
    data = snd.data()
    rate = snd.specs[0]
    mono = np.abs(data).mean(axis=1) if data.ndim > 1 else np.abs(data)
    step = rate / fps
    n = int(len(mono) / step)
    lv = [float(mono[int(i * step):int((i + 1) * step)].mean()) for i in range(n)]
    m = max(lv) if lv else 0.0
    return [v / m for v in lv] if m > 0 else lv

def say(path, frame, volume=1.0, end="smile", closed="neutral", opened="open"):
    """Shu personaj gapiradi: ovoz fayli qo'shiladi va og'zi ovoz balandligiga qarab ochiladi
    (jim = closed, o'rtacha = opened, baland = wide). Tugash kadrini qaytaradi."""
    s = voice(path, frame, volume, channel=3 if PREFIX else 2)
    f1 = frame + _length(s)
    try:
        lv = _levels(path)
    except Exception:
        lv = None
    if not lv:
        talk(frame, f1, end=end, closed=closed, opened=opened)
        return f1
    last = None
    for i in range(0, len(lv), 2):
        v = max(lv[i:i + 2])
        m = "wide" if v > 0.6 else (opened if v > 0.28 else closed)
        if m != last:
            mouth(m, frame + i)
            last = m
    mouth(end, f1)
    return f1

def sfx(name, frame, volume=1.0):
    """Tovush effekti: sfx papkasidagi fayl nomi (ding, pop, chaching, jump, land, knock3, slam, whoosh, drop, whirl, splat, hit, trombone, boom, rumble, buzz, spring, boing, type, tick, error, glitch, scratch, fall, rewind, ffwd, roar, roar_small, heart, heart_fast, riser, riser2). Manbalari: sfx/MANBA.txt"""
    _audio_setup()
    path = name if ("/" in name or "\\" in name) else "//sfx/" + name + ".wav"
    strips = _strips()
    n = len([s for s in strips if s.name.startswith("Sfx")])
    s = strips.new_sound("Sfx", path, 6 + (n % 6), frame)
    s.volume = volume
    return s

def music(path, volume=0.1, fade=25, end=None):
    """Fon musiqasi: end kadrgacha (berilmasa video oxirigacha) chaladi, oxirgi fade kadrda so'nadi.
    Avval S.frame_end ni qo'ying, keyin shu buyruqni chaqiring."""
    _audio_setup()
    S = bpy.context.scene
    s = _strips().new_sound("Music", path, 5, 1)
    end = (S.frame_end + 1) if end is None else end
    _set_end(s, end)
    s.volume = volume
    s.keyframe_insert("volume", frame=end - fade)
    s.volume = 0.0
    s.keyframe_insert("volume", frame=end)
    return s

def clear_audio():
    """Skript qo'shgan ovoz, musiqa va effektlarni olib tashlaydi."""
    S = bpy.context.scene
    se = S.sequence_editor
    if se is None:
        return
    strips = se.strips if hasattr(se, "strips") else se.sequences
    for s in list(strips):
        if s.type == 'SOUND' and s.name.split(".")[0] in AUDIO_NAMES:
            strips.remove(s)
    S.animation_data_clear()

# ================= v4: jonliroq animatsiya =================
_FX = {"star": 0, "dust": 0, "lines": 0}

def snap(name, frame, lead=3, over=0.2, settle=4, face=True):
    """Pozaga keskin o'tish: lead kadrda tez o'tadi, biroz oshib ketadi va settle kadrda joyiga tushadi.
    Keyingi snap gacha poza o'zi ushlanib turadi (hold kerak emas)."""
    rig = _rig()
    pose = POSES[name]
    total = {}
    plan = []
    for b in _ordered(rig):
        pb = rig.pose.bones[b.name]
        ptot = total[b.parent.name] if b.parent else 0.0
        cur = math.degrees(pb.rotation_euler.z)
        tgt = (pose[b.name] - _rest_angle(b)) - ptot if b.name in pose else 0.0
        tgt = _nearest(tgt, cur)
        total[b.name] = ptot + tgt
        plan.append((pb, cur, tgt))
    for pb, cur, tgt in plan:
        pb.keyframe_insert("rotation_euler", index=2, frame=frame - lead)
        pb.rotation_euler = (0.0, 0.0, math.radians(tgt + over * (tgt - cur)))
        pb.keyframe_insert("rotation_euler", index=2, frame=frame)
        pb.rotation_euler = (0.0, 0.0, math.radians(tgt))
        pb.keyframe_insert("rotation_euler", index=2, frame=frame + settle)
    front = pose.get("front", "")
    for side, names in ARM_PARTS.items():
        for n in names:
            ob = _o(n)
            ob.location.y = -0.10 if side in front else 0.0
            ob.keyframe_insert("location", index=1, frame=frame)
    if face and name in POSE_FACE:
        m, tilt, lift, cock = POSE_FACE[name]
        mouth(m, frame)
        brows(tilt, lift, frame, cock)
    bpy.context.view_layer.update()

def punch(frame, amount=0.08, length=5):
    """Kichik siqilish zarbasi (cho'chib tushish, urilish)."""
    root = _rig().pose.bones["root"]
    for f, sx, sy in ((frame - 2, 1.0, 1.0), (frame, 1.0 + amount, 1.0 - amount), (frame + length, 1.0, 1.0)):
        root.scale = (sx, sy, 1.0)
        root.keyframe_insert("scale", frame=f)

def spin(frame, turns=2, length=16):
    """Pirildoqdek aylanadi."""
    root = _rig().pose.bones["root"]
    root.scale = (1.0, 1.0, 1.0)
    root.keyframe_insert("scale", frame=frame - 1)
    for i in range(length + 1):
        sx = math.cos(2 * math.pi * turns * i / length)
        if abs(sx) < 0.07:
            sx = 0.07 if sx >= 0 else -0.07
        root.scale = (sx, 1.0, 1.0)
        root.keyframe_insert("scale", frame=frame + i)
    root.scale = (1.0, 1.0, 1.0)
    root.keyframe_insert("scale", frame=frame + length + 1)

def flatten(frame, hold=14):
    """Yapaloq bo'lib qoladi, keyin "pop" bilan tiklanadi. Tiklanish kadrini qaytaradi."""
    root = _rig().pose.bones["root"]
    for f, sx, sy in ((frame - 2, 1.0, 1.0), (frame, 1.7, 0.1), (frame + hold, 1.7, 0.1), (frame + hold + 3, 0.8, 1.25),
                      (frame + hold + 6, 1.06, 0.96), (frame + hold + 8, 1.0, 1.0)):
        root.scale = (sx, sy, 1.0)
        root.keyframe_insert("scale", frame=f)
    return frame + hold + 3

def alive(f0, f1, blink_skip=()):
    """Tirik turish: nafas oladi va tasodifiy ko'z qisadi. blink_skip = ko'z qisilmaydigan oraliqlar [(a, b), ...]."""
    rig = _rig()
    tb = rig.pose.bones["torso"]
    f = f0
    up = False
    while f <= f1:
        tb.scale = (1.0, 1.03 if up else 1.0, 1.0)
        tb.keyframe_insert("scale", frame=f)
        up = not up
        f += 22
    rnd = random.Random(f0 + len(PREFIX))
    f = f0 + rnd.randint(20, 50)
    while f < f1 - 5:
        if not any(a - 4 <= f <= b + 4 for a, b in blink_skip):
            blink(f)
        f += rnd.randint(45, 95)

def tears(f0, f1):
    """Ko'z yoshi oqadi."""
    for side in ("L", "R"):
        ob = _o("Tear." + side)
        _step(ob, "scale", f0, (1.0, 1.0, 0.05))
        ob.scale = (1.0, 1.0, 1.0)
        ob.keyframe_insert("scale", frame=f0 + 8)
        k = 0
        for f in range(f0 + 14, f1 - 2, 6):
            ob.scale = (1.25 if k % 2 == 0 else 0.85, 1.0, 1.0)
            ob.keyframe_insert("scale", frame=f)
            k += 1
        _step(ob, "scale", f1, (0.0, 0.0, 0.0))

def fx(kind, frame, x, z, size=1.0, length=None):
    """Chizma effekt: star (zarba yulduzi), dust (chang), lines (hayrat chiziqlari, length kadr turadi)."""
    pool = {"star": 3, "dust": 4, "lines": 2}[kind]
    i = _FX[kind] % pool + 1
    _FX[kind] += 1
    name = "FX_%s_%d" % (kind.capitalize(), i)
    ob = bpy.data.objects[name]
    if kind == "star":
        place(name, frame, x=x, z=z, scale=0.0, step=True)
        ob.rotation_euler.y = random.Random(frame).uniform(0.0, 0.7)
        place(name, frame + 2, scale=1.3 * size)
        place(name, frame + 4, scale=size)
        place(name, frame + (length or 8), scale=0.0)
    elif kind == "dust":
        place(name, frame, x=x, z=z, scale=0.3 * size, step=True)
        place(name, frame + 8, z=z + 0.12, scale=size)
        place(name, frame + (length or 12), scale=0.0, step=True)
    else:
        n = length or 14
        place(name, frame, x=x, z=z, scale=0.6 * size, step=True)
        k = 0
        for f in range(frame + 3, frame + n, 4):
            place(name, f, scale=(1.12 if k % 2 == 0 else 1.0) * size)
            k += 1
        place(name, frame + n, scale=0.0, step=True)

def run(name, f0, f1, x1, bob=0.07, lean=8.0, dust=True):
    """Oyoqli qo'shimcha personajni (name_LegA, name_LegB) hozirgi joyidan x1 ga yugurtiradi: oyoqlari ishlaydi, tanasi tebranadi."""
    ob = bpy.data.objects[name]
    x0 = ob.location.x
    z0 = ob.location.z
    legs = [bpy.data.objects.get(name + "_LegA"), bpy.data.objects.get(name + "_LegB")]
    sp = bpy.data.objects.get(name + "_Speed")
    d = -1.0 if x1 < x0 else 1.0
    ob.keyframe_insert("location", frame=f0)
    ob.keyframe_insert("rotation_euler", frame=f0)
    for lg in legs:
        if lg:
            lg.keyframe_insert("rotation_euler", frame=f0)
    if sp:
        _step(sp, "scale", f0 + 1, (-d, 1.0, 1.0))
    frames = list(range(f0 + 3, f1, 3)) + [f1]
    for k, f in enumerate(frames):
        last = (f == f1)
        t = (f - f0) / float(f1 - f0)
        ob.location.x = x0 + (x1 - x0) * t
        ob.location.z = z0 + (0.0 if (last or k % 2) else bob)
        ob.rotation_euler.y = 0.0 if last else math.radians(d * lean + (3.0 if k % 2 else -3.0))
        ob.keyframe_insert("location", frame=f)
        ob.keyframe_insert("rotation_euler", frame=f)
        a = 0.0 if last else (38.0 if k % 2 == 0 else -38.0)
        for j, lg in enumerate(legs):
            if lg:
                lg.rotation_euler.y = math.radians(a if j == 0 else -a)
                lg.keyframe_insert("rotation_euler", frame=f)
    if sp:
        _step(sp, "scale", f1, (0.0, 0.0, 0.0))
    if dust:
        fx("dust", f0 + 1, x0 - d * 0.25, z0 - 1.25, 0.9)

def flutter(name, f0, f1, x0, z0, x1, z1, wobble=0.12):
    """Obyektni (masalan pashshani) egri-bugri yo'l bilan uchiradi va yo'qotadi."""
    rnd = random.Random(f0)
    place(name, f0, x=x0, z=z0, scale=1.0, step=True)
    for f in range(f0 + 3, f1, 3):
        t = (f - f0) / float(f1 - f0)
        place(name, f, x=x0 + (x1 - x0) * t + rnd.uniform(-wobble, wobble), z=z0 + (z1 - z0) * t + rnd.uniform(-wobble, wobble))
    place(name, f1, x=x1, z=z1)
    place(name, f1 + 1, scale=0.0, step=True)

def drift(f0, f1, amp=0.03):
    """Kamera sezilmas darajada suzib turadi (bitta kadr ichida, cut dan keyin chaqiring)."""
    cam = bpy.context.scene.camera
    rnd = random.Random(f0)
    a = amp * _CAM[2] / 7.0
    for f in range(f0 + 12, f1 - 6, 12):
        cam.location = (_CAM[0] + rnd.uniform(-a, a), -10.0, _CAM[1] + rnd.uniform(-a, a))
        cam.keyframe_insert("location", frame=f)
    cam.location = (_CAM[0], -10.0, _CAM[1])

# ================= v7: yurish, yozuv taxtachasi, chaqnash =================
def walk(f0, f1, x0, x1, step=6, arms=None):
    """f0 dan f1 gacha x0 dan x1 ga yuradi: oyoqlar almashadi, tana harakat tomonga egiladi. step = bir qadam necha kadr (kichik = tez).
    arms = qo'llar pozasi (berilmasa: bir qo'lda telefon, ikkinchisi boshda - vahima)."""
    d = 1 if x1 > x0 else -1
    a = arms or {"upper_arm.L": -62, "forearm.L": 58, "upper_arm.R": 140, "forearm.R": 75, "head": 86, "front": "R"}
    POSES["_wA"] = dict(a, **{"thigh.L": -58, "shin.L": -82, "thigh.R": -100, "shin.R": -118, "root": 90 - 5 * d})
    POSES["_wB"] = dict(a, **{"thigh.L": -80, "shin.L": -62, "thigh.R": -122, "shin.R": -98, "root": 90 - 5 * d})
    k = 0
    f = f0
    while f < f1:
        move_to(x0 + (x1 - x0) * (f - f0) / float(f1 - f0), 0.0, f)
        apply_pose("_wA" if k % 2 == 0 else "_wB", f, face=False)
        hop(f, 0.07, step)
        k += 1
        f += step
    move_to(x1, 0.0, f1)
    apply_pose("_wA" if k % 2 == 0 else "_wB", f1, face=False)

def plate(f_on, f_off, y, lines=1):
    """Kameraga yopishgan och rangli taxtacha - ustiga caption(..., hud=True) yoziladi. lines = 1 yoki 2 qator. y = caption dagi z bilan bir xil."""
    ob = bpy.data.objects["HUD_Plate%d" % lines]
    ob.location = (0.0, y, -5.06)
    ob.keyframe_insert("location", frame=f_on - 1)
    for f, sc in ((f_on - 1, 0.0), (f_on + 3, 1.08), (f_on + 6, 1.0), (f_off, 1.0), (f_off + 3, 0.0)):
        ob.scale = (sc, sc, sc)
        ob.keyframe_insert("scale", frame=f)

def pulse(ob, f0, f1, lo=1.0, hi=1.22, step=4):
    """Yozuvni (caption qaytargan obyektni) f0 dan f1 gacha chaqnatadi: kattalashib-kichrayadi."""
    k = 0
    for f in range(f0, f1, step):
        s = hi if k % 2 == 0 else lo
        ob.scale = (s, s, s)
        ob.keyframe_insert("scale", frame=f)
        k += 1

# ================= v8: gapiradigan telefon, qo'ldagi yongan telefon, otjimaniya, keskin yozuv =================
def flash(text, f0, f1, **kw):
    """Yozuv f0 kadrda birdan chiqadi va f1 kadrda birdan yo'qoladi (parametrlari caption dagidek)."""
    ob = caption(text, f0, f1, **kw)
    ob.animation_data_clear()
    for f, s in ((f0 - 1, 0.0), (f0, 1.0), (f1 - 1, 1.0), (f1, 0.0)):
        ob.scale = (s, s, s)
        ob.keyframe_insert("scale", frame=f)
    return ob

def squint(frame, v=0.55):
    """Ko'zni shu kadrda qisadi: 1 = ochiq, 0.55 = shubhali, 0.1 = yumuq."""
    for n in EYE_BASE:
        ob = _o(n)
        ob.keyframe_insert("scale", frame=frame - 1)
        ob.scale = (1.0, 1.0, v)
        ob.keyframe_insert("scale", frame=frame)

def hand_phone(frame, x, z, size=0.6, lit=True, step=True):
    """Qo'ldagi telefon (Prop_phone) va uning yongan yuzli ekrani (Prop_phoneon). size=0 - yashiradi.
    Shu buyruq ishlatilgan videoda prop("phone") ni chaqirmang. phone pozasida (0.62, 2.55), cheer da (0.62, 3.28), chap qo'lda x manfiy."""
    for ob, vis in ((_o("Prop_phone"), True), (_o("Prop_phoneon"), lit)):
        if step:
            ob.keyframe_insert("location", frame=frame - 1)
            ob.keyframe_insert("scale", frame=frame - 1)
        v = size if vis else 0.0
        ob.location = (x, 0.0, z)
        ob.scale = (v, v, v)
        ob.keyframe_insert("location", frame=frame)
        ob.keyframe_insert("scale", frame=frame)

def phone_face(frame, big=True, z=None, scale=None, step=True):
    """Telefon olamidagi (x = 40) yuzning joyi: big=True - ekran o'rtasida katta (z 2.3, 1.5),
    False - tepada kichik (z 3.2, 1.15), ostida kartochka uchun joy qoladi."""
    z = (2.3 if big else 3.2) if z is None else z
    scale = (1.5 if big else 1.15) if scale is None else scale
    place("PFace", frame, z=z, scale=scale, step=step)

def phone_on(frame, big=True):
    """Telefon ekrani yonadi va yuzi paydo bo'ladi (undan oldin place("Phone_ScreenOff", 1, scale=1.0, step=True))."""
    place("Phone_ScreenOff", frame, scale=0.0, step=True)
    place("Phone_ScreenOn", frame, scale=1.0, step=True)
    phone_face(frame, big)

def phone_mood(frame, lid=0.7, tilt=10.0, lift=0.0, cock=0.0):
    """Telefon yuzi shu kadrdan: lid = qovoq (0 katta ochiq, 0.7 mensimaydigan, 0.9 juda mag'rur),
    tilt > 0 = xo'jayin qoshi, tilt < 0 = muloyim, lift = qoshlarni ko'tarish, cock = bitta qoshni ko'tarish."""
    for side, sg in (("L", 1.0), ("R", -1.0)):
        ld = bpy.data.objects["PFace_Lid" + side]
        br = bpy.data.objects["PFace_Brow" + side]
        ld.keyframe_insert("scale", frame=frame - 1)
        br.keyframe_insert("rotation_euler", frame=frame - 1)
        br.keyframe_insert("location", frame=frame - 1)
        ld.scale = (1.0, 1.0, lid) if lid > 0.01 else (0.0, 0.0, 0.0)
        ld.keyframe_insert("scale", frame=frame)
        br.rotation_euler = (0.0, sg * math.radians(tilt), 0.0)
        br.keyframe_insert("rotation_euler", frame=frame)
        br.location.z = 0.66 + lift + (cock if side == "R" else 0.0)
        br.keyframe_insert("location", frame=frame)

def phone_blink(frame):
    for side in "LR":
        e = bpy.data.objects["PFace_Eye" + side]
        for f, s in ((frame - 2, 1.0), (frame, 0.1), (frame + 3, 1.0)):
            e.scale = (1.0, 1.0, s)
            e.keyframe_insert("scale", frame=f)

def phone_say(path, frame, volume=0.75):
    """Telefon gapiradi: ovoz qo'shiladi (4-kanal), og'zi ovoz balandligiga qarab ochiladi. Tugash kadrini qaytaradi."""
    s = voice(path, frame, volume, channel=4)
    n = _length(s)
    try:
        lv = _levels(path)
    except Exception:
        lv = []
    mo = bpy.data.objects["PFace_Mouth"]
    mo.scale = (1.0, 1.0, 0.1)
    mo.keyframe_insert("scale", frame=frame - 1)
    for i in range(0, len(lv), 2):
        v = max(lv[i:i + 2])
        mo.scale = (1.0, 1.0, 0.1) if v < 0.1 else (0.9, 1.0, min(1.0, 0.3 + v))
        mo.keyframe_insert("scale", frame=frame + i)
    mo.scale = (1.0, 1.0, 0.1)
    mo.keyframe_insert("scale", frame=frame + n + 1)
    return frame + n

def phone_grin(frame, on=True):
    """Telefon og'zi: on=True - yovuz tirjayish (PFace_Grin), False - yana gapiradigan og'iz."""
    mo = bpy.data.objects["PFace_Mouth"]
    gr = bpy.data.objects["PFace_Grin"]
    mo.keyframe_insert("scale", frame=frame - 1)
    gr.keyframe_insert("scale", frame=frame - 1)
    mo.scale = (0.0, 0.0, 0.0) if on else (1.0, 1.0, 0.1)
    gr.scale = (1.0, 1.0, 1.0) if on else (0.0, 0.0, 0.0)
    mo.keyframe_insert("scale", frame=frame)
    gr.keyframe_insert("scale", frame=frame)

def plank_pose(th, x=-1.7, z=0.27, hand=(0.46, -0.03), head=62):
    """Otjimaniya pozasi: tana th gradusga og'gan (bosh o'ngda), oyoq uchi (x, z) da, qo'llar poldagi hand nuqtasiga tiraladi."""
    arm, sh = 0.55, 2.3
    sx = x + sh * math.cos(math.radians(th))
    sz = z + sh * math.sin(math.radians(th))
    def ik(tx, tz):
        dx, dz = tx - sx, tz - sz
        d = min(math.hypot(dx, dz), 2 * arm - 1e-4)
        ua = math.degrees(math.atan2(dz, dx)) - math.degrees(math.acos(d / 2.0 / arm))
        ex = sx + arm * math.cos(math.radians(ua))
        ez = sz + arm * math.sin(math.radians(ua))
        return ua, math.degrees(math.atan2(tz - ez, tx - ex))
    ual, fal = ik(hand[0] + 0.05, hand[1])
    uar, far = ik(hand[0] - 0.06, hand[1])
    return {"root": th, "head": head, "upper_arm.L": ual, "forearm.L": fal, "upper_arm.R": uar, "forearm.R": far,
            "thigh.L": th + 180, "shin.L": th + 180, "foot.L": -80, "thigh.R": th + 178, "shin.R": th + 178, "foot.R": -84}

def plank(frame, th, x=-1.7, z=0.27, hand=(0.46, -0.03), head=62):
    """Otjimaniya kaliti: th = 20 tepada, 5 pastda. Bir marta bosish: plank(f, 20), plank(f+3, 12), plank(f+6, 5), plank(f+9, 12), plank(f+12, 20)."""
    POSES["_plank"] = plank_pose(th, x, z, hand, head)
    move_to(x, z, frame)
    apply_pose("_plank", frame, face=False)

def flat(frame, x=-1.7, z=0.15, head=40):
    """Polda yuztuban yotadi (head=72 - boshini ko'targan)."""
    POSES["_flat"] = {"root": 0, "head": head, "upper_arm.L": 4, "forearm.L": -4, "upper_arm.R": 200, "forearm.R": 176,
                      "thigh.L": 180, "shin.L": 180, "foot.L": -80, "thigh.R": 178, "shin.R": 178, "foot.R": -84}
    move_to(x, z, frame)
    apply_pose("_flat", frame, face=False)
