# P0 test asset: one curved Ti panel (solidify + bevel + weighted normals, anisotropic, U along "fiber")
# plus 6 TiN fasteners. Exercises: modifiers, tangents, extras, AO bake, glTF export.
import bpy, bmesh, math, os, sys
from mathutils import Vector
OUT = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else 'assets_src'
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'; sc.unit_settings.scale_length = 1.0

# curved sheet 0.16 x 0.10 m on a 0.12 m radius cylinder
me = bpy.data.meshes.new('ME-MM1-TEST-PANEL'); bm = bmesh.new()
nu, nv, R, W, H = 24, 16, 0.12, 0.16, 0.10
verts = [[bm.verts.new((R*math.sin((i/nu-0.5)*W/R), -R*math.cos((i/nu-0.5)*W/R)+R, (j/nv-0.5)*H)) for j in range(nv+1)] for i in range(nu+1)]
uv_layer = bm.loops.layers.uv.new('UVMap')
for i in range(nu):
    for j in range(nv):
        f = bm.faces.new((verts[i][j], verts[i+1][j], verts[i+1][j+1], verts[i][j+1]))
        for loop, (a, b) in zip(f.loops, [(i, j), (i+1, j), (i+1, j+1), (i, j+1)]):
            loop[uv_layer].uv = (a/nu, b/nv)        # U = "fiber" direction
bm.to_mesh(me); bm.free()
panel = bpy.data.objects.new('GEO-MM1-TEST-PANEL-C-01', me); sc.collection.objects.link(panel)
for p in me.polygons: p.use_smooth = True
so = panel.modifiers.new('Solidify', 'SOLIDIFY'); so.thickness = 0.001; so.offset = -1; so.use_even_offset = True
bv = panel.modifiers.new('Bevel', 'BEVEL'); bv.width = 0.0004; bv.segments = 2; bv.limit_method = 'ANGLE'; bv.face_strength_mode = 'FSTR_AFFECTED'
wn = panel.modifiers.new('WeightedNormal', 'WEIGHTED_NORMAL'); wn.mode = 'FACE_AREA_WITH_ANGLE'; wn.use_face_influence = True; wn.keep_sharp = True
panel['mm1_part_id'] = 'MM1-TEST-PANEL-C-01'; panel['mass_g'] = round(W*H*0.001*4430*1000, 1); panel['roles'] = 'D,P'

def material(name, f0, rough, aniso, img=None):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    p = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value = (*f0, 1); p.inputs['Metallic'].default_value = 1.0
    p.inputs['Roughness'].default_value = rough; p.inputs['Anisotropic'].default_value = aniso
    t = nt.nodes.new('ShaderNodeTangent'); t.direction_type = 'UV_MAP'; t.uv_map = 'UVMap'
    nt.links.new(t.outputs['Tangent'], p.inputs['Tangent'])
    if img:
        tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = img; tex.image.colorspace_settings.name = 'Non-Color'
        sep = nt.nodes.new('ShaderNodeSeparateColor'); nt.links.new(tex.outputs['Color'], sep.inputs[0])
        # glTF exporter reads occlusion from a glTF Material Output/settings group; keep AO as separate image for compression test
    return m
ti = material('MA-ti64_beadblast', (0.441, 0.400, 0.361), 0.36, 0.55)
tin = material('MA-tin_polished', (0.614, 0.462, 0.233), 0.15, 0.0)
panel.data.materials.append(ti)

# fasteners (M2.5 countersunk proxies) along the panel border
for k in range(6):
    a = (k/5 - 0.5) * (W*0.85) / R
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.0025, depth=0.0012,
        location=(R*math.sin(a)*1.0005, -R*math.cos(a)*1.0005 + R + 0.0003, H*0.42))
    f = bpy.context.active_object; f.name = f'GEO-MM1-TEST-FIX-C-{k:02d}'
    f.rotation_euler = (math.pi/2, 0, a); f.data.materials.append(tin)
    f['mm1_part_id'] = f'MM1-FIX-CS-M2.5-{k:02d}'
    b = f.modifiers.new('Bevel', 'BEVEL'); b.width = 0.0003; b.segments = 2
    for p in f.data.polygons: p.use_smooth = True

# bake AO for the panel (512px) → PNG (compression test texture)
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 64
img = bpy.data.images.new('IM-MM1-TEST-PANEL-ao', 512, 512)
nt = ti.node_tree; tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = img; nt.nodes.active = tn
bpy.ops.object.select_all(action='DESELECT'); panel.select_set(True); bpy.context.view_layer.objects.active = panel
bpy.ops.object.bake(type='AO', margin=8)
img.filepath_raw = os.path.abspath(os.path.join(OUT, 'panel_ao.png')); img.file_format = 'PNG'; img.save()
nt.nodes.remove(tn)

bpy.ops.object.select_all(action='SELECT')
fp = os.path.abspath(os.path.join(OUT, 'test_panel.glb'))
bpy.ops.export_scene.gltf(filepath=fp, export_format='GLB', export_apply=True, export_tangents=True, export_extras=True, use_selection=True)
print('EXPORTED', fp, os.path.getsize(fp), 'bytes')
