"""Blender (EEVEE) renderer for the EXID crest cards — real-time-engine look.

Run:  xvfb-run -a blender -b -P crest_render.py -- [card ...]
Each card is modelled in 3D (bevelled gold frames, recessed obsidian panels,
extruded Cinzel lettering, enamel hexagons, glossy jewels), lit by a procedural
studio environment with bloom, screen-space reflections and ambient occlusion,
and rendered with a transparent background to assets/crest/render/<card>.png.
crest.py then wraps each render in an SVG with a slow specular sweep.
"""
import bpy, bmesh, math, sys, os
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(bpy.data.filepath or __file__))
if not os.path.exists(os.path.join(ROOT, "crest.py")):
    ROOT = os.getcwd()
OUT = os.path.join(ROOT, "assets", "crest", "render")
FONTS = os.path.join(ROOT, "assets", "crest", "fonts")
CREST_PNG = os.path.join(ROOT, "assets", "porsche", "src", "EXID_Crest_Transparent.png")
KR_FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
SCALE = 100.0  # design px per Blender unit
KR_SIZE = 26 * 2.0  # Noto CJK (.ttc) is set at ~half size by Blender; compensate

# --------------------------------------------------------------------------- scene
def reset(w_px, h_px, res_scale):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    e = sc.eevee
    e.taa_render_samples = 48
    e.use_bloom = True; e.bloom_threshold = 1.4; e.bloom_intensity = 0.025; e.bloom_radius = 3.0; e.bloom_knee = 0.4
    e.use_ssr = True; e.use_ssr_refraction = True; e.ssr_quality = 1.0; e.ssr_thickness = 0.4
    e.use_gtao = True; e.gtao_distance = 0.6; e.gtao_factor = 1.2
    e.use_soft_shadows = True; e.shadow_cube_size = "2048"; e.shadow_cascade_size = "2048"
    sc.render.film_transparent = True
    sc.render.resolution_x = int(w_px * res_scale); sc.render.resolution_y = int(h_px * res_scale)
    sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "Filmic"; sc.view_settings.look = "Medium High Contrast"
    sc.view_settings.exposure = 0.0
    world(sc)
    camera(sc, w_px, h_px)
    lights()
    return sc


def world(sc):
    """Procedural studio HDRI: dark warm room, a big graded softbox behind the camera,
    strip lights for the bevels and a warm floor bounce."""
    import numpy as np
    W, H = 1024, 512
    u = (np.arange(W) + .5) / W; v = (np.arange(H) + .5) / H
    U, V = np.meshgrid(u, v)                      # V: 0 = bottom (nadir), 1 = top (zenith)
    img = np.zeros((H, W, 3), np.float32)
    img += np.array([0.004, 0.0035, 0.003])
    def box(uc, vc, uw, vh, power, col=(1, .96, .88), soft=0.25):
        du = np.minimum(np.abs(U - uc), 1 - np.abs(U - uc)) / (uw / 2)
        dv = np.abs(V - vc) / (vh / 2)
        m = np.clip((1 - np.maximum(du, dv)) / soft, 0, 1)
        img[...] += m[..., None] * np.array(col) * power
    # camera faces -Y: flat front faces reflect u=.25, v=.5 -> keep that dim so panels stay black
    du = np.minimum(np.abs(U - .25), 1 - np.abs(U - .25))
    front = np.exp(-(du / .10) ** 2) * np.exp(-((V - .5) / .10) ** 2)
    img += (front * 0.06)[..., None] * np.array([1, .9, .75])
    box(.25, .80, .26, .10, 9.0, (1, .95, .86), .3)       # big softbox above the camera -> top bevels
    box(.25, .66, .40, .03, 4.0, (1, .93, .82), .2)       # thin horizon strip -> sharp highlight line
    box(.25, .30, .30, .10, 1.6, (1, .72, .38), .4)       # warm low fill -> bottom bevels
    box(.11, .56, .03, .34, 10.0, (1, .92, .80), .15)     # left strip
    box(.39, .56, .03, .34, 6.0, (1, .90, .78), .15)      # right strip
    box(.75, .60, .40, .40, 0.35, (1, .85, .6))           # back rim
    pix = np.concatenate([img, np.ones((H, W, 1), np.float32)], 2)
    im = bpy.data.images.new("studio", W, H, alpha=False, float_buffer=True)
    im.pixels.foreach_set(pix.ravel())
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    nt = w.node_tree; nt.nodes.clear()
    env = nt.nodes.new("ShaderNodeTexEnvironment"); env.image = im
    bg = nt.nodes.new("ShaderNodeBackground"); bg.inputs["Strength"].default_value = 1.0
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(env.outputs["Color"], bg.inputs["Color"]); nt.links.new(bg.outputs["Background"], out.inputs["Surface"])


