# video_16.py  -  "He Carried Water for Money. His Brother Built a Pipe." (Buckets or Pipes)
# Narrator Fenrir (S01-S04, S06, S07, S09-S15), Sticky Puck (S05, S08). Town set at x = 130 (v16_assets.py).
import bpy, os, math, random, aud
T = bpy.data.texts["stickman_tools.py"]
st = T.as_module()                        # Sticky - buckets
mx = T.as_module(); mx.use("R_")          # Max - blue cap, builds the pipe (silent)
tm = T.as_module(); tm.use("T_")          # Tom - townsman, later the hired helper
ly = T.as_module(); ly.use("L_")          # Lily - townswoman
gp = T.as_module(); gp.use("G_")          # Grandpa = the Mayor
ALL = (st, mx, tm, ly, gp)
S = bpy.context.scene
O = bpy.data.objects
A = "//video_16_audio/"
GAIN = 1.3
SX, MX = 131.2, 132.85                    # shot-1 spots (loop end returns here)
BX, TX = 130.55, 131.1                    # town barrel; tap origin (pipe 1 starts here, spout at TX-0.55, z 1.19)
PZ = 0.12                                 # pipe height

st.clear_animation()
for m in ALL[1:]:
    m.clear_animation(); m.show()
st.backdrop("room")
S.frame_start = 1; S.frame_end = 1500
S.render.filepath = "//He Carried Water for Money. His Brother Built a Pipe.mp4"

EST = {"S01": 49, "S02": 84, "S03": 101, "S04": 61, "S05": 31, "S06": 108, "S07": 25, "S08": 32, "S09": 108,
       "S10": 186, "S11": 57, "S12": 90, "S13": 73, "S14": 131, "S15": 73}
def clip(key):
    p = bpy.path.abspath(A + key + ".wav")
    if not os.path.exists(p): return EST[key]
    s = aud.Sound.file(p); return int(round(s.length / s.specs[0] * 30))
def N(key, f, vol=0.9):
    """Narrator line (no mouth). Returns the end frame."""
    st.voice(A + key + ".wav", f, volume=vol, channel=1); return f + clip(key)
def say(m, key, f, vol=0.95):
    m.say(A + key + ".wav", f, volume=vol); return f + clip(key)
def sfx(name, f, vol=0.5, cut=None):
    s = st.sfx(name, f, vol)
    if cut: st._set_end(s, f + cut)
    return s
def keyall(ob, f):
    for p in ("location", "rotation_euler", "scale"): ob.keyframe_insert(p, frame=f)
def put(ob, f, x=None, z=None, rot=None, s=None, y=None, step=False):
    if isinstance(ob, str): ob = O[ob]
    if step: keyall(ob, f - 1)
    if x is not None: ob.location.x = x
    if z is not None: ob.location.z = z
    if y is not None: ob.location.y = y
    if rot is not None: ob.rotation_euler = (0.0, math.radians(rot), 0.0)
    if s is not None: ob.scale = (s, s, s) if isinstance(s, (int, float)) else tuple(s)
    keyall(ob, f)
def skey(ob, pairs):
    if isinstance(ob, str): ob = O[ob]
    for f, s in pairs:
        ob.scale = (s, s, s) if isinstance(s, (int, float)) else tuple(s); ob.keyframe_insert("scale", frame=f)
def on(name, f, x=None, z=None, s=1.0, y=None): put(name, f, x=x, z=z, s=s, y=y, step=True)
def off(name, f): put(name, f, s=0.0, step=True)
def popin(name, f, x=None, z=None, s=1.0, y=None):
    put(name, f, x=x, z=z, y=y, s=0.0, step=True); put(name, f + 3, s=s * 1.15); put(name, f + 6, s=s)
def P(m, pose, f): m.apply_pose(pose, f, face=False)
def swap(m, old, new, f): P(m, old, f - 1); P(m, new, f)
def go(m, f, x, z=0.0):
    pb = m._rig().pose.bones["root"]; pb.keyframe_insert("location", frame=f - 1); m.move_to(x, z, f)
class Face:
    def __init__(self, m): self.m = m; self.l = [0.0, 0.0]
    def look(self, f, dx, dz):
        self.m.look(self.l[0], self.l[1], f - 1); self.m.look(dx, dz, f); self.l[:] = [dx, dz]
FS, FM, FT, FLY, FG = Face(st), Face(mx), Face(tm), Face(ly), Face(gp)
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
STAND_L = {"upper_arm.L": -80, "forearm.L": -86}; STAND_R = {"upper_arm.R": -100, "forearm.R": -94}
def tilt(d, ang):
    """Whole body rotated to root angle ang (90 = upright); absolute arm/head angles turn with it."""
    out = {k: (v + ang - 90 if isinstance(v, (int, float)) else v) for k, v in d.items()}
    out["root"] = ang; return out
PO = {
    "catch": pose(reach("L", 0.45, 3.05), STAND_R, head=88),
    "carry1": pose(reach("L", 0.42, 1.38), STAND_R, head=88),
    "carry1l": pose(reach("L", 0.42, 1.38), STAND_R, head=82),
    "carry2": pose(reach("L", 0.42, 1.38), reach("R", -0.42, 1.38)),
    "bent": {"torso": 38, "head": 20, "upper_arm.L": -95, "forearm.L": -100, "upper_arm.R": -112, "forearm.R": -104},
    "pat_up": pose(reach("R", -0.8, 1.95), STAND_L, head=94),
    "pat": pose(reach("R", -0.85, 1.62), STAND_L, head=96),
    "cup": pose(reach("R", -0.1, 3.05), STAND_L, head=100),
    "sign_up": pose(reach("L", 0.3, 3.2), reach("R", -0.3, 3.2)),
    "sign_dn": pose(reach("L", 0.3, 1.55), reach("R", -0.3, 1.55)),
}
for m in ALL:
    m.POSES.update(PO)

# ---- buckets follow a hand through a Copy Location constraint (influence keyed) ----
BK = ["FX_Bucket"] + ["FX_Bucket_%d" % k for k in range(2, 7)]
for n in BK:
    ob = O[n]
    for c in [c for c in ob.constraints if c.name == "v16hand"]: ob.constraints.remove(c)
    c = ob.constraints.new("COPY_LOCATION"); c.name = "v16hand"; c.use_offset = True; c.influence = 0.0
    ob.location.y = -0.15
def hold(n, m, side, f):
    """Bucket n hangs from m's hand (side "L"/"R") from frame f."""
    ob = O[n]; c = ob.constraints["v16hand"]
    c.keyframe_insert("influence", frame=f - 1); keyall(ob, f - 1)
    c.target = m._rig(); c.subtarget = "forearm." + side; c.head_tail = 1.0
    c.influence = 1.0; c.keyframe_insert("influence", frame=f)
    ob.location = (0.0, -0.15, 0.0); ob.rotation_euler = (0, 0, 0); keyall(ob, f)
def drop(n, f, x, z, rot=0.0, s=None):
    """Bucket n is free again at (x, z) from frame f."""
    ob = O[n]; c = ob.constraints["v16hand"]
    c.keyframe_insert("influence", frame=f - 1); keyall(ob, f - 1)
    c.influence = 0.0; c.keyframe_insert("influence", frame=f)
    put(ob, f, x=x, z=z, y=-0.15, rot=rot, s=s)
