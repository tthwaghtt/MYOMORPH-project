"""The assembly cell (R2 storyboard): where Doha stands while ceiling robots build MYOMORPH-MK. 1 around him.

Ceiling (z = 4.0 m): steel grid, two gantry rails with carriages and telescopic Z masts, inverted 6-axis arms, energy
chains, ladder cable trays with bundles, spiral duct, LED line lights, the scanner ring, the umbilical balancer.
Floor: epoxy concrete with markings, the plinth (foot plates, hazard ring, LED edge). Around it, an engineer's space:
workbench with tools and a lamp, tool wall, kitting carts with pre-assembled modules, a panel rack, Doha's blueprint on
a light table, a monitor wall with live telemetry. Previs geometry (primitives + materials), dense on purpose.
"""
import math, os
import numpy as np
import bpy
from mathutils import Vector, Matrix
import lib, props

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
CEIL = 4.0
RNG = np.random.default_rng(7)
MAT = {}


def mats():
    if MAT: return MAT
    M = lib.materials()
    def paint(name, col, rough=0.55):
        return lib.mat_basic(name, col, rough=rough)
    MAT.update({
        'steel_paint': paint('MA-cell_steel_paint', (0.022, 0.023, 0.025), 0.6),
        'galv': lib.mat_metal('MA-cell_galvanised', (0.52, 0.53, 0.54), rough=0.45),
        'alu': lib.mat_metal('MA-cell_alu_profile', (0.80, 0.80, 0.80), rough=0.38),
        'cable_blk': lib.mat_basic('MA-cell_cable_black', (0.012, 0.012, 0.013), rough=0.55),
        'cable_gry': lib.mat_basic('MA-cell_cable_grey', (0.08, 0.08, 0.085), rough=0.55),
        'cable_org': lib.mat_basic('MA-cell_cable_orange', (0.55, 0.16, 0.02), rough=0.5),
        'chain': lib.mat_basic('MA-cell_energy_chain', (0.03, 0.03, 0.032), rough=0.5),
        'esd': lib.mat_basic('MA-cell_esd_mat', (0.06, 0.08, 0.10), rough=0.7),
        'wood': lib.mat_basic('MA-cell_birch', (0.42, 0.32, 0.21), rough=0.6),
        'foam': lib.mat_basic('MA-cell_kit_foam', (0.015, 0.015, 0.016), rough=0.9),
        'hazard': hazard_material(),
        'floor': floor_material(),
        'led': lib.mat_basic('MA-cell_led_line', (1, 1, 1), rough=0.3, emit=(1.0, 0.97, 0.92), strength=0.0),
        'led_cool': lib.mat_basic('MA-cell_led_cool', (1, 1, 1), rough=0.3, emit=(0.80, 0.92, 1.0), strength=0.0),
        'lamp': lib.mat_basic('MA-cell_desk_lamp', (1, 1, 1), rough=0.3, emit=(1.0, 0.82, 0.62), strength=0.0),
        'glass': lib.mat_basic('MA-cell_glass', (0.8, 0.85, 0.9), rough=0.05, transmission=1.0),
        'rubber': M['rubber'], 'yellow': M['yellow'], 'anod': M['anod'], 'steel': M['steel'], 'ti': M['ti_jc'],
        'red': lib.mat_basic('MA-cell_extinguisher', (0.5, 0.03, 0.02), rough=0.35),
        'white_mark': lib.mat_basic('MA-cell_floor_mark', (0.55, 0.55, 0.52), rough=0.6),
        'yellow_mark': lib.mat_basic('MA-cell_floor_yellow', (0.62, 0.45, 0.02), rough=0.6),
    })
    return MAT