def camera(sc, w_px, h_px):
    lens = 105.0
    wb, hb = w_px / SCALE, h_px / SCALE
    fov = 2 * math.atan(18 / lens)
    d = (wb / 2) / math.tan(fov / 2)
    bpy.ops.object.camera_add(location=(0, -d, 0), rotation=(math.radians(90), 0, 0))
    cam = bpy.context.object; cam.data.lens = lens; cam.data.sensor_fit = "HORIZONTAL"
    cam.data.sensor_width = 36; cam.data.clip_end = d * 4
    sc.camera = cam


def lights():
    def area(loc, rot, size, energy, color=(1, .95, .88)):
        bpy.ops.object.light_add(type="AREA", location=loc, rotation=[math.radians(a) for a in rot])
        l = bpy.context.object.data; l.shape = "RECTANGLE"; l.size, l.size_y = size; l.energy = energy; l.color = color
        l.use_contact_shadow = False
    area((-10, -8, 9), (50, 0, -48), (1.5, 1.5), 900)
    area((10, -6, 5), (65, 0, 55), (1, 3), 350, (1, .85, .65))


# --------------------------------------------------------------------------- materials
MATS = {}

def mat(name):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    def setp(k, v):
        p.inputs[k].default_value = v
    if name == "gold":
        setp("Base Color", (1.0, .66, .24, 1)); setp("Metallic", 1); setp("Roughness", .16)
        noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 60
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs[3].default_value = .10; mr.inputs[4].default_value = .22
        nt.links.new(noise.outputs["Fac"], mr.inputs[0]); nt.links.new(mr.outputs[0], p.inputs["Roughness"])
    elif name == "gold_bright":
        setp("Base Color", (1.0, .78, .38, 1)); setp("Metallic", 1); setp("Roughness", .14)
    elif name == "gold_brushed":
        setp("Base Color", (.85, .55, .18, 1)); setp("Metallic", 1); setp("Roughness", .34)
        setp("Anisotropic", .8)
        n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 4; n.inputs["Detail"].default_value = 14
        mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1, 1, 60)
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs[3].default_value = .26; mr.inputs[4].default_value = .44
        nt.links.new(n.outputs["Fac"], mr.inputs[0]); nt.links.new(mr.outputs[0], p.inputs["Roughness"])
    elif name == "gold_dark":
        setp("Base Color", (.55, .36, .12, 1)); setp("Metallic", 1); setp("Roughness", .35)
    elif name == "obsidian":
        setp("Base Color", (.003, .0025, .002, 1)); setp("Metallic", 0); setp("Roughness", .4); setp("Specular IOR Level", .12)
        setp("Coat Weight", .25); setp("Coat Roughness", .02)
        # faint brushed streaks
        wave = nt.nodes.new("ShaderNodeTexNoise"); wave.inputs["Scale"].default_value = 3; wave.inputs["Detail"].default_value = 12
        mapn = nt.nodes.new("ShaderNodeMapping"); mapn.inputs["Scale"].default_value = (1, 40, 1)
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nt.links.new(tc.outputs["Object"], mapn.inputs["Vector"]); nt.links.new(mapn.outputs["Vector"], wave.inputs["Vector"])
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs[3].default_value = .45; mr.inputs[4].default_value = .65
        nt.links.new(wave.outputs["Fac"], mr.inputs[0]); nt.links.new(mr.outputs[0], p.inputs["Roughness"])
    elif name == "enamel":
        setp("Base Color", (.16, .006, .016, 1)); setp("Roughness", .18); setp("Coat Weight", 1); setp("Coat Roughness", .02)
        setp("Emission Color", (.5, .02, .05, 1)); setp("Emission Strength", .02)
    elif name == "stud":
        setp("Base Color", (.30, .01, .03, 1)); setp("Roughness", .08); setp("Coat Weight", 1)
        setp("Emission Color", (1, .06, .1, 1)); setp("Emission Strength", .12)
    elif name == "jewel":
        setp("Base Color", (.55, .01, .04, 1)); setp("Roughness", .04); setp("Coat Weight", 1); setp("Specular IOR Level", .9)
        setp("Emission Color", (1, .05, .1, 1)); setp("Emission Strength", .9)
    elif name in ("ivory", "muted", "dim", "winetext", "goldtext"):
        col = {"ivory": (.80, .74, .60), "muted": (.42, .36, .26), "dim": (.20, .17, .12), "winetext": (.75, .10, .15), "goldtext": (.95, .70, .32)}[name]
        nt.nodes.remove(p)
        em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*col, 1); em.inputs["Strength"].default_value = 1.0
        nt.links.new(em.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    elif name.startswith("lang_"):
        h = name[5:]
        col = tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        col = tuple(c ** 2.2 for c in col)
        setp("Base Color", (*col, 1)); setp("Roughness", .12); setp("Coat Weight", 1); setp("Coat Roughness", .03)
        setp("Emission Color", (*col, 1)); setp("Emission Strength", .25)
    MATS[name] = m
    return m


def assign(obj, name):
    obj.data.materials.clear(); obj.data.materials.append(mat(name))


# --------------------------------------------------------------------------- geometry
def P(x, y, W, H):
    """design px (origin top-left, y down) -> Blender XZ (origin centre, z up)."""
    return ((x - W / 2) / SCALE, (H / 2 - y) / SCALE)


def chamfer_pts(x, y, w, h, c):
    return [(x + c, y), (x + w - c, y), (x + w, y + c), (x + w, y + h - c), (x + w - c, y + h),
            (x + c, y + h), (x, y + h - c), (x, y + c)]


def curve_shape(name, loops, W, H, depth=0.0, bevel=0.0, ydepth=0.0, fill="BOTH", res=4):
    """Flat curve (in local XY) from design-px loops, rotated to face the camera (-Y)."""
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "2D"; cu.fill_mode = fill
    cu.extrude = depth; cu.bevel_depth = bevel; cu.bevel_resolution = res
    for loop in loops:
        sp = cu.splines.new("POLY"); sp.points.add(len(loop) - 1)
        for i, (px, py) in enumerate(loop):
            bx, bz = P(px, py, W, H)
            sp.points[i].co = (bx, bz, 0, 1)
        sp.use_cyclic_u = True
    ob = bpy.data.objects.new(name, cu); bpy.context.collection.objects.link(ob)
    ob.rotation_euler = (math.radians(90), 0, 0)
    ob.location = (0, ydepth, 0)
    return ob


def tube(name, pts, r_px, W, H, z, matname="gold"):
    ob = curve_shape(name, [pts], W, H, depth=0, bevel=r_px / SCALE, ydepth=z, fill="NONE", res=6)
    assign(ob, matname)
    return ob


def frame(x, y, w, h, c, W, H, width=18, depth=.09, z=0.0):
    """Moulded gold frame: brushed band + polished outer bead + fine inner bead."""
    outer = chamfer_pts(x, y, w, h, c)
    inner = chamfer_pts(x + width, y + width, w - 2 * width, h - 2 * width, max(4, c - width * .41))
    band = curve_shape("band", [outer, inner[::-1]], W, H, depth=.012, bevel=.004, ydepth=z + .035)
    assign(band, "gold_brushed")
    r1 = width * .30
    o1 = r1 + .5
    tube("bead_out", chamfer_pts(x + o1, y + o1, w - 2 * o1, h - 2 * o1, max(3, c - o1 * .41)), r1, W, H, z)
    r2 = width * .17
    o2 = width - r2 - .5
    tube("bead_in", chamfer_pts(x + o2, y + o2, w - 2 * o2, h - 2 * o2, max(3, c - o2 * .41)), r2, W, H, z + .01, "gold_bright")
    return band


_PANEL_N = [0]


def panel_material(w, h, seed):
    """Obsidian lacquer with etched gold circuit traces and a warm light pool from above."""
    import numpy as np, random
    rnd = random.Random(seed)
    sc = 2
    iw, ih = int(w * sc), int(h * sc)
    img = np.zeros((ih, iw), np.float32)
    def seg(x0, y0, x1, y1, t=1.2):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * sc) + 1
        for k in range(n):
            xx = int((x0 + (x1 - x0) * k / max(n - 1, 1)) * sc); yy = int((y0 + (y1 - y0) * k / max(n - 1, 1)) * sc)
            r = int(t * sc)
            img[max(0, yy - r):yy + r + 1, max(0, xx - r):xx + r + 1] = 1
    def dot(x0, y0, r=3.2):
        yy, xx = np.ogrid[:ih, :iw]
        m = (xx - x0 * sc) ** 2 + (yy - y0 * sc) ** 2
        img[(m <= (r * sc) ** 2) & (m >= ((r - 1.4) * sc) ** 2)] = 1
    for _ in range(max(5, int(w // 110))):
        side = 1 if rnd.random() < .7 else 0
        y0 = rnd.uniform(h * .15, h * .85)
        run = rnd.uniform(w * .03, w * .08)
        dy = rnd.choice([-1, 1]) * rnd.uniform(10, 26)
        tail = rnd.uniform(18, 45)
        if side == 0:
            x0, x1 = 0, run; x2 = x1 + abs(dy); x3 = x2 + tail
        else:
            x0, x1 = w, w - run; x2 = x1 - abs(dy); x3 = x2 - tail
        y1 = min(h - 8, max(8, y0 + dy))
        seg(x0, y0, x1, y0, .8); seg(x1, y0, x2, y1, .8); seg(x2, y1, x3, y1, .8); dot(x3, y1, 2.6)
    import bpy
    im = bpy.data.images.new(f"traces{seed}", iw, ih, alpha=False)
    pix = np.zeros((ih, iw, 4), np.float32); pix[..., 0] = pix[..., 1] = pix[..., 2] = img[::-1]; pix[..., 3] = 1
    im.pixels.foreach_set(pix.ravel()); im.pack()
    m = mat("obsidian").copy(); m.name = f"panel{seed}"
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = im; tex.interpolation = "Linear"; tex.extension = "CLIP"
    nt.links.new(tc.outputs["Generated"], tex.inputs["Vector"])
    # warm light pool from the top edge
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    grad = nt.nodes.new("ShaderNodeMapRange"); grad.inputs[1].default_value = .35; grad.inputs[2].default_value = 1.0
    grad.inputs[3].default_value = 0; grad.inputs[4].default_value = 1
    nt.links.new(sep.outputs["Y"], grad.inputs[0])
    trace = nt.nodes.new("ShaderNodeMath"); trace.operation = "MULTIPLY"; trace.inputs[1].default_value = .07
    nt.links.new(tex.outputs["Color"], trace.inputs[0])
    pool = nt.nodes.new("ShaderNodeMath"); pool.operation = "MULTIPLY"; pool.inputs[1].default_value = .035
    nt.links.new(grad.outputs[0], pool.inputs[0])
    add = nt.nodes.new("ShaderNodeMath"); add.operation = "ADD"
    nt.links.new(trace.outputs[0], add.inputs[0]); nt.links.new(pool.outputs[0], add.inputs[1])
    p.inputs["Emission Color"].default_value = (1.0, .62, .22, 1)
    nt.links.new(add.outputs[0], p.inputs["Emission Strength"])
    # traces are metallic and slightly raised
    met = nt.nodes.new("ShaderNodeMath"); met.operation = "MULTIPLY"; met.inputs[1].default_value = .45
    nt.links.new(tex.outputs["Color"], met.inputs[0]); nt.links.new(met.outputs[0], p.inputs["Metallic"])
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = .35; bump.inputs["Distance"].default_value = .002
    nt.links.new(tex.outputs["Color"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def plate(x, y, w, h, c, W, H, gem=True, hairline=True, width=18, traces=True):
    """Gold moulded frame + recessed obsidian panel (etched traces) + inner hairline + top jewel."""
    panel = curve_shape("panel", [chamfer_pts(x + 6, y + 6, w - 12, h - 12, c - 3)], W, H, depth=.03, ydepth=.10)
    if traces:
        _PANEL_N[0] += 1
        panel.data.materials.append(panel_material(w - 12, h - 12, int(x * 7 + y * 13 + w) + _PANEL_N[0]))
    else:
        assign(panel, "obsidian")
    frame(x, y, w, h, c, W, H, width=width, depth=.09, z=-.02)
    if hairline:
        ins = width + 10
        hl = chamfer_pts(x + ins, y + ins, w - 2 * ins, h - 2 * ins, max(4, c - ins * .45))
        ob = curve_shape("hair", [hl, chamfer_pts(x + ins + 2.2, y + ins + 2.2, w - 2 * ins - 4.4, h - 2 * ins - 4.4, max(3, c - ins * .45 - 1))[::-1]],
                         W, H, depth=.006, bevel=.004, ydepth=.06)
        assign(ob, "gold_dark")
    if gem:
        jewel(x + w / 2, y + 2, 12, W, H)


def jewel(cx, cy, r, W, H, z=None):
    bx, bz = P(cx, cy, W, H)
    y0 = -.13 if z is None else z
    bpy.ops.mesh.primitive_torus_add(major_radius=r * 1.25 / SCALE, minor_radius=r * .28 / SCALE, major_segments=48, minor_segments=12,
                                     location=(bx, y0 + .02, bz), rotation=(math.radians(90), 0, 0))
    assign(bpy.context.object, "gold_bright")
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=4, radius=r * 1.05 / SCALE, location=(bx, y0, bz))
    g = bpy.context.object; g.scale = (1, .55, 1); g.rotation_euler = (0, math.radians(22.5), 0)
    assign(g, "jewel")


def text(value, x, y, size, W, H, font="cinzel", matname="gold", align="LEFT", depth=.025, bevel=.006, spacing=1.0, z=None):
    cu = bpy.data.curves.new("t", "FONT"); cu.body = value
    cu.font = load_font(font); cu.size = size / SCALE * (1.0 if font != "kr" else 1.0)
    flat = depth <= .005
    cu.align_x = align
    cu.extrude = 0 if flat else depth * (size / 40)
    cu.bevel_depth = 0 if flat else bevel * (size / 40); cu.bevel_resolution = 4
    if z is None:
        z = .066 if flat else .07 - cu.extrude - cu.bevel_depth
    cu.space_character = spacing
    ob = bpy.data.objects.new("t", cu); bpy.context.collection.objects.link(ob)
    bx, bz = P(x, y, W, H)
    ob.location = (bx, z, bz); ob.rotation_euler = (math.radians(90), 0, 0)
    assign(ob, matname)
    return ob


_FONTS = {}
def load_font(key):
    if key not in _FONTS:
        path = {"cinzel": os.path.join(FONTS, "Cinzel-Bold.ttf"), "mont": os.path.join(FONTS, "Montserrat-Medium.ttf"),
                "montb": os.path.join(FONTS, "Montserrat-Bold.ttf"), "kr": KR_FONT}[key]
        _FONTS[key] = bpy.data.fonts.load(path)
    return _FONTS[key]


def rule(x1, x2, y, W, H, z=.0, t=2.6):
    a, bz = P(x1, y, W, H); b, _ = P(x2, y, W, H)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=t / SCALE, depth=(b - a), location=((a + b) / 2, z, bz), rotation=(0, math.radians(90), 0))
    ob = bpy.context.object
    # taper ends via scale on a lattice-free trick: use two cones? keep simple, add soft ends with gem
    assign(ob, "gold_bright")
    return ob


def diamond(cx, cy, r, W, H, matname="gold_bright", z=None):
    """Small faceted stud (gold or coloured enamel)."""
    bx, bz = P(cx, cy, W, H)
    y0 = .02 if z is None else z
    bpy.ops.mesh.primitive_uv_sphere_add(segments=4, ring_count=2, radius=r / SCALE, location=(bx, y0, bz))
    g = bpy.context.object; g.scale = (1, .5, 1)
    assign(g, matname)


def hexagon(cx, cy, r, glyph, W, H):
    bx, bz = P(cx, cy, W, H)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=r / SCALE, depth=.14, location=(bx, -.05, bz), rotation=(math.radians(90), 0, 0))
    o = bpy.context.object; o.rotation_euler.rotate_axis("Z", math.radians(30))
    m = o.modifiers.new("b", "BEVEL"); m.width = .045; m.segments = 4
    assign(o, "gold")
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=(r - 13) / SCALE, depth=.05, location=(bx, -.13, bz), rotation=(math.radians(90), 0, 0))
    o = bpy.context.object; o.rotation_euler.rotate_axis("Z", math.radians(30))
    m = o.modifiers.new("b", "BEVEL"); m.width = .015; m.segments = 3
    assign(o, "enamel")
    text(glyph, cx, cy + r * .24, r * .66, W, H, "montb", "gold_bright", "CENTER", z=-.17)


def crest_plane(cx, cy, h_px, W, H, z=-.05):
    img = bpy.data.images.load(CREST_PNG)
    aspect = img.size[0] / img.size[1]
    bx, bz = P(cx, cy, W, H)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(bx, z, bz), rotation=(math.radians(90), 0, 0))
    o = bpy.context.object; o.scale = (h_px * aspect / SCALE, h_px / SCALE, 1)
    m = bpy.data.materials.new("crest"); m.use_nodes = True; m.blend_method = "HASHED"; m.shadow_method = "HASHED"
    nt = m.node_tree; nt.nodes.clear()
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = img
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 1.15
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); mix = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(tex.outputs["Color"], em.inputs["Color"]); nt.links.new(tex.outputs["Alpha"], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(em.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], out.inputs["Surface"])
    o.data.materials.append(m)