def water(n, f, full):
    skey(n + "_W", ((f - 1, O[n + "_W"].scale.x), (f, 1.0 if full else 0.0)))

# ---------- town set ----------
on("Town_Back", 1)
for k, x in ((1, 129.3), (2, 128.0), (3, 126.7), (4, 125.4)): on("Town_House_%d" % k, 1, x=x)
for n in ("R_Hat", "R_Bowtie", "T_Helmet", "G_Helmet"): off(n, 1)
on("R_Cap", 1); on("T_Beanie", 1)
O["FX_Barrel"].location.y = 0.1
for m, x in ((st, SX), (mx, MX), (tm, 140.0), (ly, 141.0), (gp, 142.0)):
    go(m, 1, x); P(m, "stand", 1); m.mouth("neutral", 1)
HOOK = st.caption("SAME TOWN. SAME OPPORTUNITY.", -6, 95, z=2.72, size=0.32, color="black", max_width=3.6, hud=True)

# =================== shot 1 (f1-53): HOOK - buckets drop into both hands ===================
e1 = N("S01", 5)
st.cut(1, 132.05, 2.35, 6.8); st.zoom(1, 53, 132.05, 2.35, 5.9); st.shake(9, 13, 0.08)
sfx("wind", 1, 0.2, cut=150)
for m, n, x in ((st, "FX_Bucket", SX), (mx, "FX_Bucket_2", MX)):
    P(m, "catch", 1); m.eyes("wide", 1); m.mouth("open", 1)
    put(n, 1, x=x + 0.45, z=6.1, y=-0.15, rot=-25, s=1.0, step=True)
    put(n, 4, z=5.3, rot=-12); put(n, 6, z=4.3, rot=6); put(n, 7, z=3.4, rot=0)
    hold(n, m, "L", 8); P(m, "catch", 8); P(m, "carry1", 11)
    m.punch(9, 0.16, 6); m.mouth("wide", 9); m.eyes("normal", 15); m.mouth("neutral", 18)
    st.fx("dust", 10, x, 0.12, 0.7)
sfx("pickaxe", 9, 0.42); sfx("pickaxe", 11, 0.3)
for m in (st, mx): P(m, "carry1", 13); P(m, "carry1l", 15)
FS.look(13, 0.0, 0.0); FS.look(15, 0.05, -0.01); FM.look(13, 0.0, 0.0); FM.look(15, 0.05, -0.01)
O["Town_Glint"].location.x = 132.6
popin("Town_Glint", 16, s=0.9); off("Town_Glint", 30); sfx("shimmer", 16, 0.35)

# =================== shot 2 (f54-): outcome tease, whip left (Sticky) / right (Max) ===================
s2 = e1
st.cut(s2, 132.05, 2.35, 5.2); st.zoom(s2, s2 + 6, 132.05, 2.35, 4.8); st.shake(s2, s2 + 6, 0.14)
sfx("whoosh", s2, 0.5)
v2 = s2 + 4
e2 = N("S02", v2)
f = s2 + 6
st.cut(f, 131.35, 2.2, 4.6)
off("FX_Bucket", f); off("FX_Bucket_2", f); go(mx, f, 150.0)
P(st, "carry1l", f - 1); P(st, "bent", f); go(st, f, 130.95); st.mouth("sad", f); st.squint(f, 0.25)
for n, x in (("FX_Bucket_3", 130.35), ("FX_Bucket_4", 131.55)):
    put(n, f, x=x, z=0.62, y=-0.15, s=1.0, step=True); water(n, f, True)
st.prop("sweat", f + 4, v2 + 40, x=1.35, z=2.6, size=0.7)
CR = v2 + 34                                            # "bad back"
sfx("crack", CR, 0.55); st.punch(CR, 0.1, 5); st.fx("star", CR, 131.25, 1.75, 0.7)
for i, n in enumerate(("FX_Star_1", "FX_Star_2", "FX_Star_3")):
    a0 = i * 2.1
    for j, ff in enumerate(range(CR + 1, v2 + 46, 3)):
        a = a0 + j * 0.7
        put(n, ff, x=132.05 + 0.42 * math.cos(a), z=2.6 + 0.16 * math.sin(a), y=-0.3, s=0.32, step=(j == 0))
    off(n, v2 + 46)
WR = v2 + 45                                            # whip right: "the other built a pipeline"
st.cut(WR, 131.7, 2.25, 4.6); st.shake(WR, WR + 4, 0.12); sfx("whoosh", WR - 2, 0.45)
go(st, WR, 150.0); off("FX_Bucket_3", WR); off("FX_Bucket_4", WR)
go(mx, WR, 131.95); P(mx, "stand", WR); mx.mouth("smile", WR); FM.look(WR, -0.04, -0.01)
on("FX_PipeTap", WR, x=TX, z=PZ, y=0.28)
for k in range(1, 9): on("FX_Pipe_%d" % k, WR, x=TX + (k - 1), z=PZ, y=0.28)
PAT = e2 - 10                                           # "pipeline"
P(mx, "stand", PAT - 8); P(mx, "pat_up", PAT - 3); P(mx, "pat", PAT); P(mx, "pat_up", PAT + 4); P(mx, "pat", PAT + 7)
sfx("pickaxe", PAT, 0.4); sfx("pickaxe", PAT + 7, 0.25); mx.punch(PAT, 0.04, 4)
mx.apply_pose("pat", PAT + 12, face=False); P(mx, "stand", PAT + 16)
FM.look(PAT + 12, 0.0, 0.0)

# =================== shot 3: rewind, Tom's empty cup, the Mayor's sign ===================
s3 = e2 + 8
st.cut(s3, 131.6, 2.35, 7.7); st.zoom(s3, s3 + 9, 131.6, 2.35, 7.25); st.shake(s3, s3 + 5, 0.1)
sfx("rewind", s3 - 4, 0.5)
off("FX_PipeTap", s3)
for k in range(1, 9): off("FX_Pipe_%d" % k, s3)
go(st, s3, 131.1); P(st, "stand", s3); st.mouth("neutral", s3); st.squint(s3, 1.0); FS.look(s3, 0.0, 0.0)
go(mx, s3, 133.1); P(mx, "stand", s3); mx.mouth("neutral", s3); FM.look(s3, 0.0, 0.0)
go(tm, s3, 130.1); P(tm, "stand", s3); tm.mouth("neutral", s3)
v3 = s3 + 6
e3 = N("S03", v3)
CUP = O["FX_Cup"]
P(tm, "stand", v3 + 5); P(tm, "cup", v3 + 9); tm.mouth("open", v3 + 9); FT.look(v3 + 9, -0.02, 0.05)
put(CUP, v3 + 8, x=130.0, z=3.2, y=-0.2, rot=160, s=0.0, step=True); put(CUP, v3 + 9, s=0.9)
DR = O["T_Prop_sweat"]
put(DR, v3 + 19, x=-0.12, z=3.0, s=0.0, step=True); put(DR, v3 + 20, s=0.5); put(DR, v3 + 28, x=-0.3, z=0.25, s=0.5)
put(DR, v3 + 30, z=0.1, s=(0.9, 0.5, 0.25)); put(DR, v3 + 36, s=0.0)
sfx("pop", v3 + 29, 0.3); tm.mouth("sad", v3 + 30); FT.look(v3 + 30, 0.0, -0.06)
P(tm, "cup", v3 + 30); P(tm, "shrug", v3 + 34); off("FX_Cup", v3 + 34)
MP = v3 + 40                                            # "and the mayor paid"
go(gp, MP, 132.1, -4.6); P(gp, "sign_up", MP); gp.mouth("grin", MP)
gp.move_to(132.1, 0.3, MP + 5); gp.move_to(132.1, 0.0, MP + 8)
SG = O["FX_Sign"]
put(SG, MP, x=132.1, z=-1.5, y=-0.22, s=1.4, step=True); put(SG, MP + 5, z=3.25); put(SG, MP + 8, z=3.0)
sfx("spring", MP + 1, 0.35)
SL = v3 + 64                                            # "one dollar"
P(gp, "sign_up", SL - 4); put(SG, SL - 4, z=3.3)
P(gp, "sign_dn", SL); put(SG, SL, z=-0.05); put(SG, SL + 3, z=0.0)
sfx("land", SL, 0.7); st.fx("dust", SL, 131.75, 0.1, 1.0); st.fx("dust", SL + 1, 132.4, 0.1, 0.9); st.shake(SL, SL + 6, 0.12)
for m, x in ((st, 131.0), (mx, 133.2)):
    m.eyes("wide", SL); m.mouth("open", SL)
    m.hop(SL, 0.22, 8); go(m, SL + 1, x)
    m.eyes("normal", SL + 14); m.mouth("neutral", SL + 16)
