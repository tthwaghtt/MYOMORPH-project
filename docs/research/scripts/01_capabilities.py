import bpy, sys, os, json
out = {}
app = bpy.app
out['version'] = app.version_string
out['build_hash'] = app.build_hash.decode() if isinstance(app.build_hash, bytes) else app.build_hash
out['build_date'] = app.build_date.decode() if isinstance(app.build_date, bytes) else app.build_date
bo = app.build_options
out['build_options'] = {k: getattr(bo, k) for k in dir(bo) if not k.startswith('_') and isinstance(getattr(bo, k), bool)}
sc = bpy.context.scene
def enum_items(owner, prop):
    return [i.identifier for i in owner.bl_rna.properties[prop].enum_items]
out['render_engines'] = enum_items(sc.render, 'engine')
out['view_transforms'] = enum_items(sc.view_settings, 'view_transform')
out['looks'] = enum_items(sc.view_settings, 'look')
out['display_devices'] = enum_items(sc.display_settings, 'display_device')
out['default_view'] = (sc.display_settings.display_device, sc.view_settings.view_transform, sc.view_settings.look)
# working color space (5.0+): search RNA
ws = {}
for tname in ['BlendData', 'Scene', 'ColorManagedViewSettings', 'ColorManagedDisplaySettings']:
    t = getattr(bpy.types, tname)
    for p in t.bl_rna.properties:
        if 'work' in p.identifier.lower() or 'colorspace' in p.identifier.lower():
            ws[f'{tname}.{p.identifier}'] = p.type
out['working_space_props'] = ws
try:
    out['working_space_value'] = bpy.data.colorspace.working_space
    out['working_space_items'] = enum_items(bpy.data.colorspace, 'working_space')
except Exception as e:
    out['working_space_value'] = repr(e)
cm = os.path.join(os.path.dirname(bpy.__file__), )
out['bpy_path'] = os.path.dirname(bpy.__file__)
out['modifier_types'] = [i.identifier for i in bpy.types.Modifier.bl_rna.properties['type'].enum_items]
ops = ['object.quadriflow_remesh','object.voxel_remesh','object.bake','mesh.bevel','object.shade_auto_smooth','object.shade_smooth_by_angle','export_scene.gltf','wm.obj_export','wm.usd_export','object.modifier_apply','mesh.looptools_relax']
def has_op(o):
    a,b = o.split('.')
    try:
        getattr(getattr(bpy.ops, a), b).get_rna_type(); return True
    except Exception: return False
out['operators'] = {o: has_op(o) for o in ops}
gn = sorted(t for t in dir(bpy.types) if t.startswith('GeometryNode'))
out['geometry_node_count'] = len(gn)
want = ['GeometryNodeBevel','GeometryNodeSampleNearestSurface','GeometryNodeInstanceOnPoints','GeometryNodeCurveToMesh','GeometryNodeMeshToSDFGrid','GeometryNodeMeshToVolume','GeometryNodeVolumeToMesh','GeometryNodeSampleGrid','GeometryNodeGridToMesh','GeometryNodeRaycast','GeometryNodeMeshBoolean','GeometryNodeSetShadeSmooth','GeometryNodeBake','GeometryNodeRepeatInput','GeometryNodeForeachGeometryElementInput','GeometryNodeSampleSoundFrequencies']
out['gn_nodes'] = {w: (w in gn) for w in want}
out['gn_bevel_like'] = [t for t in gn if 'Bevel' in t or 'Fillet' in t or 'Chamfer' in t]
# gltf exporter options
props = bpy.ops.export_scene.gltf.get_rna_type().properties
out['gltf_options'] = sorted(p.identifier for p in props if p.identifier.startswith('export_'))
# addons
import addon_utils
out['addons_enabled'] = sorted(m.__name__ for m in addon_utils.modules() if addon_utils.check(m.__name__)[1])
out['addons_available'] = len(list(addon_utils.modules()))
# cycles devices
try:
    cp = bpy.context.preferences.addons['cycles'].preferences
    out['cycles_device_types'] = [i.identifier for i in cp.bl_rna.properties['compute_device_type'].enum_items]
    cp.refresh_devices()
    out['cycles_devices'] = [(d.name, d.type) for d in cp.devices]
except Exception as e:
    out['cycles_devices'] = repr(e)
out['denoisers'] = enum_items(sc.cycles, 'denoiser')
try:
    import numpy; out['numpy'] = numpy.__version__
except Exception as e: out['numpy'] = repr(e)
print(json.dumps(out, indent=1, ensure_ascii=False))