def render(name):
    os.makedirs(OUT, exist_ok=True)
    sc = bpy.context.scene
    sc.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", name)


# --------------------------------------------------------------------------- cards
SNAPSHOT = "2026-10-06"
STACK = [("I", "BACKEND", "{ }", ["Java", "Spring Boot", "MyBatis"]),
         ("II", "FRONTEND", "</>", ["TypeScript", "React", "Vite"]),
         ("III", "AI & TOOLS", "AI", ["Spring AI", "Git"])]
LANGS = [("Java", 53.76, "d9a441"), ("TypeScript", 30.41, "b8323f"), ("Python", 13.09, "eadcb4"),
         ("HTML", 2.30, "9a6a2f"), ("CSS", 0.36, "8a8790"), ("JavaScript", 0.09, "f3df85")]
ACTIVITY = [("114", "CONTRIBUTIONS"), ("1", "CURRENT STREAK"), ("5", "LONGEST STREAK")]
PROJECTS = [("damso", "TypeScript", "Explore source code and development history."),
            ("SpringAiBasic", "Java", "Spring AI study notes and experiments."),
            ("sivertown", "HTML", "React + Vite web project."),
            ("SpringBootMyBatis", "Java", "Spring Boot MyBatis project.")]
LANG_DOT = {"TypeScript": "lang_b8323f", "Java": "lang_d9a441", "HTML": "lang_9a6a2f"}
LINKS = [("github", "GITHUB", "@EXID-Developer"), ("repositories", "REPOSITORIES", "Browse every project"), ("stars", "STARS", "Starred collection")]
SECTIONS = {"stack": "TECH STACK", "connect": "CONNECT", "activity": "ACTIVITY", "projects": "FEATURED PROJECTS"}
RS = float(os.environ.get("RS", "1.5"))  # render scale