sfx("pop", SL + 8, 0.25)
FS.look(SL, 0.04, -0.02); FM.look(SL, -0.04, -0.02)
s4 = e3 + 8
# ---- PART 1 END (shots 1-3) ----

# =================== PART 2: shots 4-7 ===================
def dirt_copy(src, name):
    """Dirt-coloured copy of a library object (made once, rests at scale 0)."""
    if name in O: return O[name]
    a = O[src]; ob = a.copy(); ob.data = a.data.copy(); ob.name = name; ob.animation_data_clear()
    for c in a.users_collection: c.objects.link(ob)
    mats = [bpy.data.materials["Stk_Dirt"], bpy.data.materials.get("Stk_DirtDark") or bpy.data.materials["Stk_Dirt"]]
    for i, m in enumerate(ob.data.materials):
        if m and m.name != "Stk_Black": ob.data.materials[i] = mats[i % 2]
    ob["rest_loc"] = list(ob.location); ob["rest_rot"] = list(ob.rotation_euler); ob["rest_scale"] = [0.0] * 3; ob["rest_hide"] = 0
    ob.scale = (0, 0, 0); return ob
DIRT = dirt_copy("FX_CoinPile", "FX_DirtPile")
CLODS = [dirt_copy("Coin_%d" % k, "FX_Clod_%d" % k) for k in (1, 2, 3, 4)]
PILE = O["FX_CoinPile"]; TAG = O["FX_Tag"]
def arc(ob, f0, f1, p0, p1, h=1.5, s=0.5, rot=0.0):
    n = f1 - f0
    put(ob, f0, x=p0[0], z=p0[1], y=-0.35, s=0.0, step=True); put(ob, f0 + 1, s=s)
    for i in range(1, n + 1):
        t = i / n; put(ob, f0 + i, x=p0[0] + (p1[0] - p0[0]) * t, z=p0[1] + (p1[1] - p0[1]) * t + 4 * h * t * (1 - t), rot=rot * t)
    put(ob, f1 + 1, s=0.0)
ci = [0]
def coin(f, p0, p1, h=0.8):
    ci[0] = ci[0] % 10 + 1; arc(O["Coin_%d" % ci[0]], f, f + 7, p0, p1, h, s=0.5)
SH_TOP, SH_TIP = 0.62, 0.98
DIG = {"dig_up": ((-0.08, 2.4), math.radians(-32)), "dig_down": ((0.1, 1.85), math.radians(-18))}
def grip(top, ang, t):
    L = SH_TOP + SH_TIP; return (top[0] - t * L * math.sin(ang), top[1] - t * L * math.cos(ang))
for k, (top, ang) in DIG.items():
    h1 = grip(top, ang, 0.06); h2 = grip(top, ang, 0.36)
    mx.POSES[k] = pose(reach("R", h1[0], h1[1]), reach("L", h2[0], h2[1]))
SHV = O["FX_Shovel"]
def shovel(f, bx, k, step=False):
    top, ang = DIG[k]; ux, uz = math.sin(ang), math.cos(ang)
    put(SHV, f, x=bx + top[0] - SH_TOP * ux, z=top[1] - SH_TOP * uz, y=-0.3, rot=math.degrees(ang), s=1.0, step=step)
    return (bx + top[0] - (SH_TOP + SH_TIP) * ux, top[1] - (SH_TOP + SH_TIP) * uz)
STIFF = {"upper_arm.L": -84, "forearm.L": -86, "upper_arm.R": -96, "forearm.R": -94, "head": 90}
FLEX = {"upper_arm.L": 18, "forearm.L": 112, "upper_arm.R": 162, "forearm.R": 68, "head": 90}
LAUGH = pose(reach("L", 0.75, 1.75), reach("R", -0.35, 1.6), head=97)
for a in (60, 76, 120, 160, 180): st.POSES["stiff%d" % a] = tilt(STIFF, a)
st.POSES["flex"] = FLEX; st.POSES["locked"] = tilt(FLEX, 103)
for a in (94, 100, 106, 120, 150, 180): st.POSES["laugh%d" % a] = tilt(LAUGH, a)
mx.POSES["shh"] = pose(reach("L", 0.08, 2.72), STAND_R, head=90)
mx.POSES["wheelA"] = {"torso": 40, "head": 25, "upper_arm.L": -40, "forearm.L": -75, "upper_arm.R": -55, "forearm.R": -60}
mx.POSES["wheelB"] = {"torso": 40, "head": 25, "upper_arm.L": -55, "forearm.L": -95, "upper_arm.R": -45, "forearm.R": -78}
for m in (tm, ly): m.POSES["cheerB"] = pose(reach("L", 0.5, 1.7), reach("R", -0.35, 3.1))

