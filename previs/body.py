"""Wearer body model, bpy-free: MakeHuman/MPFB2 base mesh (CC0) + shape targets, posing, ANSUR-style measurement.

Coordinates: the OBJ is Y-up/+Z-front in decimetres; world output is Blender Z-up, -Y front, metres, feet on z=0.
Shape  = base + asian-male-young (race macro, Doha is Korean) + universal muscle/weight blend + signed sliders.
Pose   = arms rotated about the shoulder in the frontal plane, forearm chain about the elbow (skin weights).
Measure: definitions follow ANSUR II (Gordon et al. 2014) where a surface mesh allows; see MEASURES.
"""
import gzip, json, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(HERE, 'vendor', 'mpfb')
TDIR = os.path.join(VENDOR, 'targets')


class Base:
    _inst = None

    @classmethod
    def get(cls):
        if cls._inst is None:
            cls._inst = cls()
        return cls._inst

    def __init__(self):
        v, groups, faces, cur = [], {}, [], None
        for line in open(os.path.join(VENDOR, 'base.obj')):
            if line.startswith('v '):
                v.append([float(x) for x in line.split()[1:4]])
            elif line.startswith('g '):
                cur = line.split()[1]
            elif line.startswith('f '):
                idx = [int(x.split('/')[0]) - 1 for x in line.split()[1:]]
                groups.setdefault(cur, set()).update(idx)
                if cur == 'body':
                    faces.append(idx)
        self.v0 = np.array(v)
        self.groups = {k: np.array(sorted(s)) for k, s in groups.items()}
        self.body = self.groups['body']
        self.remap = -np.ones(len(self.v0), np.int64); self.remap[self.body] = np.arange(len(self.body))
        self.faces_full = faces
        self.faces = [[int(self.remap[i]) for i in f] for f in faces]
        A = np.load(os.path.join(VENDOR, 'arm_weights.npz'))
        self.arm_w = {'l': A['L'], 'r': A['R']}
        D = np.load(os.path.join(VENDOR, 'body_weights.npz'))
        W = D['W'].astype(np.float32); names = [str(n) for n in D['names']]
        self.bone_names = names; self.Wbody = W
        self.fore_w = {}
        for side, S in (('l', 'L'), ('r', 'R')):
            cols = [i for i, n in enumerate(names) if n.endswith('.' + S) and n.split('.')[0].rstrip('0123456789-')
                    in ('lowerarm', 'wrist', 'metacarpal', 'finger')]
            w = np.zeros(len(self.v0)); w[self.body] = np.clip(W[:, cols].sum(1), 0, 1)
            for g, ix in self.groups.items():          # rig joint helpers of the hand follow the forearm rigidly
                if g.startswith(f'joint-{side}-hand') or g.startswith(f'joint-{side}-finger'):
                    w[ix] = 1.0
            self.fore_w[side] = w
        self._t = {}
        self.catalog = self._catalog()

    def _catalog(self):
        """Slider name -> (negative targets, positive targets), from MPFB2 target.json."""
        cat = {}
        tj = json.load(open(os.path.join(VENDOR, 'target.json')))
        for g, grp in tj.items():
            for c in grp['categories']:
                o = c.get('opposites', {})
                neg = [o.get('negative-left'), o.get('negative-right')] if c.get('has_left_and_right') else [o.get('negative-unsided')]
                pos = [o.get('positive-left'), o.get('positive-right')] if c.get('has_left_and_right') else [o.get('positive-unsided')]
                cat[c['name']] = (g, [n for n in neg if n], [p for p in pos if p])
        return cat

    def target(self, name, group=None):
        if name not in self._t:
            cands = [os.path.join(TDIR, group or '', name + '.target.gz'), os.path.join(TDIR, name + '.target.gz'),
                     os.path.join(VENDOR, name + '.target.gz')]
            path = next((p for p in cands if os.path.exists(p)), None)
            if path is None:
                for g in os.listdir(TDIR):
                    p = os.path.join(TDIR, g, name + '.target.gz')
                    if os.path.exists(p):
                        path = p; break
            if path is None:
                raise FileNotFoundError(name)
            idx, d = [], []
            with gzip.open(path, 'rt') as f:
                for line in f:
                    p = line.split()
                    if len(p) == 4:
                        idx.append(int(p[0])); d.append([float(x) for x in p[1:]])
            self._t[name] = (np.array(idx, dtype=np.int64), np.array(d, dtype=float).reshape(-1, 3))
        return self._t[name]