def card_project(i, repo, lang, desc):
    W, H = 800, 380
    reset(W, H, RS)
    plate(14, 18, 772, 344, 30, W, H)
    text(f"FEATURED  ·  0{i}", 54, 84, 17, W, H, "montb", "muted", spacing=1.25, depth=.004, bevel=0)
    text(repo, 52, 165, 52 if len(repo) < 14 else 43, W, H, "cinzel", "gold", depth=.05, bevel=.012, z=-.02)
    text(desc, 54, 214, 22, W, H, "mont", "ivory", depth=.004, bevel=0)
    rule(54, 746, 258, W, H, z=.0, t=1.6)
    diamond(64, 304, 10, W, H, LANG_DOT.get(lang, "gold_bright"))
    text(lang, 86, 313, 23, W, H, "mont", "ivory", depth=.004, bevel=0)
    text("OPEN REPOSITORY  →", 746, 313, 17, W, H, "montb", "goldtext", "RIGHT", spacing=1.15, depth=.0, bevel=0)
    render(f"project-{repo}")


def card_activity():
    W, H = 800, 470
    reset(W, H, RS)
    plate(12, 16, 776, 438, 30, W, H)
    text("CONTRIBUTIONS  ·  TELEMETRY", 54, 82, 17, W, H, "montb", "muted", spacing=1.25, depth=.004, bevel=0)
    for k, (n, label) in enumerate(ACTIVITY):
        cx, cy, r = 160 + k * 240, 225, 74
        bx, bz = P(cx, cy, W, H)
        bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=(r - 4) / SCALE, depth=.04, location=(bx, .02, bz), rotation=(math.radians(90), 0, 0))
        assign(bpy.context.object, "obsidian")
        bpy.ops.mesh.primitive_torus_add(major_radius=r / SCALE, minor_radius=6.5 / SCALE, major_segments=128, minor_segments=24,
                                         location=(bx, -.03, bz), rotation=(math.radians(90), 0, 0))
        assign(bpy.context.object, "gold")
        bpy.ops.mesh.primitive_torus_add(major_radius=(r - 15) / SCALE, minor_radius=1.6 / SCALE, major_segments=128, minor_segments=12,
                                         location=(bx, -.01, bz), rotation=(math.radians(90), 0, 0))
        assign(bpy.context.object, "gold_dark")
        jewel(cx, cy + r, 9, W, H)
        text(n, cx, cy + 21, 62, W, H, "cinzel", "gold", "CENTER", depth=.05, bevel=.012, z=-.04)
        text(label, cx, cy + 128, 15, W, H, "montb", "ivory", "CENTER", spacing=1.2, depth=.004, bevel=0)
    text(f"SNAPSHOT  {SNAPSHOT}", 58, 404, 14, W, H, "montb", "dim", spacing=1.2, depth=.003, bevel=0)
    text("LIVE STATS  ↗", 742, 404, 14, W, H, "montb", "winetext", "RIGHT", spacing=1.2, depth=.003, bevel=0)
    render("activity")