def lights_on(strength=1.0):
    """cell power: LED line lights, plinth ring, desk lamp. 0 = dark (opening)."""
    m = mats()
    m['led'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 28.0 * strength
    m['led_cool'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 9.0 * strength
    m['lamp'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 40.0


def hazard_material():
    m = bpy.data.materials.new('MA-cell_hazard'); m.use_nodes = True; nt = m.node_tree; nd = nt.nodes; ln = nt.links
    p = nd['Principled BSDF']; tc = nd.new('ShaderNodeTexCoord'); w = nd.new('ShaderNodeTexWave')
    w.wave_type = 'BANDS'; w.bands_direction = 'DIAGONAL'; w.inputs['Scale'].default_value = 9.0
    ln.new(tc.outputs['Object'], w.inputs['Vector'])
    gt = nd.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; gt.inputs[1].default_value = 0.5; ln.new(w.outputs['Fac'], gt.inputs[0])
    mx = nd.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.inputs[6].default_value = (0.012, 0.012, 0.012, 1); mx.inputs[7].default_value = (0.62, 0.44, 0.02, 1)
    ln.new(gt.outputs['Value'], mx.inputs[0])
    # wear: scuffed paint
    nz = nd.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 40; ln.new(tc.outputs['Object'], nz.inputs['Vector'])
    sc = nd.new('ShaderNodeMapRange'); sc.inputs['From Min'].default_value = 0.62; sc.inputs['From Max'].default_value = 0.7
    ln.new(nz.outputs['Fac'], sc.inputs['Value'])
    mx2 = nd.new('ShaderNodeMix'); mx2.data_type = 'RGBA'; mx2.inputs[7].default_value = (0.09, 0.09, 0.09, 1)
    ln.new(sc.outputs['Result'], mx2.inputs[0]); ln.new(mx.outputs[2], mx2.inputs[6])
    ln.new(mx2.outputs[2], p.inputs['Base Color']); p.inputs['Roughness'].default_value = 0.6
    return m


def floor_material():
    """epoxy-coated concrete: dark grey, satin, scuffed and patchy (roughness noise), tyre marks."""
    m = bpy.data.materials.new('MA-cell_floor_epoxy'); m.use_nodes = True; nt = m.node_tree; nd = nt.nodes; ln = nt.links
    p = nd['Principled BSDF']; tc = nd.new('ShaderNodeTexCoord')
    n1 = nd.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 0.8; n1.inputs['Detail'].default_value = 6
    n2 = nd.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 60; n2.inputs['Detail'].default_value = 4
    for n_ in (n1, n2): ln.new(tc.outputs['Object'], n_.inputs['Vector'])
    c = nd.new('ShaderNodeMapRange'); c.inputs['To Min'].default_value = 0.022; c.inputs['To Max'].default_value = 0.040
    ln.new(n1.outputs['Fac'], c.inputs['Value'])
    cc = nd.new('ShaderNodeCombineColor'); [ln.new(c.outputs['Result'], cc.inputs[k]) for k in range(3)]
    ln.new(cc.outputs['Color'], p.inputs['Base Color'])
    r = nd.new('ShaderNodeMapRange'); r.inputs['To Min'].default_value = 0.18; r.inputs['To Max'].default_value = 0.55
    mx = nd.new('ShaderNodeMath'); mx.operation = 'MULTIPLY_ADD'; mx.inputs[1].default_value = 0.6
    ln.new(n1.outputs['Fac'], mx.inputs[0]); ln.new(n2.outputs['Fac'], mx.inputs[2])
    ln.new(mx.outputs['Value'], r.inputs['Value']); ln.new(r.outputs['Result'], p.inputs['Roughness'])
    return m


def box(name, size, loc, mat, rot=(0, 0, 0), bevel=0.004):
    return lib.beveled_box(name, size, loc=loc, rot=rot, bevel=bevel, mat=mat)


def image_plane(name, path, w, loc, rot, emit=0.0, rough=0.35):
    from PIL import Image
    im = Image.open(path); h = w * im.height / im.width
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.scale = (w, h, 1)
    m = bpy.data.materials.new('MA-' + name); m.use_nodes = True; nt = m.node_tree; p = nt.nodes['Principled BSDF']
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(path)
    nt.links.new(t.outputs['Color'], p.inputs['Base Color']); p.inputs['Roughness'].default_value = rough
    if emit:
        nt.links.new(t.outputs['Color'], p.inputs['Emission Color']); p.inputs['Emission Strength'].default_value = emit
    o.data.materials.append(m)
    return o


# ---------------------------------------------------------------- telemetry screens (generated, data-true)
def screens(outdir):
    """monitor images drawn from the engineering data: EMG traces + motor-unit raster, EEG map, system tree."""
    import json
    from PIL import Image, ImageDraw, ImageFont
    os.makedirs(outdir, exist_ok=True)
    U = json.load(open(os.path.join(ROOT, 'engineering', 'undersuit.json'))); E = json.load(open(os.path.join(ROOT, 'engineering', 'engineering.json')))
    try:
        F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 15); Fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 12)
    except Exception:
        F = Fs = ImageFont.load_default()
    paths = []
    # 1) EMG
    W, H = 1280, 720; im = Image.new('RGB', (W, H), (8, 10, 12)); d = ImageDraw.Draw(im)
    d.text((20, 14), 'NEURAL WEAR  ·  HD-sEMG  %d ch  ·  2048 Hz' % E['neural']['emg_channels'], fill=(150, 210, 230), font=F)
    sites = [s for s in U['emg_sites'] if s['site'].endswith('-L')][:12]
    rng = np.random.default_rng(3)
    for k, s in enumerate(sites):
        y0 = 60 + k * 52
        d.text((20, y0 + 14), f"{s['site'][:-2]:5s} {s['en'][:20]}", fill=(120, 140, 150), font=Fs)
        t = np.arange(860); burst = np.exp(-((t - 300 - 30 * k) / 90.0) ** 2) + 0.6 * np.exp(-((t - 640 + 10 * k) / 60.0) ** 2)
        sig = rng.normal(0, 1, len(t)) * (0.12 + burst)
        pts = [(330 + i, y0 + 22 - float(v) * 14) for i, v in enumerate(sig)]
        d.line(pts, fill=(90, 200, 230), width=1)
    d.text((20, H - 30), 'motor-unit decomposition: 37 MU tracked · neural drive -> joint torque in %.0f ms' % E['neural']['latency_total_ms'], fill=(150, 210, 230), font=Fs)
    p = os.path.join(outdir, 'screen_emg.png'); im.save(p); paths.append(p)
    # 2) motor-unit raster + EEG topomap
    im = Image.new('RGB', (W, H), (8, 10, 12)); d = ImageDraw.Draw(im)
    d.text((20, 14), 'MOTOR UNITS  ·  VASTUS LATERALIS L  ·  EEG 32 ch (intent / error)', fill=(150, 210, 230), font=F)
    for u in range(37):
        rate = 8 + u * 0.35; t = 0.0
        while t < 4.0:
            t += 1.0 / rate * (1 + rng.normal(0, 0.12))
            x = 30 + t / 4.0 * 700; y = 60 + u * 16
            d.line([(x, y), (x, y + 11)], fill=(90, 200, 230))
    cx, cy, R = 1000, 380, 220
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(70, 90, 100), width=2)
    for e in U['eeg']:
        th, ph = math.radians(e['theta']), math.radians(e['phi'])
        x = cx - R * (th / (math.pi / 2)) * math.sin(ph); y = cy - R * (th / (math.pi / 2)) * math.cos(ph)
        v = 0.5 + 0.5 * math.sin(e['theta'] * 0.11 + e['phi'] * 0.05)
        col = (int(40 + 200 * v), int(120 + 80 * (1 - v)), int(220 - 150 * v))
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=col); d.text((x + 11, y - 7), e['name'], fill=(110, 130, 140), font=Fs)
    p = os.path.join(outdir, 'screen_mu_eeg.png'); im.save(p); paths.append(p)
    # 3) system tree / assembly status
    B = json.load(open(os.path.join(ROOT, 'engineering', 'bom.json')))
    im = Image.new('RGB', (W, H), (8, 10, 12)); d = ImageDraw.Draw(im)
    d.text((20, 14), 'MM1 ASSEMBLY  ·  %d parts  ·  %d modules  ·  %.1f kg' % (B['total_parts'], B['pre_assembled_modules'], E['suit']['mass_total_kg']), fill=(150, 210, 230), font=F)
    y = 56
    for k, sy in B['systems'].items():
        d.text((20, y), f"{k:9s} {sy['name_en'][:16]:16s} {sy.get('parts', 0):5d} parts {sy.get('mass_kg', 0):6.2f} kg", fill=(130, 150, 160), font=Fs)
        frac = min(1.0, sy.get('parts', 0) / 3000)
        d.rectangle([520, y + 3, 520 + int(700 * frac), y + 12], fill=(60, 150, 180)); y += 26
    y += 12
    for k, st in B['stages'].items():
        d.text((20, y), f"STAGE {k}  {st['name_en']:10s} {st.get('parts', 0) or 0:5d} parts", fill=(110, 130, 140), font=Fs); y += 20
    p = os.path.join(outdir, 'screen_bom.png'); im.save(p); paths.append(p)
    return paths


