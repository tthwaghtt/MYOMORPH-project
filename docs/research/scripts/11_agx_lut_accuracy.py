import os, importlib.util
import numpy as np, PyOpenColorIO as OCIO, colour, warnings, json, time
warnings.filterwarnings('ignore')
cfg = OCIO.Config.CreateFromFile(os.path.join(os.path.dirname(importlib.util.find_spec('bpy').origin), '5.2', 'datafiles', 'colormanagement', 'config.ocio'))
t = OCIO.DisplayViewTransform(); t.setSrc('Linear Rec.709'); t.setDisplay('sRGB'); t.setView('AgX')
proc = cfg.getProcessor(t).getDefaultCPUProcessor()
def exact(rgb):
    a = np.ascontiguousarray(rgb, dtype=np.float32).copy(); proc.applyRGB(a); return np.clip(a, 0, 1)
LO, HI = -12.47393, 12.5260688117
enc = lambda x: np.clip((np.log2(np.maximum(x, 2.0**LO)) - LO) / (HI - LO), 0, 1)
dec = lambda s: 2.0 ** (s * (HI - LO) + LO)
def bake(N):
    g = np.linspace(0, 1, N); B, G, R = np.meshgrid(g, g, g, indexing='ij')
    s = np.stack([R, G, B], -1).reshape(-1, 3); return exact(dec(s)).reshape(N, N, N, 3)  # [b,g,r]
def trilinear(lut, s):
    N = lut.shape[0]; p = s * (N - 1); i0 = np.clip(np.floor(p).astype(int), 0, N - 2); f = p - i0
    r0, g0, b0 = i0[:, 0], i0[:, 1], i0[:, 2]; fr, fg, fb = f[:, :1], f[:, 1:2], f[:, 2:3]
    c = lambda db, dg, dr: lut[b0 + db, g0 + dg, r0 + dr]
    c00 = c(0,0,0)*(1-fr)+c(0,0,1)*fr; c01 = c(0,1,0)*(1-fr)+c(0,1,1)*fr; c10 = c(1,0,0)*(1-fr)+c(1,0,1)*fr; c11 = c(1,1,0)*(1-fr)+c(1,1,1)*fr
    return (c00*(1-fg)+c01*fg)*(1-fb) + (c10*(1-fg)+c11*fg)*fb
def de(a, b): return colour.delta_E(colour.XYZ_to_Lab(colour.sRGB_to_XYZ(a)), colour.XYZ_to_Lab(colour.sRGB_to_XYZ(b)), method='CIE 2000')
rng = np.random.default_rng(7)
test = np.concatenate([ (0.18 * 2.0 ** rng.uniform(-8, 7, (20000, 1))) * rng.dirichlet([0.6,0.6,0.6], 20000) * 3,  # random chroma, wide exposure
                        (0.18 * 2.0 ** np.linspace(-8, 8, 200))[:, None].repeat(3, 1) ])
ref = exact(test); out = {}
for N in [33, 48, 65]:
    t0 = time.time(); lut = bake(N); tb = time.time() - t0
    d = de(ref, trilinear(lut, enc(test)))
    out[N] = {'bake_s': round(tb, 1), 'mean_dE': round(float(d.mean()), 3), 'p99_dE': round(float(np.percentile(d, 99)), 3), 'max_dE': round(float(d.max()), 3), 'bytes_rgba16f': N**3 * 8}
print(json.dumps(out, indent=1))