# ---------- shot 4: sprint laps, the counter, the flex and the back crack ----------
st.cut(s4, 131.9, 2.3, 7.0)
off("FX_Sign", s4); go(gp, s4, 142.0); go(tm, s4, 140.0); go(mx, s4, 146.0)
put("FX_Barrel", s4, x=BX, z=0.0, y=0.1, s=0.95, step=True)
put(PILE, s4, x=131.3, z=0.0, y=-0.25, s=(0.4, 1.0, 0.04), step=True)
put(TAG, s4, x=132.35, z=0.0, y=0.2, s=1.0, step=True)
skey("FX_Tag_Txt1", ((s4 - 1, 0.0), (s4, 0.0)))
put("FX_Sticker_1", s4, x=132.62, z=1.33, y=0.1, s=0.75, step=True)
go(st, s4, 131.1); swap(st, "stand", "carry2", s4); st.mouth("grin", s4)
hold("FX_Bucket", st, "L", s4); hold("FX_Bucket_3", st, "R", s4)
on("FX_Bucket", s4); on("FX_Bucket_3", s4); water("FX_Bucket", s4, False); water("FX_Bucket_3", s4, False)
v4 = s4 + 4
e4 = N("S04", v4)
sfx("ffwd", s4 + 2, 0.35, cut=58)
f = s4 + 3
for lap, num in enumerate(("33", "66", "100")):
    P(st, "carry2", f - 1); st.walk(f, f + 8, 131.1, 133.7, step=2, arms=PO["carry2"])
    water("FX_Bucket", f + 9, True); water("FX_Bucket_3", f + 9, True); sfx("splash", f + 8, 0.18, cut=12)
    st.walk(f + 9, f + 17, 133.7, 131.1, step=2, arms=PO["carry2"])
    d = f + 18; P(st, "carry2", d)
    water("FX_Bucket", d, False); water("FX_Bucket_3", d, False)
    popin("FX_Splash", d, x=BX, z=0.8, s=0.5, y=0.05); off("FX_Splash", d + 6)
    sfx("splash", d, 0.35, cut=20); coin(d, (BX, 1.2), (131.3, 0.35 + 0.15 * lap)); sfx("tick", d + 6, 0.4)
    put(PILE, d + 7, s=(0.4, 1.0, 0.12 + 0.12 * lap))
    if lap < 2: st.flash(num, d + 6, d + 18, x=132.35, z=0.95, size=0.32, color="black")
    f = d + 1
HUN = f + 5
MONEY = max(e4 + 1, HUN + 8)
skey("FX_Tag_Txt1", ((HUN - 1, 0.0), (HUN, 1.15), (HUN + 3, 1.0), (MONEY - 1, 1.0), (MONEY, 0.0)))
skey("FX_Tag_Txt2", ((MONEY - 1, 0.0), (MONEY + 3, 1.2), (MONEY + 6, 1.0)))
sfx("tick", HUN, 0.4); sfx("chaching", MONEY, 0.45)
FL = MONEY + 3
drop("FX_Bucket", FL, 131.75, 0.62); drop("FX_Bucket_3", FL, 132.75, 0.62)
P(st, "carry2", FL - 1); P(st, "cheer", FL + 2); sfx("jump", FL, 0.4)
st.move_to(131.1, 0.0, FL); st.move_to(132.0, 1.2, FL + 4); st.move_to(132.75, 0.62, FL + 8)
P(st, "flex", FL + 8); st.mouth("grin", FL + 8); st.punch(FL + 8, 0.08, 4)
for i in range(4): coin(FL + 8 + 2 * i, (131.3, 0.7), (131.0 + 0.25 * i, 3.6 - 0.2 * i), h=0.5)
st.cut(FL + 6, 132.3, 2.45, 5.2); st.zoom(FL + 6, FL + 40, 132.3, 2.35, 4.8)
v5 = FL + 8
e5 = say(st, "S05", v5)
CK = e5 + 3
P(st, "flex", CK - 1); P(st, "locked", CK); st.mouth("scream", CK); st.squint(CK, 0.12)
sfx("crack", CK, 0.6); st.fx("star", CK, 132.85, 1.75, 0.8); st.shake(CK, CK + 4, 0.1)
TP = CK + 12
P(st, "locked", TP - 1); P(st, "stiff76", TP)
P(st, "stiff120", TP + 4); P(st, "stiff160", TP + 7); P(st, "stiff180", TP + 9)
st.move_to(132.75, 0.62, TP); st.move_to(132.85, 0.45, TP + 4); st.move_to(132.95, 0.15, TP + 9)
sfx("pop", TP + 9, 0.5); sfx("land", TP + 9, 0.35); st.fx("dust", TP + 9, 130.2, 0.1, 0.9)
st.cut(TP + 2, 131.45, 2.0, 7.9); st.shake(TP + 9, TP + 12, 0.08)
s5 = TP + 18

# ---------- shot 5: Max carries fewer; night; dirt clods bury sleeping Sticky; pipe laid secretly ----------
st.cut(s5, 131.6, 2.0, 7.9); st.zoom(s5, s5 + 50, 131.75, 2.0, 7.6)
st.squint(s5, 0.08); st.mouth("neutral", s5)
off("FX_Tag", s5); off("FX_Sticker_1", s5); off("FX_Bucket", s5); off("FX_Bucket_3", s5)
v6 = s5 + 2
e6 = N("S06", v6)
go(mx, s5, 129.0); P(mx, "carry1", s5); on("FX_Bucket_2", s5); water("FX_Bucket_2", s5, True)
mx.walk(s5 + 1, s5 + 37, 129.0, 132.95, step=6, arms=PO["carry1"]); P(mx, "carry1", s5 + 38)
drop("FX_Bucket_2", s5 + 42, 133.65, 0.62); P(mx, "stand", s5 + 42)
NIGHT = v6 + 49
on("Town_Back_Night", NIGHT); sfx("whoosh", NIGHT, 0.3)
on("Town_Trench", NIGHT, x=TX, z=0.1, s=(0.05, 1.0, 1.0))
f = NIGHT + 6; tip = shovel(f - 1, 132.95, "dig_up", step=True)
for k in range(4):
    P(mx, "dig_up", f); shovel(f, 132.95, "dig_up")
    P(mx, "dig_down", f + 5); tip = shovel(f + 5, 132.95, "dig_down")
    sfx("dig" if k % 2 == 0 else "dig2", f + 5, 0.5); st.fx("dust", f + 5, tip[0], 0.2, 0.5)
    put("Town_Trench", f + 5, s=(0.12 + 0.07 * k, 1.0, 1.0))
    arc(CLODS[k], f + 6, f + 15, (tip[0], 0.6), (129.95 + 0.08 * k, 0.45), h=2.0, s=0.9, rot=200)
    sfx("pop", f + 15, 0.22)
    put(DIRT, f + 15, x=130.1, z=-0.05, y=-0.3, s=(0.26 + 0.03 * k, 1.0, 0.12 + 0.09 * k), step=(k == 0))
    f += 12
P(mx, "stand", f); off("FX_Shovel", f)
for k in (1, 2, 3):
    put("FX_Pipe_%d" % k, f + 2 * k, x=TX + (k - 1), z=PZ + 0.5, y=0.28, s=0.0, step=True); put("FX_Pipe_%d" % k, f + 2 * k + 3, z=PZ, s=1.0)
sfx("pickaxe", f + 5, 0.4); sfx("pickaxe", f + 9, 0.3)
SH = f + 14
P(mx, "stand", SH - 1); P(mx, "shh", SH); mx.mouth("neutral", SH)
FM.look(SH + 2, -0.05, 0.0); FM.look(SH + 10, 0.05, 0.0); FM.look(SH + 18, 0.0, 0.0)
s6 = max(e6, SH + 20) + 4

# ---------- shot 6: day; Sticky laughs at the trench and falls in; his buckets dump on his face ----------
off("Town_Back_Night", s6); off("FX_DirtPile", s6); sfx("whoosh", s6, 0.3)
st.cut(s6, 132.55, 2.3, 5.4)
P(mx, "shh", s6 - 1); go(mx, s6, 133.15); P(mx, "dig_up", s6); shovel(s6, 133.15, "dig_up", step=True)
for k, ff in enumerate(range(s6 + 8, s6 + 70, 14)):
    P(mx, "dig_up", ff); shovel(ff, 133.15, "dig_up"); P(mx, "dig_down", ff + 5); shovel(ff + 5, 133.15, "dig_down")
    sfx("dig2", ff + 5, 0.25)
