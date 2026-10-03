"""Doha's functional undersuit (NEURAL WEAR): racing-suit outside, sensing and cooling inside.

Sensor sites come from the muscle research: each EMG site follows the SENIAM placement rule for that muscle (Hermens
et al. 2000, seniam.org) evaluated on Doha's fitted mannequin landmarks; HD grids (32 ch, 4 x 8, 10 mm) sit on the
twelve prime movers of the actuated joints, bipolar pairs on eight more. EEG: 32 dry electrodes of the 10-10 system
(sensorimotor-weighted) on the balaclava. Cooling garment: vertical tube runs every 15 mm (NASA LCVG style) over the
torso, upper arms and thighs. Output: engineering/undersuit.json; build() makes the previs objects.
Run: python undersuit.py [OUT.webp]   (writes the json; with OUT also renders a sensor-map sheet)
"""
import os, sys, json, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
FINGER = 0.018
MUS = {m['key']: m for m in json.load(open(os.path.join(ROOT, 'docs', 'research', 'corpus', 'muscles.json')))['muscles']}
TRUNK = {'TRAP': ('upper trapezius', '등세모근 위부분', 'trapezius pars descendens'), 'ES': ('erector spinae (longissimus)', '척주세움근(가장긴근)', 'erector spinae'),
         'LAT': ('latissimus dorsi', '넓은등근', 'latissimus dorsi')}

# name, muscle key, type, landmark A, landmark B, fraction from A, offset (finger widths, +lateral), facing, SENIAM / literature rule
SITES = [
    ('VL', 'vaslat', 'HD32', 'asis', 'patella_lat', 2 / 3, 0, 'lateral_front', 'SENIAM: 2/3 on the line from the anterior superior iliac spine to the lateral side of the patella'),
    ('VM', 'vasmed', 'HD32', 'asis', 'knee_med_joint', 0.80, 0, 'medial_front', 'SENIAM: 80 % on the line between the ASIS and the joint space in front of the medial ligament'),
    ('RF', 'recfem', 'HD32', 'asis', 'patella_sup', 0.50, 0, 'front', 'SENIAM: 50 % on the line from the ASIS to the superior part of the patella'),
    ('BF', 'bflh', 'HD32', 'isch', 'tib_epi_lat', 0.50, 0, 'back_lateral', 'SENIAM: 50 % on the line between the ischial tuberosity and the lateral epicondyle of the tibia'),
    ('ST', 'semiten', 'HD32', 'isch', 'tib_epi_med', 0.50, 0, 'back_medial', 'SENIAM: 50 % on the line between the ischial tuberosity and the medial epicondyle of the tibia'),
    ('GMAX', 'glmax', 'HD32', 'sacrum', 'troch', 0.50, 0, 'back', 'SENIAM: 50 % on the line between the sacral vertebrae and the greater trochanter'),
    ('GM', 'gasmed', 'HD32', 'femur_cond_med', 'heel', 0.22, 0, 'back_medial', 'SENIAM: on the most prominent bulge of the medial head'),
    ('GL', 'gaslat', 'HD32', 'fib_head', 'heel', 1 / 3, 0, 'back_lateral', 'SENIAM: 1/3 of the line between the head of the fibula and the heel'),
    ('SOL', 'soleus', 'HD32', 'femur_cond_med', 'malleolus_med', 2 / 3, 0, 'back_medial', 'SENIAM: 2/3 of the line between the medial femoral condyle and the medial malleolus'),
    ('TA', 'tibant', 'HD32', 'fib_head', 'malleolus_med', 1 / 3, 0, 'front', 'SENIAM: 1/3 on the line between the tip of the fibula and the tip of the medial malleolus'),
    ('BB', 'BIC', 'HD32', 'fossa_cubiti', 'acromion_med', 1 / 3, 0, 'front', 'SENIAM: on the line between the medial acromion and the fossa cubiti at 1/3 from the fossa cubiti'),
    ('TB', 'TRI', 'HD32', 'acromion_post', 'olecranon', 0.50, 0, 'back', 'SENIAM: 50 % on the line between the posterior crista of the acromion and the olecranon (grid spans both heads)'),
    ('DA', 'DELT1', 'BIP', 'acromion', 'fossa_cubiti', 0.12, 0, 'front', 'SENIAM: one finger width distal and anterior to the acromion'),
    ('DM', 'DELT2', 'BIP', 'acromion', 'epi_lat_h', 0.22, 0, 'lateral', 'SENIAM: on the line acromion - lateral epicondyle, at the greatest bulge'),
    ('TRAP', 'TRAP', 'BIP', 'acromion', 'c7', 0.50, 0, 'top_back', 'SENIAM: 50 % on the line from the acromion to the spine of C7'),
    ('PM', 'PECM', 'BIP', 'thelion', 'axilla_front', 0.45, 0, 'front', 'literature: sternal head, between the nipple and the anterior axillary fold'),
    ('LD', 'LAT', 'BIP', 'scap_inf', 'flank_back', 0.45, 0, 'back', 'literature: ~4 cm below the inferior angle of the scapula, midway to the lateral border'),
    ('ES', 'ES', 'BIP', 'l1', 'l1_lat', 1.0, 0, 'back', 'SENIAM: two finger widths lateral to the spinous process of L1'),
    ('FCR', 'FCR', 'BIP', 'epi_med_h', 'styloid_rad', 0.30, 0, 'front', 'literature: proximal third of the line medial epicondyle - radial styloid'),
    ('ECR', 'ECR', 'BIP', 'epi_lat_h', 'styloid_rad', 0.22, 0, 'lateral_back', 'literature: proximal fifth of the line lateral epicondyle - radial styloid'),
]
# EEG 10-10 subset: name, theta from Cz (deg), phi from nasion direction (deg, + = wearer left)
EEG = [('Fp1', 72, 18), ('Fp2', 72, -18), ('F7', 72, 54), ('F3', 48, 40), ('Fz', 36, 0), ('F4', 48, -40), ('F8', 72, -54),
       ('FC5', 58, 72), ('FC3', 40, 63), ('FC1', 22, 45), ('FCz', 18, 0), ('FC2', 22, -45), ('FC4', 40, -63), ('FC6', 58, -72),
       ('T7', 72, 90), ('C5', 54, 90), ('C3', 36, 90), ('C1', 18, 90), ('Cz', 0, 0), ('C2', 18, -90), ('C4', 36, -90), ('C6', 54, -90),
       ('T8', 72, -90), ('CP5', 58, 108), ('CP3', 40, 117), ('CP1', 22, 135), ('CPz', 18, 180), ('CP2', 22, -135), ('CP4', 40, -117),
       ('CP6', 58, -108), ('Pz', 36, 180), ('Oz', 72, 180)]


def normals(V, F):
    tri = []
    for f in F:
        for k in range(1, len(f) - 1):
            tri.append((f[0], f[k], f[k + 1]))
    tri = np.array(tri)
    n = np.cross(V[tri[:, 1]] - V[tri[:, 0]], V[tri[:, 2]] - V[tri[:, 0]])
    N = np.zeros_like(V)
    for k in range(3):
        np.add.at(N, tri[:, k], n)
    return N / (np.linalg.norm(N, axis=1, keepdims=True) + 1e-12), tri