def card_languages():
    W, H = 800, 470
    reset(W, H, RS)
    plate(12, 16, 776, 438, 30, W, H)
    text("MOST USED LANGUAGES", 54, 82, 17, W, H, "montb", "muted", spacing=1.25, depth=.004, bevel=0)
    # gold rail with enamel segments
    x0, bw, y = 54, 692, 122
    a, bz = P(x0 - 6, y, W, H); b, _ = P(x0 + bw + 6, y, W, H)
    bpy.ops.mesh.primitive_cube_add(size=1, location=((a + b) / 2, .0, bz)); o = bpy.context.object
    o.scale = (b - a, .08, 28 / SCALE); m = o.modifiers.new("b", "BEVEL"); m.width = .06; m.segments = 5
    assign(o, "gold")
    x = x0
    for name, v, col in LANGS:
        w = max(bw * v / 100, 1.2)
        a, bz = P(x, y, W, H); b, _ = P(x + w, y, W, H)
        bpy.ops.mesh.primitive_cube_add(size=1, location=((a + b) / 2, -.05, bz)); o = bpy.context.object
        o.scale = (b - a, .04, 16 / SCALE); assign(o, "lang_" + col)
        x += w
    for k, (name, v, col) in enumerate(LANGS):
        cx, cy = 62 + (k // 3) * 360, 196 + (k % 3) * 64
        diamond(cx, cy - 9, 10, W, H, "lang_" + col)
        text(name, cx + 26, cy, 25, W, H, "mont", "ivory", depth=.004, bevel=0)
        text(f"{v:.2f}%", cx + 318, cy, 25, W, H, "montb", "goldtext", "RIGHT", depth=0, bevel=0)
    text(f"GITHUB README STATS  ·  SNAPSHOT  {SNAPSHOT}", 58, 404, 14, W, H, "montb", "dim", spacing=1.2, depth=.003, bevel=0)
    render("languages")


def card_link(key, title, sub):
    W, H = 520, 160
    reset(W, H, RS * 1.3)
    plate(8, 12, 504, 136, 22, W, H, gem=False, width=12, traces=False)
    cx, cy = 82, 80
    bx, bz = P(cx, cy, W, H)
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=44 / SCALE, depth=.12, location=(bx, -.04, bz), rotation=(math.radians(90), 0, 0))
    o = bpy.context.object; m = o.modifiers.new("b", "BEVEL"); m.width = .05; m.segments = 4; assign(o, "gold")
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=34 / SCALE, depth=.04, location=(bx, -.11, bz), rotation=(math.radians(90), 0, 0))
    assign(bpy.context.object, "enamel")
    icon(key, cx, cy, W, H)
    text(title, 150, 84, 30, W, H, "cinzel", "gold", spacing=1.08, depth=.04, bevel=.01, z=-.02)
    text(sub, 151, 116, 18, W, H, "mont", "muted", depth=.003, bevel=0)
    text("→", 478, 92, 36, W, H, "montb", "gold_bright", "RIGHT", depth=.03, bevel=.006)
    render(f"link-{key}")


