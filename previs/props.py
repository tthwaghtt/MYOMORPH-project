"""Previs props for the styleframes: industrial 6-axis robot arm with nutrunner (assembly cell, PLAN 4.2 / 07),
and blockout internals (OS frame, hydraulic cylinders, HPU, battery modules, cables) for the X-ray frames.
Throwaway geometry for mood frames; the production parts library is MYOFORGE §7.4 (P4)."""
import math
import numpy as np
import bpy
from mathutils import Vector, Matrix
import lib


def _orient(o, a, b, up=(0, 0, 1)):
    """Place object o (built along local +Z, centred) between points a and b, local X kept horizontal."""
    a, b = Vector(a), Vector(b); d = (b - a)
    z = d.normalized(); x = Vector(up).cross(z)
    if x.length < 1e-6:
        x = Vector((1, 0, 0))
    x.normalize(); y = z.cross(x)
    o.matrix_world = Matrix.Translation((a + b) / 2) @ Matrix((x, y, z)).transposed().to_4x4()


def beam(name, a, b, w, h, mat, bevel=0.012):
    L = (Vector(b) - Vector(a)).length
    o = lib.beveled_box(name, (w, h, L), bevel=bevel, mat=mat)
    _orient(o, a, b)
    return o


def cyl(name, a, b, r, mat, bevel=0.004, verts=48):
    L = (Vector(b) - Vector(a)).length
    o = lib.beveled_cyl(name, r, L, bevel=bevel, mat=mat, verts=verts)
    _orient(o, a, b)
    return o


def cable(name, pts, r, mat):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 4
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


def robot_arm(base, tip, approach, name='ROB', reach=(0.78, 0.72), tool_len=0.26):
    """6-axis arm on the floor at `base`, nutrunner socket at `tip` pointing along `approach` (unit vector).
    Two-link IK in the vertical plane through the base yaw, elbow up. Industrial yellow, chipped where it gets hit."""
    M = lib.materials(); Y, steel, dark, rub = M['yellow'], M['steel'], M['anod'], M['rubber']
    base = Vector(base); tip = Vector(tip); ap = Vector(approach).normalized()
    L1, L2 = reach
    S = base + Vector((0, 0, 0.62))
    W = tip - ap * (tool_len + 0.10)
    yaw_v = Vector((W.x - S.x, W.y - S.y, 0)); r = yaw_v.length; yaw_v.normalize()
    zr = W.z - S.z; d = math.hypot(r, zr)
    d = min(d, L1 + L2 - 1e-3)
    a2 = math.acos(np.clip((L1 ** 2 + L2 ** 2 - d ** 2) / (2 * L1 * L2), -1, 1))
    a1 = math.atan2(zr, r) + math.acos(np.clip((L1 ** 2 + d ** 2 - L2 ** 2) / (2 * L1 * d), -1, 1))
    E = S + yaw_v * (L1 * math.cos(a1)) + Vector((0, 0, L1 * math.sin(a1)))
    parts = []
    parts.append(lib.beveled_cyl(f'{name}-base', 0.24, 0.10, loc=base + Vector((0, 0, 0.05)), bevel=0.01, mat=Y))
    parts.append(lib.beveled_cyl(f'{name}-base_plate', 0.30, 0.025, loc=base + Vector((0, 0, 0.0125)), bevel=0.004, mat=dark))
    parts.append(cyl(f'{name}-turret', base + Vector((0, 0, 0.10)), base + Vector((0, 0, 0.42)), 0.19, Y, bevel=0.015))
    side = Vector((-yaw_v.y, yaw_v.x, 0))
    parts.append(cyl(f'{name}-shoulder', S - side * 0.17, S + side * 0.17, 0.16, Y, bevel=0.012))
    parts.append(beam(f'{name}-column', base + Vector((0, 0, 0.40)), S, 0.30, 0.26, Y, bevel=0.03))
    parts.append(beam(f'{name}-lower_arm', S + side * 0.10, E + side * 0.10, 0.12, 0.20, Y, bevel=0.02))
    parts.append(cyl(f'{name}-elbow', E - side * 0.06, E + side * 0.20, 0.12, Y, bevel=0.01))
    parts.append(beam(f'{name}-upper_arm', E, W, 0.14, 0.13, Y, bevel=0.018))
    parts.append(cyl(f'{name}-motor_a3', E + side * 0.20, E + side * 0.34, 0.07, dark, bevel=0.006))
    parts.append(cyl(f'{name}-wrist_a4', W - (W - E).normalized() * 0.05, W + ap * 0.04, 0.075, Y, bevel=0.008))
    parts.append(cyl(f'{name}-wrist_a5', W - side * 0.07, W + side * 0.07, 0.06, dark, bevel=0.006))
    F0 = W + ap * 0.06; F1 = W + ap * 0.10
    parts.append(cyl(f'{name}-flange', F0, F1, 0.05, steel, bevel=0.003))
    # nutrunner: angle-free inline tool, motor body + gearbox + torque transducer + socket
    T0 = F1; T1 = T0 + ap * 0.14; T2 = T1 + ap * 0.07; T3 = tip
    parts.append(cyl(f'{name}-nr_motor', T0, T1, 0.032, dark, bevel=0.004))
    parts.append(cyl(f'{name}-nr_transducer', T1, T1 + ap * 0.02, 0.036, steel, bevel=0.002))
    parts.append(cyl(f'{name}-nr_gear', T1 + ap * 0.02, T2, 0.026, dark, bevel=0.003))
    parts.append(cyl(f'{name}-nr_socket', T2, T3, 0.009, steel, bevel=0.001, verts=6))
    parts.append(cable(f'{name}-cable', [base + Vector((0.12, -0.18, 0.08)), S + Vector((0, 0, 0.16)) - side * 0.18,
                                         E + Vector((0, 0, 0.14)), W + Vector((0, 0, 0.10)), T0 + Vector((0, 0, 0.04))], 0.011, rub))
    return parts, dict(S=S, E=E, W=W)


