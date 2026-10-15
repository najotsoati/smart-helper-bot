# v14_assets.py  -  "Who Really Got Rich in the Gold Rush?" uchun yangi obyektlar (bir marta ishga tushiriladi)
# Oltin tog' foni, kon og'zi, xazina xaritasi, belkuraklar, suv bochkasi, kaska (Ben va Bobo uchun),
# "SHOVELS/SUPPLIES" do'koni va "WATER & SNACKS" stoli.
import bpy, math
from mathutils import Vector
O = bpy.data.objects
MATS = bpy.data.materials

def srgb2lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def mat(name, hexs, like="Stk_Sand"):
    m = MATS.get(name)
    if m is None:
        m = MATS[like].copy(); m.name = name
    h = hexs.lstrip("#")
    rgb = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    m.diffuse_color = (srgb2lin(rgb[0]), srgb2lin(rgb[1]), srgb2lin(rgb[2]), 1.0)
    m.use_fake_user = True
    return m
mat("Stk_Rock", "#B89A70"); mat("Stk_RockDark", "#9C7D57"); mat("Stk_RockLight", "#D6C6A2")
mat("Stk_Dirt", "#C9AE7A"); mat("Stk_DirtDark", "#B0925E"); mat("Stk_Parch", "#EAD7A8"); mat("Stk_ParchDark", "#C8AA72")
mat("Stk_HelmetDark", "#C98A12")

def area(pts):
    n = len(pts)
    return sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n)) / 2.0
def ccw(pts):
    return list(pts) if area(pts) > 0 else list(reversed(pts))
def grow(pts, d):
    pts = ccw(pts); n = len(pts); out = []
    for i in range(n):
        p0, p1, p2 = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % n])
        e1 = p1 - p0; e2 = p2 - p1
        if e1.length < 1e-9 or e2.length < 1e-9:
            out.append(tuple(p1)); continue
        e1.normalize(); e2.normalize()
        n1 = Vector((e1.y, -e1.x)); n2 = Vector((e2.y, -e2.x))
        nm = n1 + n2
        if nm.length < 1e-6: nm = n1.copy()
        nm.normalize()
        c = max(nm.dot(n1), 0.35)
        q = p1 + nm * (d / c)
        out.append((q.x, q.y))
    return out
def rect(x0, z0, x1, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
def circ(cx, cz, rx, rz=None, n=28, a0=0.0, a1=360.0):
    rz = rx if rz is None else rz
    full = abs(a1 - a0) >= 359.9
    k = n if full else n + 1
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cz + rz * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(k)]
def rrect(x0, z0, x1, z1, r, n=6):
    pts = []
    for cx, cz, a in ((x1 - r, z0 + r, -90), (x1 - r, z1 - r, 0), (x0 + r, z1 - r, 90), (x0 + r, z0 + r, 180)):
        for i in range(n + 1):
            t = math.radians(a + 90.0 * i / n); pts.append((cx + r * math.cos(t), cz + r * math.sin(t)))
    return pts
def seg(p0, p1, w):
    a, b = Vector(p0), Vector(p1); d = (b - a).normalized(); nn = Vector((-d.y, d.x)) * (w / 2.0)
    return [tuple(a + nn), tuple(b + nn), tuple(b - nn), tuple(a - nn)]

class Shape:
    def __init__(self): self.items = []
    def add(self, m, pts, y):
        self.items.append((m, [tuple(p) for p in pts], y)); return self
    def ol(self, m, pts, y, w=0.03, om="Stk_Black"):
        self.items.append((om, grow(pts, w), y + 0.002)); self.items.append((m, [tuple(p) for p in pts], y)); return self

def stamp(ob, hidden=True):
    ob["rest_loc"] = list(ob.location); ob["rest_rot"] = list(ob.rotation_euler)
    ob["rest_scale"] = [0.0, 0.0, 0.0] if hidden else [1.0, 1.0, 1.0]; ob["rest_hide"] = 0
    if hidden: ob.scale = (0.0, 0.0, 0.0)