FM.look(s6, -0.03, -0.05)
st.squint(s6, 1.0); st.mouth("grin", s6)
P(st, "stiff180", s6 - 1); go(st, s6, 129.8); P(st, "carry2", s6)
hold("FX_Bucket", st, "L", s6); hold("FX_Bucket_3", st, "R", s6)
on("FX_Bucket", s6); on("FX_Bucket_3", s6); water("FX_Bucket", s6, True); water("FX_Bucket_3", s6, True)
st.walk(s6 + 1, s6 + 15, 129.8, 132.1, step=3, arms=PO["carry2"]); P(st, "carry2", s6 + 16)
sfx("run", s6 + 1, 0.3, cut=14) if os.path.exists(bpy.path.abspath("//sfx/run.wav")) else sfx("ffwd", s6 + 1, 0.2, cut=14)
v7 = s6 + 12
e7 = N("S07", v7)
FS.look(e7 - 6, 0.05, -0.04)
for i, ff in enumerate(range(e7 - 8, e7 + 40, 5)):
    P(st, "laugh%d" % (94 if i % 2 == 0 else 100), ff)
v8 = e7 + 3
e8 = say(st, "S08", v8, vol=0.95)
FALL = e8 - 5
P(st, "laugh100", FALL - 1); P(st, "laugh120", FALL + 3); P(st, "stiff160", FALL + 6); P(st, "stiff180", FALL + 8)
st.move_to(132.1, 0.0, FALL - 1); st.move_to(132.3, 0.1, FALL + 8)
st.eyes("wide", FALL); st.mouth("scream", FALL); sfx("boing", FALL, 0.5)
st.cut(FALL + 3, 131.4, 2.0, 7.9)
drop("FX_Bucket", FALL + 3, 132.45, 1.4, rot=-40); drop("FX_Bucket_3", FALL + 3, 131.75, 1.5, rot=40)
put("FX_Bucket", FALL + 10, x=129.6, z=0.85, rot=-180); put("FX_Bucket_3", FALL + 11, x=130.15, z=0.75, rot=170)
water("FX_Bucket", FALL + 9, False); water("FX_Bucket_3", FALL + 9, False)
popin("FX_Splash", FALL + 10, x=129.75, z=0.2, s=0.9, y=-0.4); off("FX_Splash", FALL + 18)
sfx("splash_cartoon", FALL + 10, 0.55); sfx("land", FALL + 8, 0.45); st.shake(FALL + 8, FALL + 14, 0.12)
P(mx, "dig_down", FALL + 15); P(mx, "shrug", FALL + 18); off("FX_Shovel", FALL + 18); mx.mouth("neutral", FALL + 18)
P(mx, "shrug", FALL + 30); P(mx, "stand", FALL + 34)
s7 = FALL + 36

# ---------- shot 7: TWIST - the pipe connects and water races to town ----------
for n in ("FX_Bucket", "FX_Bucket_3", "FX_Bucket_2", "FX_CoinPile"): off(n, s7)
go(st, s7, 150.0); P(st, "stand", s7); st.eyes("normal", s7); st.mouth("neutral", s7)
go(mx, s7, 133.55)
mx.POSES["holdpipe"] = pose(reach("L", 0.5, 1.45), reach("R", -0.5, 1.45)); P(mx, "holdpipe", s7); mx.mouth("smile", s7)
on("FX_PipeTap", s7, x=TX, z=PZ, y=0.28)
for k in range(1, 9):
    if k != 4: on("FX_Pipe_%d" % k, s7, x=TX + (k - 1), z=PZ, y=0.28)
    if k >= 5: skey("FX_Pipe_%d_W" % k, ((s7 - 1, 0.0), (s7, 1.0)))
put("FX_Pipe_4", s7, x=133.05, z=1.35, y=0.0, s=1.0, step=True)
on("FX_Valve", s7, x=134.85, z=PZ, y=0.2, s=1.5)
st.cut(s7, 133.6, 2.0, 5.6)
v9 = s7 + 6
e9 = N("S09", v9)
CL = v9 + 16
put("FX_Pipe_4", CL - 3, z=1.35); put("FX_Pipe_4", CL, x=TX + 3, z=PZ, y=0.28)
P(mx, "holdpipe", CL - 3); P(mx, "stand", CL); mx.punch(CL, 0.05, 4)
sfx("pickaxe", CL, 0.55); st.fx("dust", CL, 134.0, 0.15, 0.7); st.shake(CL, CL + 3, 0.06)
go(mx, CL + 6, 133.55); mx.move_to(134.25, 0.0, CL + 12); P(mx, "stand", CL + 6); P(mx, "wheelA", CL + 12)
st.cut(CL + 10, 134.9, 1.9, 5.2)
WH = O["FX_Valve_Wheel"]
for i, ff in enumerate(range(CL + 12, CL + 34, 4)):
    P(mx, "wheelA" if i % 2 == 0 else "wheelB", ff)
    WH.rotation_euler = (0.0, -1.2 * i, 0.0); WH.keyframe_insert("rotation_euler", frame=ff)
sfx("whirl", CL + 12, 0.4, cut=24)
SIL = v9 + 47                                        # music cuts here (part 3), pipe shudders
P(mx, "wheelA", SIL - 1); P(mx, "stand", SIL + 2); mx.move_to(134.25, 0.0, SIL + 2); mx.move_to(135.0, 0.0, SIL + 8); mx.eyes("wide", SIL); mx.mouth("open", SIL)
st.shake(SIL, SIL + 7, 0.09); sfx("rumble", SIL + 4, 0.45, cut=30)
for k in range(1, 9):
    ob = O["FX_Pipe_%d" % k]
    for j, ff in enumerate(range(SIL, SIL + 8, 2)):
        ob.location.z = PZ + (0.03 if j % 2 == 0 else -0.02); ob.keyframe_insert("location", frame=ff)
    ob.location.z = PZ; ob.keyframe_insert("location", frame=SIL + 8)
W0 = SIL + 12
sfx("water_rush", W0, 0.5, cut=50)
for k in range(8, 0, -1):
    if k >= 5: continue
    w = O["FX_Pipe_%d_W" % k]; t0 = W0 + 5 * (4 - k)
    skey(w, ((t0 - 1, (0.0, 1.0, 1.0)), (t0 + 3, (1.0, 1.0, 1.0))))