# universal macro corners present in vendor/ (muscle: average->max, weight: average->min)
def macro_weights(muscle, weight):
    return {'universal-male-young-averagemuscle-averageweight': (1 - muscle) * (1 - weight),
            'universal-male-young-averagemuscle-minweight': (1 - muscle) * weight,
            'universal-male-young-maxmuscle-averageweight': muscle * (1 - weight),
            'universal-male-young-maxmuscle-minweight': muscle * weight}


def shape(params, B=None):
    """params: {'macro': {'muscle': m, 'weight': w, 'asian': a}, 'sliders': {slider: s in [-1,1]}, 'targets': {name: w}}"""
    B = B or Base.get()
    v = B.v0.copy()
    mac = params.get('macro', {})
    tw = dict(macro_weights(mac.get('muscle', 0.5), mac.get('weight', 0.0)))
    if mac.get('asian', 1.0):
        tw['asian-male-young'] = mac.get('asian', 1.0)
    for sl, s in params.get('sliders', {}).items():
        g, neg, pos = B.catalog[sl]
        for t in (pos if s > 0 else neg):
            tw[t] = tw.get(t, 0) + abs(s)
    for t, w in params.get('targets', {}).items():
        tw[t] = tw.get(t, 0) + w
    for t, w in tw.items():
        if w:
            idx, d = B.target(t)
            v[idx] += w * d
    return v


def joints(v, B=None):
    B = B or Base.get()
    return {g: v[ix].mean(0) for g, ix in B.groups.items() if g.startswith('joint-')}


def _rot_frontal(v, J, side, target_deg, w):
    """OBJ space: rotate about the shoulder joint in the x-y (frontal) plane so the upper arm is target_deg from vertical."""
    sh, el = J[f'joint-{side}-shoulder'], J[f'joint-{side}-elbow']
    cur = math.degrees(math.atan2(abs(el[0] - sh[0]), sh[1] - el[1]))
    sgn = 1 if side == 'l' else -1
    a = -math.radians(cur - target_deg) * sgn * w
    c, s_ = np.cos(a), np.sin(a)
    x, y = v[:, 0] - sh[0], v[:, 1] - sh[1]
    out = v.copy(); out[:, 0] = sh[0] + x * c - y * s_; out[:, 1] = sh[1] + x * s_ + y * c
    return out


def _rodrigues(P, k, a):
    a = np.broadcast_to(a, (len(P),))
    return (P * np.cos(a)[:, None] + np.cross(k, P) * np.sin(a)[:, None] + np.outer(P @ k, k) * (1 - np.cos(a))[:, None])


def pose(v, arm_deg=17.0, elbow_deg=8.0, B=None):
    """Arms to arm_deg from vertical (frontal plane), elbows to elbow_deg flexion. Returns posed verts and joints."""
    B = B or Base.get()
    J = joints(v, B)
    for side in ('l', 'r'):
        v = _rot_frontal(v, J, side, arm_deg, B.arm_w[side])
        J = joints(v, B)
        if elbow_deg is not None:
            sh, el, wr = J[f'joint-{side}-shoulder'], J[f'joint-{side}-elbow'], J[f'joint-{side}-hand']
            u, f = el - sh, wr - el
            flex = math.degrees(math.acos(np.clip(np.dot(u, f) / np.linalg.norm(u) / np.linalg.norm(f), -1, 1)))
            k = np.cross(u, f); nk = np.linalg.norm(k)
            if nk > 1e-9 and abs(flex - elbow_deg) > 0.01:
                k /= nk
                v = el + _rodrigues(v - el, k, -math.radians(flex - elbow_deg) * B.fore_w[side])
            J = joints(v, B)
    return v, J


