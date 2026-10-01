import os, importlib.util
import numpy as np, PyOpenColorIO as OCIO, colour, warnings, json
warnings.filterwarnings('ignore')
CFG = os.path.join(os.path.dirname(importlib.util.find_spec('bpy').origin), '5.2', 'datafiles', 'colormanagement', 'config.ocio')
cfg = OCIO.Config.CreateFromFile(CFG)
def blender_agx(rgb_lin709, look=None):
    t = OCIO.DisplayViewTransform(); t.setSrc('Linear Rec.709'); t.setDisplay('sRGB'); t.setView('AgX')
    lt = t
    proc = cfg.getProcessor(lt).getDefaultCPUProcessor()
    a = np.ascontiguousarray(rgb_lin709, dtype=np.float32).copy()
    out = np.empty_like(a)
    for i in range(len(a)): out[i] = proc.applyRGB(a[i].tolist())
    return np.clip(out, 0, 1)
C = lambda *cols: np.array(cols, dtype=np.float64).T   # GLSL column-major
S2R = C((0.6274,0.0691,0.0164),(0.3293,0.9195,0.0880),(0.0433,0.0113,0.8956))
R2S = C((1.6605,-0.1246,-0.0182),(-0.5876,1.1329,-0.1006),(-0.0728,-0.0083,1.1187))
INSET = C((0.856627153315983,0.137318972929847,0.11189821299995),(0.0951212405381588,0.761241990602591,0.0767994186031903),(0.0482516061458583,0.101439036467562,0.811302368396859))
OUTSET = C((1.1271005818144368,-0.1413297634984383,-0.14132976349843826),(-0.11060664309660323,1.157823702216272,-0.11060664309660294),(-0.016493938717834573,-0.016493938717834257,1.2519364065950405))
def three_agx(c):
    c = (S2R @ c.T).T; c = (INSET @ c.T).T
    c = np.log2(np.maximum(c, 1e-10)); c = (c + 12.47393) / (4.026069 + 12.47393); c = np.clip(c, 0, 1)
    x2 = c*c; x4 = x2*x2
    c = 15.5*x4*x2 - 40.14*x4*c + 31.96*x4 - 6.868*x2*c + 0.4298*x2 + 0.1191*c - 0.00232
    c = (OUTSET @ c.T).T; c = np.power(np.maximum(c, 0), 2.2); c = (R2S @ c.T).T; c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, 12.92*c, 1.055*np.power(c, 1/2.4) - 0.055)   # sRGB OETF (three.js output)
def de(a, b):
    la = colour.XYZ_to_Lab(colour.sRGB_to_XYZ(a)); lb = colour.XYZ_to_Lab(colour.sRGB_to_XYZ(b))
    return colour.delta_E(la, lb, method='CIE 2000')
res = {}
# 1) grey ramp -8..+8 stops around 0.18
stops = np.arange(-8, 8.5, 1.0); g = (0.18 * 2.0**stops)[:, None].repeat(3, 1)
bg, tg = blender_agx(g), three_agx(g); d = de(bg, tg)
res['grey'] = [(float(s), round(float(b[0]),4), round(float(t[0]),4), round(float(x),2)) for s,b,t,x in zip(stops,bg,tg,d)]
# 2) ColorChecker 24 (linear sRGB from colour lib reference)
cc = colour.CCS_COLOURCHECKERS['ColorChecker24 - After November 2014']
xyY = np.array(list(cc.data.values())); XYZ = colour.xyY_to_XYZ(xyY)
lin = colour.XYZ_to_RGB(XYZ, colour.RGB_COLOURSPACES['sRGB'], illuminant=cc.illuminant, chromatic_adaptation_transform='Bradford', apply_cctf_encoding=False)
lin = np.clip(lin, 0, None)
for ev in [0, 2]:
    L = lin * 2.0**ev; d = de(blender_agx(L), three_agx(L))
    res[f'checker_ev{ev}'] = {'mean': round(float(d.mean()),2), 'max': round(float(d.max()),2), 'worst_patch': list(cc.data.keys())[int(d.argmax())]}
# 3) saturated emissives (status lights) at increasing intensity
em = {'cyan': (0.0, 0.8, 1.0), 'amber': (1.0, 0.45, 0.0), 'red': (1.0, 0.02, 0.01), 'signal_orange': (1.0, 0.2, 0.0)}
res['emissive'] = {}
for k, v in em.items():
    row = []
    for I in [1, 4, 16, 64]:
        c = np.array([v]) * I; b, t = blender_agx(c), three_agx(c)
        row.append({'I': I, 'blender': [round(float(x),3) for x in b[0]], 'three': [round(float(x),3) for x in t[0]], 'dE': round(float(de(b, t)[0]),2)})
    res['emissive'][k] = row
# 4) titanium F0-ish albedo under unit light
ti = np.array([[0.542, 0.497, 0.449]]); res['titanium_albedo'] = {'blender': blender_agx(ti)[0].round(4).tolist(), 'three': three_agx(ti)[0].round(4).tolist(), 'dE': round(float(de(blender_agx(ti), three_agx(ti))[0]),2)}
print(json.dumps(res, indent=1))
