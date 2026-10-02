import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
base = dict(lib.SHAPE); base['measure-waist-circ-decr'] = 0.0
def run(wi):
    lib.SHAPE.clear(); lib.SHAPE.update(base); lib.SHAPE['measure-waist-circ-incr'] = wi
    v, f, j = lib.load_wearer(); return lib.measure(v, j)
target, wi = 65.0, 0.4
for it in range(6):
    m = run(wi); e = m['waist_circ_cm'] - target; print(it, round(wi, 3), m, 'err', round(e, 2))
    if abs(e) < 0.15: break
    m2 = run(wi + 0.05); slope = (m2['waist_circ_cm'] - m['waist_circ_cm']) / 0.05
    wi -= e / slope
print('FINAL', round(wi, 3))