st.cut(W0, 134.4, 1.55, 4.0); st.zoom(W0, W0 + 4, 134.2, 1.55, 4.0); st.zoom(W0 + 4, W0 + 23, 131.4, 1.6, 4.4)
BURST = W0 + 24
O["FX_Water"].location.y = 0.15
put("FX_Water", BURST, x=TX - 0.55, z=PZ + 1.07, y=0.15, rot=90, s=(0.0, 1.0, 1.0), step=True)
put("FX_Water", BURST + 3, s=(0.62, 1.0, 1.0))
popin("FX_Splash", BURST + 2, x=BX, z=0.8, s=0.7, y=0.05)
sfx("splash", BURST, 0.6); sfx("water_flow", BURST + 4, 0.25, cut=200)
st.cut(BURST, 130.9, 2.3, 5.6); st.shake(BURST, BURST + 6, 0.14)
go(tm, BURST, 128.6); go(ly, BURST, 128.4)
P(tm, "stand", BURST); P(ly, "stand", BURST); tm.mouth("grin", BURST); ly.mouth("grin", BURST)
tm.walk(BURST + 1, BURST + 13, 128.6, 131.75, step=3, arms=PO["sign_up"]); P(tm, "cheer", BURST + 14)
ly.walk(BURST + 1, BURST + 11, 128.4, 129.6, step=3, arms=PO["sign_up"]); P(ly, "cheerB", BURST + 12)
tm.hop(BURST + 16, 0.2, 8); ly.hop(BURST + 18, 0.2, 8)
s8 = max(e9, BURST + 22) + 6
# ---- PART 2 END (shots 4-7) ----

# =================== PART 3: shots 8-12, music, gain, marks ===================
for m in (st, mx, tm, ly, gp):
    m.POSES["tapg"] = pose(reach("R", -0.55, 1.25), STAND_L, head=84)
    m.POSES["shakeR"] = pose(reach("R", -0.5, 1.6), STAND_L); m.POSES["shakeL"] = pose(reach("L", 0.5, 1.6), STAND_R)
    m.POSES["thumb"] = pose(reach("L", 0.45, 2.75), STAND_R)
    m.POSES["peer"] = pose(reach("L", 0.42, 1.38), STAND_R, head=66)
    m.POSES["idea1"] = pose(reach("L", 0.42, 1.38), reach("R", -0.3, 3.05))
st.POSES["stiff0"] = tilt(STIFF, 0)
def bill(k, f, x_in, x_heap):
    b = "Bill_%d" % k
    put(b, f, x=x_in, z=1.25, y=-0.45, s=0.05, step=True); put(b, f + 3, s=1.25); sfx("pop", f, 0.3)
    st.run(b, f + 3, f + 11, x_heap); coin(f + 11, (x_heap - 0.3, 0.5), (x_heap + 0.2, 1.7), h=0.4)
    sfx("whoosh", f + 12, 0.35); st.run(b, f + 13, f + 22, x_in + 0.6); off(b, f + 23)

# ---------- shot 8: the town pays; revenue board; three bills take coins ----------
st.cut(s8, 131.55, 2.35, 7.0); st.zoom(s8, s8 + 60, 131.55, 2.35, 6.6)
go(ly, s8, 129.8); go(tm, s8, 131.35); go(mx, s8, 133.05)
P(ly, "stand", s8); P(tm, "stand", s8); P(mx, "stand", s8); mx.mouth("smile", s8); mx.eyes("normal", s8)
put(PILE, s8, x=131.95, z=0.0, y=-0.25, s=(0.4, 1.0, 0.05), step=True)
put("FX_Board", s8, x=132.35, z=0.0, y=0.2, s=0.0, step=True)
v10 = s8 + 4
e10 = N("S10", v10)
for i, (m, x0) in enumerate(((ly, 129.95), (tm, 131.5), (ly, 129.95), (tm, 131.5))):
    ff = v10 + 6 + 14 * i
    P(m, "stand", ff - 3); P(m, "give" if "give" in m.POSES else "present", ff); P(m, "stand", ff + 8)
    coin(ff, (x0 + 0.4, 1.6), (131.95, 0.3 + 0.08 * i), h=0.6); sfx("clink" if i % 2 else "chaching", ff + 7, 0.35)
    put(PILE, ff + 8, s=(0.4, 1.0, 0.15 + 0.1 * i))
BD = v10 + 66                                             # "up to a thousand dollars a day"
popin("FX_Board", BD, x=132.35, z=0.0, y=0.2, s=1.0); sfx("chaching", BD + 2, 0.4)
put("FX_Sticker_2", BD + 4, x=133.15, z=1.8, y=0.1, s=0.0, step=True); put("FX_Sticker_2", BD + 7, s=0.8)
mx.hop(BD + 2, 0.15, 8); mx.mouth("grin", BD + 2)
for k, ff in ((1, v10 + 132), (2, v10 + 153), (3, v10 + 173)):
    bill(k, ff - 10, 134.4, 132.35)
    put(PILE, ff + 2, s=(0.4, 1.0, 0.45 - 0.09 * k)); FM.look(ff - 4, 0.05, -0.03)
P(mx, "stand", e10 - 6); P(mx, "slump", e10 - 2); mx.mouth("sad", e10 - 2); FM.look(e10, 0.0, -0.05)
FLY.look(e10 - 8, 0.04, 0.0); FT.look(e10 - 8, 0.04, 0.0)
s9 = e10 + 6

# ---------- shot 9: Sticky sick; thermometer dart; income $0 ----------
for n in ("FX_Board", "FX_Sticker_2", "FX_Valve"): off(n, s9)
go(ly, s9, 141.0); go(tm, s9, 140.0); go(mx, s9, 146.0)
st.cut(s9, 134.25, 1.7, 5.2); st.zoom(s9, s9 + 60, 134.25, 1.6, 5.0)
P(st, "stiff0", s9); go(st, s9, 132.45, 0.15); st.mouth("sad", s9); st.squint(s9, 0.35); st.eyes("normal", s9); FS.look(s9, 0.0, 0.0)
put("Set_Blanket", s9, x=134.3, z=-0.1, y=-0.32, s=0.45, step=True)
put(TAG, s9, x=133.45, z=0.0, y=0.3, s=1.0, step=True); put("FX_Sticker_1", s9, x=133.72, z=1.33, y=0.2, s=0.75, step=True)
put(PILE, s9, x=133.45, z=0.0, y=0.1, s=(0.35, 1.0, 0.3), step=True)
for n, x in (("FX_Bucket_4", 134.15), ("FX_Bucket_6", 134.65)): put(n, s9, x=x, z=0.62, y=0.25, s=1.0, step=True)
PEN = O["FX_Pen"]; put(PEN, s9, x=135.2, z=0.4, y=-0.4, rot=-55, s=0.7, step=True)
v11 = s9 + 4
e11 = N("S11", v11)
CO = v11 + 22
st.punch(CO, 0.12, 5); st.mouth("open", CO); sfx("cough", CO, 0.55); st.mouth("sad", CO + 6)
arc(PEN, CO + 1, CO + 6, (135.2, 0.4), (134.65, 0.85), h=0.7, s=0.7, rot=300)
put(PEN, CO + 7, x=134.5, z=1.15, s=0.7); put(PEN, CO + 12, x=134.3, z=0.25, s=0.7, rot=500); off("FX_Pen", CO + 14)
sfx("pickaxe", CO + 6, 0.35); st.fx("star", CO + 6, 134.65, 0.85, 0.4)
CRASH = e11 - 6                                          # "stopped"
skey("FX_Tag_Txt2", ((CRASH - 1, 1.0), (CRASH, 0.0)))
skey("FX_Tag_Txt3", ((CRASH - 1, 0.0), (CRASH, 1.25), (CRASH + 3, 1.0)))
put(PILE, CRASH - 1, s=(0.35, 1.0, 0.35)); put(PILE, CRASH + 2, s=(0.45, 1.0, 0.05)); put(PILE, CRASH + 3, s=0.0)
st.fx("dust", CRASH + 1, 133.45, 0.2, 1.1); sfx("error", CRASH, 0.4); st.shake(CRASH, CRASH + 3, 0.08)
O["FX_Fly"].location.y = -0.5
st.flutter("FX_Fly", CRASH + 4, CRASH + 30, 133.15, 1.45, 133.75, 1.55, wobble=0.14); sfx("buzz", CRASH + 4, 0.25, cut=26)
s10 = max(e11, CRASH + 30) + 4

