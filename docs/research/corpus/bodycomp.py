"""CORPUS-1: body composition of the wearer from NHANES 2011-2012 DXA (CDC, public domain).

Wearer (Doha, brief + 2026-10-02): male, early 20s (22 used), stature 178 cm, span 182 cm, mass 65 kg,
body fat 10 % (consumer BIA, assumed InBody), skeletal muscle 'slightly above average'.

Questions answered here
  1. What DXA body fat corresponds to a BIA reading of 10 %? (scenarios, NHANES uses Hologic DXA)
  2. Fat-free mass, FFMI and their percentile among young men; is 'slightly above average muscle' consistent?
  3. Segmental lean mass (arms / legs / trunk), appendicular lean soft tissue -> total skeletal muscle (Kim 2002).
  4. Waist circumference (NHANES site: top of the right iliac crest) and relaxed mid upper-arm circumference,
     predicted from stature, mass, fat mass and age, with 90 % prediction intervals.
Run: python bodycomp.py <dir with DEMO_G.xpt BMX_G.xpt DXX_G.xpt>  ->  bodycomp.json
"""
import json, math, os, sys
import numpy as np
import pandas as pd
import statsmodels.api as sm

D = sys.argv[1] if len(sys.argv) > 1 else '.'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bodycomp.json')
W = dict(age=22.0, H=178.0, M=65.0, bf_bia=10.0)

m = (pd.read_sas(os.path.join(D, 'DEMO_G.xpt')).merge(pd.read_sas(os.path.join(D, 'BMX_G.xpt')), on='SEQN')
     .merge(pd.read_sas(os.path.join(D, 'DXX_G.xpt')), on='SEQN'))
men = m[(m.RIAGENDR == 1) & m.DXDTOPF.notna() & m.BMXHT.notna() & m.BMXWT.notna()].copy()
men['FM'] = men.DXDTOFAT / 1000; men['FFM'] = (men.DXDTOLE + men.DXDTOBMC) / 1000
men['LST'] = men.DXDTOLE / 1000
men['ARM_L'] = (men.DXDLALE + men.DXDRALE) / 1000; men['LEG_L'] = (men.DXDLLLE + men.DXDRLLE) / 1000
men['TRUNK_L'] = men.DXDTRLE / 1000; men['ALST'] = men.ARM_L + men.LEG_L
men['FFMI'] = men.FFM / (men.BMXHT / 100) ** 2; men['asian'] = (men.RIDRETH3 == 6).astype(float)
men['BMC'] = men.DXDTOBMC / 1000
young = men[men.RIDAGEYR.between(18, 35)].copy()


def wpct(x, w, v):
    o = np.argsort(x); x, w = np.asarray(x)[o], np.asarray(w)[o]; c = np.cumsum(w) / w.sum()
    return float(np.interp(v, x, c) * 100)


def fit(df, y, X):
    d = df[[y] + X].dropna()
    r = sm.OLS(d[y], sm.add_constant(d[X])).fit()
    return r, len(d)


def predict(r, row, alpha=0.10):
    x = pd.DataFrame([row])[r.model.exog_names[1:]]
    p = r.get_prediction(sm.add_constant(x, has_constant='add')).summary_frame(alpha=alpha)
    return dict(mean=round(float(p['mean'].iloc[0]), 2), pi90=[round(float(p['obs_ci_lower'].iloc[0]), 2),
                                                              round(float(p['obs_ci_upper'].iloc[0]), 2)])


out = {'inputs': W, 'source': 'NHANES 2011-2012 DEMO_G, BMX_G, DXX_G (Hologic Discovery A DXA)',
       'sample': {'men_18_35_with_dxa': int(len(young)), 'of_which_dxa_bf_lt_17': int((young.DXDTOPF < 17).sum()),
                  'asian_18_35': int(young.asian.sum())}}

