"""check render: Doha in the undersuit + balaclava (sensor pads, nodes, bus runs). python test_undersuit.py OUT.png [tubes]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, lib, undersuit
a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
out = a[0]; tubes = len(a) > 1
sc = lib.new_scene(res=(1200, 1500), samples=48)
lib.floor(mat='floor')
objs, info = undersuit.build(tubes=tubes)
lib.area('key', (1.5, -2.4, 2.2), (0, 0, 1.1), size=(1.2, 1.6), energy=260)
lib.area('rim', (-1.6, 1.6, 1.8), (0, 0, 1.1), size=(0.3, 2.0), energy=300)
lib.area('fill', (-2.0, -1.8, 1.2), (0, 0, 1.0), size=(1.0, 1.6), energy=90)
lib.area('top', (0, 0, 3.2), (0, 0, 1.0), size=(1.2, 0.6), energy=120)
lib.camera((0.9, -2.2, 1.35), (0.05, 0, 1.22), lens=50)
sc.view_settings.exposure = -1.4
lib.render(out)
