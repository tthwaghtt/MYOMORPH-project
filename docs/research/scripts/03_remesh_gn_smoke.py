import bpy, time, bmesh
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=0.1)
o = bpy.context.active_object
t = time.time()
r = bpy.ops.object.quadriflow_remesh(target_faces=800, use_preserve_sharp=False)
print('QUADRIFLOW', r, len(o.data.polygons), 'faces', round(time.time()-t,2), 's', 'quads=', sum(1 for p in o.data.polygons if len(p.vertices)==4))
o.data.remesh_voxel_size = 0.004
t = time.time(); bpy.ops.object.voxel_remesh(); print('VOXEL_REMESH', len(o.data.polygons), round(time.time()-t,2), 's')
# geometry nodes: mesh -> SDF grid -> fillet -> mesh
ng = bpy.data.node_groups.new('sdf_test', 'GeometryNodeTree')
ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
n = ng.nodes; gi = n.new('NodeGroupInput'); go = n.new('NodeGroupOutput')
a = n.new('GeometryNodeMeshToSDFGrid'); b = n.new('GeometryNodeGridToMesh')
ng.links.new(gi.outputs[0], a.inputs[0]); ng.links.new(a.outputs[0], b.inputs[0]); ng.links.new(b.outputs[0], go.inputs[0])
md = o.modifiers.new('GN', 'NODES'); md.node_group = ng
dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg)
print('GN_SDF_GRID', len(ev.data.polygons), 'faces after SDF round-trip', [i.name for i in a.inputs])
