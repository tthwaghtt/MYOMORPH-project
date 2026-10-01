import bpy
sc = bpy.context.scene; c = sc.cycles
names = [p.identifier for p in c.bl_rna.properties]
print('cycles guiding:', [n for n in names if 'guiding' in n][:8])
print('cycles texture cache:', [n for n in names if 'cache' in n or 'texture' in n][:10])
print('cycles light tree:', [n for n in names if 'light_tree' in n or 'tree' in n])
print('cycles adaptive:', [n for n in names if 'adaptive' in n])
print('cycles denoise:', [n for n in names if 'denois' in n][:12])
print('light linking on Object:', 'light_linking' in bpy.types.Object.bl_rna.properties, [p.identifier for p in bpy.types.LightLinking.bl_rna.properties] if hasattr(bpy.types,'LightLinking') else '')
print('camera dof props:', [p.identifier for p in bpy.types.CameraDOFSettings.bl_rna.properties][:12])
print('camera sensor default:', bpy.types.Camera.bl_rna.properties['sensor_width'].default, 'lens', bpy.types.Camera.bl_rna.properties['lens'].default)
print('light units: area energy unit:', bpy.types.AreaLight.bl_rna.properties['energy'].unit, '| exposure prop on light:', 'exposure' in bpy.types.Light.bl_rna.properties, '| normalize:', 'normalize' in bpy.types.Light.bl_rna.properties)