def to_world(v, J, height_m=1.78, B=None):
    """OBJ -> Blender world, feet on the floor, body scaled to stature height_m. Returns full-mesh verts, joints, scale."""
    B = B or Base.get()
    conv = lambda a: np.stack([a[..., 0], -a[..., 2], a[..., 1]], -1)
    vb = conv(v); zb = vb[B.body, 2]
    zmin, zmax = zb.min(), zb.max()
    s = height_m / (zmax - zmin)
    vb = (vb - [0, 0, zmin]) * s
    Jw = {k: (conv(j) - [0, 0, zmin]) * s for k, j in J.items()}
    return vb, Jw, s


# ---------------------------------------------------------------- measurement (ANSUR II style)
def hull_perimeter(P):
    P = np.unique(np.round(P, 5), axis=0)
    if len(P) < 3:
        return 0.0
    P = P[np.lexsort((P[:, 1], P[:, 0]))]
    cross = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in P:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in P[::-1]:
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    H = np.array(lo[:-1] + up[:-1])
    return float(np.linalg.norm(H - np.roll(H, -1, 0), axis=1).sum())


def plane_section(V, E, origin, normal, sel=None):
    """Points where mesh edges cross the plane (exact section polygon points). E: (m,2) edge array."""
    d = (V - origin) @ normal
    a, b = E[:, 0], E[:, 1]
    m = (d[a] * d[b]) < 0
    if sel is not None:
        m &= sel[a] & sel[b]
    t = d[a[m]] / (d[a[m]] - d[b[m]])
    return V[a[m]] + (V[b[m]] - V[a[m]]) * t[:, None]


def girth(V, E, origin, normal, sel=None):
    P = plane_section(V, E, origin, normal, sel)
    if len(P) < 3:
        return 0.0, P
    n = normal / np.linalg.norm(normal)
    u = np.cross(n, [0, 0, 1.0]) if abs(n[2]) < 0.9 else np.cross(n, [1.0, 0, 0])
    u /= np.linalg.norm(u); w = np.cross(n, u)
    return hull_perimeter(np.stack([(P - origin) @ u, (P - origin) @ w], 1)), P


