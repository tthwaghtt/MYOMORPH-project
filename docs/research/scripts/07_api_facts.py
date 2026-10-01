import bpy
def props(t): return {p.identifier: (p.type, [i.identifier for i in p.enum_items] if p.type=='ENUM' else getattr(p,'default',None)) for p in t.bl_rna.properties}
print('Mesh.use_auto_smooth exists:', 'use_auto_smooth' in bpy.types.Mesh.bl_rna.properties)
u = bpy.ops.uv.unwrap.get_rna_type().properties; print('uv.unwrap method:', [i.identifier for i in u['method'].enum_items])
pk = bpy.ops.uv.pack_islands.get_rna_type().properties; print('pack_islands:', {k: ([i.identifier for i in pk[k].enum_items] if pk[k].type=='ENUM' else pk[k].default) for k in ['shape_method','rotate_method','margin_method','margin','udim_source']})
bv = props(bpy.types.BevelModifier); print('Bevel:', {k: bv[k] for k in ['limit_method','profile_type','face_strength_mode','harden_normals','miter_outer','vmesh_method','affect'] if k in bv})
wn = props(bpy.types.WeightedNormalModifier); print('WeightedNormal:', {k: wn[k] for k in ['mode','weight','thresh','keep_sharp','use_face_influence'] if k in wn})
so = props(bpy.types.SolidifyModifier); print('Solidify:', {k: so[k] for k in ['solidify_mode','nonmanifold_thickness_mode','use_rim','use_even_offset','use_quality_normals','offset'] if k in so})
sw = props(bpy.types.ShrinkwrapModifier); print('Shrinkwrap:', {k: sw[k] for k in ['wrap_method','wrap_mode'] if k in sw})
dt = props(bpy.types.DataTransferModifier); print('DataTransfer loop data types:', dt.get('data_types_loops'))
rm = props(bpy.types.RemeshModifier); print('Remesh modes:', rm['mode'])
mb = props(bpy.types.ShaderNodeBsdfMetallic) if hasattr(bpy.types,'ShaderNodeBsdfMetallic') else None
print('Metallic BSDF fresnel types:', mb['fresnel_type'] if mb else 'n/a', '| distribution:', mb['distribution'] if mb else '')
pb = props(bpy.types.ShaderNodeBsdfPrincipled); print('Principled:', {k: pb[k] for k in ['distribution','subsurface_method'] if k in pb})
gn = sorted(t for t in dir(bpy.types) if t.startswith('GeometryNode') and ('SDF' in t or 'Grid' in t or 'Points' in t))
print('SDF/grid/points nodes:', gn)
