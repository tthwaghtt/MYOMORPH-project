import bpy, time, os
bpy.ops.wm.read_factory_settings(use_empty=False)
sc = bpy.context.scene
sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x = 160; sc.render.resolution_y = 120
sc.render.filepath = os.path.abspath('render_eevee.png')
t = time.time(); bpy.ops.render.render(write_still=True); print('EEVEE_OK', round(time.time()-t, 2))
