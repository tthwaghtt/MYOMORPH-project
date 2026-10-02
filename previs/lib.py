"""MYOMORPH previs library (P1 storyboard styleframes).

Throwaway blockout tooling for mood frames — not the production pipeline (that is MYOFORGE, P2+).
Wearer body: body.py (MakeHuman/MPFB2 CC0 base mesh + targets) fitted to Doha's CORPUS profile (fit_corpus.py).
"""
import gzip, math, os, json
import numpy as np
import bpy, bmesh
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(HERE, 'vendor', 'mpfb')

# ---------------------------------------------------------------- wearer body
LAST = {}


def load_wearer(height_m=1.78, arm_deg=17.0, elbow_deg=8.0, fit=os.path.join(HERE, 'wearer_fit.json')):
    """Doha's body: the CORPUS MAP fit (fit_corpus.py -> wearer_fit.json) on the MakeHuman base mesh, posed to the
    drawing's A-pose (upper arms 17° from vertical, elbows 8°). Returns body verts (Blender Z-up, m), faces, joints."""
    import body
    B = body.Base.get()
    params = json.load(open(fit))
    v = body.shape({'macro': params['macro'], 'sliders': params['sliders']}, B)
    vp, J = body.pose(v, arm_deg, elbow_deg, B)
    vw, Jw, _ = body.to_world(vp, J, height_m, B)
    LAST['arm_w'] = np.maximum(B.arm_w['l'], B.arm_w['r'])[B.body]
    LAST['fit'] = params
    return vw[B.body], B.faces, Jw


def mesh_object(name, verts, faces, smooth=True, subsurf=1):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(p) for p in verts], [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    for p in me.polygons:
        p.use_smooth = smooth
    if subsurf:
        m = ob.modifiers.new('Subsurf', 'SUBSURF'); m.levels = subsurf; m.render_levels = subsurf
    return ob


# ---------------------------------------------------------------- materials
NK = {  # complex IOR in linear sRGB primaries (physicallybased.info DB / refractiveindex.info, CC0)
    'Ti': ((1.9345, 1.86761, 2.05863), (2.33987, 2.05312, 1.74518)),
}

def _bsdf(m):
    return next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')


def mat_metal(name, f0, rough=0.35, aniso=0.0, rot=0.0, tangent_uv=True, bump=0.0, thin_film_nm=None):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    p = _bsdf(m)
    p.inputs['Base Color'].default_value = (*f0, 1); p.inputs['Metallic'].default_value = 1.0
    p.inputs['Roughness'].default_value = rough; p.inputs['Anisotropic'].default_value = aniso
    p.inputs['Anisotropic Rotation'].default_value = rot
    p.distribution = 'MULTI_GGX'
    if aniso and tangent_uv:
        t = nt.nodes.new('ShaderNodeTangent'); t.direction_type = 'RADIAL'; t.axis = 'Z'
        nt.links.new(t.outputs['Tangent'], p.inputs['Tangent'])
    if bump:
        n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 2200; n.inputs['Detail'].default_value = 2
        b = nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value = bump; b.inputs['Distance'].default_value = 0.00005
        nt.links.new(n.outputs['Fac'], b.inputs['Height']); nt.links.new(b.outputs['Normal'], p.inputs['Normal'])
    if thin_film_nm is not None and 'Thin Film Thickness' in p.inputs:
        p.inputs['Thin Film Thickness'].default_value = thin_film_nm; p.inputs['Thin Film IOR'].default_value = 2.4
    return m


def mat_heat_tint(name, f0=(0.441, 0.400, 0.361), axis='Z', lo=0.0, hi=1.0, rough=0.28, nm=(15.0, 75.0), coord='Object'):
    """Titanium with an oxide thin film whose thickness grows toward a heat source (temper colours). First-order
    TiO2 interference: ~20-35 nm straw/gold, ~45 nm purple, ~55-70 nm blue (thicker gives second-order rainbows)."""
    m = mat_metal(name, f0, rough=rough, bump=0.15)
    nt = m.node_tree; p = _bsdf(m)
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs[coord], sep.inputs[0])
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = lo; mr.inputs['From Max'].default_value = hi
    mr.inputs['To Min'].default_value = nm[0]; mr.inputs['To Max'].default_value = nm[1]
    nt.links.new(sep.outputs[axis], mr.inputs['Value'])
    if 'Thin Film Thickness' in p.inputs:
        nt.links.new(mr.outputs['Result'], p.inputs['Thin Film Thickness']); p.inputs['Thin Film IOR'].default_value = 2.5
    return m