# ---------------------------------------------------------------- inverted robot on a telescopic Z mast
def robot_ceiling(carriage, tip, approach, name='ROB', tool='nutrunner', reach=(0.64, 0.60), tool_len=0.24, held=None):
    """6-axis arm hanging from a telescopic Z mast on a gantry carriage. `tip` = tool centre point, `approach` = tool
    axis (unit, pointing from robot to work). tool: nutrunner | gripper | vacuum. Industrial yellow, chipped."""
    m = mats(); Y, steel, dark, rub = m['yellow'], m['steel'], m['anod'], m['rubber']
    C = Vector(carriage); tip = Vector(tip); ap = Vector(approach).normalized()
    L1, L2 = reach
    W = tip - ap * (tool_len + 0.09)
    z_base = min(CEIL - 0.45, max(W.z + 0.95, 1.05))
    B = Vector((C.x, C.y, z_base)); S = B - Vector((0, 0, 0.42))
    parts = []
    # carriage + mast (three telescoping stages)
    parts.append(box(f'{name}-carriage', (0.42, 0.50, 0.16), C + Vector((0, 0, 0.0)), steel_or(m), bevel=0.01))
    stages = [(0.20, 0.20), (0.16, 0.16), (0.125, 0.125)]
    top = C.z - 0.08; span = top - (B.z + 0.06)
    for k, (w, d_) in enumerate(stages):
        z0 = top - span * k / 3 - 0.05 * k; z1 = top - span * (k + 1) / 3 - 0.05 * k - 0.12
        if k == 2: z1 = B.z + 0.06
        parts.append(props.beam(f'{name}-mast{k}', (C.x, C.y, z0), (C.x, C.y, z1), w, d_, m['alu'] if k else steel_or(m), bevel=0.006))
    parts.append(lib.beveled_cyl(f'{name}-base', 0.17, 0.08, loc=B + Vector((0, 0, 0.02)), bevel=0.008, mat=Y))
    yaw_v = Vector((W.x - S.x, W.y - S.y, 0)); r = yaw_v.length or 1e-6; yaw_v.normalize()
    zr = W.z - S.z; dd = min(math.hypot(r, zr), L1 + L2 - 1e-3)
    a2 = math.acos(np.clip((L1 ** 2 + L2 ** 2 - dd ** 2) / (2 * L1 * L2), -1, 1))
    a1 = math.atan2(zr, r) - math.acos(np.clip((L1 ** 2 + dd ** 2 - L2 ** 2) / (2 * L1 * dd), -1, 1))   # elbow down-out
    E = S + yaw_v * (L1 * math.cos(a1)) + Vector((0, 0, L1 * math.sin(a1)))
    if E.z > S.z:                                    # prefer elbow below the shoulder for a hanging arm
        a1 = math.atan2(zr, r) + math.acos(np.clip((L1 ** 2 + dd ** 2 - L2 ** 2) / (2 * L1 * dd), -1, 1))
        E = S + yaw_v * (L1 * math.cos(a1)) + Vector((0, 0, L1 * math.sin(a1)))
    side = Vector((-yaw_v.y, yaw_v.x, 0))
    parts.append(props.cyl(f'{name}-turret', B, S + Vector((0, 0, 0.06)), 0.14, Y, bevel=0.012))
    parts.append(props.cyl(f'{name}-shoulder', S - side * 0.13, S + side * 0.13, 0.12, Y, bevel=0.01))
    parts.append(props.beam(f'{name}-lower_arm', S + side * 0.08, E + side * 0.08, 0.10, 0.16, Y, bevel=0.016))
    parts.append(props.cyl(f'{name}-elbow', E - side * 0.05, E + side * 0.16, 0.095, Y, bevel=0.008))
    parts.append(props.cyl(f'{name}-motor_a3', E + side * 0.16, E + side * 0.27, 0.055, dark, bevel=0.005))
    parts.append(props.beam(f'{name}-upper_arm', E, W, 0.11, 0.10, Y, bevel=0.014))
    parts.append(props.cyl(f'{name}-wrist_a4', W - (W - E).normalized() * 0.04, W + ap * 0.03, 0.06, Y, bevel=0.006))
    parts.append(props.cyl(f'{name}-wrist_a5', W - side * 0.055, W + side * 0.055, 0.05, dark, bevel=0.005))
    F0 = W + ap * 0.05; F1 = W + ap * 0.09
    parts.append(props.cyl(f'{name}-flange', F0, F1, 0.042, steel, bevel=0.003))
    parts.append(props.cyl(f'{name}-tool_changer', F1, F1 + ap * 0.03, 0.046, m['alu'], bevel=0.003))
    T0 = F1 + ap * 0.03
    if tool == 'nutrunner':
        T1 = T0 + ap * 0.12; T2 = T1 + ap * 0.06
        parts.append(props.cyl(f'{name}-nr_motor', T0, T1, 0.028, dark, bevel=0.004))
        parts.append(props.cyl(f'{name}-nr_transducer', T1, T1 + ap * 0.018, 0.031, steel, bevel=0.002))
        parts.append(props.cyl(f'{name}-nr_gear', T1 + ap * 0.018, T2, 0.022, dark, bevel=0.003))
        parts.append(props.cyl(f'{name}-nr_socket', T2, tip, 0.006, steel, bevel=0.001, verts=6))
    elif tool == 'gripper':
        Tb = T0 + ap * 0.07
        parts.append(props.cyl(f'{name}-gr_body', T0, Tb, 0.045, dark, bevel=0.004))
        q = side
        for s_ in (-1, 1):
            a_ = Tb + q * s_ * 0.035; b_ = tip + q * s_ * 0.03
            parts.append(props.beam(f'{name}-gr_finger', a_, b_, 0.018, 0.03, steel, bevel=0.003))
    elif tool == 'vacuum':
        Tb = T0 + ap * 0.05
        parts.append(props.cyl(f'{name}-vac_body', T0, Tb, 0.035, dark, bevel=0.003))
        up_ = (W - E).normalized().cross(ap).normalized()
        frame = props.beam(f'{name}-vac_frame', Tb - side * 0.12, Tb + side * 0.12, 0.022, 0.022, m['alu'], bevel=0.003); parts.append(frame)
        for s_ in (-1, 1):
            for t_ in (-1, 1):
                c0 = Tb + side * s_ * 0.10 + up_ * t_ * 0.06
                parts.append(props.cyl(f'{name}-vac_cup', c0, c0 + ap * (tip - Tb).length, 0.016, rub, bevel=0.002))
    # dress pack: cable from the carriage down the mast and along the arm
    parts.append(props.cable(f'{name}-dress', [C + Vector((0.16, 0.18, -0.05)), B + Vector((0.14, 0.16, 0.2)), S + side * 0.18 + Vector((0, 0, 0.05)),
                                               E + Vector((0, 0, 0.09)), W + Vector((0, 0, 0.08)), T0 + Vector((0, 0, 0.03))], 0.012, rub))
    return parts, dict(B=B, S=S, E=E, W=W)


