"""Fit the wearer mannequin to the CORPUS anthropometric profile (docs/research/corpus/anthro.json + bodycomp.json).

MAP estimate: minimise sum(((measured - target) / sigma)^2) + prior on every shape variable.
  sigma = sqrt(sigma_stat^2 + sigma_def^2): statistical uncertainty of the predicted value (ANSUR/NHANES 90 % PI / 3.29)
  plus a definitional term for measuring a skin mesh instead of a person (6 mm lengths, 1.5 % girths).
  Stature and span are Doha's own values (tight). Variables: MakeHuman sliders in [-1, 1] (prior N(0, 0.6)) and the
  muscle/weight macros in [0, 1]. The race macro is fixed at Asian (Doha is Korean).
Writes previs/wearer_fit.json, used by lib.load_wearer().
"""
import json, os, sys, time
import numpy as np
from scipy.optimize import least_squares
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import body

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, '..', 'docs', 'research', 'corpus')
A = json.load(open(os.path.join(CORPUS, 'anthro.json')))['measurements']
BC = json.load(open(os.path.join(CORPUS, 'bodycomp.json')))

SLIDERS = ['torso-scale-horiz-decr-incr', 'torso-scale-depth-decr-incr', 'torso-scale-vert-decr-incr', 'torso-vshape-decr-incr',
           'torso-muscle-pectoral-decr-incr', 'torso-muscle-dorsi-decr-incr', 'measure-bust-circ-decr-incr',
           'measure-underbust-circ-decr-incr', 'measure-waist-circ-decr-incr', 'measure-napetowaist-dist-decr-incr',
           'measure-waisttohip-dist-decr-incr', 'measure-shoulder-dist-decr-incr', 'measure-hips-circ-decr-incr',
           'measure-frontchest-dist-decr-incr', 'hip-scale-horiz-decr-incr', 'hip-scale-depth-decr-incr', 'hip-scale-vert-decr-incr',
           'hip-waist-down-up', 'buttocks-volume-decr-incr', 'measure-neck-circ-decr-incr', 'measure-neck-height-decr-incr',
           'neck-scale-horiz-decr-incr', 'neck-scale-depth-decr-incr', 'upperarm-scale-horiz-decr-incr', 'upperarm-scale-depth-decr-incr',
           'upperarm-muscle-decr-incr', 'upperarm-fat-decr-incr', 'upperarm-shoulder-muscle-decr-incr', 'measure-upperarm-circ-decr-incr',
           'measure-upperarm-length-decr-incr', 'lowerarm-scale-horiz-decr-incr', 'lowerarm-scale-depth-decr-incr',
           'lowerarm-muscle-decr-incr', 'lowerarm-fat-decr-incr', 'measure-lowerarm-length-decr-incr', 'hand-scale-decr-incr',
           'hand-fingers-length-decr-incr', 'measure-wrist-circ-decr-incr', 'upperleg-scale-horiz-decr-incr',
           'upperleg-scale-depth-decr-incr', 'upperleg-muscle-decr-incr', 'upperleg-fat-decr-incr', 'measure-thigh-circ-decr-incr',
           'measure-upperleg-height-decr-incr', 'upperlegs-height-decr-incr', 'lowerleg-scale-horiz-decr-incr',
           'lowerleg-scale-depth-decr-incr', 'lowerleg-muscle-decr-incr', 'lowerleg-fat-decr-incr', 'measure-calf-circ-decr-incr',
           'measure-knee-circ-decr-incr', 'measure-lowerleg-height-decr-incr', 'lowerlegs-height-decr-incr', 'foot-scale-decr-incr',
           'foot-scale-horiz-decr-incr', 'measure-ankle-circ-decr-incr', 'head-scale-horiz-decr-incr', 'head-scale-depth-decr-incr',
           'head-scale-vert-decr-incr']
FIXED = {'stomach-tone-decr-incr': 0.6, 'pelvis-tone-decr-incr': 0.3}     # 10 % body fat: visible abdominal definition

# targets (mm) and sigma
T = {}
for k, r in A.items():
    lo, hi = r['pi90_mm']
    T[k] = (r['value_mm'], (hi - lo) / 3.29)
arm = np.interp(11.0, [10, 12.5], [BC['composition']['low']['arm_circ_relaxed_cm']['mean'], BC['composition']['mid']['arm_circ_relaxed_cm']['mean']])
api = BC['composition']['mid']['arm_circ_relaxed_cm']['pi90']
T['armcircumference_relaxed'] = (arm * 10, (api[1] - api[0]) * 10 / 3.29)
T['forearmcircumference_relaxed'] = (A['forearmcircumferenceflexed']['value_mm'] - 10.0, 15.0)
T['span'] = (1820.0, 0.0); T['stature'] = (1780.0, 0.0)
GIRTH = lambda k: 'circumference' in k
# not fitted: definitions that a skin mesh cannot reproduce faithfully (see wearer-anatomy.md §3.3)
#   chestbreadth (ANSUR caliper at the anterior axillary lines, not the maximum torso width),
#   neckcircumferencebase (tape over the trapezius roots; a planar section runs out along the shoulder slope)
for k in ('chestbreadth', 'neckcircumferencebase'):
    T.pop(k, None)


