import numpy as np, colour, warnings, re, json, os, urllib.request
BASE = 'https://raw.githubusercontent.com/polyanskiy/refractiveindex.info-database/master/database/data/main/'
for f in ['TiN/nk/Pfluger.yml', 'Ti/nk/Palm.yml', 'Ti/nk/Johnson.yml', 'Au/nk/Johnson.yml', 'Au/nk/Babar.yml']:
    dst = 'nk_' + f.replace('/', '_')
    if not os.path.exists(dst): urllib.request.urlretrieve(BASE + f, dst)
warnings.filterwarnings('ignore')
def load(fn):
    t = open(fn).read(); blk = t.split('data: |')[1]
    rows = []
    for line in blk.splitlines():
        p = line.split()
        if len(p) == 3:
            try: rows.append([float(x) for x in p])
            except: break
        elif rows: break
    a = np.array(rows); return a[:,0]*1000, a[:,1], a[:,2]   # nm, n, k
cmfs = colour.MSDS_CMFS['CIE 1931 2 Degree Standard Observer']; D65 = colour.SDS_ILLUMINANTS['D65']
wl = np.arange(380, 781, 5)
def fresnel_conductor(n, k, theta_deg):
    th = np.radians(theta_deg); c = np.cos(th); s2 = np.sin(th)**2
    eta = n + 1j*k; ct = np.sqrt(1 - s2/eta**2)
    rs = (c - eta*ct)/(c + eta*ct); rp = (eta*c - ct)/(eta*c + ct)
    return 0.5*(abs(rs)**2 + abs(rp)**2)
out = {}
for name, fn in [('TiN (Pfluger 1984)', 'nk_TiN_nk_Pfluger.yml'), ('Ti (Palm)', 'nk_Ti_nk_Palm.yml'), ('Ti (Johnson&Christy)', 'nk_Ti_nk_Johnson.yml'), ('Au (Johnson&Christy)', 'nk_Au_nk_Johnson.yml'), ('Au (Babar)', 'nk_Au_nk_Babar.yml')]:
    L, n, k = load(fn); o = np.argsort(L); L, n, k = L[o], n[o], k[o]
    ni, ki = np.interp(wl, L, n), np.interp(wl, L, k)
    res = {}
    for ang in [0, 82]:
        R = fresnel_conductor(ni, ki, ang)
        sd = colour.SpectralDistribution(dict(zip(wl, R)))
        XYZ = colour.sd_to_XYZ(sd, cmfs, D65) / 100
        rgb = colour.XYZ_to_RGB(XYZ, colour.RGB_COLOURSPACES['sRGB'], illuminant=colour.CCS_ILLUMINANTS['CIE 1931 2 Degree Standard Observer']['D65'], apply_cctf_encoding=False)
        res[f'{ang}deg_linear_sRGB'] = [round(float(x), 3) for x in rgb]
    res['range_nm'] = [float(L.min()), float(L.max())]
    out[name] = res
print(json.dumps(out, indent=1))