def icon(key, cx, cy, W, H):
    z = -.16
    if key == "stars":
        pts = []
        for k in range(10):
            rr = 25 if k % 2 == 0 else 10.5
            a = math.radians(-90 + k * 36)
            pts.append((cx + rr * math.cos(a), cy + 2 + rr * math.sin(a)))
        o = curve_shape("star", [pts], W, H, depth=.03, bevel=.012, ydepth=z)
        assign(o, "gold_bright")
    elif key == "github":
        head = [(cx + 11 * math.cos(math.radians(t)), cy - 11 + 11 * math.sin(math.radians(t))) for t in range(0, 360, 15)]
        o = curve_shape("head", [head], W, H, depth=.03, bevel=.01, ydepth=z); assign(o, "gold_bright")
        sh = [(cx + 22 * math.cos(math.radians(t)), cy + 24 + 20 * math.sin(math.radians(t))) for t in range(180, 361, 10)]
        o = curve_shape("shoulders", [sh], W, H, depth=.03, bevel=.01, ydepth=z); assign(o, "gold_bright")
    else:
        o = curve_shape("book", [chamfer_pts(cx - 19, cy - 24, 38, 48, 4), chamfer_pts(cx - 14, cy - 19, 28, 38, 2)[::-1]], W, H, depth=.03, bevel=.008, ydepth=z)
        assign(o, "gold_bright")
        for k, ww in enumerate([20, 20, 13]):
            a, bz = P(cx - 10, cy - 9 + k * 10, W, H); b, _ = P(cx - 10 + ww, cy - 9 + k * 10, W, H)
            bpy.ops.mesh.primitive_cube_add(size=1, location=((a + b) / 2, z, bz)); o = bpy.context.object
            o.scale = (b - a, .02, 3 / SCALE); assign(o, "gold_bright")