def mat_paint_worn(name, paint=(0.62, 0.42, 0.02), primer=(0.18, 0.18, 0.17), metal_f0=(0.6, 0.58, 0.55), wear=0.55):
    """Industrial yellow paint chipped at exposed edges: pointiness × noise mask → primer, deeper → bare metal."""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; p = _bsdf(m)
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    noise = nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 38; noise.inputs['Detail'].default_value = 12; noise.inputs['Roughness'].default_value = 0.7
    mix = nt.nodes.new('ShaderNodeMath'); mix.operation = 'MULTIPLY_ADD'
    nt.links.new(geo.outputs['Pointiness'], mix.inputs[0]); mix.inputs[1].default_value = 1.6
    nt.links.new(noise.outputs['Fac'], mix.inputs[2])
    edge = nt.nodes.new('ShaderNodeMapRange'); edge.inputs['From Min'].default_value = 1.32 + (1 - wear) * 0.25; edge.inputs['From Max'].default_value = 1.42 + (1 - wear) * 0.25
    nt.links.new(mix.outputs[0], edge.inputs['Value'])
    deep = nt.nodes.new('ShaderNodeMapRange'); deep.inputs['From Min'].default_value = 1.46 + (1 - wear) * 0.25; deep.inputs['From Max'].default_value = 1.52 + (1 - wear) * 0.25
    nt.links.new(mix.outputs[0], deep.inputs['Value'])
    c1 = nt.nodes.new('ShaderNodeMix'); c1.data_type = 'RGBA'
    c1.inputs['A'].default_value = (*paint, 1); c1.inputs['B'].default_value = (*primer, 1)
    nt.links.new(edge.outputs['Result'], c1.inputs['Factor'])
    c2 = nt.nodes.new('ShaderNodeMix'); c2.data_type = 'RGBA'
    nt.links.new(c1.outputs['Result'], c2.inputs['A']); c2.inputs['B'].default_value = (*metal_f0, 1)
    nt.links.new(deep.outputs['Result'], c2.inputs['Factor'])
    nt.links.new(c2.outputs['Result'], p.inputs['Base Color'])
    nt.links.new(deep.outputs['Result'], p.inputs['Metallic'])
    rr = nt.nodes.new('ShaderNodeMapRange'); rr.inputs['To Min'].default_value = 0.38; rr.inputs['To Max'].default_value = 0.62
    nt.links.new(noise.outputs['Fac'], rr.inputs['Value']); nt.links.new(rr.outputs['Result'], p.inputs['Roughness'])
    if 'Coat Weight' in p.inputs:
        p.inputs['Coat Weight'].default_value = 0.25; p.inputs['Coat Roughness'].default_value = 0.3
    return m


def mat_basic(name, color, rough=0.5, metal=0.0, emit=None, strength=0.0, transmission=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; p = _bsdf(m)
    p.inputs['Base Color'].default_value = (*color, 1); p.inputs['Roughness'].default_value = rough; p.inputs['Metallic'].default_value = metal
    if emit:
        p.inputs['Emission Color'].default_value = (*emit, 1); p.inputs['Emission Strength'].default_value = strength
    if transmission:
        p.inputs['Transmission Weight'].default_value = transmission
    return m


MATS = {}
def materials():
    if MATS:
        return MATS
    MATS.update({
        'ti': mat_metal('MA-ti64_beadblast', (0.441, 0.400, 0.361), rough=0.34, bump=0.25),
        'ti_jc': mat_metal('MA-ti64_jc', (0.619, 0.579, 0.543), rough=0.34, bump=0.25),
        'ti_brushed': mat_metal('MA-ti64_hairline', (0.441, 0.400, 0.361), rough=0.30, aniso=0.75),
        'tin': mat_metal('MA-tin_polished', (0.614, 0.462, 0.233), rough=0.12),
        'tin_brushed': mat_metal('MA-tin_hairline', (0.614, 0.462, 0.233), rough=0.28, aniso=0.75),
        'tin_satin': mat_metal('MA-tin_beadblast', (0.614, 0.462, 0.233), rough=0.42, bump=0.3),
        'anod': mat_basic('MA-black_anodize', (0.018, 0.018, 0.02), rough=0.38, metal=0.0),
        'steel': mat_metal('MA-steel', (0.669, 0.639, 0.598), rough=0.22),
        'yellow': mat_paint_worn('MA-robot_yellow_worn'),
        'clay': mat_basic('MA-clay', (0.42, 0.41, 0.40), rough=0.62),
        'visor': mat_basic('MA-visor_smoke', (0.02, 0.022, 0.025), rough=0.06, metal=0.0),
        'rubber': mat_basic('MA-elastomer', (0.03, 0.03, 0.03), rough=0.75),
        'cyan': mat_basic('MA-lightpipe', (0.05, 0.3, 0.35), rough=0.2, emit=(0.25, 0.85, 1.0), strength=12),
        'floor': mat_basic('MA-floor', (0.025, 0.025, 0.027), rough=0.32),
    })
    return MATS


# ---------------------------------------------------------------- scene, lights, camera
def new_scene(res=(1920, 1080), samples=96, exposure=0.0):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    MATS.clear()                                  # the factory reset removed the cached datablocks
    try:
        import suit; suit.FIN.clear()
    except Exception:
        pass
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
    sc.cycles.samples = samples; sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.02
    sc.cycles.use_denoising = True; sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.cycles.max_bounces = 8; sc.cycles.glossy_bounces = 6; sc.cycles.transmission_bounces = 6
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'None'; sc.view_settings.exposure = exposure
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.004, 0.004, 0.005, 1)
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
    materials()
    return sc


