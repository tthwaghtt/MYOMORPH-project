"""MYOMORPH-MK. 1 panel materials (kept from R2, 2026-10-03; Doha: 'not too shiny, slight wear').

Finishes (F0 linear sRGB, roughness): ti bead-blast (0.40 0.378 0.352, 0.54) · ti hairline (0.45 0.425 0.395, 0.44,
anisotropic) · ti dark PVD (0.11 0.105 0.10, 0.56) · TiN gold hairline / bead-blast (coating worn through to Ti on edges
and scratches) · black anodize · elastomer · smoked visor. Spec: docs/storyboard/BIBLES.md (A2).

Attribute contract (the R2 shell carried these per vertex; the reference-based panels must provide them, e.g. from
bevel / curvature / AO bakes, or the nodes are re-wired):
  groove  0..1  dark gap at a panel edge (also where NERVUS light pipes glow)
  edge    0..1  burnished chamfer face
  grime   0..1  dirt settling beside edges
  fiber   vec3  brushing direction (anisotropic finishes)
  muscle  int   panel id (per-panel batch variation of colour and roughness)
  visor   0..1  eye-slit / visor mix (smoked polycarbonate + display glow)
View-layer properties: myo_wear (wear amount, 1 = lightly used), myo_lp (light pipes), myo_slit (glow behind the slits).
"""
import bpy
import lib

FIN = {}