def card_stack():
    W, H = 1600, 520
    reset(W, H, 1.25)
    for k, (num, title, glyph, items) in enumerate(STACK):
        x = 40 + k * 520
        plate(x, 30, 480, 460, 32, W, H)
        text(num, x + 50, 92, 22, W, H, "cinzel", "muted", depth=0, bevel=0)
        hexagon(x + 240, 140, 64, glyph, W, H)
        text(title, x + 240, 262, 38, W, H, "cinzel", "gold", "CENTER", spacing=1.12, depth=.05, bevel=.012, z=-.02)
        rule(x + 100, x + 380, 290, W, H, t=1.4)
        diamond(x + 240, 290, 7, W, H)
        for j, item in enumerate(items):
            yy = 348 + j * 50
            diamond(x + 120, yy - 9, 7, W, H, "stud")
            text(item, x + 140, yy, 27, W, H, "mont", "ivory", depth=.004, bevel=0)
    render("stack")


def card_about():
    W, H = 1600, 470
    reset(W, H, 1.25)
    plate(24, 24, 1552, 422, 36, W, H, gem=False, width=18)
    crest_plane(95 + 155, 235, 330, W, H)
    x = 470
    text("PROFILE", x, 104, 20, W, H, "montb", "winetext", spacing=1.5, depth=0, bevel=0)
    text("EXID", x - 4, 196, 104, W, H, "cinzel", "gold", spacing=1.06, depth=.09, bevel=.02, z=-.03)
    text("SOFTWARE DEVELOPER", x + 2, 240, 27, W, H, "mont", "ivory", spacing=1.45, depth=0, bevel=0)
    rule(x - 10, x + 640, 268, W, H, t=1.5)
    text("Java와 Spring으로 서버를 세우고, React로 화면을 그리며,", x, 322, KR_SIZE, W, H, "kr", "ivory", depth=0, bevel=0)
    text("Spring AI로 새로운 가능성을 실험합니다.", x, 362, KR_SIZE, W, H, "kr", "ivory", depth=0, bevel=0)
    text("CODE  ·  BUILD  ·  SHIP", x, 400, 17, W, H, "montb", "muted", spacing=1.5, depth=0, bevel=0)
    render("about")