class Anat:
    """Landmarks on the posed wearer (world m). Left = +X; right = mirrored rules."""

    def __init__(self, V, F, J, B, LM, headw=None, armw=None, legw=None):
        self.V, self.F, self.J, self.B, self.LM = V, F, J, B, LM
        self.N, self.tri = normals(V, F)
        self.armw, self.legw, self.headw = armw, legw, headw
        self.cache = {}

    def lm(self, k, side):
        i = self.LM.idx[k] if side == 'L' or k not in self.LM.mirror else self.LM.mirror[k]
        return self.V[self.B.remap[i]]

    def snap(self, p, d, radius=0.06, mask=None):
        """nearest skin vertex to p among those whose normal faces d"""
        d = np.asarray(d, float); d /= np.linalg.norm(d)
        m = (self.N @ d > 0.25) & (np.linalg.norm(self.V - p, axis=1) < radius)
        if mask is not None: m &= mask
        ix = np.where(m)[0]
        if not len(ix):
            ix = np.where(np.linalg.norm(self.V - p, axis=1) < radius * 2)[0]
        r = self.V[ix] - p
        score = np.linalg.norm(r, axis=1) - 0.5 * (r @ d)
        return int(ix[np.argmin(score)])

    def ray(self, c, d, mask=None):
        """outermost skin vertex along the ray from c (inside the body) in direction d (tube of growing radius)"""
        d = np.asarray(d, float); d /= np.linalg.norm(d)
        r = self.V - c; proj = r @ d; perp = np.linalg.norm(r - np.outer(proj, d), axis=1)
        for tol in (0.006, 0.010, 0.016, 0.025, 0.04):
            m = (proj > 0) & (perp < tol)
            if mask is not None: m &= mask
            ix = np.where(m)[0]
            if len(ix): return int(ix[np.argmax(proj[ix])])
        raise ValueError('ray found no skin')

    def p(self, name, side):
        key = (name, side)
        if key in self.cache: return self.cache[key]
        s = 1 if side == 'L' else -1; sd = side.lower(); J = self.J
        V = self.V
        lm = lambda k: self.lm(k, side)
        knee, ankle, elbow, wrist, sh = J[f'joint-{sd}-knee'], J[f'joint-{sd}-ankle'], J[f'joint-{sd}-elbow'], J[f'joint-{sd}-hand'], J[f'joint-{sd}-shoulder']
        troch_z = lm('trochanterion')[2]; omph = self.lm('omphalion', 'L'); crotch = self.lm('crotch', 'L')
        legm = self.legw[sd] > 0.5 if self.legw is not None else None
        armm = self.armw[sd] > 0.5 if self.armw is not None else None
        tor = None
        if self.legw is not None:
            tor = (self.legw['l'] < 0.5) & (self.legw['r'] < 0.5) & (self.armw['l'] < 0.5) & (self.armw['r'] < 0.5) & (self.headw < 0.5)
        fa = (wrist - elbow) / np.linalg.norm(wrist - elbow)
        out = np.array([s, 0, 0.0]); out -= out.dot(fa) * fa; out /= np.linalg.norm(out)
        ant = np.array([0, -1.0, 0]); ant -= ant.dot(fa) * fa; ant /= np.linalg.norm(ant)
        ua = (elbow - sh) / np.linalg.norm(elbow - sh)
        ant_u = np.array([0, -1.0, 0]); ant_u -= ant_u.dot(ua) * ua; ant_u /= np.linalg.norm(ant_u)
        rule = {
            'asis': lambda: V[self.snap(np.array([s * 0.105, omph[1] + 0.02, troch_z + 0.085]), (s * 0.5, -0.86, 0), mask=tor)],
            'patella_lat': lambda: V[self.snap(lm('patella') + [s * 0.035, 0.01, 0.0], (s * 0.6, -0.8, 0), mask=legm)],
            'patella_sup': lambda: V[self.snap(lm('patella') + [0, 0, 0.035], (0, -1, 0), mask=legm)],
            'knee_med_joint': lambda: V[self.ray(knee, (-s * 0.75, -0.66, 0), mask=legm)],
            'isch': lambda: V[self.snap(np.array([s * 0.055, omph[1] + 0.13, crotch[2] + 0.035]), (0, 1, -0.3), mask=tor | legm if tor is not None else None)],
            'tib_epi_lat': lambda: V[self.ray(knee - [0, 0, 0.015], (s, 0.25, 0), mask=legm)],
            'tib_epi_med': lambda: V[self.ray(knee - [0, 0, 0.015], (-s, 0.25, 0), mask=legm)],
            'fib_head': lambda: V[self.ray(knee - [0, 0, 0.055], (s * 0.8, 0.6, 0), mask=legm)],
            'femur_cond_med': lambda: V[self.ray(knee + [0, 0, 0.01], (-s * 0.8, 0.6, 0), mask=legm)],
            'malleolus_med': lambda: V[self.ray(ankle, (-s, 0, 0), mask=legm)],
            'heel': lambda: lm('pternion'),
            'troch': lambda: lm('trochanterion'),
            'sacrum': lambda: V[self.ray(np.array([0, omph[1] + 0.06, troch_z + 0.07]), (0, 1, 0), mask=tor)],
            'acromion': lambda: lm('acromion'),
            'acromion_post': lambda: V[self.snap(lm('acromion') + [-s * 0.005, 0.03, -0.012], (0, 1, 0.3))],
            'acromion_med': lambda: V[self.snap(lm('acromion') + [-s * 0.025, -0.01, 0.0], (0, -0.3, 1))],
            'fossa_cubiti': lambda: V[self.ray(elbow, ant_u, mask=armm)],
            'olecranon': lambda: V[self.ray(elbow, -ant_u, mask=armm)],
            'epi_lat_h': lambda: lm('radiale'),
            'epi_med_h': lambda: V[self.ray(elbow, -out, mask=armm)],
            'styloid_rad': lambda: lm('stylion'),
            'c7': lambda: self.lm('cervicale', 'L'),
            'thelion': lambda: lm('thelion'),
            'axilla_front': lambda: V[self.snap(sh + [-s * 0.035, -0.06, -0.10], (0, -1, 0), mask=tor)],
            'scap_inf': lambda: V[self.ray(np.array([s * 0.085, sh[1], sh[2] - 0.17]), (0, 1, 0), mask=tor)],
            'flank_back': lambda: V[self.ray(np.array([s * 0.10, sh[1], sh[2] - 0.24]), (s * 0.7, 0.7, 0), mask=tor)],
            'l1': lambda: V[self.ray(np.array([0, omph[1] + 0.06, omph[2] + 0.10]), (0, 1, 0), mask=tor)],
            'l1_lat': lambda: V[self.ray(np.array([s * 2 * FINGER, omph[1] + 0.06, omph[2] + 0.10]), (0, 1, 0), mask=tor)],
        }
        v = np.array(rule[name](), float)
        self.cache[key] = v
        return v

    def facing(self, f, side, seg_axis=None):
        s = 1 if side == 'L' else -1
        return {'front': (0, -1, 0), 'back': (0, 1, 0), 'lateral': (s, 0, 0), 'medial': (-s, 0, 0), 'top_back': (0, 0.5, 0.86),
                'lateral_front': (s * 0.6, -0.8, 0), 'medial_front': (-s * 0.6, -0.8, 0), 'back_lateral': (s * 0.6, 0.8, 0),
                'back_medial': (-s * 0.6, 0.8, 0), 'lateral_back': (s * 0.7, 0.7, 0)}[f]


