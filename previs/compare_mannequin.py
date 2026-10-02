import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
OUT = '/tmp/claude-0/-home-user-MYOMORPH-project/d54a34ea-8150-5612-94af-75c46b1d240a/scratchpad/'
tag = sys.argv[1]
if tag == 'before':
    lib.SHAPE.pop('measure-shoulder-dist-decr'); lib.SHAPE['measure-shoulder-dist-incr'] = 0.45; lib.SHAPE['measure-waist-circ-decr'] = 0.45
sc = lib.new_scene(res=(700, 1000), samples=24)
v, f, j = lib.load_wearer(); print(tag, lib.measure(v, j))
b = lib.mesh_object('GEO-wearer', v, f); b.data.materials.append(lib.materials()['clay'])
lib.floor()
lib.area('key', (2, -4, 3), (0, 0, 1), size=(2, 2), energy=900); lib.area('fill', (-3, -3, 1.5), (0, 0, 1), size=(2, 2), energy=300)
lib.camera((0, -7.5, 0.95), (0, 0, 0.92), lens=50, ortho_scale=2.0)
lib.render(OUT + f'mannequin_{tag}.png')