# ---------- shot 10: the system runs, the storm cracks it, Max repairs and hires Tom ----------
for n in ("Set_Blanket", "FX_Tag", "FX_Sticker_1", "FX_Bucket_4", "FX_Bucket_6"): off(n, s10)
P(st, "stiff0", s10 - 1); go(st, s10, 150.0); P(st, "stand", s10); st.squint(s10, 1.0)
go(mx, s10, 132.35); P(mx, "stand", s10); mx.mouth("smile", s10); mx.eyes("normal", s10)
on("T_Helmet", s10); off("T_Beanie", s10)
put("FX_Gauge", s10, x=131.75, z=0.2, y=0.15, s=1.4, step=True)
ND = O["FX_Gauge_Needle"]; ND.keyframe_insert("rotation_euler", frame=s10)
st.cut(s10, 132.3, 2.25, 5.6); st.zoom(s10, s10 + 46, 132.4, 2.35, 4.8)
v12 = s10 + 4
e12 = N("S12", v12)
GT = v12 + 18
P(mx, "stand", GT - 4); P(mx, "tapg", GT); P(mx, "stand", GT + 8); P(mx, "tapg", GT + 12); sfx("tick", GT, 0.4); sfx("tick", GT + 12, 0.4)
for ff, a in ((GT, -0.7), (GT + 3, 0.2), (GT + 6, -0.2), (GT + 14, 0.6), (GT + 20, 0.95)):
    ND.rotation_euler = (0.0, a, 0.0); ND.keyframe_insert("rotation_euler", frame=ff)
FM.look(GT, -0.05, -0.05)
FLASH = v12 + 46                                         # "but"
on("FX_Flash", FLASH); off("FX_Flash", FLASH + 2)
on("Town_Back_Storm", FLASH); off("Town_Back_Storm", FLASH + 34)
popin("FX_Bolt", FLASH, x=133.4, z=4.0, s=0.9); off("FX_Bolt", FLASH + 8)
sfx("thunder", FLASH, 0.55, cut=60); st.shake(FLASH, FLASH + 8, 0.14)
J = FLASH + 4
put("FX_Water_2", J, x=133.1, z=0.15, y=-0.35, rot=-104, s=(0.0, 1.0, 1.0), step=True); put("FX_Water_2", J + 3, s=(2.55, 1.0, 1.0))
popin("FX_Splash_2", J + 3, x=132.45, z=2.75, s=0.6, y=-0.5); off("FX_Splash_2", J + 22)
sfx("water_rush", J, 0.45, cut=40); sfx("splash_cartoon", J + 3, 0.45)
P(mx, "stand", J + 2); P(mx, "shock", J + 3); mx.eyes("wide", J + 3); mx.mouth("open", J + 3); mx.punch(J + 3, 0.1, 5)
st.cut(J + 1, 133.05, 2.3, 4.6)
mx.blink(J + 18); P(mx, "shock", J + 17); P(mx, "cup", J + 21); P(mx, "stand", J + 30); mx.eyes("normal", J + 22); mx.mouth("neutral", J + 22)
v13 = e12 + 8
e13 = N("S13", v13)
RP = v13 - 4
P(mx, "stand", RP - 1); mx.move_to(132.35, 0.0, RP - 1); mx.move_to(132.35, 0.0, RP + 2); P(mx, "wheelA", RP + 2)
for i in range(3):
    ff = RP + 6 + 12 * i
    P(mx, "wheelB", ff - 3); P(mx, "wheelA", ff); sfx("pickaxe", ff, 0.4); st.fx("star", ff, 133.15, 0.35, 0.45)
put("FX_Water_2", RP + 30, s=(2.55, 1.0, 1.0)); put("FX_Water_2", RP + 32, s=(0.0, 1.0, 1.0))
mx.prop("sweat", RP + 10, RP + 34, x=0.75, z=2.4, size=0.6)
HI = RP + 40
P(mx, "wheelA", HI - 1); P(mx, "stand", HI + 2); mx.move_to(132.35, 0.0, HI + 1); mx.move_to(132.45, 0.0, HI + 4)
st.cut(HI, 132.0, 2.3, 5.6)
go(tm, HI - 14, 129.6); P(tm, "stand", HI - 15); tm.mouth("grin", HI - 14)
tm.walk(HI - 14, HI + 2, 129.6, 131.4, step=4, arms=PO["sign_dn"]); P(tm, "stand", HI + 3)
SHK = HI + 8
P(tm, "stand", SHK - 3); P(tm, "shakeL", SHK); P(mx, "stand", SHK - 3); P(mx, "shakeR", SHK); mx.mouth("smile", SHK)
for k, ff in enumerate(range(SHK, SHK + 16, 4)):
    for m, nm in ((tm, "shakeL"), (mx, "shakeR")):
        m.POSES["_sh"] = pose(reach(nm[-1], 0.5 if nm[-1] == "L" else -0.5, 1.6 + (0.12 if k % 2 == 0 else -0.05)), STAND_R if nm[-1] == "L" else STAND_L)
        P(m, "_sh", ff)
P(tm, "thumb", SHK + 18); P(mx, "stand", SHK + 18); sfx("ding", SHK + 18, 0.3)
s11 = max(e13, SHK + 22) + 6

# ---------- shot 11: one house by hand vs three houses by pipe ----------
st.cut(s11, 131.5, 2.2, 7.7); st.zoom(s11, s11 + 140, 131.5, 2.2, 7.5)
sfx("hit_up", s11, 0.45)
off("FX_Gauge", s11); off("FX_PipeTap", s11); off("FX_Barrel", s11); off("FX_Water", s11)
for k in range(1, 9):
    if k <= 3: put("FX_Pipe_%d" % k, s11, x=130.65 + (k - 1), z=PZ, y=0.3, step=True)
    else: off("FX_Pipe_%d" % k, s11)
for k, x in ((1, 131.0), (2, 132.0), (3, 133.0)):
    put("Town_House_%d" % k, s11, x=x, y=0.55 + 0.01 * k, step=True)
    put("FX_PipeBranch_%d" % k, s11, x=x + 0.2, z=0.12, y=0.27, s=1.0, step=True)