def sites(an):
    out = []
    for side in ('L', 'R'):
        for name, key, typ, a, b, f, off, fc, rule in SITES:
            A, Bp = an.p(a, side), an.p(b, side)
            q = A + f * (Bp - A)
            d = np.array(an.facing(fc, side), float)
            i = an.snap(q, d, radius=0.08)
            pos = an.V[i]; n = an.N[i]
            ax = Bp - A; ax -= ax.dot(n) * n; ax /= np.linalg.norm(ax) + 1e-12
            if key in MUS:
                mm = MUS[key]; info = {'latin': mm['latin'], 'en': mm['en'], 'ko': mm['ko'], 'fmax_N': mm['fmax_N'],
                                       'fibre_length_cm': mm['fibre_length_cm'], 'pennation_deg': mm['pennation_deg'], 'volume_cm3': mm['volume_cm3_per_side']}
            else:
                en, ko, la = TRUNK.get(key, (key, key, key)); info = {'latin': la, 'en': en, 'ko': ko}
            out.append({'site': f'{name}-{side}', 'muscle': key, 'type': typ, 'channels': 32 if typ == 'HD32' else 1,
                        'size_mm': [80, 40] if typ == 'HD32' else [40, 18], 'rule': rule, 'pos_m': [round(float(x), 4) for x in pos],
                        'normal': [round(float(x), 3) for x in n], 'fibre_axis': [round(float(x), 3) for x in ax], **info, 'vi': i})
    return out


def eeg(an):
    hv = np.where(an.headw > 0.5)[0]
    H = an.V[hv]
    top = H[:, 2].max()
    c = np.array([0.0, 0.5 * (H[:, 1].min() + H[:, 1].max()) + 0.005, top - 0.105])
    msk = an.headw > 0.5
    res = []
    for nm, th, ph in EEG:
        t, p = math.radians(th), math.radians(ph)
        d = np.array([math.sin(t) * math.sin(p), -math.sin(t) * math.cos(p), math.cos(t)])
        i = an.ray(c, d, mask=msk)
        res.append({'name': nm, 'theta': th, 'phi': ph, 'pos_m': [round(float(x), 4) for x in an.V[i]], 'normal': [round(float(x), 3) for x in an.N[i]], 'vi': int(i)})
    return res


def nodes_for(S):
    """group sensor sites into 64-ch nodes: two HD grids per node on the same segment, bipolars shared."""
    groups = {}
    seg = {'VL': 'thigh_f', 'VM': 'thigh_f', 'RF': 'thigh_f2', 'BF': 'thigh_b', 'ST': 'thigh_b', 'GMAX': 'glute', 'GM': 'calf', 'GL': 'calf',
           'SOL': 'calf2', 'TA': 'calf2', 'BB': 'arm', 'TB': 'arm', 'DA': 'shoulder', 'DM': 'shoulder', 'TRAP': 'shoulder',
           'PM': 'chest', 'LD': 'back', 'ES': 'back', 'FCR': 'fore', 'ECR': 'fore'}
    for s in S:
        nm, side = s['site'].split('-')
        groups.setdefault((seg[nm], side), []).append(s)
    nodes = []
    for (g, side), lst in groups.items():
        P = np.array([x['pos_m'] for x in lst]).mean(0)
        nodes.append({'node': f'N-{g}-{side}', 'sites': [x['site'] for x in lst], 'channels': sum(x['channels'] for x in lst), 'pos_m': [round(float(v), 4) for v in P]})
    return nodes


def wearer(arm_deg=17.0, elbow_deg=8.0):
    import body, lib
    V, F, J = lib.load_wearer(arm_deg=arm_deg, elbow_deg=elbow_deg)
    B = body.Base.get(); LM = body.Landmarks.load(os.path.join(body.VENDOR, 'landmarks.json'))
    W = B.Wbody; names = B.bone_names
    wsum = lambda stems, side=None: np.clip(W[:, [i for i, n in enumerate(names) if n.split('.')[0].rstrip('0123456789-') in stems
                                                 and (side is None or n.endswith('.' + side))]].sum(1), 0, 1)
    headw = wsum(('head', 'jaw', 'eye', 'levator', 'oculi', 'orbicularis', 'oris', 'risorius', 'special', 'temporalis', 'tongue'))
    M = body.region_masks(B)
    legw = {'l': M['leg_l'][B.body].astype(float), 'r': M['leg_r'][B.body].astype(float)}
    armw = {'l': B.arm_w['l'][B.body], 'r': B.arm_w['r'][B.body]}
    return V, F, J, B, LM, Anat(V, F, J, B, LM, headw=headw, armw=armw, legw=legw)


def analyse():
    V, F, J, B, LM, an = wearer()
    S = sites(an); E = eeg(an); Nd = nodes_for(S)
    eng = json.load(open(os.path.join(ROOT, 'engineering', 'engineering.json')))
    out = {'version': 'v1 (R2, 2026-10-03)', 'method': __doc__.split('\n\n')[1].replace('\n', ' '),
           'emg_sites': S, 'emg_nodes': Nd, 'eeg': E,
           'totals': {'hd_grids': sum(s['type'] == 'HD32' for s in S), 'bipolar': sum(s['type'] == 'BIP' for s in S),
                      'emg_channels': sum(s['channels'] for s in S), 'nodes': len(Nd), 'eeg_channels': len(E)},
           'cooling_garment': {k: eng['thermal'][k] for k in ('lcg_tube_m', 'lcg_circuits', 'lcg_cover_m2', 'lcg_flow_L_min', 'lcg_dp_kPa')},
           'connectors': [{'name': 'waist L', 'carries': 'coolant supply + return (dry-break), 24-pin data', 'pos': 'left flank above the iliac crest'},
                          {'name': 'waist R', 'carries': 'coolant supply + return (dry-break), 24-pin data', 'pos': 'right flank above the iliac crest'},
                          {'name': 'nape', 'carries': 'EEG balaclava + upper-body nodes', 'pos': 'C7, under the collar'}]}
    json.dump(out, open(os.path.join(ROOT, 'engineering', 'undersuit.json'), 'w'), indent=1, ensure_ascii=False)
    print(out['totals'])
    for s in S[:20]:
        print(s['site'], s['type'], s['ko'], s['pos_m'])
    return V, F, J, an, S, E, Nd