def card_section(key, label):
    W, H = 1600, 120
    reset(W, H, 1.25)
    tw = len(label) * 31 + 70
    l, r = 800 - tw / 2 - 30, 800 + tw / 2 + 30
    rule(130, l - 14, 60, W, H, t=1.6); rule(r + 14, 1470, 60, W, H, t=1.6)
    jewel(l, 60, 6, W, H); jewel(r, 60, 6, W, H)
    jewel(120, 60, 8, W, H); jewel(1480, 60, 8, W, H)
    text(label, 800, 74, 40, W, H, "cinzel", "gold", "CENTER", spacing=1.25, depth=.05, bevel=.012)
    render(f"section-{key}")


def card_footer():
    W, H = 1600, 280
    reset(W, H, 1.25)
    crest_plane(800, 105, 150, W, H)
    rule(130, 700, 105, W, H, t=1.6); rule(900, 1470, 105, W, H, t=1.6)
    jewel(120, 105, 8, W, H); jewel(1480, 105, 8, W, H)
    text("CODE  ·  BUILD  ·  SHIP", 800, 230, 26, W, H, "cinzel", "gold", "CENTER", spacing=1.3, depth=.035, bevel=.008)
    text("EXID-DEVELOPER", 800, 264, 15, W, H, "montb", "dim", "CENTER", spacing=1.5, depth=.003, bevel=0)
    render("footer")


CARDS = {"about": card_about, "stack": card_stack, "activity": card_activity, "languages": card_languages, "footer": card_footer}
for _k, _t, _s in LINKS:
    CARDS[f"link-{_k}"] = (lambda k=_k, t=_t, s=_s: card_link(k, t, s))
for _i, (_r, _l, _d) in enumerate(PROJECTS, 1):
    CARDS[f"project-{_r}"] = (lambda i=_i, r=_r, l=_l, d=_d: card_project(i, r, l, d))
for _k, _v in SECTIONS.items():
    CARDS[f"section-{_k}"] = (lambda k=_k, v=_v: card_section(k, v))

if __name__ in ("__main__",) and "__none__" not in sys.argv:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    for name in (argv or list(CARDS)):
        CARDS[name]()