put("Town_House_4", s11, x=129.35, step=True)
put("FX_Barrel", s11, x=129.85, z=0.0, y=0.1, s=0.75, step=True)
go(mx, s11, 132.05); go(tm, s11, 133.1); P(mx, "stand", s11); P(tm, "stand", s11); mx.mouth("smile", s11); tm.mouth("smile", s11)
go(st, s11, 131.0); P(st, "carry2", s11); st.mouth("sad", s11); st.squint(s11, 0.6)
hold("FX_Bucket", st, "L", s11); hold("FX_Bucket_3", st, "R", s11)
on("FX_Bucket", s11); on("FX_Bucket_3", s11); water("FX_Bucket", s11, True); water("FX_Bucket_3", s11, True)
st.POSES["trudge"] = dict(PO["carry2"], head=78)
st.walk(s11 + 1, s11 + 60, 131.0, 130.35, step=10, arms=st.POSES["trudge"]); P(st, "trudge", s11 + 61)
water("FX_Bucket", s11 + 66, False); popin("FX_Splash", s11 + 66, x=129.85, z=0.66, s=0.45, y=0.05); off("FX_Splash", s11 + 74); sfx("splash", s11 + 66, 0.25, cut=20)
v14 = s11 + 4
e14 = N("S14", v14)
BUILD = st.caption("BUILD SYSTEMS. MAINTAIN THEM.", v14 + 2, e14 + 4, z=2.72, size=0.34, color="black", max_width=3.6, hud=True)
for i, k in enumerate((1, 2, 3)):
    ff = v14 + 64 + 12 * i
    w = O["FX_PipeBranch_%d_W" % k]; skey(w, ((ff - 1, (1.0, 1.0, 0.0)), (ff + 3, (1.0, 1.0, 1.0))))
    sfx("pop", ff, 0.3); st.fx("star", ff, 131.0 + (k - 1), 0.95, 0.35)
skey("FX_Pipe_1_W", ((s11 - 1, 1.0), (s11, 1.0))); skey("FX_Pipe_2_W", ((s11, 1.0),)); skey("FX_Pipe_3_W", ((s11, 1.0),))
sfx("water_flow", v14 + 64, 0.2, cut=e14 - v14 - 60)
P(tm, "stand", e14 - 22); P(tm, "thumb", e14 - 18); mx.hop(e14 - 16, 0.1, 8)
s12 = e14 + 6

# ---------- shot 12: Sticky's bucket "pipe system" sprays his face; back to the frame-1 spot (loop) ----------
for k in range(1, 4): off("FX_PipeBranch_%d" % k, s12); off("FX_Pipe_%d" % k, s12)
for k, x in ((1, 129.3), (2, 128.0), (3, 126.7), (4, 125.4)): put("Town_House_%d" % k, s12, x=x, y=0.55, step=True)
off("FX_Barrel", s12); off("FX_Bucket_3", s12)
go(st, s12, SX); P(st, "carry1", s12); st.mouth("neutral", s12); st.squint(s12, 1.0); water("FX_Bucket", s12, True)
go(mx, s12, MX); P(mx, "stand", s12); go(tm, s12, 140.0)
st.cut(s12, 132.05, 2.35, 6.2); st.zoom(s12, s12 + 26, 132.05, 2.35, 5.4)
v15 = s12 + 4
e15 = N("S15", v15)
QQ = st.caption("BUCKETS or SYSTEMS?", v15, 100000, z=2.72, size=0.4, color="black", max_width=3.6, hud=True)
ID = v15 + 10
P(st, "carry1", ID - 1); P(st, "idea1", ID); st.eyes("wide", ID); st.mouth("grin", ID); sfx("ding", ID, 0.35)
st.prop("bulb", ID, ID + 16, x=0.0, z=3.75, size=0.7)
JM = v15 + 34
P(st, "idea1", JM - 4); P(st, "carry1", JM); st.eyes("normal", JM)
SP = O["FX_Pipe_8"]; SP.location.y = -0.3
put(SP, JM - 2, x=SX + 0.75, z=0.5, y=-0.3, rot=-90, s=0.0, step=True); put(SP, JM, s=(1.15, 1.0, 1.0))
sfx("pickaxe", JM, 0.45); st.punch(JM, 0.05, 4)
st.cut(JM + 2, 131.75, 2.2, 4.4)
PR = JM + 12
P(st, "carry1", PR - 1); P(st, "peer", PR + 3); FS.look(PR + 3, 0.05, -0.05); st.mouth("neutral", PR)
sfx("water_rush", PR + 10, 0.3, cut=20)
SPL = max(e15 + 9, PR + 22)
put("FX_Water_3", SPL - 3, x=SX + 0.75, z=1.65, y=-0.4, rot=-118, s=(0.0, 1.0, 1.0), step=True); put("FX_Water_3", SPL, s=(0.95, 1.0, 1.0))
popin("FX_Splash_3", SPL, x=SX + 0.25, z=2.7, s=0.7, y=-0.5); off("FX_Splash_3", SPL + 12); off("FX_Water_3", SPL + 10)
sfx("splash_cartoon", SPL, 0.6); st.shake(SPL, SPL + 6, 0.12); st.punch(SPL, 0.1, 5)
P(st, "peer", SPL - 1); P(st, "shock", SPL + 1); st.eyes("wide", SPL + 1); st.mouth("open", SPL + 1)
st.prop("sweat", SPL + 6, SPL + 40, x=0.35, z=2.9, size=0.6)
TURN = SPL + 14
off("FX_Pipe_8", TURN); P(st, "shock", TURN - 1); P(st, "carry1", TURN); st.eyes("normal", TURN); st.mouth("neutral", TURN)
st.cut(TURN, 132.05, 2.35, 6.2); st.zoom(TURN, TURN + 22, 132.05, 2.35, 6.7)
P(st, "carry1", TURN + 6); P(st, "carry1l", TURN + 9); FS.look(TURN + 9, 0.05, -0.01)
sfx("wind", TURN, 0.2, cut=30)
END = TURN + 22
S.frame_end = END

# ---------- music, gain, idle life ----------
MU = st.music("//musiqa_04_western.wav", volume=0.11, fade=12, end=END + 1)
def mv(f, v): MU.volume = v; MU.keyframe_insert("volume", frame=f)
for f_, v_ in ((1, 0.11), (s5, 0.11), (s5 + 8, 0.07), (s6, 0.07), (s6 + 6, 0.11), (SIL - 1, 0.11), (SIL, 0.0), (BURST - 1, 0.0), (BURST, 0.16),
               (BURST + 40, 0.11), (s9 - 1, 0.11), (s9 + 6, 0.05), (CRASH, 0.05), (CRASH + 6, 0.09), (FLASH - 1, 0.1), (FLASH, 0.0),
               (FLASH + 30, 0.0), (FLASH + 45, 0.08), (s11, 0.14), (s12, 0.11), (SPL, 0.11), (END - 12, 0.11)):
    mv(f_, v_)
for sp in st._strips():
    if sp.type == "SOUND" and not sp.name.startswith("Music"): sp.volume = sp.volume * GAIN
for m in ALL: m.alive(1, END)
S.frame_set(1)
bpy.app.driver_namespace["v16_marks"] = dict(s2=s2, s3=s3, s4=s4, FL=FL, CK=CK, s5=s5, NIGHT=NIGHT, s6=s6, FALL=FALL, s7=s7, SIL=SIL, W0=W0,
    BURST=BURST, s8=s8, BD=BD, s9=s9, CRASH=CRASH, s10=s10, FLASH=FLASH, s11=s11, s12=s12, SPL=SPL, TURN=TURN, END=END)
# ---- END OF SCRIPT ----
