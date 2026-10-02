import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
base = dict(lib.SHAPE)
def run(ws, wd, wc):
    lib.SHAPE.clear(); lib.SHAPE.update(base)
    lib.SHAPE.update({'measure-shoulder-dist-incr': ws, 'measure-shoulder-dist-decr': wd, 'measure-waist-circ-decr': wc})
    v, f, j = lib.load_wearer(); return lib.measure(v, j)
m0 = run(0.45, 0.0, 0.45); print('start', m0)
tw, tb = m0['waist_circ_cm'] + 5.0, m0['bideltoid_cm'] - 4.0
ws, wd, wc = 0.0, 0.3, 0.0
for it in range(6):
    m = run(ws, wd, wc); ew, eb = m['waist_circ_cm'] - tw, m['bideltoid_cm'] - tb
    print(it, (round(ws,3), round(wd,3), round(wc,3)), m, 'err', round(ew,2), round(eb,2))
    if abs(ew) < 0.2 and abs(eb) < 0.2: break
    wc += ew / 11.0          # waist-decr: +0.1 weight -> -1.1 cm
    wd += eb / 5.0 if wd > 0 else 0   # decr target sensitivity estimate, refined by iteration
print('FINAL', {'measure-shoulder-dist-incr': ws, 'measure-shoulder-dist-decr': round(wd, 3), 'measure-waist-circ-decr': round(wc, 3)})