# 1. BIA -> DXA scenarios. Literature disagrees in lean men (BIA under-reads in college males, over-reads <15 %
#    in a large Chinese cohort), so the analysis carries three scenarios and uses the middle one.
scen = {'low': 10.0, 'mid': 12.5, 'high': 15.0}
out['bf_dxa_scenarios'] = scen
lean = young[young.DXDTOPF < 17]
out['nhanes_floor'] = {'min_dxa_bf_men_18_35': round(float(young.DXDTOPF.min()), 1),
                       'pct_men_18_29_below_12.5': round(wpct(men[men.RIDAGEYR.between(18, 29)].DXDTOPF,
                                                              men[men.RIDAGEYR.between(18, 29)].WTMEC2YR, 12.5), 1)}

# 2-3. composition per scenario
y29 = men[men.RIDAGEYR.between(18, 29)]
res = {}
for k, bf in scen.items():
    FM = W['M'] * bf / 100; FFM = W['M'] - FM; FFMI = FFM / (W['H'] / 100) ** 2
    row = dict(BMXHT=W['H'], BMXWT=W['M'], FM=FM, FFM=FFM, RIDAGEYR=W['age'], asian=1.0)
    comp = {'FM_kg': round(FM, 2), 'FFM_kg': round(FFM, 2), 'FFMI': round(FFMI, 2),
            'FFMI_pct_men_18_29_weighted': round(wpct(y29.FFMI, y29.WTMEC2YR, FFMI), 1),
            'FFMI_pct_asian_men_18_29': round(wpct(y29[y29.asian == 1].FFMI, y29[y29.asian == 1].WTMEC2YR, FFMI), 1)}
    for tgt in ('ARM_L', 'LEG_L', 'TRUNK_L', 'ALST', 'BMC'):
        r, n = fit(young, tgt, ['FFM', 'BMXHT', 'RIDAGEYR', 'asian'])
        comp[tgt + '_kg'] = predict(r, row)
    alst = comp['ALST_kg']['mean']
    comp['SMM_kim2002_kg'] = round(1.13 * alst - 0.02 * W['age'] + 0.61 * 1 + 0.97, 2)
    comp['SMM_pct_body_mass'] = round(comp['SMM_kim2002_kg'] / W['M'] * 100, 1)
    # 4. circumferences: fat mass and fat-free mass enter separately (lean mass widens the waist far less than fat)
    for tgt, nm in (('BMXWAIST', 'waist_iliac_crest_cm'), ('BMXARMC', 'arm_circ_relaxed_cm')):
        r, n = fit(young, tgt, ['BMXHT', 'FM', 'FFM', 'RIDAGEYR', 'asian'])
        comp[nm] = predict(r, row); comp[nm]['r2'] = round(r.rsquared, 3); comp[nm]['n'] = n
    res[k] = comp
out['composition'] = res

# cross-checks on the waist: local neighbours and two published fat equations solved for the waist
nb = young[young.BMXHT.between(173, 183) & young.BMXWT.between(60, 70) & (young.DXDTOPF < 17)]
out['neighbours_173_183cm_60_70kg_bf_lt17'] = {
    'n': int(len(nb)), 'waist_ic_cm_mean': round(float(nb.BMXWAIST.mean()), 1), 'waist_sd': round(float(nb.BMXWAIST.std()), 1),
    'dxa_bf_mean': round(float(nb.DXDTOPF.mean()), 1), 'arm_circ_mean': round(float(nb.BMXARMC.mean()), 1),
    'ffmi_mean': round(float(nb.FFMI.mean()), 2)}
inch = W['H'] / 2.54
out['navy_method_waist_minus_neck_cm'] = {  # Hodgdon & Beckett 1984, %BF = 86.010 log10(waist-neck) - 70.041 log10(H) + 36.76 (in)
    str(bf): round(10 ** ((bf + 70.041 * math.log10(inch) - 36.76) / 86.010) * 2.54, 1) for bf in (10, 12.5, 15)}
out['rfm_waist_cm'] = {str(bf): round(20 * W['H'] / (64 - bf), 1) for bf in (10, 12.5, 15)}  # Woolcott & Bergman 2018

json.dump(out, open(OUT, 'w'), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