# ---------------------------------------------------------------- previs objects
def _seam_fields(V, N, J, an):
    """racing-suit seams as distance fields (m): side seams, inseams, raglan, waist, zip, collar, cuffs; panel tone."""
    x, y, z = V[:, 0], V[:, 1], V[:, 2]
    s_ = np.sign(x + 1e-9)
    legw = np.maximum(an.legw['l'], an.legw['r']); armw = np.maximum(an.armw['l'], an.armw['r']); hw = an.headw
    tor = (legw < 0.5) & (armw < 0.5) & (hw < 0.5)
    omph = an.lm('omphalion', 'L'); sh = 0.5 * (J['joint-l-shoulder'] + J['joint-r-shoulder'])
    # torso azimuth around a vertical axis through the trunk centre
    cy = omph[1] + 0.05
    az = np.degrees(np.arctan2(np.abs(x), -(y - cy)))                          # 0 front, 90 side, 180 back
    r_t = np.hypot(x, y - cy)
    side = np.abs(az - 92) * np.pi / 180 * r_t
    inf = np.full(len(V), 9.0)
    d = inf.copy()
    d = np.where(tor & (z < sh[2] - 0.12), np.minimum(d, side), d)
    zip_ = np.where(tor & (y < cy) & (z > omph[2] - 0.20) & (z < sh[2] + 0.12), np.abs(x), inf)
    waist = np.where(tor | (legw > 0.5), np.abs(z - (omph[2] - 0.045)), inf)
    collar = np.where(z > sh[2] + 0.02, np.abs(z - (J['joint-neck'][2] - 0.01)), inf)
    # yoke: a horizontal seam across chest and back 6 cm below the shoulder joints
    rag = np.where(tor & (np.abs(x) < 0.14), np.abs(z - (sh[2] - 0.06)), inf)
    # limbs: outer and inner lines, cuffs, knee / elbow articulation patches
    limb = inf.copy(); cuffs = inf.copy(); patch = inf.copy(); stripe = inf.copy()
    for sd, sg in (('l', 1), ('r', -1)):
        for seg, (a, b, w) in {'thigh': ('upper-leg', 'knee', an.legw[sd]), 'shank': ('knee', 'ankle', an.legw[sd]),
                               'uarm': ('shoulder', 'elbow', an.armw[sd]), 'farm': ('elbow', 'hand', an.armw[sd])}.items():
            A, Bp = J[f'joint-{sd}-{a}'], J[f'joint-{sd}-{b}']
            ax = (Bp - A) / np.linalg.norm(Bp - A); t = (V - A) @ ax; rr = V - A - np.outer(t, ax)
            rad = np.linalg.norm(rr, axis=1) + 1e-9
            outd = np.array([sg, 0, 0.0]); outd -= outd.dot(ax) * ax; outd /= np.linalg.norm(outd)
            ang = np.degrees(np.arccos(np.clip((rr @ outd) / rad, -1, 1)))
            m = (w > 0.5) & (t > -0.05) & (t < np.linalg.norm(Bp - A) + 0.05)
            arc_out = np.abs(ang) * np.pi / 180 * rad
            limb = np.where(m, np.minimum(limb, np.minimum(np.abs(arc_out - 0.022), np.abs(180 - ang) * np.pi / 180 * rad)), limb)
            stripe = np.where(m, np.minimum(stripe, arc_out), stripe)
        kn, an_ = J[f'joint-{sd}-knee'], J[f'joint-{sd}-ankle']
        el, wr = J[f'joint-{sd}-elbow'], J[f'joint-{sd}-hand']
        cuffs = np.minimum(cuffs, np.where(an.legw[sd] > 0.5, np.abs(z - (an_[2] + 0.06)), inf))
        cuffs = np.minimum(cuffs, np.where(an.armw[sd] > 0.5, np.abs((V - wr) @ ((wr - el) / np.linalg.norm(wr - el)) + 0.03), inf))
        pk = an.lm('patella', 'L' if sg > 0 else 'R')
        e = np.sqrt(((x - pk[0]) / 0.055) ** 2 + ((z - pk[2]) / 0.085) ** 2)
        patch = np.minimum(patch, np.where((an.legw[sd] > 0.5) & (y < pk[1] + 0.05), np.abs(e - 1) * 0.06, inf))
    seam = np.minimum.reduce([d, waist, collar, rag, limb, cuffs, patch])
    tone = ((az > 66) & (az < 118) & tor) | (stripe < 0.022)
    rib = np.zeros(len(V))
    for sd in ('l', 'r'):
        an_, el, wr = J[f'joint-{sd}-ankle'], J[f'joint-{sd}-elbow'], J[f'joint-{sd}-hand']
        rib = np.maximum(rib, (an.legw[sd] > 0.5) & (z > an_[2] + 0.015) & (z < an_[2] + 0.06))
        u = (wr - el) / np.linalg.norm(wr - el); tt = (V - wr) @ u
        rib = np.maximum(rib, (an.armw[sd] > 0.5) & (tt > -0.03) & (tt < 0.012))
    rib = np.maximum(rib, (z > J['joint-neck'][2] - 0.01) & (z < J['joint-neck'][2] + 0.035) & (hw < 0.5))
    return seam, zip_, tone.astype(float), patch, rib.astype(float)