def area(name, loc, look_at, size=(0.3, 1.6), energy=300, color=(1, 0.98, 0.95), spread=None):
    bpy.ops.object.light_add(type='AREA', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.shape = 'RECTANGLE'; L.data.size, L.data.size_y = size; L.data.energy = energy; L.data.color = color
    if spread is not None:
        L.data.spread = math.radians(spread)
    d = (Vector(look_at) - Vector(loc)).normalized(); L.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return L


def spot(name, loc, look_at, energy=200, size_deg=20, blend=0.6, radius=0.02, color=(1, 0.97, 0.92)):
    bpy.ops.object.light_add(type='SPOT', location=loc)
    L = bpy.context.active_object; L.name = name
    L.data.energy = energy; L.data.spot_size = math.radians(size_deg); L.data.spot_blend = blend; L.data.shadow_soft_size = radius; L.data.color = color
    d = (Vector(look_at) - Vector(loc)).normalized(); L.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return L


def camera(loc, look_at, lens=85, fstop=None, focus=None, ortho_scale=None):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.active_object; bpy.context.scene.camera = c
    c.data.lens = lens; c.data.sensor_width = 36
    if ortho_scale:
        c.data.type = 'ORTHO'; c.data.ortho_scale = ortho_scale
    d = (Vector(look_at) - Vector(loc)).normalized(); c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if fstop:
        c.data.dof.use_dof = True; c.data.dof.aperture_fstop = fstop
        c.data.dof.focus_distance = focus if focus else (Vector(look_at) - Vector(loc)).length
    return c


def floor(size=30, mat='floor', z=0.0):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z))
    f = bpy.context.active_object; f.name = 'ENV-floor'; f.data.materials.append(materials()[mat])
    return f


def sweep(z=0.0, r=5.0, mat='floor'):
    """Seamless studio cyclorama behind the subject."""
    bm = bmesh.new()
    prof = [(-12, 4.5, 0)] + [(0, r - r * math.sin(a), r - r * math.cos(a)) for a in np.linspace(0, math.pi / 2, 12)][1:] + [(0, -0.1, 9)]
    pts = [(0, 6, 0)] + [(0, 6 - r * math.sin(a) + 0, r - r * math.cos(a)) for a in np.linspace(0, math.pi / 2, 14)]
    pts = [(0, y, zz) for (_, y, zz) in [(0, 30, 0), (0, 6, 0)] + [(0, 6 + r * math.sin(a), r - r * math.cos(a)) for a in np.linspace(0, math.pi / 2, 14)][1:] + [(0, 6 + r, 12)]]
    rows = []
    for x in (-15, 15):
        rows.append([bm.verts.new((x, -y + 12, zz + z)) for (_, y, zz) in pts])
    for i in range(len(pts) - 1):
        bm.faces.new((rows[0][i], rows[1][i], rows[1][i + 1], rows[0][i + 1]))
    me = bpy.data.meshes.new('ENV-sweep'); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('ENV-sweep', me); bpy.context.scene.collection.objects.link(ob)
    for p in me.polygons: p.use_smooth = True
    ob.data.materials.append(materials()[mat])
    return ob


def render(path):
    sc = bpy.context.scene; sc.render.filepath = os.path.abspath(path)
    sc.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True)


# ---------------------------------------------------------------- simple hard-surface primitives
def beveled_box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.004, mat=None, segs=3):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    b = o.modifiers.new('Bevel', 'BEVEL'); b.width = bevel; b.segments = segs; b.limit_method = 'ANGLE'
    o.modifiers.new('WN', 'WEIGHTED_NORMAL').keep_sharp = True
    for p in o.data.polygons: p.use_smooth = True
    if mat: o.data.materials.append(mat)
    return o


def beveled_cyl(name, r, depth, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.003, mat=None, verts=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name
    b = o.modifiers.new('Bevel', 'BEVEL'); b.width = bevel; b.segments = 3; b.limit_method = 'ANGLE'
    o.modifiers.new('WN', 'WEIGHTED_NORMAL').keep_sharp = True
    for p in o.data.polygons: p.use_smooth = True
    if mat: o.data.materials.append(mat)
    return o


def rod_between(name, a, b, r, mat=None, bevel=0.002):
    a, b = Vector(a), Vector(b); d = b - a
    o = beveled_cyl(name, r, d.length, loc=(a + b) / 2, mat=mat, bevel=bevel, verts=32)
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return o