# ---------------------------------------------------------------- landmarks
class Landmarks:
    """Vertex-index landmarks found once by geometric rules on a reference shape (topology is fixed, so the same
    indices stay anatomically valid on every fitted shape). Left side = +X; right side is the mirror vertex."""

    def __init__(self, vw, Jw, B=None):
        B = B or Base.get(); self.B = B
        body = B.body; V = vw
        arm = np.maximum(B.arm_w['l'], B.arm_w['r'])
        isb = np.zeros(len(V), bool); isb[body] = True
        L = {}

        def pick(mask, score):
            ix = np.where(mask & isb)[0]
            return int(ix[np.argmax(score(V[ix]))])

        x, y, z = V[:, 0], V[:, 1], V[:, 2]
        mid = np.abs(x) < 0.0065
        js, je, jw = Jw['joint-l-shoulder'], Jw['joint-l-elbow'], Jw['joint-l-hand']
        # acromion: lateral acromial edge, ~2.5 cm lateral of and above the glenohumeral centre (rig joint)
        L['acromion'] = pick((np.abs(y - js[1]) < 0.025) & (x > js[0] + 0.018) & (x < js[0] + 0.032) & (z > js[2]), lambda P: P[:, 2])
        fa = (jw - je) / np.linalg.norm(jw - je)
        lat = np.array([1.0, 0, 0]) - fa[0] * fa; lat /= np.linalg.norm(lat)
        L['radiale'] = pick((np.linalg.norm(V - je, axis=1) < 0.06) & (z < je[2] + 0.005) & (z > je[2] - 0.03),
                            lambda P: (P - je) @ lat)
        th = Jw['joint-l-finger-1-1'] - jw; th = th - th.dot(fa) * fa; th /= np.linalg.norm(th)
        L['stylion'] = pick((np.linalg.norm(V - jw, axis=1) < 0.045) & (np.abs((V - jw) @ fa) < 0.015), lambda P: (P - jw) @ th)
        names = B.bone_names
        f3 = np.zeros(len(V)); f3[body] = B.Wbody[:, names.index('finger3-3.L')]
        L['dactylion'] = pick(f3 > 0.5, lambda P: (P - jw) @ fa)
        jn, jcl = Jw['joint-neck'], Jw['joint-l-clavicle']
        # C7 sits at the neck01 rig joint level on the posterior midline; the jugular notch ~1 cm above the
        # sternoclavicular joints on the anterior midline (ANSUR: cervicale - suprasternale ~ 80 mm, matches the rig)
        L['cervicale'] = pick(mid & (y > jn[1]), lambda P: -np.abs(P[:, 2] - (jn[2] + 0.005)))
        L['suprasternale'] = pick(mid & (y < jcl[1] - 0.01), lambda P: -np.abs(P[:, 2] - (jcl[2] + 0.008)) - 0.3 * np.maximum(0, P[:, 1] - jcl[1]))
        L['thelion'] = pick((x > 0.06) & (x < 0.14) & (z > 1.22) & (z < 1.40) & (arm < 0.2), lambda P: -P[:, 1])
        jp = Jw['joint-pelvis']
        L['omphalion'] = pick(mid & (z > 0.97) & (z < 1.16) & (y < jp[1] - 0.05), lambda P: P[:, 1])
        jh = Jw['joint-l-upper-leg']
        L['trochanterion'] = pick((np.abs(z - jh[2]) < 0.06) & (arm < 0.1) & (x > 0), lambda P: P[:, 0])
        L['crotch'] = pick(mid & (z > 0.6) & (z < 1.0) & (y > jp[1] - 0.03) & (arm < 0.1), lambda P: -P[:, 2])
        jk, ja = Jw['joint-l-knee'], Jw['joint-l-ankle']
        L['patella'] = pick((np.linalg.norm(V - jk, axis=1) < 0.08) & (np.abs(z - jk[2]) < 0.03), lambda P: -P[:, 1])
        L['femoral_epicondyle'] = pick((np.linalg.norm(V - jk, axis=1) < 0.07) & (np.abs(z - jk[2]) < 0.02), lambda P: P[:, 0])
        L['malleolus'] = pick((np.linalg.norm(V - ja, axis=1) < 0.06) & (z > ja[2] - 0.025) & (z < ja[2] + 0.03), lambda P: P[:, 0])
        foot = (z < 0.06) & (x > 0.05)
        L['pternion'] = pick(foot, lambda P: P[:, 1]); L['acropodion'] = pick(foot, lambda P: -P[:, 1])
        L['vertex'] = pick(np.ones(len(V), bool), lambda P: P[:, 2])
        self.idx = L
        # mirror partners for sided landmarks
        self.mirror = {}
        bv = V[body]
        for k in ('acromion', 'radiale', 'stylion', 'dactylion', 'thelion', 'trochanterion', 'patella',
                  'femoral_epicondyle', 'malleolus', 'pternion', 'acropodion'):
            p = V[L[k]] * [-1, 1, 1]
            self.mirror[k] = int(body[np.argmin(np.linalg.norm(bv - p, axis=1))])

    def p(self, V, k, side='l'):
        return V[self.idx[k]] if side == 'l' or k not in self.mirror else V[self.mirror[k]]

    def save(self, path):
        json.dump({'idx': self.idx, 'mirror': self.mirror}, open(path, 'w'), indent=1)

    @classmethod
    def load(cls, path, B=None):
        o = cls.__new__(cls); d = json.load(open(path)); o.B = B or Base.get()
        o.idx = {k: int(v) for k, v in d['idx'].items()}; o.mirror = {k: int(v) for k, v in d['mirror'].items()}
        return o


def edges(B=None):
    B = B or Base.get()
    E = set()
    for f in B.faces_full:
        for i in range(len(f)):
            a, b = f[i], f[(i + 1) % len(f)]
            E.add((min(a, b), max(a, b)))
    return np.array(sorted(E))