def knit_material(name='MAT-undersuit'):
    import bpy
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nd = nt.nodes; ln = nt.links
    p = next(n for n in nd if n.type == 'BSDF_PRINCIPLED')
    at = lambda nm: (lambda a: (setattr(a, 'attribute_name', nm), a)[1])(nd.new('ShaderNodeAttribute'))
    seam, zp, tone = at('seam'), at('zip'), at('tone')
    # base: graphite aramid knit, side panels darker; sheen for fabric
    mix = nd.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    mix.inputs[6].default_value = (0.036, 0.038, 0.042, 1); mix.inputs[7].default_value = (0.0075, 0.0078, 0.0085, 1)
    ln.new(tone.outputs['Fac'], mix.inputs[0])
    # stitch: two lines 2.5 mm each side of the seam, dashed
    tc = nd.new('ShaderNodeTexCoord'); wave = nd.new('ShaderNodeTexWave'); wave.inputs['Scale'].default_value = 260.0
    wave.wave_profile = 'SIN'; wave.inputs['Distortion'].default_value = 0.0
    ln.new(tc.outputs['Object'], wave.inputs['Vector'])
    sq = nd.new('ShaderNodeMath'); sq.operation = 'GREATER_THAN'; sq.inputs[1].default_value = 0.5
    ln.new(wave.outputs['Fac'], sq.inputs[0])
    band = nd.new('ShaderNodeMapRange'); band.inputs['From Min'].default_value = 0.0022; band.inputs['From Max'].default_value = 0.0042
    band.inputs['To Min'].default_value = 0.0; band.inputs['To Max'].default_value = 1.0; band.clamp = True
    ln.new(seam.outputs['Fac'], band.inputs['Value'])
    ring = nd.new('ShaderNodeMath'); ring.operation = 'PINGPONG'; ring.inputs[1].default_value = 0.5
    ln.new(band.outputs['Result'], ring.inputs[0])
    st = nd.new('ShaderNodeMath'); st.operation = 'GREATER_THAN'; st.inputs[1].default_value = 0.38
    ln.new(ring.outputs['Value'], st.inputs[0])
    dash = nd.new('ShaderNodeMath'); dash.operation = 'MULTIPLY'
    ln.new(st.outputs['Value'], dash.inputs[0]); ln.new(sq.outputs['Value'], dash.inputs[1])
    thread = nd.new('ShaderNodeMix'); thread.data_type = 'RGBA'; thread.inputs[7].default_value = (0.24, 0.24, 0.245, 1)
    ln.new(dash.outputs['Value'], thread.inputs[0]); ln.new(mix.outputs[2], thread.inputs[6])
    # zip: dark teeth strip 7 mm
    zr = nd.new('ShaderNodeMapRange'); zr.inputs['From Min'].default_value = 0.0035; zr.inputs['From Max'].default_value = 0.0045
    zr.inputs['To Min'].default_value = 1.0; zr.inputs['To Max'].default_value = 0.0
    ln.new(zp.outputs['Fac'], zr.inputs['Value'])
    zc = nd.new('ShaderNodeMix'); zc.data_type = 'RGBA'; zc.inputs[7].default_value = (0.010, 0.010, 0.011, 1)
    ln.new(zr.outputs['Result'], zc.inputs[0]); ln.new(thread.outputs[2], zc.inputs[6])
    gv = nd.new('ShaderNodeMapRange'); gv.inputs['From Min'].default_value = 0.0008; gv.inputs['From Max'].default_value = 0.0016
    gv.inputs['To Min'].default_value = 1.0; gv.inputs['To Max'].default_value = 0.0
    ln.new(seam.outputs['Fac'], gv.inputs['Value'])
    gc = nd.new('ShaderNodeMix'); gc.data_type = 'RGBA'; gc.inputs[7].default_value = (0.004, 0.004, 0.0045, 1)
    ln.new(gv.outputs['Result'], gc.inputs[0]); ln.new(zc.outputs[2], gc.inputs[6])
    eye = at('eyeslot')
    ec = nd.new('ShaderNodeMix'); ec.data_type = 'RGBA'; ec.inputs[7].default_value = (0.004, 0.004, 0.0045, 1)
    ln.new(eye.outputs['Fac'], ec.inputs[0]); ln.new(gc.outputs[2], ec.inputs[6])
    ln.new(ec.outputs[2], p.inputs['Base Color'])
    rr = nd.new('ShaderNodeMapRange'); rr.inputs['To Min'].default_value = 0.84; rr.inputs['To Max'].default_value = 0.30
    ln.new(eye.outputs['Fac'], rr.inputs['Value']); ln.new(rr.outputs['Result'], p.inputs['Roughness'])
    p.inputs['Sheen Weight'].default_value = 0.22; p.inputs['Sheen Roughness'].default_value = 0.5
    p.inputs['Sheen Tint'].default_value = (0.30, 0.31, 0.34, 1)
    # knit micro-relief + seam groove
    noise = nd.new('ShaderNodeTexVoronoi'); noise.inputs['Scale'].default_value = 900.0
    ln.new(tc.outputs['Object'], noise.inputs['Vector'])
    gr = nd.new('ShaderNodeMapRange'); gr.inputs['From Min'].default_value = 0.0; gr.inputs['From Max'].default_value = 0.0022
    ln.new(seam.outputs['Fac'], gr.inputs['Value'])
    hsum = nd.new('ShaderNodeMath'); hsum.operation = 'MULTIPLY_ADD'; hsum.inputs[1].default_value = 0.15
    ln.new(noise.outputs['Distance'], hsum.inputs[0]); ln.new(gr.outputs['Result'], hsum.inputs[2])
    ribA = at('rib'); rw = nd.new('ShaderNodeTexWave'); rw.wave_type = 'BANDS'; rw.bands_direction = 'Z'
    rw.inputs['Scale'].default_value = 900.0; ln.new(tc.outputs['Object'], rw.inputs['Vector'])
    rm = nd.new('ShaderNodeMath'); rm.operation = 'MULTIPLY'; ln.new(rw.outputs['Fac'], rm.inputs[0]); ln.new(ribA.outputs['Fac'], rm.inputs[1])
    hs2 = nd.new('ShaderNodeMath'); hs2.operation = 'MULTIPLY_ADD'; hs2.inputs[1].default_value = 0.6
    ln.new(rm.outputs['Value'], hs2.inputs[0]); ln.new(hsum.outputs['Value'], hs2.inputs[2]); hsum = hs2
    bump = nd.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.5; bump.inputs['Distance'].default_value = 0.0018
    ln.new(hsum.outputs['Value'], bump.inputs['Height']); ln.new(bump.outputs['Normal'], p.inputs['Normal'])
    return m


def pad_material(name='MAT-emg-pad'):
    """TPU-laminated sensor patch with the electrode grid printed through (10 mm pitch silver dots)."""
    import bpy
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nd = nt.nodes; ln = nt.links
    p = next(n for n in nd if n.type == 'BSDF_PRINCIPLED')
    tc = nd.new('ShaderNodeTexCoord'); sc = nd.new('ShaderNodeVectorMath'); sc.operation = 'SCALE'; sc.inputs['Scale'].default_value = 100.0
    ln.new(tc.outputs['Object'], sc.inputs[0])
    fr = nd.new('ShaderNodeVectorMath'); fr.operation = 'FRACTION'; ln.new(sc.outputs['Vector'], fr.inputs[0])
    off = nd.new('ShaderNodeVectorMath'); off.operation = 'SUBTRACT'; off.inputs[1].default_value = (0.5, 0.5, 0.5)
    ln.new(fr.outputs['Vector'], off.inputs[0])
    sep = nd.new('ShaderNodeSeparateXYZ'); ln.new(off.outputs['Vector'], sep.inputs[0])
    cmb = nd.new('ShaderNodeCombineXYZ'); ln.new(sep.outputs['X'], cmb.inputs['X']); ln.new(sep.outputs['Y'], cmb.inputs['Y'])
    ln_ = nd.new('ShaderNodeVectorMath'); ln_.operation = 'LENGTH'; ln.new(cmb.outputs['Vector'], ln_.inputs[0])
    dot = nd.new('ShaderNodeMath'); dot.operation = 'LESS_THAN'; dot.inputs[1].default_value = 0.17
    ln.new(ln_.outputs['Value'], dot.inputs[0])
    mix = nd.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    mix.inputs[6].default_value = (0.022, 0.023, 0.026, 1); mix.inputs[7].default_value = (0.55, 0.55, 0.56, 1)
    ln.new(dot.outputs['Value'], mix.inputs[0]); ln.new(mix.outputs[2], p.inputs['Base Color'])
    ln.new(dot.outputs['Value'], p.inputs['Metallic'])
    rr = nd.new('ShaderNodeMapRange'); rr.inputs['To Min'].default_value = 0.55; rr.inputs['To Max'].default_value = 0.3
    ln.new(dot.outputs['Value'], rr.inputs['Value']); ln.new(rr.outputs['Result'], p.inputs['Roughness'])
    return m