def steel_or(m):
    return m['steel_paint']


# ---------------------------------------------------------------- the cell
def build(blueprint_img=os.path.join(ROOT, 'docs', 'brief', 'reference-drawing-mk1.webp'), screens_dir=None, periphery=True, umbilical_to=None):
    m = mats(); objs = []
    # floor + markings
    bpy.ops.mesh.primitive_plane_add(size=24, location=(0, 0, 0)); fl = bpy.context.active_object; fl.name = 'ENV-floor'; fl.data.materials.append(m['floor'])
    for (x0, y0, x1, y1) in ((-2.6, -2.6, 2.6, -2.55), (-2.6, 2.55, 2.6, 2.6), (-2.6, -2.6, -2.55, 2.6), (2.55, -2.6, 2.6, 2.6)):
        objs.append(box('ENV-floor_line', (abs(x1 - x0), abs(y1 - y0), 0.002), ((x0 + x1) / 2, (y0 + y1) / 2, 0.001), m['yellow_mark'], bevel=0.0))
    for k in range(12):                                   # walkway hatch at the front edge
        objs.append(box('ENV-hatch', (0.06, 0.32, 0.002), (-1.4 + k * 0.25, -2.9, 0.001), m['yellow_mark'], rot=(0, 0, 0.6), bevel=0.0))
    # plinth
    objs.append(lib.beveled_cyl('ENV-plinth', 0.72, 0.10, loc=(0, 0, 0.05), bevel=0.006, mat=m['steel_paint'], verts=96))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.70, minor_radius=0.012, location=(0, 0, 0.1)); t = bpy.context.active_object; t.name = 'ENV-plinth_led'; t.data.materials.append(m['led_cool']); objs.append(t)
    bpy.ops.mesh.primitive_circle_add(vertices=96, radius=0.66, fill_type='NOTHING', location=(0, 0, 0.1005))
    ring = bpy.context.active_object; ring.name = 'ENV-plinth_hazard'
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.extrude_region_shrink_fatten(TRANSFORM_OT_shrink_fatten={'value': 0.05}); bpy.ops.object.mode_set(mode='OBJECT')
    ring.data.materials.append(m['hazard']); objs.append(ring)
    for sx in (-1, 1):                                    # foot plates
        objs.append(box('ENV-foot_plate', (0.14, 0.30, 0.006), (sx * 0.19, 0.0, 0.103), m['galv'], bevel=0.003))
    for a in range(0, 360, 15):                           # degree ticks
        r0 = 0.52 if a % 45 else 0.48
        x, y = math.sin(math.radians(a)), -math.cos(math.radians(a))
        objs.append(box('ENV-tick', (0.006, 0.6 - r0 + 0.0, 0.001), (x * (r0 + 0.6) / 2, y * (r0 + 0.6) / 2, 0.1005), m['white_mark'], rot=(0, 0, -math.radians(a)), bevel=0.0))
    # ceiling grid
    for y in (-1.6, -0.55, 0.55, 1.6):
        objs.append(props.beam('ENV-ibeam', (-3.4, y, CEIL), (3.4, y, CEIL), 0.16, 0.30, m['steel_paint'], bevel=0.004))
    for x in (-2.7, 2.7):
        objs.append(props.beam('ENV-ibeam_x', (x, -2.4, CEIL + 0.02), (x, 2.4, CEIL + 0.02), 0.18, 0.34, m['steel_paint'], bevel=0.004))
    # gantry rails + energy chains
    for x in (-1.05, 1.05):
        objs.append(props.beam('ENV-gantry_rail', (x, -2.3, CEIL - 0.24), (x, 2.3, CEIL - 0.24), 0.14, 0.20, m['alu'], bevel=0.006))
        objs.append(props.beam('ENV-rail_track', (x, -2.3, CEIL - 0.345), (x, 2.3, CEIL - 0.345), 0.05, 0.012, m['steel'], bevel=0.002))
        objs.append(props.beam('ENV-chain_tray', (x + 0.22 * np.sign(x), -2.3, CEIL - 0.20), (x + 0.22 * np.sign(x), 2.3, CEIL - 0.20), 0.13, 0.08, m['galv'], bevel=0.003))
        n_links = 80
        for k in range(n_links):
            yy = -2.25 + k * 0.056
            objs.append(box('ENV-chain_link', (0.09, 0.05, 0.05), (x + 0.22 * np.sign(x), yy, CEIL - 0.16), m['chain'], bevel=0.006))
    # cable trays with bundles
    for x in (-2.2, 2.2, 0.0):
        objs.append(props.beam('ENV-cable_tray', (x, -2.4, CEIL - 0.42), (x, 2.4, CEIL - 0.42), 0.30, 0.06, m['galv'], bevel=0.003))
        for k in range(10):                               # rungs
            objs.append(box('ENV-tray_rung', (0.30, 0.02, 0.01), (x, -2.2 + k * 0.48, CEIL - 0.45), m['galv'], bevel=0.002))
        for c in range(18):
            off = (c % 6 - 2.5) * 0.04; zz = CEIL - 0.39 + (c // 6) * 0.025
            mat = m['cable_org'] if c == 7 else (m['cable_gry'] if c % 4 == 0 else m['cable_blk'])
            pts = [(x + off, -2.4, zz), (x + off + RNG.normal(0, 0.004), -0.8, zz + 0.006), (x + off, 0.8, zz), (x + off, 2.4, zz)]
            objs.append(props.cable('ENV-cable', pts, 0.008 + 0.004 * (c % 3), mat))
    # festoon loops from the central tray down to the umbilical balancer
    objs.append(props.cyl('ENV-duct', (-3.4, 1.15, CEIL - 0.55), (3.4, 1.15, CEIL - 0.55), 0.16, m['galv'], bevel=0.002, verts=40))
    for x in (-2.0, -0.7, 0.7, 2.0):
        objs.append(lib.beveled_cyl('ENV-diffuser', 0.13, 0.05, loc=(x, 1.15, CEIL - 0.73), bevel=0.01, mat=m['galv']))
    # LED line lights between the beams (the cell's main light when powered)
    for y in (-1.07, 0.0, 1.07):
        for x in (-1.6, 1.6):
            objs.append(box('ENV-led_line', (1.6, 0.06, 0.03), (x, y, CEIL - 0.18), m['led'], bevel=0.004))
    # scanner ring (retracted)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.95, minor_radius=0.035, location=(0, 0, CEIL - 0.85), major_segments=96)
    sr = bpy.context.active_object; sr.name = 'ENV-scanner_ring'; sr.data.materials.append(m['alu']); objs.append(sr)
    for a in range(0, 360, 30):
        x, y = 0.95 * math.cos(math.radians(a)), 0.95 * math.sin(math.radians(a))
        objs.append(box('ENV-scan_head', (0.06, 0.08, 0.10), (x, y, CEIL - 0.92), m['anod'], rot=(0, 0, math.radians(a)), bevel=0.006))
        objs.append(props.cyl('ENV-scan_lens', (x * 0.97, y * 0.97, CEIL - 0.95), (x * 0.94, y * 0.94, CEIL - 0.97), 0.014, m['glass'], bevel=0.001))
    for a in (45, 135, 225, 315):
        x, y = 0.95 * math.cos(math.radians(a)), 0.95 * math.sin(math.radians(a))
        objs.append(props.cyl('ENV-scan_hanger', (x, y, CEIL - 0.84), (x, y, CEIL - 0.42), 0.008, m['steel'], bevel=0.001))
    # umbilical balancer + bundle down to the wearer (optional)
    objs.append(lib.beveled_cyl('ENV-balancer', 0.09, 0.14, loc=(0, 0.75, CEIL - 0.62), rot=(math.pi / 2, 0, 0), bevel=0.01, mat=m['anod']))
    if umbilical_to is not None:
        a = Vector((0, 0.75, CEIL - 0.70)); b = Vector(umbilical_to)
        mid = a.lerp(b, 0.5) + Vector((0, 0.35, 0.0))
        objs.append(props.cable('ENV-umbilical', [a, a.lerp(mid, 0.5) + Vector((0, 0.05, 0)), mid, mid.lerp(b, 0.6) + Vector((0, 0.12, 0)), b], 0.022, m['cable_blk']))
        objs.append(props.cable('ENV-umbilical_cool_a', [a + Vector((0.03, 0, 0)), mid + Vector((0.04, 0, 0)), b + Vector((0.02, 0, 0.02))], 0.006, m['glass']))
    # ceiling hoist + cameras
    objs.append(box('ENV-hoist', (0.25, 0.3, 0.35), (-2.2, -1.6, CEIL - 0.35), m['yellow'], bevel=0.02))
    for k in range(10):
        objs.append(lib.beveled_cyl('ENV-hoist_chain', 0.012, 0.03, loc=(-2.2, -1.6, CEIL - 0.56 - k * 0.032), bevel=0.003, mat=m['steel']))
    for (x, y) in ((-2.6, -2.2), (2.6, -2.2), (-2.6, 2.2), (2.6, 2.2)):
        objs.append(box('ENV-camera', (0.12, 0.18, 0.09), (x, y, CEIL - 0.3), m['anod'], rot=(0.5, 0, 0), bevel=0.01))
    if periphery:
        objs += periphery_build(m, blueprint_img, screens_dir)
    return objs


def periphery_build(m, blueprint_img, screens_dir):
    objs = []
    # workbench (left, -x)
    bx, by = -2.55, -0.3
    objs.append(box('ENV-bench_top', (0.80, 2.0, 0.04), (bx, by, 0.90), m['esd'], bevel=0.004))
    for sx in (-1, 1):
        for sy in (-1, 1):
            objs.append(props.beam('ENV-bench_leg', (bx + sx * 0.36, by + sy * 0.95, 0.0), (bx + sx * 0.36, by + sy * 0.95, 0.88), 0.05, 0.05, m['steel_paint'], bevel=0.004))
    objs.append(box('ENV-bench_shelf', (0.78, 1.96, 0.025), (bx, by, 0.25), m['steel_paint'], bevel=0.004))
    # tool wall
    objs.append(box('ENV-pegboard', (0.02, 2.0, 1.1), (bx - 0.40, by, 1.62), m['steel_paint'], bevel=0.003))
    for k in range(16):                                   # hanging tools: wrenches / drivers
        yy = by - 0.9 + k * 0.12; L = 0.16 + 0.05 * (k % 4)
        objs.append(box('ENV-tool', (0.012, 0.022, L), (bx - 0.37, yy, 1.75 - L / 2 + 0.05 * (k % 2)), m['steel'], bevel=0.003))
    for k in range(8):
        objs.append(props.cyl('ENV-driver', (bx - 0.36, by - 0.8 + k * 0.08, 1.30), (bx - 0.36, by - 0.8 + k * 0.08, 1.12), 0.012, m['anod'], bevel=0.002))
    # bench items: torque tool case, parts organiser, laptop, oscilloscope, lamp
    objs.append(box('ENV-tool_case', (0.40, 0.55, 0.09), (bx + 0.05, by - 0.55, 0.965), m['anod'], bevel=0.01))
    for i in range(6):
        for j in range(4):
            objs.append(box('ENV-bin', (0.075, 0.055, 0.035), (bx + 0.25 - j * 0.08, by + 0.2 + i * 0.06, 0.94), m['cable_gry'], bevel=0.004))
    objs.append(box('ENV-scope', (0.28, 0.32, 0.17), (bx + 0.12, by + 0.72, 1.005), m['cable_gry'], bevel=0.01))
    objs.append(box('ENV-laptop_base', (0.24, 0.34, 0.015), (bx + 0.12, by - 0.05, 0.928), m['anod'], bevel=0.004))
    lap = box('ENV-laptop_lid', (0.012, 0.34, 0.23), (bx - 0.005, by - 0.05, 1.04), m['anod'], rot=(0, -0.25, 0), bevel=0.004); objs.append(lap)
    objs.append(props.cyl('ENV-lamp_arm', (bx + 0.3, by + 0.95, 0.92), (bx + 0.2, by + 0.75, 1.40), 0.008, m['anod']))
    objs.append(props.cyl('ENV-lamp_arm2', (bx + 0.2, by + 0.75, 1.40), (bx + 0.05, by + 0.55, 1.25), 0.008, m['anod']))
    objs.append(lib.beveled_cyl('ENV-lamp_head', 0.05, 0.03, loc=(bx + 0.05, by + 0.55, 1.23), bevel=0.004, mat=m['lamp']))
    bpy.ops.object.light_add(type='SPOT', location=(bx + 0.05, by + 0.55, 1.21)); L = bpy.context.active_object; L.name = 'L-desk_lamp'
    L.data.energy = 25; L.data.color = (1.0, 0.82, 0.62); L.data.spot_size = math.radians(70); L.data.shadow_soft_size = 0.03
    # kitting carts (right, +x) - the modules ride here pre-assembled (filled by assembly.kits())
    for k, cy in enumerate((-0.9, 0.35)):
        cx = 2.45
        objs.append(box('ENV-cart_top', (0.70, 1.0, 0.03), (cx, cy, 0.86), m['steel_paint'], bevel=0.004))
        objs.append(box('ENV-cart_foam', (0.66, 0.96, 0.05), (cx, cy, 0.90), m['foam'], bevel=0.004))
        objs.append(box('ENV-cart_shelf', (0.70, 1.0, 0.03), (cx, cy, 0.30), m['steel_paint'], bevel=0.004))
        objs.append(box('ENV-cart_foam2', (0.66, 0.96, 0.05), (cx, cy, 0.34), m['foam'], bevel=0.004))
        for sx in (-1, 1):
            for sy in (-1, 1):
                objs.append(props.beam('ENV-cart_post', (cx + sx * 0.33, cy + sy * 0.48, 0.12), (cx + sx * 0.33, cy + sy * 0.48, 0.86), 0.03, 0.03, m['steel_paint'], bevel=0.003))
                objs.append(lib.beveled_cyl('ENV-caster', 0.05, 0.035, loc=(cx + sx * 0.30, cy + sy * 0.44, 0.05), rot=(0, math.pi / 2, 0), bevel=0.006, mat=m['rubber']))
        objs.append(props.cyl('ENV-cart_handle', (cx - 0.36, cy - 0.45, 0.95), (cx - 0.36, cy + 0.45, 0.95), 0.012, m['steel']))
    # panel rack (back right): titanium panels hanging on rails, waiting to be installed
    rx, ry = 1.9, 2.2
    objs.append(props.beam('ENV-rack_top', (rx - 0.9, ry, 1.95), (rx + 0.9, ry, 1.95), 0.04, 0.04, m['steel_paint'], bevel=0.004))
    for sx in (-1, 1):
        objs.append(props.beam('ENV-rack_post', (rx + sx * 0.9, ry, 0.0), (rx + sx * 0.9, ry, 1.95), 0.04, 0.04, m['steel_paint'], bevel=0.004))
    ti_panel = lib.materials()['ti']
    for k in range(16):                                   # blueprint panels hanging in sets, waiting for the vacuum gripper
        x = rx - 0.82 + k * 0.105; h = 0.18 + 0.12 * ((k * 7) % 5) / 4; w = 0.07 + 0.03 * ((k * 3) % 4) / 3
        objs.append(props.cyl('ENV-rack_hook', (x, ry, 1.95), (x, ry, 1.88), 0.003, m['steel'], bevel=0.0005))
        objs.append(box('ENV-rack_panel', (w, 0.004, h), (x, ry - 0.01, 1.86 - h / 2), ti_panel, rot=(0.08, 0, 0.05 * ((k % 3) - 1)), bevel=0.0015))
    # light table with Doha's blueprint (back left)
    lx, ly = -1.6, 2.35
    objs.append(box('ENV-lighttable', (1.25, 0.06, 0.85), (lx, ly, 1.35), m['anod'], rot=(0.2, 0, 0), bevel=0.01))
    if blueprint_img and os.path.exists(blueprint_img):
        objs.append(image_plane('ENV-blueprint_sheet', blueprint_img, 0.56, (lx, ly - 0.04, 1.36), (math.pi / 2 + 0.2, 0, 0), emit=1.6, rough=0.6))
    for sx in (-1, 1):
        objs.append(props.beam('ENV-lt_leg', (lx + sx * 0.55, ly + 0.08, 0.0), (lx + sx * 0.55, ly - 0.02, 0.95), 0.04, 0.04, m['steel_paint']))
    # monitor wall (back centre)
    if screens_dir:
        imgs = screens(screens_dir)
        for k, p in enumerate(imgs):
            x = -0.25 + (k - 1) * 0.70
            objs.append(box('ENV-monitor', (0.66, 0.05, 0.40), (x, 2.55, 1.75), m['anod'], bevel=0.008))
            objs.append(image_plane(f'ENV-screen_{k}', p, 0.62, (x, 2.52, 1.75), (math.pi / 2, 0, 0), emit=2.2, rough=0.25))
        objs.append(props.beam('ENV-monitor_post', (-0.25, 2.6, 0.0), (-0.25, 2.6, 1.6), 0.08, 0.08, m['steel_paint']))
    # flight cases, extinguisher, light-curtain posts, shelving
    for k, (x, y, s) in enumerate(((2.9, 1.5, 0.5), (2.9, 1.5, 0.5), (3.0, -2.0, 0.6))):
        objs.append(box('ENV-flightcase', (s, s * 0.7, 0.42), (x, y, 0.21 + 0.42 * (k == 1)), m['anod'], bevel=0.02))
    objs.append(props.cyl('ENV-extinguisher', (-3.0, 1.9, 0.0), (-3.0, 1.9, 0.55), 0.08, m['red'], bevel=0.02))
    for x in (-2.75, 2.75):
        objs.append(props.beam('ENV-light_curtain', (x, -2.6, 0.0), (x, -2.6, 1.6), 0.05, 0.05, m['yellow'], bevel=0.005))
    objs.append(box('ENV-shelving', (0.45, 1.6, 2.0), (-3.2, 1.3, 1.0), m['steel_paint'], bevel=0.005))
    for k in range(4):
        for j in range(5):
            objs.append(box('ENV-shelf_bin', (0.35, 0.26, 0.18), (-3.12, 0.66 + j * 0.31, 0.25 + k * 0.48), m['cable_gry'], bevel=0.01))
    return objs