def region_masks(B=None):
    B = B or Base.get(); n = len(B.v0); names = B.bone_names
    def wsum(stems, side):
        cols = [i for i, nm in enumerate(names) if nm.endswith('.' + side) and nm.split('.')[0].rstrip('0123456789-') in stems]
        w = np.zeros(n); w[B.body] = B.Wbody[:, cols].sum(1); return w
    m = {}
    for s, S in (('l', 'L'), ('r', 'R')):
        m['leg_' + s] = wsum(('upperleg', 'lowerleg', 'foot', 'toe'), S) > 0.5
        m['arm_' + s] = B.arm_w[s] > 0.5
        m['ua_' + s] = wsum(('upperarm', 'shoulder'), S) > 0.4
        m['fa_' + s] = wsum(('lowerarm', 'wrist'), S) > 0.4
    isb = np.zeros(n, bool); isb[B.body] = True
    arm = np.maximum(B.arm_w['l'], B.arm_w['r'])
    m['torso'] = isb & (arm < 0.2) & ~m['leg_l'] & ~m['leg_r']
    limb = np.zeros(n)
    for S in ('L', 'R'):
        limb = np.maximum(limb, wsum(('upperarm', 'lowerarm', 'wrist', 'metacarpal', 'finger'), S))
    m['torso_chest'] = isb & (limb < 0.5) & ~m['leg_l'] & ~m['leg_r']      # keeps lats and axillary folds (tape passes over them)
    m['torso_legs'] = isb & (arm < 0.2)
    m['body'] = isb
    return m


RULERS = {   # MakeHuman measurement plugin vertex loops (hm08 topology)
    'neck': [7514, 10358, 7631, 7496, 7488, 7489, 7474, 7475, 7531, 7537, 7543, 7549, 7555, 7561, 7743, 7722, 856, 1030, 1051,
             850, 844, 838, 832, 826, 820, 756, 755, 770, 769, 777, 929, 3690, 804, 800, 808, 801, 799, 803, 7513, 7515, 7521, 7514]}