def _rbox(name, dims, mat, bevel=0.002):
    import bpy
    sx, sy, sz = [d / 2 for d in dims]
    v = [(-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz), (-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    me = bpy.data.meshes.new(name); me.from_pydata(v, [], f); me.update()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    bv = ob.modifiers.new('B', 'BEVEL'); bv.width = min(bevel, min(dims) * 0.45); bv.segments = 3
    for pl in me.polygons: pl.use_smooth = True
    me.materials.append(mat)
    return ob


def _place(ob, pos, n, ax):
    from mathutils import Matrix, Vector
    n = Vector(n).normalized(); u = Vector(ax); u = (u - u.dot(n) * n).normalized(); v = n.cross(u)
    M = Matrix(((u.x, v.x, n.x, pos[0]), (u.y, v.y, n.y, pos[1]), (u.z, v.z, n.z, pos[2]), (0, 0, 0, 1)))
    ob.matrix_world = M


def dress(V, F, J, an):
    """fabric over the body: socks smooth the toes, the balaclava bridges the face and ears; eye-slot field (0..1)."""
    import scipy.sparse as sp
    E = set()
    for f in F:
        for k in range(len(f)):
            a, b = f[k], f[(k + 1) % len(f)]
            if a != b: E.add((min(a, b), max(a, b)))
    E = np.array(sorted(E)); n = len(V)
    A = sp.coo_matrix((np.ones(2 * len(E)), (np.r_[E[:, 0], E[:, 1]], np.r_[E[:, 1], E[:, 0]])), shape=(n, n)).tocsr()
    deg = np.asarray(A.sum(1)).ravel()
    legw = np.maximum(an.legw['l'], an.legw['r'])
    az_ = 0.5 * (J['joint-l-ankle'][2] + J['joint-r-ankle'][2])
    wf = (legw > 0.5) * np.clip((az_ + 0.05 - V[:, 2]) / 0.04, 0, 1)
    eye_z = 0.5 * (J['joint-l-eye'][2] + J['joint-r-eye'][2]); eye_y = 0.5 * (J['joint-l-eye'][1] + J['joint-r-eye'][1])
    face = (an.headw > 0.5) & (V[:, 1] < eye_y + 0.02) & (V[:, 2] < eye_z + 0.03)
    ears = (an.headw > 0.5) & (np.abs(V[:, 0]) > 0.06) & (np.abs(V[:, 2] - (eye_z - 0.02)) < 0.05)
    mouth = (an.headw > 0.5) & (V[:, 1] < eye_y + 0.03) & (V[:, 2] < eye_z - 0.035)
    # close the mouth: cavity vertices behind the lips are pulled forward onto the lip surface
    zl = eye_z - 0.070
    cav = (an.headw > 0.5) & (np.abs(V[:, 0]) < 0.030) & (np.abs(V[:, 2] - zl) < 0.022)
    if cav.any():
        yl = np.percentile(V[cav, 1], 3) + 0.006
        V = V.copy(); V[cav, 1] = np.minimum(V[cav, 1], yl)
    wh = np.clip(face * 0.6 + ears * 0.7 + mouth * 0.3, 0, 0.8)
    V = V.copy()
    for _ in range(26):
        V = V + wh[:, None] * ((A @ V) / deg[:, None] - V)
    # eye slot: a 9 mm band across both eyes, front of the head
    ex = 0.5 * abs(J['joint-l-eye'][0] - J['joint-r-eye'][0]) + 0.026
    eyeslot = ((an.headw > 0.5) & (V[:, 1] < eye_y) & (np.abs(V[:, 0]) < ex)).astype(float)
    eyeslot *= np.clip(1 - (np.abs(V[:, 2] - eye_z) - 0.0045) / 0.0015, 0, 1)
    return V, A, eyeslot


def booties(V, F, J, an, mat):
    """integrated socks: the foot below the ankle replaced by a smoothed convex shell (the toes disappear under the knit)."""
    import bpy, lib
    from scipy.spatial import ConvexHull
    keep = np.ones(len(F), bool); obs = []
    for sd in ('l', 'r'):
        az_ = J[f'joint-{sd}-ankle'][2]
        m = (an.legw[sd] > 0.5) & (V[:, 2] < az_ + 0.015)
        ix = np.where(m)[0]
        h = ConvexHull(V[ix])
        verts = V[ix][np.unique(h.simplices)]
        remap = {old: k for k, old in enumerate(np.unique(h.simplices))}
        faces = [[remap[a] for a in f_] for f_ in h.simplices]
        # orient outward
        c = verts.mean(0)
        for f_ in faces:
            a, b, c2 = verts[f_[0]], verts[f_[1]], verts[f_[2]]
            if np.dot(np.cross(b - a, c2 - a), a - c) < 0: f_[1], f_[2] = f_[2], f_[1]
        ob = lib.mesh_object(f'GEO-bootie-{sd}', verts, faces, subsurf=2)
        ob.data.materials.append(mat)
        for nm_ in ('seam', 'zip', 'tone', 'eyeslot', 'rib'):
            a = ob.data.attributes.new(nm_, 'FLOAT', 'POINT'); a.data.foreach_set('value', np.full(len(verts), 9.0 if nm_ in ('seam', 'zip') else 0.0, np.float32))
        obs.append(ob)
        inner = set(ix[V[ix, 2] < az_ - 0.005])
        for k, f_ in enumerate(F):
            if all(v in inner for v in f_): keep[k] = False
    return obs, keep


def route(V, N, A, a, b):
    """shortest path over the skin graph from vertex a to b, relaxed and lifted 1.2 mm (embroidered run)."""
    from scipy.sparse.csgraph import dijkstra
    Acoo = A.tocoo()
    W = A.copy().astype(float); W.data = np.linalg.norm(V[Acoo.row] - V[Acoo.col], axis=1)[np.argsort(np.lexsort((Acoo.col, Acoo.row)))] if False else None
    rows, cols = Acoo.row, Acoo.col
    import scipy.sparse as sp
    G = sp.csr_matrix((np.linalg.norm(V[rows] - V[cols], axis=1), (rows, cols)), shape=A.shape)
    d, pred = dijkstra(G, indices=a, return_predecessors=True)
    path = [b]
    while path[-1] != a and pred[path[-1]] >= 0:
        path.append(pred[path[-1]])
    P = V[path[::-1]] + N[path[::-1]] * 0.0012
    for _ in range(6):
        P[1:-1] = 0.5 * P[1:-1] + 0.25 * (P[:-2] + P[2:])
    return P


def build(arm_deg=17.0, elbow_deg=8.0, offset=(0, 0, 0), tubes=False, level=1, name='GEO-undersuit', xray_left=False):
    """Doha in the undersuit + balaclava: body mesh with the knit shader, sensor pads and nodes, embroidered bus runs,
    waist and nape connectors, EEG electrodes under the knit. tubes=True adds the cooling-garment runs (X-ray)."""
    import bpy, lib
    V, F, J, B, LM, an = wearer(arm_deg, elbow_deg)
    V = V + np.asarray(offset); J = {k: v + np.asarray(offset) for k, v in J.items()}
    an.V = V; an.J = J; an.cache = {}
    S = sites(an); E = eeg(an); Nd = nodes_for(S)
    V, Adj, eyeslot = dress(V, F, J, an)
    an.V = V; an.N, an.tri = normals(V, F)
    for s_ in S:
        s_['pos_m'] = list(V[s_['vi']]); s_['normal'] = list(an.N[s_['vi']])
    for e_ in E:
        e_['pos_m'] = list(V[e_['vi']]); e_['normal'] = list(an.N[e_['vi']])
    seam, zp, tone, patch, rib = _seam_fields(V, an.N, J, an)
    mk = knit_material()
    boots_, keep = booties(V, F, J, an, mk)
    ob = lib.mesh_object(name, V, [f_ for f_, k in zip(F, keep) if k], subsurf=level)
    for nm_, arr in (('seam', seam), ('zip', zp), ('tone', tone), ('eyeslot', eyeslot), ('rib', rib)):
        a = ob.data.attributes.new(nm_, 'FLOAT', 'POINT'); a.data.foreach_set('value', np.asarray(arr, np.float32))
    ob.data.materials.append(mk)
    objs = [ob] + boots_
    mat_pad = pad_material()
    mat_pod = lib.mat_basic('MAT-node', (0.016, 0.016, 0.017), rough=0.55)
    mat_led = lib.mat_basic('MAT-node-led', (0.1, 0.3, 0.3), rough=0.3, emit=(0.35, 0.9, 1.0), strength=6)
    mat_ti = lib.mat_metal('MAT-conn-ti', (0.42, 0.40, 0.37), rough=0.42)
    mat_ag = lib.mat_metal('MAT-ag-yarn', (0.62, 0.62, 0.63), rough=0.35)
    for s in S:
        w, h = s['size_mm']
        pad = _rbox('EMG-' + s['site'], (w / 1000, h / 1000, 0.0016), mat_pad, bevel=0.003)
        _place(pad, np.array(s['pos_m']) + np.array(s['normal']) * 0.0006, s['normal'], s['fibre_axis']); objs.append(pad)
    for nd_ in Nd:
        i = an.snap(np.array(nd_['pos_m']), np.array(nd_['pos_m']) - np.array([0, 0, nd_['pos_m'][2]]) * 0 + an.N[an.snap(np.array(nd_['pos_m']), (0, 0, 1), radius=0.2)], radius=0.08)
        p, n = V[i], an.N[i]
        pod = _rbox(nd_['node'], (0.026, 0.017, 0.006), mat_pod, bevel=0.0025)
        _place(pod, p + n * 0.0032, n, (0, 0, 1)); objs.append(pod)
        led = _rbox(nd_['node'] + '-led', (0.003, 0.0016, 0.0008), mat_led, bevel=0.0003)
        _place(led, p + n * 0.0063 + np.cross(n, [0, 0, 1]) * 0.0, n, (0, 0, 1)); objs.append(led)
        nd_['vi'] = i
    # connectors: waist L/R and nape
    omph = an.lm('omphalion', 'L'); conns = []
    torso_m = (np.maximum(an.legw['l'], an.legw['r']) < 0.5) & (np.maximum(an.armw['l'], an.armw['r']) < 0.3) & (an.headw < 0.5)
    for sg in (1, -1):
        i = an.ray(np.array([0, omph[1] + 0.05, omph[2] + 0.02]), (sg, 0, 0), mask=torso_m)
        c = _rbox(f'CONN-waist-{"L" if sg > 0 else "R"}', (0.042, 0.030, 0.012), mat_ti, bevel=0.004)
        _place(c, V[i] + an.N[i] * 0.006, an.N[i], (0, 0, 1)); objs.append(c); conns.append(i)
    i = an.ray(J['joint-neck'] - [0, -0.02, 0.02], (0, 1, 0.1), mask=torso_m | (an.headw > 0.2))
    c = _rbox('CONN-nape', (0.030, 0.020, 0.008), mat_ti, bevel=0.003); _place(c, V[i] + an.N[i] * 0.004, an.N[i], (1, 0, 0)); objs.append(c); conns.append(i)
    # embroidered bus runs over the skin: site -> node -> connector (upper body to the nape, lower body to the waist)
    curves = []
    upper = ('arm', 'shoulder', 'chest', 'fore', 'back')
    for nd_ in Nd:
        g = nd_['node'].split('-')[1]; side = nd_['node'].split('-')[-1]
        tgt = conns[2] if g in upper else conns[0 if side == 'L' else 1]
        curves.append(route(V, an.N, Adj, nd_['vi'], tgt))
    for s_ in S:
        nd_ = next(n_ for n_ in Nd if s_['site'] in n_['sites'])
        curves.append(route(V, an.N, Adj, s_['vi'], nd_['vi']))
    cu = bpy.data.curves.new('BUS-runs', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.0006; cu.bevel_resolution = 2
    for pts in curves:
        sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
        for k, q in enumerate(pts): sp.points[k].co = (*q, 1)
    co = bpy.data.objects.new('BUS-runs', cu); bpy.context.scene.collection.objects.link(co); cu.materials.append(mat_ag); objs.append(co)
    # epaulettes: FIA-style rescue straps (collar -> acromion, 38 mm), a ribbon laid along the skin route
    for sd, sg in (('l', 1), ('r', -1)):
        a = an.ray(J['joint-neck'] + [sg * 0.040, 0.0, -0.045], (sg * 0.2, 0, 1), mask=torso_m)
        b = an.snap(an.lm('acromion', 'L' if sg > 0 else 'R') + [-sg * 0.012, 0, 0], (0, 0, 1), mask=torso_m | (an.armw[sd] > 0))
        P_ = route(V, an.N, Adj, a, b)
        L_ = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P_, axis=0), axis=1))]
        ts = np.linspace(0, L_[-1], 24); C = np.array([np.interp(ts, L_, P_[:, k]) for k in range(3)]).T
        rows = []
        for k in range(len(C)):
            t_ = C[min(k + 1, len(C) - 1)] - C[max(k - 1, 0)]; t_ /= np.linalg.norm(t_)
            i_ = int(np.argmin(np.linalg.norm(V - C[k], axis=1))); n_ = an.N[i_]
            w_ = np.cross(n_, t_); w_ /= np.linalg.norm(w_)
            row = []
            for o in np.linspace(-0.019, 0.019, 7):
                q = C[k] + w_ * o; j_ = int(np.argmin(np.linalg.norm(V - q, axis=1)))
                row.append(q + n_ * (0.0016 + max(0.0, (V[j_] - q) @ n_)))
            rows.append(row)
        verts = [p for r_ in rows for p in r_]; nw = 7
        faces = [[k * nw + j, k * nw + j + 1, (k + 1) * nw + j + 1, (k + 1) * nw + j] for k in range(len(rows) - 1) for j in range(nw - 1)]
        ep = lib.mesh_object(f'EP-epaulette-{sd}', np.array(verts), faces, subsurf=1)
        so = ep.modifiers.new('S', 'SOLIDIFY'); so.thickness = 0.0022; so.offset = 1.0
        edge = np.array([abs(j - (nw - 1) / 2) / ((nw - 1) / 2) for k in range(len(rows)) for j in range(nw)])
        for nm_, val in (('seam', (1 - edge) * 0.004 + 0.0028), ('zip', np.full(len(verts), 9.0)), ('tone', np.ones(len(verts))),
                         ('eyeslot', np.zeros(len(verts))), ('rib', np.zeros(len(verts)))):
            at_ = ep.data.attributes.new(nm_, 'FLOAT', 'POINT'); at_.data.foreach_set('value', np.asarray(val, np.float32))
        ep.data.materials.append(mk); objs.append(ep)
    # balaclava over the mouth: a knit patch fitted to the surrounding face surface (the base mesh mouth is open)
    eye_z = 0.5 * (J['joint-l-eye'][2] + J['joint-r-eye'][2]); zl = eye_z - 0.070
    rim = (an.headw > 0.5) & (np.abs(V[:, 0]) < 0.045) & (np.abs(V[:, 2] - zl) < 0.034) & (an.N[:, 1] < -0.4)
    rim &= ~((np.abs(V[:, 0]) < 0.028) & (np.abs(V[:, 2] - zl) < 0.012))
    X_ = np.c_[np.ones(rim.sum()), V[rim, 0], V[rim, 2] - zl, V[rim, 0] ** 2, (V[rim, 2] - zl) ** 2, V[rim, 0] * (V[rim, 2] - zl)]
    cf = np.linalg.lstsq(X_, V[rim, 1], rcond=None)[0]
    gx, gz = np.meshgrid(np.linspace(-0.036, 0.036, 13), np.linspace(-0.02, 0.02, 9))
    rr_ = np.clip(np.sqrt((gx / 0.036) ** 2 + (gz / 0.02) ** 2), 0, 1)
    gy = cf[0] + cf[1] * gx + cf[2] * gz + cf[3] * gx ** 2 + cf[4] * gz ** 2 + cf[5] * gx * gz - 0.0012 + 0.0035 * rr_ ** 3
    pv = np.c_[gx.ravel(), gy.ravel(), (gz + zl).ravel()]
    pf = [[r * 13 + c, r * 13 + c + 1, (r + 1) * 13 + c + 1, (r + 1) * 13 + c] for r in range(8) for c in range(12)]
    mp = lib.mesh_object('GEO-balaclava-mouth', pv, pf, subsurf=1)
    for nm_, val in (('seam', 9.0), ('zip', 9.0), ('tone', 0.0), ('eyeslot', 0.0), ('rib', 0.0)):
        at_ = mp.data.attributes.new(nm_, 'FLOAT', 'POINT'); at_.data.foreach_set('value', np.full(len(pv), val, np.float32))
    mp.data.materials.append(mk); objs.append(mp)
    # EEG electrodes: small domes under the balaclava knit
    for e in E:
        d = lib.beveled_cyl('EEG-' + e['name'], 0.0055, 0.0026, bevel=0.0011, mat=mk, verts=20)
        _place(d, np.array(e['pos_m']) + np.array(e['normal']) * 0.0006, e['normal'], (1, 0, 0)); objs.append(d)
    if tubes:
        objs.append(cooling_tubes(V, F, J, an, only_left=xray_left))
    if xray_left:
        objs += xray(ob, mk, V, F, an)
    return objs, dict(sites=S, eeg=E, nodes=Nd, J=J, V=V, an=an)


