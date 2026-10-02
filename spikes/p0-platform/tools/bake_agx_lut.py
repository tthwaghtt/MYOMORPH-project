# Bake Blender 5.2.1 AgX (sRGB display, look None) to a log2-shaped 3D LUT for the web.
# Output: public/lut/agx_<N>.bin = Float16 RGBA, r fastest, then g, then b. Shaper: s = (log2(x) - LO) / (HI - LO).
import os, sys, importlib.util, numpy as np, PyOpenColorIO as OCIO
N = int(sys.argv[1]) if len(sys.argv) > 1 else 48
LO, HI = -12.47393, 12.5260688117
cfg = OCIO.Config.CreateFromFile(os.path.join(os.path.dirname(importlib.util.find_spec('bpy').origin), '5.2', 'datafiles', 'colormanagement', 'config.ocio'))
t = OCIO.DisplayViewTransform(); t.setSrc('Linear Rec.709'); t.setDisplay('sRGB'); t.setView('AgX')
proc = cfg.getProcessor(t).getDefaultCPUProcessor()
g = np.linspace(0, 1, N); B, G, R = np.meshgrid(g, g, g, indexing='ij')
rgb = (2.0 ** (np.stack([R, G, B], -1).reshape(-1, 3) * (HI - LO) + LO)).astype(np.float32)
proc.applyRGB(rgb); rgb = np.clip(rgb, 0, 1)
rgba = np.concatenate([rgb, np.ones((len(rgb), 1), np.float32)], 1).astype(np.float16)
os.makedirs('public/lut', exist_ok=True); fn = f'public/lut/agx_{N}.bin'; rgba.tofile(fn)
print(fn, os.path.getsize(fn), 'bytes', 'grey 0.18 ->', rgb[np.argmin(abs(g - (np.log2(0.18) - LO) / (HI - LO)))].round(4) if False else '')
