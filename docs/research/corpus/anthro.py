"""CORPUS-2: full anthropometric profile of the wearer from ANSUR II (2012 US Army survey, public domain).

Conditioning variables (all known or derived for Doha):
  stature 1780 mm, span 1820 mm, mass 65.0 kg, age 22, Asian (DODRace 4) indicator = 1,
  waist circumference at omphalion from CORPUS-1 (NHANES iliac-crest waist minus the iliac-crest/umbilicus site
  offset in men, ~1 cm; Mason & Katzmarzyk 2009) -> W_omph = 71.2 cm +/- 2.6 cm (1 sd, model + site uncertainty).
The wearer sits in the lean tail of ANSUR (BMI 20.5 vs mean 27.7), so a global linear model would extrapolate.
Every measurement is predicted twice and the local estimate is adopted:
  global : OLS on logs over all 4,082 men
  local  : the same model, Gaussian-kernel weighted around the wearer in standardized covariate space
           (bandwidth giving an effective n of ~350), so the slopes are those of lean men
90 % prediction intervals include the propagated waist uncertainty.
Run: python anthro.py <ANSUR_II_MALE_Public.csv> -> anthro.json
"""
import json, os, sys
import numpy as np
import pandas as pd

CSV = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'anthro.json')
BC = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bodycomp.json')))

a = pd.read_csv(CSV, encoding='latin-1')
a = a.copy(); a['weight'] = a.weightkg / 10.0      # hectograms -> kg
a['asian'] = (a.DODRace == 4).astype(float)
META = {'subjectid', 'Gender', 'Date', 'Installation', 'Component', 'Branch', 'PrimaryMOS', 'SubjectsBirthLocation',
        'SubjectNumericRace', 'Ethnicity', 'DODRace', 'Age', 'Heightin', 'Weightlbs', 'WritingPreference', 'weightkg',
        'weight', 'asian'}
MEAS = [c for c in a.columns if c not in META]

# waist at omphalion for the wearer (adopted body-fat scenario: DXA 11 %, see wearer-anatomy.md §2)
wic = np.interp(11.0, [10.0, 12.5], [BC['composition']['low']['waist_iliac_crest_cm']['mean'],
                                     BC['composition']['mid']['waist_iliac_crest_cm']['mean']])
pi = BC['composition']['mid']['waist_iliac_crest_cm']['pi90']
w_sd = np.hypot((pi[1] - pi[0]) / 2 / 1.645 * 0.55, 1.0)      # model sd shrunk by the neighbour evidence, + site sd
W_OMPH = (wic - 1.0) * 10                                     # mm
TARGET = {'stature': 1780.0, 'span': 1820.0, 'weight': 65.0, 'waistcircumference': W_OMPH, 'Age': 22.0, 'asian': 1.0}
COV = ['stature', 'span', 'weight', 'waistcircumference']
LOGC = ['stature', 'span', 'weight', 'waistcircumference']


def design(df):
    X = np.column_stack([np.ones(len(df))] + [np.log(df[c]) for c in LOGC] + [df.Age, df.asian])
    return X


def wls(X, y, w):
    sw = np.sqrt(w)
    beta, *_ = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)
    r = y - X @ beta
    neff = w.sum() ** 2 / (w ** 2).sum()
    s2 = (w * r ** 2).sum() / w.sum() * neff / max(neff - X.shape[1], 1)
    XtWX_inv = np.linalg.pinv((X * w[:, None]).T @ X)
    return beta, s2, XtWX_inv, neff


tdf = pd.DataFrame([TARGET])
x0 = design(tdf)[0]
Z = (a[COV] - a[COV].mean()) / a[COV].std()
z0 = (tdf[COV].iloc[0] - a[COV].mean()) / a[COV].std()
d2 = ((Z - z0) ** 2).sum(axis=1).values
bw = 1.0
for _ in range(40):                                           # bandwidth for effective n ~ 350
    k = np.exp(-0.5 * d2 / bw ** 2); neff = k.sum() ** 2 / (k ** 2).sum()
    bw *= (350 / neff) ** 0.25
kern = np.exp(-0.5 * d2 / bw ** 2)
near = a.loc[np.argsort(d2)[:40]]

X = design(a)
res, rows = {}, []
for mcol in MEAS:
    y = np.log(a[mcol].values.astype(float))
    out = {}
    for tag, w in (('global', np.ones(len(a))), ('local', kern)):
        beta, s2, Vb, neff = wls(X, y, w)
        mu = x0 @ beta
        var_pred = s2 + x0 @ Vb @ x0 * s2
        if mcol != 'waistcircumference':
            bw_w = beta[4]                                    # d log(y) / d log(waist)
            var_pred += (bw_w * (w_sd * 10 / W_OMPH)) ** 2
        sd = np.sqrt(var_pred)
        out[tag] = dict(mean=float(np.exp(mu)), lo=float(np.exp(mu - 1.645 * sd)), hi=float(np.exp(mu + 1.645 * sd)),
                        neff=float(neff))
    pop = a[mcol]
    res[mcol] = {'value_mm': round(out['local']['mean'], 1), 'pi90_mm': [round(out['local']['lo'], 1), round(out['local']['hi'], 1)],
                 'global_mm': round(out['global']['mean'], 1), 'ansur_mean_mm': round(float(pop.mean()), 1),
                 'ansur_pct_of_wearer': round(float((pop < out['local']['mean']).mean() * 100), 1),
                 'nearest40_mean_mm': round(float(near[mcol].mean()), 1)}
    rows.append((mcol, res[mcol]))


out = {'source': 'ANSUR II male public data (n = 4082), Gordon et al. 2014, NATICK/TR-15/007',
       'target': {k: (round(v, 1) if isinstance(v, float) else v) for k, v in TARGET.items()},
       'waist_omphalion_sd_mm': round(w_sd * 10, 1), 'kernel_bandwidth_sd': round(bw, 3),
       'effective_n_local': round(float(kern.sum() ** 2 / (kern ** 2).sum()), 1),
       'nearest40': {'stature': round(float(near.stature.mean()), 1), 'span': round(float(near.span.mean()), 1),
                     'weight': round(float(near.weight.mean()), 1), 'waist': round(float(near.waistcircumference.mean()), 1),
                     'asian': int(near.asian.sum())},
       'measurements': res}
json.dump(out, open(OUT, 'w'), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != 'measurements'}, indent=1))
for mcol, r in rows:
    print(f"{mcol:34s} {r['value_mm']:8.1f}  [{r['pi90_mm'][0]:7.1f},{r['pi90_mm'][1]:7.1f}]  global {r['global_mm']:8.1f}"
          f"  pop {r['ansur_mean_mm']:8.1f} ({r['ansur_pct_of_wearer']:5.1f} pct)  nn40 {r['nearest40_mean_mm']:8.1f}")