def xray(ob, mk, V, F, an):
    """wearer's left half (screen right, front view) of the knit turns into a fresnel ghost, a dark inner body 4 mm
    below shows the cooling runs and sensors in between (03 NEURAL)."""
    import bpy, lib
    nt = mk.node_tree; nd = nt.nodes; ln = nt.links
    out = next(n for n in nd if n.type == 'OUTPUT_MATERIAL'); bsdf = next(n for n in nd if n.type == 'BSDF_PRINCIPLED')
    tc = nd.new('ShaderNodeTexCoord'); sep = nd.new('ShaderNodeSeparateXYZ'); ln.new(tc.outputs['Object'], sep.inputs[0])
    mr = nd.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.0; mr.inputs['From Max'].default_value = 0.012
    ln.new(sep.outputs['X'], mr.inputs['Value'])
    lw = nd.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.25
    em = nd.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (0.35, 0.75, 0.95, 1)
    gm = nd.new('ShaderNodeMath'); gm.operation = 'MULTIPLY'; gm.inputs[1].default_value = 0.9
    ln.new(lw.outputs['Facing'], gm.inputs[0]); ln.new(gm.outputs['Value'], em.inputs['Strength'])
    tr = nd.new('ShaderNodeBsdfTransparent'); add = nd.new('ShaderNodeAddShader')
    ln.new(tr.outputs[0], add.inputs[0]); ln.new(em.outputs[0], add.inputs[1])
    mx = nd.new('ShaderNodeMixShader'); ln.new(mr.outputs['Result'], mx.inputs['Fac'])
    ln.new(bsdf.outputs[0], mx.inputs[1]); ln.new(add.outputs[0], mx.inputs[2]); ln.new(mx.outputs[0], out.inputs['Surface'])
    N_ = an.N
    inner = lib.mesh_object('GEO-xray_inner', V - N_ * 0.004, F, subsurf=1)
    inner.data.materials.append(lib.mat_basic('MAT-xray_inner', (0.006, 0.007, 0.008), rough=0.6))
    return [inner]