def sigma(k):
    st = T[k][1]; de = 0.015 * T[k][0] if GIRTH(k) else 6.0
    if k in ('span',):
        de = 8.0          # T-pose of a rest-pose mesh, fingers slightly flexed
    return float(np.hypot(st, de))


B = body.Base.get(); E = body.edges(); M = body.region_masks()
LM_PATH = os.path.join(body.VENDOR, 'landmarks.json')
v_ref = body.shape({'macro': {'muscle': 0.3, 'weight': 0.3, 'asian': 1.0}, 'sliders': FIXED})
vp, J = body.pose(v_ref, 6, 5); vw, Jw, _ = body.to_world(vp, J)
LM = body.Landmarks(vw, Jw); LM.save(LM_PATH)

# dense slider deltas for speed
def delta(names):
    d = np.zeros_like(B.v0)
    for t in names:
        idx, dd = B.target(t); d[idx] += dd
    return d
DPOS = np.array([delta(B.catalog[s][2]) for s in SLIDERS]); DNEG = np.array([delta(B.catalog[s][1]) for s in SLIDERS])
MAC = {k: delta([k]) for k in body.macro_weights(0, 0)}
BASE = B.v0 + delta(['asian-male-young']) + sum(FIXED[s] * delta(B.catalog[s][2]) for s in FIXED)
NS = len(SLIDERS)


def build(x):
    s = x[:NS]; mu, wt = x[NS], x[NS + 1]
    v = BASE.copy()
    v += np.tensordot(np.clip(s, 0, None), DPOS, 1) + np.tensordot(np.clip(-s, 0, None), DNEG, 1)
    for k, w in body.macro_weights(mu, wt).items():
        v += w * MAC[k]
    return v


def measure_x(x, tpose=True):
    v = build(x)
    vp, J = body.pose(v, 6, 5); vw, Jw, sc = body.to_world(vp, J)
    vt = None
    if tpose:
        vt_, Jt = body.pose(v, 90, 0)
        conv = lambda a: np.stack([a[..., 0], -a[..., 2], a[..., 1]], -1)
        vt = conv(vt_) * sc                  # same scale as the standing pose (only x-extent is used)
    return body.measure(vw, Jw, LM, E, M, vt, None), vw, Jw


KEYS = [k for k in measure_x(np.r_[np.zeros(NS), 0.3, 0.35])[0] if k in T and k != 'stature']
PRIOR_MU = np.r_[np.zeros(NS), 0.3, 0.35]; PRIOR_SD = np.r_[np.full(NS, 0.6), 0.25, 0.25]


def resid(x):
    m, _, _ = measure_x(x)
    r = [(m[k] - T[k][0]) / sigma(k) for k in KEYS]
    return np.r_[r, (x - PRIOR_MU) / PRIOR_SD]


if __name__ == '__main__':
    x0 = PRIOR_MU.copy()
    lo = np.r_[np.full(NS, -1.0), 0.0, 0.0]; hi = np.r_[np.full(NS, 1.0), 1.0, 1.0]
    t0 = time.time()
    m0, _, _ = measure_x(x0)
    r = least_squares(resid, x0, bounds=(lo, hi), diff_step=0.02, x_scale=0.3, max_nfev=60, verbose=1)
    m1, vw, Jw = measure_x(r.x)
    rows = {k: {'target_mm': round(T[k][0], 1), 'sigma_mm': round(sigma(k), 1), 'start_mm': round(m0[k], 1),
                'fit_mm': round(m1[k], 1), 'z': round((m1[k] - T[k][0]) / sigma(k), 2)} for k in KEYS}
    out = {'method': __doc__.strip().splitlines()[0], 'chi2_per_measure': round(float(np.mean([v['z'] ** 2 for v in rows.values()])), 3),
           'macro': {'muscle': round(float(r.x[NS]), 4), 'weight': round(float(r.x[NS + 1]), 4), 'asian': 1.0},
           'sliders': {**{s: round(float(v), 4) for s, v in zip(SLIDERS, r.x[:NS]) if abs(v) > 1e-4}, **FIXED},
           'measurements': rows, 'seconds': round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, 'wearer_fit.json'), 'w'), indent=1)
    print('chi2/measure', out['chi2_per_measure'], 'macro', out['macro'], 'time', out['seconds'])
    for k, v in rows.items():
        print(f"{k:32s} target {v['target_mm']:7.1f} ±{v['sigma_mm']:5.1f}  start {v['start_mm']:7.1f}  fit {v['fit_mm']:7.1f}  z {v['z']:+5.2f}")
