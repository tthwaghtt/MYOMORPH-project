import bpy, os, json, struct, time
bpy.ops.wm.read_factory_settings(use_empty=False)
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 16
cube = bpy.data.objects['Cube']
bpy.context.view_layer.objects.active = cube; cube.select_set(True)
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.uv.smart_project(); bpy.ops.object.mode_set(mode='OBJECT')
m = bpy.data.materials.new('BakeMat'); m.use_nodes = True; cube.data.materials.append(m)
img = bpy.data.images.new('ao', 128, 128); tn = m.node_tree.nodes.new('ShaderNodeTexImage'); tn.image = img
m.node_tree.nodes.active = tn
t = time.time(); r = bpy.ops.object.bake(type='AO'); print('BAKE_AO', r, round(time.time()-t,2), 's')
cube['mm1_part_id'] = 'MM1-TEST-CUBE-C-01'; cube['mass_g'] = 212
for mode, kw in [('plain', {}), ('meshopt', {'export_meshopt_compression_enable': True})]:
    fp = os.path.abspath(f'smoke_{mode}.glb')
    try:
        bpy.ops.export_scene.gltf(filepath=fp, export_format='GLB', export_extras=True, export_tangents=True, export_apply=True, use_selection=True, **kw)
        d = open(fp,'rb').read(); jl = struct.unpack('<I', d[12:16])[0]; j = json.loads(d[20:20+jl])
        print('GLTF', mode, len(d), 'bytes', 'extUsed=', j.get('extensionsUsed'), 'extras=', j['nodes'][0].get('extras'), 'attrs=', list(j['meshes'][0]['primitives'][0]['attributes'].keys()))
    except Exception as e:
        print('GLTF', mode, 'ERR', repr(e)[:300])
props = bpy.ops.export_scene.gltf.get_rna_type().properties
for k in ['export_meshopt_compression_enable','export_meshopt_extension','export_use_gltfpack','export_image_format','export_gpu_instances']:
    p = props[k]; print('OPT', k, '|', p.description[:160], '|', [i.identifier for i in p.enum_items] if p.type=='ENUM' else p.default)