def cooling_tubes(V, F, J, an, spacing=0.015, name='LCG-tubes', offset=-0.0012, only_left=False):
    """vertical runs every `spacing` m: iso-lines of arc length around the trunk / limb axes, clipped near joints."""
    import bpy, lib
    x, y, z = V[:, 0], V[:, 1], V[:, 2]
    legw = np.maximum(an.legw['l'], an.legw['r']); armw = np.maximum(an.armw['l'], an.armw['r'])
    tor = (legw < 0.5) & (armw < 0.5) & (an.headw < 0.5)
    omph = an.lm('omphalion', 'L'); sh = 0.5 * (J['joint-l-shoulder'][2] + J['joint-r-shoulder'][2])
    cy = omph[1] + 0.05
    s = np.full(len(V), np.nan)
    th = np.arctan2(x, -(y - cy)); s_t = th * 0.13
    m_t = tor & (z > omph[2] - 0.16) & (z < sh - 0.07)
    s[m_t] = s_t[m_t]
    for sd in ('l', 'r'):
        for a, b, w, lo, hi, R in (('upper-leg', 'knee', an.legw[sd], 0.10, 0.80, 0.075), ('shoulder', 'elbow', an.armw[sd], 0.20, 0.78, 0.045)):
            A, Bp = J[f'joint-{sd}-{a}'], J[f'joint-{sd}-{b}']
            L_ = np.linalg.norm(Bp - A); ax = (Bp - A) / L_
            t = (V - A) @ ax; rr = V - A - np.outer(t, ax)
            e1 = np.array([0, -1.0, 0]); e1 -= e1.dot(ax) * ax; e1 /= np.linalg.norm(e1); e2 = np.cross(ax, e1)
            ang = np.arctan2(rr @ e2, rr @ e1)
            m = (w > 0.5) & (t > lo * L_) & (t < hi * L_)
            s[m] = ang[m] * R + (10.0 if sd == 'l' else 20.0) + (0 if a == 'upper-leg' else 5.0)
    if only_left: s[V[:, 0] < -0.01] = np.nan
    f = s / spacing
    tri = an.tri
    keys = {}; pts = []; edges = []
    fv = f[tri]
    ok = np.all(np.isfinite(fv), 1) & ((fv.max(1) - fv.min(1)) < 3)
    for k_ in np.where(ok)[0]:
        a, b, c = tri[k_]; va, vb, vc = f[a], f[b], f[c]
        for L in range(int(math.ceil(min(va, vb, vc))), int(math.floor(max(va, vb, vc))) + 1):
            seg = []
            for (i, j, fi, fj) in ((a, b, va, vb), (b, c, vb, vc), (c, a, vc, va)):
                if (fi - L) * (fj - L) < 0:
                    key = (min(i, j), max(i, j), L)
                    if key not in keys:
                        t = (L - fi) / (fj - fi)
                        p = V[i] + t * (V[j] - V[i]); n = an.N[i] + t * (an.N[j] - an.N[i]); n /= np.linalg.norm(n)
                        keys[key] = len(pts); pts.append(p + n * offset)
                    seg.append(keys[key])
            if len(seg) == 2: edges.append(seg)
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(p) for p in pts], edges, []); me.update()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    bpy.ops.object.convert(target='CURVE')
    ob.data.bevel_depth = 0.0016; ob.data.bevel_resolution = 2
    ob.data.materials.append(lib.mat_basic('MAT-lcg', (0.55, 0.62, 0.70), rough=0.25))
    print(f'[undersuit] cooling runs: {len(edges)} segments, {sum(np.linalg.norm(pts[a] - pts[b]) for a, b in edges):.1f} m')
    return ob


if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    analyse()
