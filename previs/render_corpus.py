"""CORPUS contact sheet: Doha's fitted body (front / side / back / three-quarter), orthographic, clay, dark studio."""
import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib, bpy, math
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
sc = lib.new_scene(res=(560, 1000), samples=32)
v, f, j = lib.load_wearer()
b = lib.mesh_object('GEO-wearer', v, f, subsurf=1); b.data.materials.append(lib.materials()['clay'])
lib.floor()
lib.area('key', (2.2, -3.6, 3.0), (0, 0, 1), size=(2.4, 2.4), energy=900)
lib.area('fill', (-3, -2.5, 1.6), (0, 0, 1), size=(2, 2), energy=260)
lib.area('rim', (0.5, 3.5, 2.4), (0, 0, 1.2), size=(1.2, 2.4), energy=700)
views = {'front': (0, -8, 0.92), 'side': (8, 0, 0.92), 'back': (0, 8, 0.92), 'threequarter': (5.6, -5.6, 0.92)}
for name, loc in views.items():
    lib.camera(loc, (0, 0, 0.92), lens=50, ortho_scale=2.02)
    lib.render(os.path.join(OUT, f'corpus_{name}.png'))
