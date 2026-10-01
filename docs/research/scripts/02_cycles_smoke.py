import bpy, time, os, sys
bpy.ops.wm.read_factory_settings(use_empty=False)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = 64
sc.cycles.use_denoising = True
try:
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'; den = sc.cycles.denoiser
except Exception as e: den = 'ERR ' + repr(e)
sc.render.resolution_x = 320; sc.render.resolution_y = 240; sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'None'
# beveled cube with titanium-like material
cube = bpy.data.objects['Cube']
bv = cube.modifiers.new('Bevel', 'BEVEL'); bv.width = 0.03; bv.segments = 3; bv.limit_method = 'ANGLE'
wn = cube.modifiers.new('WN', 'WEIGHTED_NORMAL'); wn.keep_sharp = True
bpy.context.view_layer.objects.active = cube; cube.select_set(True)
bpy.ops.object.shade_smooth()
m = bpy.data.materials.new('Ti'); m.use_nodes = True
p = m.node_tree.nodes.get('Principled BSDF')
p.inputs['Base Color'].default_value = (0.542, 0.497, 0.449, 1); p.inputs['Metallic'].default_value = 1.0; p.inputs['Roughness'].default_value = 0.35
p.inputs['Anisotropic'].default_value = 0.6
cube.data.materials.append(m)
t = time.time(); sc.render.filepath = os.path.abspath('render_cycles.png'); bpy.ops.render.render(write_still=True)
print('CYCLES_OK', round(time.time()-t, 2), 's', 'denoiser=', den, 'view=', sc.view_settings.view_transform, 'threads=', sc.render.threads)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('smoke.blend'))
print('SAVE_OK', os.path.getsize('smoke.blend'))