def build(name, shape, coll="Stickman_Extras", loc=(0.0, 0.0, 0.0), hidden=True, parent=None, rot=(0.0, 0.0, 0.0)):
    old = O.get(name)
    if old is not None:
        me_old = old.data; bpy.data.objects.remove(old, do_unlink=True)
        if me_old and me_old.users == 0: bpy.data.meshes.remove(me_old)
    me = bpy.data.meshes.new(name)
    verts, faces, mats, fm = [], [], [], []
    for m, pts, y in shape.items:
        if m not in mats: mats.append(m)
        i0 = len(verts)
        verts += [(x, y, z) for x, z in pts]
        faces.append(list(range(i0, i0 + len(pts)))); fm.append(mats.index(m))
    me.from_pydata(verts, [], faces)
    for m in mats: me.materials.append(MATS[m])
    for i, p in enumerate(me.polygons): p.material_index = fm[i]
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.data.collections[coll].objects.link(ob)
    if parent is not None:
        ob.parent = parent
    ob.location = loc; ob.rotation_euler = rot
    stamp(ob, hidden)
    return ob

s = Shape()
s.add("Stk_Sky", rect(-3.6, -2.7, 3.6, 7.6), 0.0)
for cx, cz, r in ((-2.55, 5.05, 0.34), (-2.15, 5.15, 0.42), (-1.75, 5.0, 0.3), (2.0, 4.85, 0.3), (2.4, 4.95, 0.4), (2.8, 4.85, 0.3)):
    s.add("Stk_Cloud", circ(cx, cz, r, n=20), -0.002)
far = [(-3.6, 0.4), (-3.6, 2.3), (-2.8, 3.05), (-2.1, 2.55), (-1.45, 3.3), (-0.8, 2.75), (0.15, 3.05), (1.0, 2.6), (1.85, 3.35), (2.65, 2.75), (3.6, 3.2), (3.6, 0.4)]
s.add("Stk_RockLight", far, -0.004)
main = [(-3.6, 0.4), (-3.6, 1.15), (-2.5, 1.95), (-1.65, 2.75), (-1.0, 3.55), (-0.45, 4.25), (-0.12, 4.52), (0.18, 4.44), (0.55, 4.0), (1.05, 3.45),
        (1.6, 2.95), (2.35, 2.25), (3.6, 1.35), (3.6, 0.4)]
s.ol("Stk_Rock", main, -0.008, w=0.028)
shade = [(-0.12, 4.52), (0.18, 4.44), (0.55, 4.0), (1.05, 3.45), (1.6, 2.95), (2.35, 2.25), (3.6, 1.35), (3.6, 0.4), (0.7, 0.4), (0.5, 1.6), (0.3, 2.9), (0.08, 3.9)]
s.add("Stk_RockDark", shade, -0.010)
for cx, cz, r in ((-0.1, 3.95, 0.17), (0.42, 3.42, 0.11), (-0.62, 3.05, 0.09), (0.95, 2.75, 0.08), (-1.15, 2.3, 0.07)):
    dia = [(cx, cz + r * 1.3), (cx + r, cz), (cx, cz - r * 1.3), (cx - r, cz)]
    s.ol("Stk_Gold", dia, -0.012, w=0.022, om="Stk_GoldDark")
for x0, x1, z in ((-2.2, -1.75, 1.55), (1.7, 2.2, 1.9), (-0.9, -0.55, 2.2), (2.5, 2.95, 1.25)):
    s.add("Stk_RockDark", seg((x0, z), (x1, z + 0.12), 0.035), -0.011)
gr = [(-3.6, -2.7), (3.6, -2.7), (3.6, 0.58), (2.3, 0.66), (1.1, 0.52), (-0.2, 0.62), (-1.5, 0.5), (-2.6, 0.6), (-3.6, 0.52)]
s.ol("Stk_Dirt", gr, -0.014, w=0.025)
gr2 = [(-3.6, -2.7), (3.6, -2.7), (3.6, -0.55), (2.0, -0.45), (0.6, -0.6), (-0.9, -0.48), (-2.3, -0.6), (-3.6, -0.5)]
s.add("Stk_DirtDark", gr2, -0.016)
for cx, cz, rx in ((-1.85, 0.2, 0.09), (1.55, 0.3, 0.07), (2.6, -0.1, 0.1), (-2.7, -0.15, 0.08), (0.5, -1.1, 0.08), (-1.2, -1.5, 0.1)):
    s.ol("Stk_RockDark", circ(cx, cz, rx, rx * 0.6, n=12), -0.018, w=0.018)
build("Gold_Back", s, coll="Stickman_Set", loc=(0.0, 0.72, 0.0))