def _panel_material(name, f0, rough, aniso=0.0, metal=1.0, coating=None):
    """Panel metal driven by shell attributes (R2: matte, lightly worn - Doha 2026-10-03 'not too shiny, some wear').
    Layers: per-panel batch variation (each panel its own forming + blasting run); dark seam gap; grime settling in
    the 2-10 mm beside every seam; burnished hem chamfer; sparse handling scratches (Voronoi edge segments masked by
    noise); low-frequency handling smudges in roughness; for coated finishes (TiN) the coating worn through to grey
    titanium on the hem and at scratches. Wear amount: view-layer property 'myo_wear' (default 1 = lightly used)."""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N, Lk = nt.nodes, nt.links
    p = next(x for x in N if x.type == 'BSDF_PRINCIPLED'); p.distribution = 'MULTI_GGX'
    def att(nm, kind='GEOMETRY'):
        a = N.new('ShaderNodeAttribute'); a.attribute_name = nm; a.attribute_type = kind; return a
    def mr(src, a, b, c, d, clamp=True):
        r = N.new('ShaderNodeMapRange'); r.inputs['From Min'].default_value = a; r.inputs['From Max'].default_value = b
        r.inputs['To Min'].default_value = c; r.inputs['To Max'].default_value = d; r.clamp = clamp; Lk.new(src, r.inputs['Value']); return r.outputs['Result']
    def math_(op, a, b=None, v=None):
        n_ = N.new('ShaderNodeMath'); n_.operation = op
        Lk.new(a, n_.inputs[0]) if not isinstance(a, (int, float)) else setattr(n_.inputs[0], 'default_value', a)
        if b is not None:
            Lk.new(b, n_.inputs[1]) if not isinstance(b, (int, float)) else setattr(n_.inputs[1], 'default_value', b)
        return n_.outputs[0]
    def mixc(fac, a, b):
        x = N.new('ShaderNodeMix'); x.data_type = 'RGBA'
        Lk.new(fac, x.inputs['Factor'])
        (Lk.new(a, x.inputs['A']) if not isinstance(a, tuple) else setattr(x.inputs['A'], 'default_value', a))
        (Lk.new(b, x.inputs['B']) if not isinstance(b, tuple) else setattr(x.inputs['B'], 'default_value', b))
        return x.outputs['Result']
    def mixf(fac, a, b):
        x = N.new('ShaderNodeMix'); x.data_type = 'FLOAT'
        Lk.new(fac, x.inputs['Factor'])
        (Lk.new(a, x.inputs['A']) if not isinstance(a, (int, float)) else setattr(x.inputs['A'], 'default_value', a))
        (Lk.new(b, x.inputs['B']) if not isinstance(b, (int, float)) else setattr(x.inputs['B'], 'default_value', b))
        return x.outputs['Result']
    g, e, fb, mu, gr = att('groove'), att('edge'), att('fiber'), att('muscle'), att('grime')
    wear = att('myo_wear', 'VIEW_LAYER')
    tc = N.new('ShaderNodeTexCoord')
    h = N.new('ShaderNodeTexWhiteNoise'); h.noise_dimensions = '1D'; Lk.new(mu.outputs['Fac'], h.inputs['W'])
    var = mr(h.outputs['Value'], 0, 1, 0.95, 1.035)
    col = N.new('ShaderNodeVectorMath'); col.operation = 'SCALE'; col.inputs[0].default_value = f0
    Lk.new(var, col.inputs['Scale'])
    base_col = col.outputs['Vector']
    # sparse scratches: Voronoi cell edges (straight segments), thinned and masked by a coarse noise
    vor = N.new('ShaderNodeTexVoronoi'); vor.feature = 'DISTANCE_TO_EDGE'; vor.inputs['Scale'].default_value = 34.0
    Lk.new(tc.outputs['Object'], vor.inputs['Vector'])
    scr = mr(vor.outputs['Distance'], 0.0, 0.006, 1.0, 0.0)
    msk = N.new('ShaderNodeTexNoise'); msk.inputs['Scale'].default_value = 7.0; msk.inputs['Detail'].default_value = 2.0
    Lk.new(tc.outputs['Object'], msk.inputs['Vector'])
    scr = math_('MULTIPLY', scr, mr(msk.outputs['Fac'], 0.56, 0.66, 0.0, 1.0))
    scr = math_('MULTIPLY', scr, wear.outputs['Fac'])
    # handling smudges
    smd = N.new('ShaderNodeTexNoise'); smd.inputs['Scale'].default_value = 3.2; smd.inputs['Detail'].default_value = 4.0
    Lk.new(tc.outputs['Object'], smd.inputs['Vector'])
    smudge = math_('MULTIPLY', mr(smd.outputs['Fac'], 0.45, 0.75, 0.0, 1.0), wear.outputs['Fac'])
    # grime beside the seams, burnished hem
    grime = math_('MULTIPLY', gr.outputs['Fac'], wear.outputs['Fac'])
    hem_wear = math_('MULTIPLY', e.outputs['Fac'], mr(msk.outputs['Fac'], 0.35, 0.6, 0.35, 1.0))
    hem_wear = math_('MULTIPLY', hem_wear, wear.outputs['Fac'])
    c1 = base_col
    if coating is not None:            # TiN worn through to titanium on the hem and in scratches
        thru = math_('MAXIMUM', math_('MULTIPLY', hem_wear, 0.9), scr)
        c1 = mixc(thru, c1, coating)
    c1 = mixc(math_('MULTIPLY', grime, 0.32), c1, (0.07, 0.065, 0.06, 1))      # slight wear: grime settles, it does not stain
    c1 = mixc(math_('MULTIPLY', scr, 0.25), c1, (0.62, 0.60, 0.57, 1))
    c1 = mixc(g.outputs['Fac'], c1, (0.005, 0.005, 0.006, 1))
    mt = math_('SUBTRACT', metal, g.outputs['Fac']); 
    rv = mr(h.outputs['Value'], 0, 1, rough * 0.93, rough * 1.08)
    r1 = mixf(math_('MULTIPLY', smudge, 0.5), rv, rough * 0.82)
    r1 = mixf(math_('MULTIPLY', grime, 0.6), r1, min(rough * 1.18, 0.9))
    r1 = mixf(e.outputs['Fac'], r1, max(rough * 0.62, 0.30))
    r1 = mixf(scr, r1, 0.30)
    if aniso:
        p.inputs['Anisotropic'].default_value = aniso
        Lk.new(fb.outputs['Vector'], p.inputs['Tangent'])
    # NERVUS light pipes in the seams: strength from the view-layer property 'myo_lp' (0 = off)
    lpv = att('myo_lp', 'VIEW_LAYER'); slv = att('myo_slit', 'VIEW_LAYER')
    p.inputs['Emission Color'].default_value = (0.62, 0.9, 1.0, 1)
    # PERSONA eye slits (smoked polycarbonate) blended in by the 'visor' attribute; 'myo_slit' = display glow behind them
    vz = att('visor')
    Lk.new(math_('ADD', math_('MULTIPLY', g.outputs['Fac'], lpv.outputs['Fac']), math_('MULTIPLY', vz.outputs['Fac'], slv.outputs['Fac'])), p.inputs['Emission Strength'])
    Lk.new(mixc(vz.outputs['Fac'], c1, (0.008, 0.009, 0.011, 1)), p.inputs['Base Color'])
    Lk.new(mixf(vz.outputs['Fac'], mt, 0.0), p.inputs['Metallic'])
    Lk.new(mixf(vz.outputs['Fac'], r1, 0.04), p.inputs['Roughness'])
    Lk.new(vz.outputs['Fac'], p.inputs['Coat Weight']); p.inputs['Coat Roughness'].default_value = 0.02
    # bead-blast micro relief + scratch grooves
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1600.0; nz.inputs['Detail'].default_value = 3
    hgt = math_('SUBTRACT', math_('MULTIPLY', nz.outputs['Fac'], 0.6), math_('MULTIPLY', scr, 0.8))
    bpn = N.new('ShaderNodeBump'); bpn.inputs['Strength'].default_value = 0.06; bpn.inputs['Distance'].default_value = 0.00004
    Lk.new(hgt, bpn.inputs['Height']); Lk.new(bpn.outputs['Normal'], p.inputs['Normal'])
    return m


