"""Blender-Rendering der Laermampel Variante B (Farbkreis + Display).

Masse wie laser/generate_laser.py. Aufruf:
  /Applications/Blender.app/Contents/MacOS/Blender -b -P render/render_laermampel.py
Optional nach "--": Samples, z. B. "-- 64".
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "render"
FONT = ROOT / "simulator" / "assets" / "fonts" / "Baloo-Regular.ttf"
MM = 0.001

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SAMPLES = int(argv[0]) if argv else 128

# --- Masse (mm) wie im Lasercut-Generator ---------------------------------
KREIS_D, RING_INNER_D = 360.0, 320.0
BOX_W, BOX_H, BOX_R = 240.0, 200.0, 12.0
GAP = 40.0
DEPTH = 60.0  # Holzaufbau
FRONT = 3.0
SEG_T, SEG_L, SEG_INSET = 16.0, 50.0, 1.5
DIGIT_X = [28.0, 130.0]
DIGIT_Y = 20.0
MIC = (196.0, 184.0)

KREIS_C = (-(KREIS_D + GAP + BOX_W) / 2 + KREIS_D / 2) * MM  # Gesamtanordnung zentriert
BOX_LEFT = KREIS_C + (KREIS_D / 2 + GAP) * MM
BOX_TOP = BOX_H / 2 * MM

STATES = [
    ("gruen", (0.0, 1.0, 0.06), "49"),
    ("gelb", (1.0, 0.42, 0.0), "64"),
    ("rot", (1.0, 0.025, 0.0), "76"),
]
DIGITS = {
    "0": "abcdef", "1": "bc", "2": "abdeg", "3": "abcdg", "4": "bcfg", "5": "acdfg",
    "6": "acdefg", "7": "abc", "8": "abcdefg", "9": "abcdfg",
}


# --- Hilfsfunktionen ----------------------------------------------------------

def principled(mat: bpy.types.Material) -> bpy.types.Node:
    return next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def new_mat(name, base=(0.8, 0.8, 0.8), rough=0.5, metal=0.0, coat=0.0, emit=None, strength=0.0):
    m = bpy.data.materials.new(name)
    if bpy.app.version < (5, 0, 0):  # ab Blender 5 immer Node-basiert
        m.use_nodes = True
    b = principled(m)
    b.inputs["Base Color"].default_value = (*base, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Coat Weight"].default_value = coat
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def prism(name, outline_xz, y_front, depth, mat, bevel=0.0):
    """Extrudiert einen Umriss in der XZ-Ebene von y_front nach hinten (Richtung Wand, +Y)."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    front = [bm.verts.new((x, y_front, z)) for x, z in outline_xz]
    face = bm.faces.new(front)
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    moved = [e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=moved, vec=(0, depth, 0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    obj = link(bpy.data.objects.new(name, me))
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        mod.limit_method = "ANGLE"
    for p in obj.data.polygons:
        p.use_smooth = False
    return obj


def rounded_rect(cx, cz, w, h, r, seg=10):
    pts = []
    corners = [(cx + w / 2 - r, cz + h / 2 - r, 0), (cx - w / 2 + r, cz + h / 2 - r, 90),
               (cx - w / 2 + r, cz - h / 2 + r, 180), (cx + w / 2 - r, cz - h / 2 + r, 270)]
    for ox, oz, a0 in corners:
        for i in range(seg + 1):
            a = math.radians(a0 + 90 * i / seg)
            pts.append((ox + r * math.cos(a), oz + r * math.sin(a)))
    return pts


def circle_pts(cx, cz, r, n=128):
    return [(cx + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def cylinder_y(name, cx, cz, r, y_front, depth, mat, n=24):
    return prism(name, circle_pts(cx, cz, r, n), y_front, depth, mat)


# --- Szene --------------------------------------------------------------------

def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene

    wood = new_mat("Pappel", base=(0.60, 0.46, 0.30), rough=0.6)
    wall = new_mat("Wand", base=(0.80, 0.78, 0.74), rough=0.92)
    smoke = new_mat("Rauchglas", base=(0.012, 0.012, 0.014), rough=0.06, coat=0.6)
    seg_off = new_mat("Segment aus", base=(0.006, 0.006, 0.007), rough=0.4)
    seg_on = new_mat("Segment an", base=(0.05, 0.05, 0.05), rough=0.3, emit=(0, 1, 0), strength=2.2)
    screw = new_mat("Schraube", base=(0.03, 0.03, 0.03), rough=0.35, metal=1.0)
    engrave = new_mat("Gravur", base=(0.35, 0.35, 0.36), rough=0.9)
    hole = new_mat("Loch", base=(0.0, 0.0, 0.0), rough=1.0)
    halo = new_mat("Halo", base=(0, 0, 0), emit=(0, 1, 0), strength=25.0)

    # Wand
    prism("Wand", [(-2, -1.2), (2, -1.2), (2, 1.2), (-2, 1.2)], 0.0, 0.02, wall)

    y_wood = -DEPTH * MM          # Vorderkante Holz
    y_front = y_wood - FRONT * MM  # Vorderkante Acryl

    # Farbkreis: Holzkoerper + Opalscheibe mit radialer Helligkeit
    R = KREIS_D / 2 * MM
    cylinder_y("Kreis_Holz", KREIS_C, 0, R, y_wood, DEPTH * MM, wood, n=128).modifiers.new("B", "BEVEL").width = 0.0015
    # dunkle Grundfarbe, damit das Raumlicht die LED-Farbe nicht ausbleicht
    opal = new_mat("Opal", base=(0.22, 0.22, 0.22), rough=0.35, emit=(0, 1, 0), strength=1.0)
    nt = opal.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    length = nt.nodes.new("ShaderNodeVectorMath"); length.operation = "LENGTH"
    inner = nt.nodes.new("ShaderNodeMapRange")  # Mitte etwas dunkler als der Rand
    inner.inputs["From Min"].default_value = 0.0
    inner.inputs["From Max"].default_value = RING_INNER_D / 2 * MM
    inner.inputs["To Min"].default_value = 0.72
    inner.inputs["To Max"].default_value = 1.0
    rim = nt.nodes.new("ShaderNodeMapRange")  # Holzwand hinter der Opalscheibe
    rim.inputs["From Min"].default_value = RING_INNER_D / 2 * MM - 0.004
    rim.inputs["From Max"].default_value = R
    rim.inputs["To Min"].default_value = 1.0
    rim.inputs["To Max"].default_value = 0.12
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    gain = nt.nodes.new("ShaderNodeMath"); gain.operation = "MULTIPLY"
    gain.inputs[1].default_value = 2.2
    gain.name = "Gain"
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    nt.links.new(sep.outputs["X"], comb.inputs["X"])
    nt.links.new(sep.outputs["Z"], comb.inputs["Y"])
    nt.links.new(comb.outputs[0], length.inputs[0])
    nt.links.new(length.outputs["Value"], inner.inputs["Value"])
    nt.links.new(length.outputs["Value"], rim.inputs["Value"])
    nt.links.new(inner.outputs["Result"], mul.inputs[0])
    nt.links.new(rim.outputs["Result"], mul.inputs[1])
    nt.links.new(mul.outputs["Value"], gain.inputs[0])
    nt.links.new(gain.outputs["Value"], principled(opal).inputs["Emission Strength"])
    disc = prism("Kreis_Opal", circle_pts(0, 0, R, 128), y_front, FRONT * MM, opal)
    disc.location.x = KREIS_C  # Objektursprung in der Kreismitte fuer die Radialmaske

    # Halo-Emitter hinter dem Kreisrand, fuer die Kamera unsichtbar
    # liegt knapp ausserhalb des Holzkoerpers zwischen Gehaeuserand und Wand
    bpy.ops.mesh.primitive_torus_add(major_radius=R + 0.006, minor_radius=0.003,
                                     location=(KREIS_C, -0.008, 0), rotation=(math.radians(90), 0, 0))
    h = bpy.context.active_object
    h.name = "Halo"
    h.data.materials.append(halo)
    h.visible_camera = False

    for k in range(6):
        a = math.radians(30 + 60 * k)
        cylinder_y(f"Schraube_K{k}", KREIS_C + 0.170 * math.cos(a), -0.170 * math.sin(a), 3 * MM,
                   y_front - 1.5 * MM, 1.5 * MM, screw)

    # Displaykasten
    bx = BOX_LEFT + BOX_W / 2 * MM
    outline = rounded_rect(bx, 0, BOX_W * MM, BOX_H * MM, BOX_R * MM)
    prism("Kasten_Holz", outline, y_wood, DEPTH * MM, wood, bevel=0.0012)
    prism("Kasten_Rauchglas", outline, y_front, FRONT * MM, smoke, bevel=0.0008)

    def box_xz(x_mm, y_mm):
        return BOX_LEFT + x_mm * MM, BOX_TOP - y_mm * MM

    segs = {}
    T, L = SEG_T, SEG_L
    for di, x0 in enumerate(DIGIT_X):
        y0 = DIGIT_Y
        rects = {
            "a": (x0 + T, y0, L, T), "b": (x0 + T + L, y0 + T, T, L),
            "c": (x0 + T + L, y0 + 2 * T + L, T, L), "d": (x0 + T, y0 + 2 * T + 2 * L, L, T),
            "e": (x0, y0 + 2 * T + L, T, L), "f": (x0, y0 + T, T, L), "g": (x0 + T, y0 + T + L, L, T),
        }
        for name, (x, y, w, hh) in rects.items():
            cx, cz = box_xz(x + w / 2, y + hh / 2)
            pts = rounded_rect(cx, cz, (w - 2 * SEG_INSET) * MM, (hh - 2 * SEG_INSET) * MM, 2 * MM, 4)
            o = prism(f"Segment_{di}{name}", pts, y_front - 0.15 * MM, 0.1 * MM, seg_off)
            segs[(di, name)] = o

    for x, y in [(10, 10), (230, 10), (10, 190), (230, 190)]:
        cx, cz = box_xz(x, y)
        cylinder_y(f"Schraube_D{x}_{y}", cx, cz, 3 * MM, y_front - 1.5 * MM, 1.5 * MM, screw)

    mx, mz = box_xz(*MIC)
    for i, (dx, dz) in enumerate([(0, 0)] + [(4 * math.cos(math.radians(a)), 4 * math.sin(math.radians(a)))
                                             for a in range(0, 360, 60)]):
        cylinder_y(f"Mikro_{i}", mx + dx * MM, mz + dz * MM, 1 * MM, y_front - 0.12 * MM, 0.1 * MM, hole, n=12)

    curve = bpy.data.curves.new("dBA", "FONT")
    curve.body = "dB(A)"
    if FONT.exists():
        curve.font = bpy.data.fonts.load(str(FONT))
    curve.size = 10 * MM
    curve.align_x = "CENTER"
    tx, tz = box_xz(110, 182)
    txt = link(bpy.data.objects.new("dBA", curve))
    txt.location = (tx, y_front - 0.12 * MM, tz)
    txt.rotation_euler = (math.radians(90), 0, 0)
    txt.data.materials.append(engrave)

    # Kabelbruecke
    x0, x1 = KREIS_C + R - 0.002, BOX_LEFT + 0.002
    prism("Kabelbruecke", [(x0, -0.006), (x1, -0.006), (x1, 0.006), (x0, 0.006)], -0.012, 0.012, wood)

    # Licht, Welt, Kamera
    world = bpy.data.worlds.new("Welt")
    sc.world = world
    if bpy.app.version < (5, 0, 0):
        world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (0.55, 0.55, 0.58, 1)
    bg.inputs["Strength"].default_value = 0.25

    key = bpy.data.lights.new("Raumlicht", "AREA")
    key.energy = 220
    key.size = 2.5
    key_o = link(bpy.data.objects.new("Raumlicht", key))
    key_o.location = (-1.2, -1.8, 1.6)

    target = link(bpy.data.objects.new("Ziel", None))
    target.location = (0.0, -0.03, 0.0)
    for o, loc in [(key_o, None)]:
        c = o.constraints.new("TRACK_TO")
        c.target = target
        c.track_axis = "TRACK_NEGATIVE_Z"
        c.up_axis = "UP_Y"

    cam_data = bpy.data.cameras.new("Kamera")
    cam_data.lens = 50
    cam = link(bpy.data.objects.new("Kamera", cam_data))
    cam.location = (0.38, -1.30, 0.10)
    c = cam.constraints.new("TRACK_TO")
    c.target = target
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"
    sc.camera = cam

    # Render-Einstellungen
    sc.render.engine = "CYCLES"
    sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.image_settings.file_format = "PNG"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        sc.cycles.device = "GPU"
    except Exception as err:  # CPU-Rendering funktioniert auch, nur langsamer
        print("GPU nicht verfuegbar:", err)
    # "Standard" statt AgX: AgX entsaettigt helle Emission, LED-Farben wirken dann blass
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"

    return opal, halo, seg_on, seg_off, segs


def main():
    opal, halo, seg_on, seg_off, segs = build()
    OUT.mkdir(parents=True, exist_ok=True)
    for name, col, digits in STATES:
        for m in (opal, halo, seg_on):
            principled(m).inputs["Emission Color"].default_value = (*col, 1)
        # Gelb wirkt durch zwei aktive Kanaele heller, deshalb leicht absenken
        opal.node_tree.nodes["Gain"].inputs[1].default_value = 1.7 if name == "gelb" else 2.2
        for (di, seg), obj in segs.items():
            obj.data.materials[0] = seg_on if seg in DIGITS[digits[di]] else seg_off
        bpy.context.scene.render.filepath = str(OUT / f"laermampel_{name}.png")
        bpy.ops.render.render(write_still=True)
        print("gerendert:", bpy.context.scene.render.filepath)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "laermampel.blend"))


main()
