import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
def run(over=None):
    if over: lib.SHAPE.update(over)
    v, f, j = lib.load_wearer()
    return lib.measure(v, j)
base = dict(lib.SHAPE)
m0 = run(); print('current', m0)
d = 0.2
lib.SHAPE.clear(); lib.SHAPE.update(base); m_s = run({'measure-shoulder-dist-incr': base['measure-shoulder-dist-incr'] - d})
lib.SHAPE.clear(); lib.SHAPE.update(base); m_w = run({'measure-waist-circ-decr': base['measure-waist-circ-decr'] - d})
print('shoulder -0.2 ->', m_s); print('waist-decr -0.2 ->', m_w)