s = Shape()
arch = [(-0.5, 0.0), (0.5, 0.0)] + circ(0.0, 0.95, 0.5, 0.45, n=16, a0=0, a1=180)
s.ol("Stk_Dark", arch, 0.0, w=0.03)
s.ol("Stk_Wood", rect(-0.62, 0.0, -0.48, 1.5), -0.004, w=0.025)
s.ol("Stk_Wood", rect(0.48, 0.0, 0.62, 1.5), -0.004, w=0.025)
s.ol("Stk_Wood", rect(-0.72, 1.42, 0.72, 1.58), -0.006, w=0.025)
s.ol("Stk_WoodDark", rect(-0.44, 0.0, 0.44, 0.08), -0.003, w=0.015)
build("Gold_Mine", s, coll="Stickman_Set", loc=(-1.25, 0.5, 0.42))

s = Shape()
W, H = 0.92, 0.66
edge = [(-W, -H), (-0.5, -H - 0.03), (0.0, -H + 0.01), (0.45, -H - 0.025), (W, -H), (W + 0.02, -0.2), (W - 0.01, 0.25), (W, H),
        (0.4, H + 0.03), (-0.1, H - 0.01), (-0.55, H + 0.025), (-W, H), (-W - 0.02, 0.2), (-W + 0.01, -0.3)]
s.ol("Stk_Parch", edge, 0.0, w=0.03)
for x in (-W, W):
    s.ol("Stk_ParchDark", rrect(x - 0.07, -H - 0.06, x + 0.07, H + 0.06, 0.06), -0.004, w=0.025)
LW = 0.035
for a, b in (((-0.45, -0.5), (0.45, -0.5)), ((-0.45, -0.5), (-0.45, 0.12)), ((0.45, -0.5), (0.45, 0.12)),
             ((-0.56, 0.08), (0.0, 0.4)), ((0.0, 0.4), (0.56, 0.08))):
    s.add("Stk_WoodDark", seg(a, b, LW), -0.006)
s.add("Stk_WoodDark", rect(0.24, -0.5, 0.38, -0.26), -0.006)
s.ol("Stk_White", rrect(-0.2, -0.04, 0.1, 0.2, 0.035), -0.008, w=0.024)
s.ol("Stk_White", rrect(-0.3, -0.13, 0.2, -0.05, 0.03), -0.0088, w=0.024)
bowl = [(-0.27, -0.13), (0.17, -0.13)] + circ(-0.05, -0.13, 0.22, 0.2, n=14, a0=0, a1=-180)[1:-1]
s.ol("Stk_White", bowl, -0.009, w=0.024)
s.ol("Stk_White", rect(-0.13, -0.47, 0.03, -0.3), -0.0085, w=0.024)
pts = [(-0.85, -0.55), (-0.72, -0.38), (-0.62, -0.18), (-0.66, 0.02), (-0.58, 0.22)]
for i in range(len(pts) - 1):
    a, b = Vector(pts[i]), Vector(pts[i + 1])
    m = a.lerp(b, 0.5)
    s.add("Stk_Red", seg(tuple(a.lerp(m, 0.2)), tuple(m.lerp(b, 0.3)), 0.03), -0.006)
build("FX_Map", s, loc=(0.0, -0.6, 2.6))
s = Shape()
s.ol("Stk_Red", seg((-0.13, -0.12), (0.13, 0.12), 0.065), -0.012, w=0.02)
s.ol("Stk_Red", seg((-0.13, 0.12), (0.13, -0.12), 0.065), -0.013, w=0.02)
build("FX_MapX", s, loc=(-0.05, 0.0, -0.22), parent=O["FX_Map"])
s = Shape()
s.add("Stk_Yellow", circ(0.0, 0.0, 0.34, n=28), 0.0)
for k in range(10):
    a = math.radians(k * 36.0)
    s.add("Stk_Yellow", seg((0.36 * math.cos(a), 0.36 * math.sin(a)), (0.5 * math.cos(a), 0.5 * math.sin(a)), 0.045), 0.0)
build("FX_MapGlow", s, loc=(-0.05, -0.0095, -0.22), parent=O["FX_Map"])
s = Shape()
s.ol("Stk_Parch", rrect(-0.32, -0.09, 0.32, 0.09, 0.08), 0.0, w=0.025)
s.ol("Stk_Red", rect(-0.12, -0.1, -0.06, 0.1), -0.003, w=0.012)
s.ol("Stk_Red", rect(0.06, -0.1, 0.12, 0.1), -0.003, w=0.012)
build("FX_MapRoll", s, loc=(0.0, -0.3, 1.5))