def measure(V, J, LM, E, M, Vt=None, Jt=None):
    """ANSUR-style measurements in mm. V/J: measurement pose (arms ~6°, elbows 5°). Vt/Jt: T-pose for span."""
    P = lambda k, s='l': LM.p(V, k, s)
    out = {}
    out['stature'] = (V[LM.B.body, 2].max() - V[LM.B.body, 2].min())
    for k, nm in (('acromion', 'acromialheight'), ('suprasternale', 'suprasternaleheight'), ('cervicale', 'cervicaleheight'),
                  ('thelion', 'chestheight'), ('omphalion', 'waistheightomphalion'), ('trochanterion', 'trochanterionheight'),
                  ('crotch', 'crotchheight'), ('patella', 'kneeheightmidpatella'), ('femoral_epicondyle', 'lateralfemoralepicondyleheight'),
                  ('malleolus', 'lateralmalleolusheight'), ('stylion', 'wristheight')):
        out[nm] = P(k)[2]
    out['biacromialbreadth'] = abs(P('acromion')[0] - P('acromion', 'r')[0])
    za = P('acromion')[2]; b = M['body']
    band = b & (V[:, 2] < za - 0.02) & (V[:, 2] > za - 0.16)
    out['bideltoidbreadth'] = V[band, 0].max() - V[band, 0].min()
    up = np.array([0, 0, 1.0])
    zc = P('thelion')[2]; tor = M['torso']
    g, S = girth(V, E, np.array([0, 0, zc]), up, M['torso_chest']); out['chestcircumference'] = g
    out['chestbreadth'] = S[:, 0].max() - S[:, 0].min(); out['chestdepth'] = S[:, 1].max() - S[:, 1].min()
    zw = P('omphalion')[2]
    g, S = girth(V, E, np.array([0, 0, zw]), up, tor); out['waistcircumference'] = g
    out['waistbreadth'] = S[:, 0].max() - S[:, 0].min(); out['waistdepth'] = S[:, 1].max() - S[:, 1].min()
    # buttock: level of maximum posterior protrusion between crotch and omphalion
    tl = M['torso_legs']
    zr = (V[:, 2] > P('crotch')[2]) & (V[:, 2] < zw) & tl & (np.abs(V[:, 0]) < 0.12)
    zb = V[zr][np.argmax(V[zr][:, 1]), 2]; out['buttockheight'] = zb
    g, S = girth(V, E, np.array([0, 0, zb]), up, tl); out['buttockcircumference'] = g; out['buttockdepth'] = S[:, 1].max() - S[:, 1].min()
    hz = tl & (V[:, 2] > P('crotch')[2] - 0.06) & (V[:, 2] < zw - 0.04)
    out['hipbreadth'] = V[hz, 0].max() - V[hz, 0].min()
    # neck: MakeHuman ruler loop; neck base: plane through cervicale and suprasternale, containing X
    R = V[RULERS['neck']]; out['neckcircumference'] = float(np.linalg.norm(np.diff(R, axis=0), axis=1).sum())
    c7, ss = P('cervicale'), P('suprasternale'); dv = c7 - ss; nb = np.cross([1.0, 0, 0], dv); nb /= np.linalg.norm(nb)
    g, S = girth(V, E, (c7 + ss) / 2, nb, b & (np.maximum(LM.B.arm_w['l'], LM.B.arm_w['r']) < 0.35)); out['neckcircumferencebase'] = g
    # thigh (gluteal furrow ~ crotch level), lower thigh (just above patella), calf (max), ankle (min): perpendicular to segment
    jh, jk, ja = J['joint-l-upper-leg'], J['joint-l-knee'], J['joint-l-ankle']
    def on_axis(a, bb, zz):
        t = (zz - a[2]) / (bb[2] - a[2]); return a + t * (bb - a), (bb - a) / np.linalg.norm(bb - a)
    o, n = on_axis(jh, jk, P('crotch')[2] - 0.012); out['thighcircumference'] = girth(V, E, o, n, M['leg_l'])[0]
    o, n = on_axis(jh, jk, P('patella')[2] + 0.045); out['lowerthighcircumference'] = girth(V, E, o, n, M['leg_l'])[0]
    zs = np.linspace(jk[2] - 0.06, jk[2] - 0.22, 17)
    out['calfcircumference'] = max(girth(V, E, *on_axis(jk, ja, zz), M['leg_l'])[0] for zz in zs)
    zs = np.linspace(P('malleolus')[2] + 0.035, P('malleolus')[2] + 0.15, 13)
    out['anklecircumference'] = min(girth(V, E, *on_axis(jk, ja, zz), M['leg_l'])[0] for zz in zs)
    # arm: relaxed mid upper-arm girth (NHANES BMXARMC), forearm max, wrist; segment lengths
    js_, je, jw = J['joint-l-shoulder'], J['joint-l-elbow'], J['joint-l-hand']
    zmid = (P('acromion')[2] + (je[2] - 0.02)) / 2
    o, n = on_axis(js_, je, zmid); out['armcircumference_relaxed'] = girth(V, E, o, n, M['ua_l'] & M['arm_l'])[0]
    zs = np.linspace(je[2] - 0.03, je[2] - 0.11, 9)
    out['forearmcircumference_relaxed'] = max(girth(V, E, *on_axis(je, jw, zz), M['fa_l'])[0] for zz in zs)
    o, n = on_axis(je, jw, P('stylion')[2]); out['wristcircumference'] = girth(V, E, o, n, M['arm_l'])[0]
    out['acromionradialelength'] = np.linalg.norm(P('acromion') - P('radiale'))
    out['radialestylionlength'] = np.linalg.norm(P('radiale') - P('stylion'))
    ulna_side = jw - (P('stylion') - jw)
    out['handlength'] = np.linalg.norm(P('dactylion') - (P('stylion') + ulna_side) / 2)
    out['footlength'] = np.linalg.norm((P('pternion') - P('acropodion'))[:2])
    fz = M['leg_l'] & (V[:, 2] < 0.08); out['footbreadthhorizontal'] = V[fz, 0].max() - V[fz, 0].min()
    hv = V[LM.idx['vertex'], 2]
    head = b & (V[:, 2] > hv - 0.115)
    best = 0
    for zz in np.linspace(hv - 0.105, hv - 0.065, 9):
        gg, S = girth(V, E, np.array([0, 0, zz]), up, head)
        if gg > best: best, SS = gg, S
    out['headcircumference'] = best; out['headbreadth'] = SS[:, 0].max() - SS[:, 0].min(); out['headlength'] = SS[:, 1].max() - SS[:, 1].min()
    if Vt is not None:
        out['span'] = abs(LM.p(Vt, 'dactylion')[0] - LM.p(Vt, 'dactylion', 'r')[0])
    return {k: float(v) * 1000 for k, v in out.items()}
