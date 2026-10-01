# Feasibility probe (research only): curve -> points(radius) -> SDF -> union -> mesh -> per-vertex ownership via Sample Grid
import bpy, time, numpy as np
bpy.ops.wm.read_factory_settings(use_empty=True)
ng = bpy.data.node_groups.new('probe', 'GeometryNodeTree')
ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
N, L = ng.nodes, ng.links
go = N.new('NodeGroupOutput')
def strand(p0, p1, r):
    ln = N.new('GeometryNodeCurvePrimitiveLine'); ln.inputs['Start'].default_value = p0; ln.inputs['End'].default_value = p1
    rs = N.new('GeometryNodeResampleCurve'); rs.inputs['Count'].default_value = 64; L.new(ln.outputs[0], rs.inputs['Curve'])
    sr = N.new('GeometryNodeSetCurveRadius'); L.new(rs.outputs[0], sr.inputs['Curve'])
    # belly profile: radius = r * sin(pi * t)^0.6 + r*0.25
    sp = N.new('GeometryNodeSplineParameter'); m1 = N.new('ShaderNodeMath'); m1.operation='MULTIPLY'; m1.inputs[1].default_value = 3.14159
    L.new(sp.outputs['Factor'], m1.inputs[0]); s = N.new('ShaderNodeMath'); s.operation='SINE'; L.new(m1.outputs[0], s.inputs[0])
    pw = N.new('ShaderNodeMath'); pw.operation='POWER'; pw.inputs[1].default_value = 0.6; L.new(s.outputs[0], pw.inputs[0])
    ma = N.new('ShaderNodeMath'); ma.operation='MULTIPLY_ADD'; ma.inputs[1].default_value = r; ma.inputs[2].default_value = r*0.25; L.new(pw.outputs[0], ma.inputs[0])
    L.new(ma.outputs[0], sr.inputs['Radius'])
    cp = N.new('GeometryNodeCurveToPoints'); cp.mode = 'EVALUATED'; L.new(sr.outputs[0], cp.inputs['Curve'])
    rad = N.new('GeometryNodeInputRadius')
    sdf = N.new('GeometryNodePointsToSDFGrid'); L.new(rad.outputs[0], sdf.inputs['Radius']); sdf.inputs['Voxel Size'].default_value = 0.0025; L.new(cp.outputs['Points'], sdf.inputs['Points'])
    return sdf
a = strand((0,0,0), (0,0,0.30), 0.035)    # "muscle A"
b = strand((0.03,0,0.05), (0.05,0.0,0.33), 0.03)   # "muscle B", overlapping
bo = N.new('GeometryNodeSDFGridBoolean'); print('bool props:', bo.operation if hasattr(bo,'operation') else None, [i.name for i in bo.inputs])
bo.operation = 'UNION'
print('p2sdf inputs', [(i.name, i.is_multi_input) for i in a.inputs]); print('bool inputs multi', [(i.name, i.is_multi_input) for i in bo.inputs])
L.new(a.outputs[0], bo.inputs['Grid 2']); L.new(b.outputs[0], bo.inputs['Grid 2'])
fl = N.new('GeometryNodeSDFGridFillet'); fl.inputs['Iterations'].default_value = 4; L.new(bo.outputs[0], fl.inputs[0])
gm = N.new('GeometryNodeGridToMesh'); gm.inputs['Threshold'].default_value = 0.0; L.new(fl.outputs[0], gm.inputs['Grid'])
# ownership: sample each SDF at vertex positions, store (dA - dB) as attribute
pos = N.new('GeometryNodeInputPosition')
sa = N.new('GeometryNodeSampleGrid'); sb = N.new('GeometryNodeSampleGrid')
L.new(a.outputs[0], sa.inputs[0]); L.new(pos.outputs[0], sa.inputs['Position']); L.new(b.outputs[0], sb.inputs[0]); L.new(pos.outputs[0], sb.inputs['Position'])
sub = N.new('ShaderNodeMath'); sub.operation='SUBTRACT'; L.new(sa.outputs[0], sub.inputs[0]); L.new(sb.outputs[0], sub.inputs[1])
st = N.new('GeometryNodeStoreNamedAttribute'); st.inputs['Name'].default_value = 'own_AminusB'; st.data_type = 'FLOAT'
L.new(gm.outputs[0], st.inputs['Geometry']); L.new(sub.outputs[0], st.inputs['Value']); L.new(st.outputs[0], go.inputs[0])
bpy.ops.mesh.primitive_plane_add(); o = bpy.context.active_object
md = o.modifiers.new('GN', 'NODES'); md.node_group = ng
t = time.time(); ev = o.evaluated_get(bpy.context.evaluated_depsgraph_get()); me = ev.to_mesh()
att = me.attributes.get('own_AminusB'); v = np.zeros(len(att.data)); att.data.foreach_get('value', v)
co=np.zeros(len(me.vertices)*3); me.vertices.foreach_get('co', co); co=co.reshape(-1,3); print('BBOX', co.min(0).round(3), co.max(0).round(3), 'seam2.5mm', int((abs(v)<0.0025).sum()))
print('PROBE_OK faces', len(me.polygons), 'verts', len(me.vertices), 'time', round(time.time()-t,2), 's | ownership A:', int((v<0).sum()), 'B:', int((v>=0).sum()), '| seam verts(|d|<1mm):', int((abs(v)<0.001).sum()))
