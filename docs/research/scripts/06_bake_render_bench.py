import bpy, time, os
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.device='CPU'
# high/low normal bake: subdivided monkey -> low monkey
bpy.ops.mesh.primitive_monkey_add(); hi = bpy.context.active_object; hi.name='hi'
s = hi.modifiers.new('S','SUBSURF'); s.levels = 3; s.render_levels = 3
d = hi.modifiers.new('D','DISPLACE'); d.strength = 0.02
tex = bpy.data.textures.new('n','VORONOI'); d.texture = tex
bpy.ops.mesh.primitive_monkey_add(); lo = bpy.context.active_object; lo.name='lo'
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.uv.smart_project(); bpy.ops.object.mode_set(mode='OBJECT')
m = bpy.data.materials.new('L'); m.use_nodes=True; lo.data.materials.append(m)
img = bpy.data.images.new('nrm', 1024, 1024); tn = m.node_tree.nodes.new('ShaderNodeTexImage'); tn.image = img; m.node_tree.nodes.active = tn
bpy.ops.object.select_all(action='DESELECT'); hi.select_set(True); lo.select_set(True); bpy.context.view_layer.objects.active = lo
sc.cycles.samples = 1
t=time.time(); r = bpy.ops.object.bake(type='NORMAL', use_selected_to_active=True, cage_extrusion=0.03, max_ray_distance=0.06, margin=8)
print('BAKE_NORMAL_1K', r, round(time.time()-t,2),'s')
img.filepath_raw = os.path.abspath('bake_normal.png'); img.file_format='PNG'; img.save()
# reference render benchmark: 1280x720, 128spp + OIDN, world strength + area light
hi.hide_render = True
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[1].default_value = 0.3
bpy.ops.object.light_add(type='AREA', location=(2,-2,3)); L = bpy.context.active_object; L.data.energy = 600; L.data.size = 2
bpy.ops.object.camera_add(location=(0,-4,0.5), rotation=(1.5,0,0)); sc.camera = bpy.context.active_object
sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.cycles.samples=128; sc.cycles.use_denoising=True
sc.cycles.use_adaptive_sampling=True
sc.render.filepath = os.path.abspath('bench_720p.png')
t=time.time(); bpy.ops.render.render(write_still=True); print('RENDER_720P_128SPP', round(time.time()-t,2),'s')