def internals(J, lift=0.0, scale_r=1.0):
    """Blockout of the load path and actuators along Doha's skeleton (joint centres from the fitted body)."""
    M = lib.materials(); ti, steel, dark, tin = M['ti_jc'], M['steel'], M['anod'], M['tin']
    up = Vector((0, 0, lift))
    P = lambda k: Vector(J[k]) + up
    parts = []
    for s in ('l', 'r'):
        sh, el, wr = P(f'joint-{s}-shoulder'), P(f'joint-{s}-elbow'), P(f'joint-{s}-hand')
        hp, kn, an = P(f'joint-{s}-upper-leg'), P(f'joint-{s}-knee'), P(f'joint-{s}-ankle')
        sx = 1 if s == 'l' else -1
        lat = Vector((sx * 0.045, 0, 0))
        # OS frame: twin titanium tubes along each long bone, LPBF nodes at the joints
        for a, b, r in ((sh, el, 0.009), (el, wr, 0.008), (hp, kn, 0.012), (kn, an, 0.011)):
            o = Vector((sx * 0.02, 0.015, 0)); parts += [cyl('OS-tube', a + o, b + o, r * scale_r, ti), cyl('OS-tube', a - o, b - o, r * scale_r, ti)]
        for c, r in ((sh, 0.05), (el, 0.038), (wr, 0.028), (hp, 0.055), (kn, 0.048), (an, 0.04)):
            parts.append(cyl('OS-node', c - Vector((sx * 0.03, 0, 0)), c + Vector((sx * 0.03, 0, 0)), r * scale_r, ti, bevel=0.006))
            parts.append(cyl('OS-bearing', c - Vector((sx * 0.034, 0, 0)), c + Vector((sx * 0.034, 0, 0)), r * 0.55 * scale_r, steel, bevel=0.002))
        # MUSCULUS: hydraulic cylinders where the human muscle is (biceps -> elbow, quadriceps -> knee, calf -> ankle)
        fr = Vector((0, -0.055, 0)); bk = Vector((0, 0.06, 0))
        for a, b, rb, rr in ((sh.lerp(el, 0.18) + fr, el.lerp(wr, 0.12) + fr * 0.8, 0.017, 0.008),
                             (hp.lerp(kn, 0.15) + fr * 1.4, kn.lerp(an, 0.1) + fr * 1.2, 0.022, 0.011),
                             (kn.lerp(an, 0.12) + bk, an + bk * 0.9 + Vector((0, 0, -0.03)), 0.02, 0.01)):
            mid = a.lerp(b, 0.55)
            parts.append(cyl('MUS-barrel', a, mid, rb * scale_r, dark, bevel=0.003))
            parts.append(cyl('MUS-rod', mid, b, rr * scale_r, tin, bevel=0.0015))
            parts.append(cyl('MUS-gland', mid - (mid - a).normalized() * 0.012, mid + (b - a).normalized() * 0.006, rb * 1.12 * scale_r, steel, bevel=0.002))
    # spine and pelvis frame, HPU at the sacrum, battery modules under the latissimus panels
    neck, sp1, pel = P('joint-neck'), P('joint-spine-1'), P('joint-pelvis')
    back = Vector((0, 0.10, 0))
    parts.append(cyl('OS-spine', neck + back * 0.9, pel + back * 1.1, 0.014, ti))
    parts.append(beam('OS-pelvis_ring', P('joint-r-upper-leg') + back * 0.6, P('joint-l-upper-leg') + back * 0.6, 0.05, 0.04, ti, bevel=0.008))
    parts.append(beam('OS-shoulder_yoke', P('joint-r-shoulder') + back * 0.55, P('joint-l-shoulder') + back * 0.55, 0.045, 0.04, ti, bevel=0.008))
    hpu = pel + back * 1.45 + Vector((0, 0, 0.05))
    parts.append(lib.beveled_box('COR-HPU', (0.20, 0.07, 0.14), loc=hpu, bevel=0.01, mat=dark))
    parts.append(cyl('COR-pump_motor', hpu + Vector((-0.10, 0.0, 0.0)), hpu + Vector((-0.02, 0, 0)), 0.035, steel))
    parts.append(cyl('COR-accumulator', hpu + Vector((0.03, 0.0, 0.07)), hpu + Vector((0.03, 0.0, 0.18)), 0.03, tin))
    for sx in (-1, 1):
        parts.append(lib.beveled_box('ENERGIA-battery', (0.09, 0.03, 0.20), loc=sp1 + Vector((sx * 0.11, 0.115, -0.10)), bevel=0.006, mat=dark))
    return parts