s = Shape()
s.ol("Stk_Wood", rect(-0.035, -0.62, 0.035, 0.55), -0.002, w=0.022)
s.ol("Stk_Wood", rrect(-0.15, 0.53, 0.15, 0.62, 0.035), -0.003, w=0.022)
blade = [(-0.17, -0.58), (0.17, -0.58), (0.17, -0.8), (0.0, -0.98), (-0.17, -0.8)]
s.ol("Stk_Grey", blade, -0.004, w=0.025)
s.ol("Stk_Grey", rect(-0.05, -0.62, 0.05, -0.5), -0.005, w=0.018)
sh = build("FX_Shovel", s, loc=(0.0, -0.3, 1.0))
for k in range(2, 7):
    nm = "FX_Shovel_%d" % k
    if O.get(nm): bpy.data.objects.remove(O[nm], do_unlink=True)
    c = sh.copy(); c.name = nm; bpy.data.collections["Stickman_Extras"].objects.link(c); stamp(c)

s = Shape()
body = [(-0.3, 0.0), (0.3, 0.0), (0.34, 0.4), (0.3, 0.8), (-0.3, 0.8), (-0.34, 0.4)]
s.ol("Stk_Wood", body, 0.0, w=0.03)
for z in (0.14, 0.66):
    s.add("Stk_WoodDark", seg((-0.32, z), (0.32, z), 0.05), -0.003)
s.ol("Stk_Blue", rrect(-0.2, 0.28, 0.2, 0.52, 0.05), -0.004, w=0.02)
s.ol("Stk_Grey", rect(0.3, 0.2, 0.44, 0.26), -0.004, w=0.02)
s.ol("Stk_Grey", rect(0.39, 0.12, 0.44, 0.22), -0.005, w=0.02)
build("FX_Barrel", s, loc=(0.0, -0.3, 0.0))

def helmet(pref):
    rig = O[pref + "Stickman_Rig"]
    s = Shape()
    s.ol("Stk_Yellow", circ(0.0, 0.0, 0.5, 0.44, n=20, a0=0, a1=180), -0.01, w=0.03)
    s.add("Stk_HelmetDark", rect(-0.05, 0.0, 0.05, 0.43), -0.015)
    s.ol("Stk_Yellow", rrect(-0.63, -0.08, 0.63, 0.03, 0.035), -0.02, w=0.03)
    s.ol("Stk_White", circ(0.0, 0.2, 0.11, n=18), -0.03, w=0.025)
    s.add("Stk_Lemon", circ(0.0, 0.2, 0.065, n=14), -0.035)
    ob = build(pref + "Helmet", s, coll=pref + "Stickman_Parts", parent=rig)
    ob.parent_type = 'BONE'; ob.parent_bone = "head"
    ob.matrix_parent_inverse.identity()
    ob.location = (0.0, 0.0, 0.17); ob.rotation_euler = (-math.pi / 2, 0.0, 0.0)
    stamp(ob)
    return ob
helmet("T_"); helmet("G_")

def stand_copy(name, texts):
    src = O["FX_Stand"]; srct = O["FX_Stand_Txt"]
    for ch in [c for c in O if c.name.startswith(name)]:
        bpy.data.objects.remove(ch, do_unlink=True)
    st_ = src.copy(); st_.name = name; bpy.data.collections["Stickman_Extras"].objects.link(st_)
    st_.animation_data_clear()
    st_.location = tuple(src["rest_loc"]); st_.rotation_euler = tuple(src["rest_rot"]); stamp(st_)
    for i, (body, sc, hidden) in enumerate(texts):
        t = srct.copy(); t.data = srct.data.copy(); t.name = "%s_Txt%d" % (name, i + 1); t.data.body = body
        t.animation_data_clear()
        bpy.data.collections["Stickman_Extras"].objects.link(t)
        t.parent = st_; t.matrix_parent_inverse = srct.matrix_parent_inverse.copy()
        t.location = tuple(srct["rest_loc"]); t.rotation_euler = tuple(srct["rest_rot"])
        t["rest_loc"] = list(t.location); t["rest_rot"] = list(t.rotation_euler)
        t["rest_scale"] = [0.0, 0.0, 0.0] if hidden else [sc, sc, sc]; t["rest_hide"] = 0
        t.scale = (0.0, 0.0, 0.0) if hidden else (sc, sc, sc)
stand_copy("Shop_Stand", [("SHOVELS", 1.0, False), ("SUPPLIES", 1.0, True)])
stand_copy("Snack_Stand", [("WATER & SNACKS", 0.72, False)])
bpy.context.view_layer.update()