def _visor_material():
    """Smoked polycarbonate with hard coat: near-black, glossy clear coat, faint transmission (opaque from outside)."""
    m = bpy.data.materials.new('MA-persona_visor'); m.use_nodes = True
    p = next(x for x in m.node_tree.nodes if x.type == 'BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value = (0.012, 0.013, 0.015, 1); p.inputs['Roughness'].default_value = 0.05
    p.inputs['Metallic'].default_value = 0.0; p.inputs['IOR'].default_value = 1.58
    p.inputs['Coat Weight'].default_value = 1.0; p.inputs['Coat Roughness'].default_value = 0.02
    return m


def set_lightpipes(strength):
    bpy.context.view_layer['myo_lp'] = float(strength)


def set_slit_glow(strength):
    bpy.context.view_layer['myo_slit'] = float(strength)


def set_wear(amount=1.0):
    bpy.context.view_layer['myo_wear'] = float(amount)


def suit_materials():
    """the finish set, created once per scene (lib.new_scene clears the cache)."""
    if FIN:
        return FIN
    if 'myo_wear' not in bpy.context.view_layer: set_wear(1.0)
    FIN.update({
        'ti': _panel_material('MA-suit_ti_beadblast', (0.40, 0.378, 0.352), 0.54),
        'ti_hair': _panel_material('MA-suit_ti_hairline', (0.45, 0.425, 0.395), 0.44, aniso=0.45),
        'ti_dark': _panel_material('MA-suit_ti_dark_pvd', (0.11, 0.105, 0.10), 0.56),
        'tin_hair': _panel_material('MA-suit_tin_hairline', (0.60, 0.44, 0.20), 0.44, aniso=0.5, coating=(0.43, 0.405, 0.375, 1)),
        'tin_satin': _panel_material('MA-suit_tin_beadblast', (0.56, 0.415, 0.195), 0.54, coating=(0.43, 0.405, 0.375, 1)),
        'anod': _panel_material('MA-suit_black_anodize', (0.02, 0.02, 0.022), 0.50, metal=0.0),
        'rubber': lib.mat_basic('MA-suit_elastomer', (0.025, 0.025, 0.026), rough=0.8),
        'visor': _visor_material(),
    })
    return FIN
