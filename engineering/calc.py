"""MYOMORPH-MK. 1 engineering bible v2 -> engineering.json + bom.json (every number on the site comes from here).

v2 (R2, 2026-10-03, Doha feedback): all machines outside the wearer, slim blueprint silhouette kept, performance
reduced to fit it, battery built into two back panels, external cable only where unavoidable (charging, optional
chill line, bring-up in the cell). Mass comes from the bill of materials (bom.py) and the sizing is iterated to a
fixed point with it (heavier suit -> bigger muscles -> heavier suit).

Inputs: CORPUS profile (docs/research/corpus), fitted mannequin (previs/wearer_fit.json), and - PROVISIONAL until the
reference-based suit exists - the panel count and shell area in engineering/provisional_inputs.json (frozen from the
retired R2 shell). The single declared exception to present-day engineering is the battery cell energy density (2036
assumption, Doha's brief).
Run: python engineering/calc.py
"""
import json, math, os
import bom

R = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(R, '..')
J = lambda *p: json.load(open(os.path.join(ROOT, *p)))
A = J('docs', 'research', 'corpus', 'anthro.json')['measurements']
FIT = J('previs', 'wearer_fit.json')['measurements']; PI = J('engineering', 'provisional_inputs.json')
MUS = {m['key']: m for m in J('docs', 'research', 'corpus', 'muscles.json')['muscles']}
g = 9.81
m_w, H = 65.0, 1.78
mm = lambda k: (FIT.get(k) or {}).get('fit_mm') or A[k]['value_mm']

# ---------------------------------------------------------------- wearer segments (de Leva 1996, male)
L = {'upper_arm': mm('acromionradialelength') / 1000, 'forearm': mm('radialestylionlength') / 1000,
     'hand': mm('handlength') / 1000, 'thigh': (mm('trochanterionheight') - mm('lateralfemoralepicondyleheight')) / 1000,
     'shank': (mm('lateralfemoralepicondyleheight') - mm('lateralmalleolusheight')) / 1000, 'foot': mm('footlength') / 1000}
DELEVA = {'head_neck': (0.0694, None), 'trunk': (0.4346, None), 'upper_arm': (0.0271, 0.5772), 'forearm': (0.0162, 0.4574),
          'hand': (0.0061, 0.7900), 'thigh': (0.1416, 0.4095), 'shank': (0.0433, 0.4459), 'foot': (0.0137, 0.4415)}
seg = {k: {'mass_kg': round(f * m_w, 2), 'com_from_proximal': c, 'length_m': round(L[k], 3) if k in L else None} for k, (f, c) in DELEVA.items()}
body_above = {'hip': 1 - 2 * (DELEVA['thigh'][0] + DELEVA['shank'][0] + DELEVA['foot'][0]),
              'knee': 1 - 2 * (DELEVA['shank'][0] + DELEVA['foot'][0]), 'ankle': 1 - 2 * DELEVA['foot'][0]}

# ---------------------------------------------------------------- design rules (R2)
ASSIST = 0.25            # share of the wearer's own peak joint moment the suit adds (v1: 0.40) - reduced to fit the slim shell
P_SYS = 21e6             # EHA working pressure
PEAK = {'hip': 1.2, 'knee': 1.3, 'ankle': 1.5}          # N·m/kg, hardest everyday task (stairs, sit-to-stand, push-off)
ARM_R = {'hip': 0.040, 'knee': 0.032, 'ankle': 0.045}    # effective moment arms (m)
ROM = {'hip': 130, 'knee': 125, 'ankle': 55}             # deg, actuated range
OMEGA_ASSIST = {'hip': 2.0, 'knee': 2.0, 'ankle': 3.0}   # rad/s at peak assisted torque (stair ascent / push-off)
TOOL_KG = 3.0            # held tool for the arm cases (v1: 5 kg)
PANEL_T = 0.6            # mm, Ti-6Al-4V SPIF panels (v1: 0.9)
# where each module's mass sits (for the moment each joint must carry): trunk/head/arm count above the hip
SEGMENT_OF = {'FAS-SUIT': {'trunk': .45, 'arm': .15, 'thigh': .25, 'shank': .15}, 'FAS-BALA': {'trunk': 1}, 'FAS-GLOVE': {'arm': 1},
              'PES-BOOT': {'foot': 1}, 'OS-LEG': {'thigh': .6, 'shank': .4}, 'OS-PELVIS': {'trunk': .7, 'thigh': .3},
              'MUS-EHA-HIP': {'trunk': .5, 'thigh': .5}, 'OS-ARM': {'arm': 1}, 'TEN-ELBOW': {'arm': 1}, 'TEN-SHOULDER': {'trunk': .6, 'arm': .4},
              'FUN-TOOLBAY': {'arm': 1}, 'FUN-HAND': {'arm': 1}, 'FUN-PORT': {'arm': 1}, 'MUS-EHA-KNEE': {'thigh': .8, 'shank': .2}, 'MUS-EHA-ANKLE': {'shank': .9, 'foot': .1},
              'MYO-PANELS': {'trunk': .38, 'arm': .20, 'thigh': .19, 'shank': .12, 'foot': .05, 'trunk_head': .06},
              'FIX-INSTALL': {'trunk': .38, 'arm': .20, 'thigh': .19, 'shank': .12, 'foot': .05, 'trunk_head': .06}}


def eha_size(T_peak, j):
    T = T_peak * 1.25; r = ARM_R[j]; F = T / r
    bore = 2 * math.sqrt(F / P_SYS / math.pi)
    b = next(x for x in (0.010, 0.012, 0.014, 0.016, 0.018, 0.020, 0.025) if x >= bore)
    Acap = math.pi * b ** 2 / 4
    stroke = 2 * r * math.sin(math.radians(ROM[j]) / 2)
    P_mech = T_peak * OMEGA_ASSIST[j]
    motor_W = P_mech / (0.85 * 0.95)
    od = b * 1000 + 6.0
    thick = max(od, 18.0)                    # flat motor (axis normal to the skin) is 18 mm; cylinder OD otherwise
    length = 2 * stroke * 1000 + 70
    return {'design_torque_Nm': round(T, 1), 'force_kN': round(F / 1000, 2), 'bore_mm': round(b * 1000, 0), 'rod_mm': round(b * 500, 0),
            'stroke_mm': round(stroke * 1000, 1), 'thrust_kN_at_21MPa': round(Acap * P_SYS / 1000, 2), 'pressure_MPa': 21,
            'motor_W': round(motor_W, 0), 'peak_flow_L_min': round(Acap * OMEGA_ASSIST[j] * r * 60000, 2),
            'envelope_mm': (round(length), 44, round(thick)), 'moment_arm_mm': r * 1000}


# ---------------------------------------------------------------- undersuit cooling garment (LCG)
LCG_Q = 150.0            # W removed by the cooling garment (half of ~300 W body heat at moderate work; the rest leaves by
                         # sweat evaporation into the ventilated gap under the panels, which the louvre fans keep moving)
# membrane gill (indirect evaporative cooler): water leaves near the ambient wet bulb + 3 K approach
AMB_C, AMB_RH = 30.0, 0.40
def wet_bulb(T, RH):     # Stull 2011 empirical fit, +/-0.3 K for RH 5-99 %, T -20..50 C
    return (T * math.atan(0.151977 * (RH * 100 + 8.313659) ** 0.5) + math.atan(T + RH * 100) - math.atan(RH * 100 - 1.676331)
            + 0.00391838 * (RH * 100) ** 1.5 * math.atan(0.023101 * RH * 100) - 4.686035)
T_WB = wet_bulb(AMB_C, AMB_RH)
T_SKIN, T_IN, DT_W = 33.0, T_WB + 3.0, 1.5
lcg_flow = LCG_Q / (4186 * DT_W)                         # kg/s
UA_need = LCG_Q / (T_SKIN - (T_IN + DT_W / 2))
UA_per_m = 0.22                                         # W/(m·K), compression-fit knit (NASA LCVG ~0.17 loose)
tube_m = UA_need / UA_per_m
n_circ = 24
q_circ = lcg_flow / 1000 / n_circ; D = 1.6e-3; mu = 1.0e-3
dp_tube = 128 * mu * (tube_m / n_circ) * q_circ / (math.pi * D ** 4)
re = 1000 * (q_circ / (math.pi * D ** 2 / 4)) * D / mu
dp_total = dp_tube + 10e3
pump_W = dp_total * lcg_flow / 1000 / 0.15
cover_m2 = tube_m * 0.015

# ---------------------------------------------------------------- neural interface
EMG_GRIDS = {k: 2 for k in ('vaslat', 'vasmed', 'recfem', 'bflh', 'semiten', 'glmax', 'gasmed', 'gaslat', 'soleus', 'tibant', 'BIC', 'TRI')}
emg_grids = sum(EMG_GRIDS.values()); emg_bip = 16; emg_ch = emg_grids * 32 + emg_bip
US_ = J('engineering', 'undersuit.json') if os.path.exists(os.path.join(R, 'undersuit.json')) else None
emg_nodes = US_['totals']['nodes'] if US_ else math.ceil(emg_ch / 64)       # previs/undersuit.py groups sites per segment
eeg_ch = 32
latency = {'EMG window (sliding, 5 ms hop)': 25, 'motor-unit decomposition + torque estimate': 5, 'EtherCAT cycle': 0.25,
           'control law': 1, 'EHA pressure rise': 12}
lat_ms = round(sum(latency.values()), 1)

# ---------------------------------------------------------------- battery panels (2036 cells)
CELL = {'Wh_per_kg': 600, 'Wh_per_L': 1300, 'dims_mm': (70, 55, 6)}
cell_L = CELL['dims_mm'][0] * CELL['dims_mm'][1] * CELL['dims_mm'][2] / 1e6
cell_Wh = cell_L * CELL['Wh_per_L']; cell_g = cell_Wh / CELL['Wh_per_kg'] * 1000
cells_per_panel = 14                                      # 14s, 48 V class bus; two panels in parallel (ideal-diode OR)
kWh_each = cells_per_panel * cell_Wh / 1000
area_each = cells_per_panel * CELL['dims_mm'][0] * CELL['dims_mm'][1] / 1e6 / 0.80

# ---------------------------------------------------------------- panels
area_shell = PI['shell_area_m2']                          # PROVISIONAL (provisional_inputs.json)
panel_area = area_shell - 0.13                            # helmet crown/occipital shells are counted in PERSONA
groups = {g_['name']: {'n': g_['n'], 'size': g_['size'], 'mounts': g_['mounts']} for g_ in PI['panel_groups']}
norm = sum(v['n'] * v['size'] for v in groups.values()) / sum(v['n'] for v in groups.values())
for v in groups.values(): v['size'] = round(v['size'] / norm, 4)

# ---------------------------------------------------------------- fixed point: BOM mass <-> sizing
m_suit = 40.0; S = None
for it in range(8):
    seg_mass = {'trunk': 0.0, 'arm': 0.0, 'thigh': 0.0, 'shank': 0.0, 'foot': 0.0}
    if S is not None:
        for mod in B['modules']:
            sp = SEGMENT_OF.get(mod['id'], {'trunk': 1})
            for k, f in sp.items():
                seg_mass['trunk' if k.startswith('trunk') else k] += mod['mass_kg_total'] * f
        seg_mass['trunk'] += fluids_kg
        m_suit = sum(seg_mass.values())
        above = {'hip': seg_mass['trunk'] + seg_mass['arm'], 'knee': m_suit - seg_mass['shank'] - seg_mass['foot'], 'ankle': m_suit - seg_mass['foot']}
    else:
        above = {'hip': 0.62 * m_suit, 'knee': 0.85 * m_suit, 'ankle': 0.95 * m_suit}
    tq = {}
    for j, k in PEAK.items():
        # the human peak k (N·m per kg of body mass) is produced by the body mass above the joint (body_above share), so
        # per kg of mass above the joint it is k / body_above. The suit carries all of its own (single support) and adds
        # ASSIST of the wearer's own moment.
        suit_self = k / body_above[j] * above[j]
        tq[j] = {'peak_Nm': round(suit_self + ASSIST * k * m_w, 1), 'suit_self_Nm': round(suit_self, 1), 'assist_Nm': round(ASSIST * k * m_w, 1)}
    eh = {j: eha_size(tq[j]['peak_Nm'], j) for j in PEAK}
    # arms: forearm horizontal with the tool; suit forearm mass ~ arm share / 2 per side split proximal/distal
    m_fore_suit = (seg_mass['arm'] / 2 * 0.45) if S else 1.0
    T_el = g * ((m_fore_suit * 0.5 + ASSIST * (DELEVA['forearm'][0] + DELEVA['hand'][0]) * m_w) * L['forearm'] * 0.55 + TOOL_KG * ASSIST * (L['forearm'] + L['hand'] * 0.5))
    T_el_design = T_el * 1.25; r_pul = 0.022
    elbow = {'design_torque_Nm': round(T_el_design, 1), 'tendon_N': round(T_el_design / r_pul, 0), 'pulley_mm': r_pul * 1000,
             'motor_Nm_cont': 0.25, 'reduction': round(T_el_design / (0.25 * 0.85), 1)}
    m_arm_suit = (seg_mass['arm'] / 2) if S else 2.0
    m_arm_w = (DELEVA['upper_arm'][0] + DELEVA['forearm'][0] + DELEVA['hand'][0]) * m_w
    arm_len = L['upper_arm'] + L['forearm'] + L['hand'] * 0.5
    comp = g * (m_arm_suit + 0.6 * m_arm_w) * arm_len * 0.45
    shoulder = {'comp_Nm': round(comp, 1), 'energy_J': round(comp, 1)}
    # power
    mech_avg = 1.6 * (m_suit + ASSIST * m_w)
    eta_eha = 0.55
    gill = {'cooling_W': LCG_Q, 'water_out_C': round(T_IN, 1), 'wet_bulb_C': round(T_WB, 1), 'L_per_h': round(LCG_Q / 2.43e6 * 3600, 3),
            'duty_mixed': 0.7}
    elec = {'muscles (EHA, pump-controlled)': mech_avg / eta_eha, 'compute (spine core)': 15.0,
            'neural sensing (EMG 800 ch + EEG 32 ch)': 3.5, 'IMU, encoders, load cells': 1.5, 'cameras + displays': 3.5,
            'bus + networking': 2.5, 'status lights': 1.5, 'helmet air (PAPR)': 3.0, 'coolant pump': round(pump_W, 1),
            'louvre fans (6)': 7.2, 'gill dosing pump': 0.6, 'muscle standby / holding': 8.0}
    P_avg = sum(elec.values()) * 1.04
    E_pack = 2 * kWh_each
    runtime = E_pack * 1000 * 0.95 / P_avg
    water_h = 0.6 / (gill['L_per_h'] * gill['duty_mixed'])
    # thermal: sensible heat to air (muscle losses + electronics) and the air the gills need to carry the evaporated water
    eha_loss = mech_avg / eta_eha - mech_avg
    q_air = eha_loss + 45.0
    air_sensible = q_air / (1005 * 12.0)
    w_in = 0.622 * AMB_RH * 4.246 / (101.325 - AMB_RH * 4.246)                     # humidity ratio at 30 C, 40 % (psat 4.246 kPa)
    air_gill = (LCG_Q / 2.43e6) / (0.6 * (0.622 * 3.17 / (101.325 - 3.17) - w_in) + 1e-9)   # 60 % of the way to saturation at 25 C
    air_L_s = (air_sensible + air_gill) / 1.2 * 1000 + 10.0                      # + 10 L/s gap ventilation
    pcm_kJ = round(6 * 0.070 * 200)
    # PAPR
    VO2 = 330 / 20.1 * 60 / 1000                          # L/min
    VCO2 = 0.85 * VO2
    papr = {'flow_L_min': 160, 'inspired_CO2_pct': round(0.04 + 0.2 * VCO2 / 160 * 100, 2),
            'inspired_CO2_pct_no_cup': round(0.04 + VCO2 / 160 * 100, 2), 'power_W': 3.0, 'standard': 'EN 12941 TH3 flow class'}
    fluids_kg = 0.25 + tube_m * 0.002 + 0.5 + 0.6
    S = {'lcg_tube_m': tube_m, 'lcg_circuits': n_circ, 'lcg_flow_L_min': round(lcg_flow * 60, 2),
         'emg_grids': emg_grids, 'emg_bipolar': emg_bip, 'emg_nodes': emg_nodes, 'emg_channels': emg_ch, 'eeg_ch': eeg_ch,
         'eha': eh, 'elbow': elbow, 'shoulder': shoulder,
         'gill': gill, 'battery': {'cells_per_panel': cells_per_panel, 'cell_g': round(cell_g, 1), 'kWh_each': round(kWh_each, 3),
                     'thickness_mm': 9, 'area_m2_each': round(area_each, 4), 'buffer_Wh': 6,
                     'envelope_mm': (round(math.sqrt(area_each * 1.6) * 1000), round(math.sqrt(area_each / 1.6) * 1000), 9)},
         'gill': gill, 'papr': papr, 'pcm_kJ': pcm_kJ, 'fan_L_s_each': round(air_L_s / 6, 1), 'latency_ms': lat_ms,
         'lightpipes': 124, 'panel_groups': groups, 'panel_t_mm': PANEL_T, 'panel_area_m2': panel_area, 'panel_picks': 168}
    B = bom.build(S)

tq['shoulder'] = {'passive_comp_Nm': shoulder['comp_Nm'], 'case': f'arm at 90 deg, {TOOL_KG:g} kg tool trimmed by the worm'}
tq['elbow'] = {'peak_Nm': elbow['design_torque_Nm'], 'case': f'forearm horizontal, {TOOL_KG:g} kg tool, {int(ASSIST*100)} % assist'}
mass_by_system = {f"{k} · {v['name_ko']}": v.get('mass_kg', 0) for k, v in B['systems'].items()}
mass_by_system['fluids (coolant loop + garment, drinking 0.5 L, evaporant 0.6 L)'] = round(fluids_kg, 2)

out = {
    'version': 'v2 (R2, 2026-10-03)',
    'changes_from_v1': ['machines outside the wearer, layered: undersuit -> cuffs -> frame -> muscles -> systems -> panels',
                        'central HPU + 8 valve-controlled cylinders -> 6 sealed EHA muscles (pump-controlled, free-swing bypass)',
                        'assist 40 % -> 25 %, tool 5 kg -> 3 kg (slim silhouette)',
                        'battery 2.4 kWh in two modules -> 0.84 kWh inside two back panels',
                        'cooling: air only -> cooling undersuit + membrane gill (evaporative, no compressor: a 56 mm compressor does not fit the 27 mm lumbar space)',
                        'life support: PAPR helmet air, gas sensors, hydration, mechanical emergency release',
                        'control: EEG balaclava (intent, error) + 800 ch HD-EMG undersuit (neural drive)'],
    'wearer': {'stature_m': H, 'span_m': 1.82, 'mass_kg': m_w, 'body_fat_bia_pct': 10, 'body_fat_dxa_adopted_pct': 11,
               'ffm_kg': round(m_w * 0.89, 1), 'ffmi': round(m_w * 0.89 / H ** 2, 2),
               'waist_omphalion_cm': round(mm('waistcircumference') / 10, 1), 'bideltoid_cm': round(mm('bideltoidbreadth') / 10, 1),
               'chest_cm': round(mm('chestcircumference') / 10, 1), 'crotch_height_cm': round(mm('crotchheight') / 10, 1), 'segments': seg},
    'suit': {'height_m': 1.837, 'shell_area_m2': area_shell, 'panels': sum(v['n'] for v in groups.values()), 'panel_thickness_mm': PANEL_T,
             'parts_total': B['total_parts'], 'pre_assembled_modules': B['pre_assembled_modules'],
             'mass_total_kg': round(m_suit, 1), 'mass_worn_by_wearer_kg': round(B['worn_mass_kg'], 2),
             'mass_by_system_kg': mass_by_system, 'mass_by_segment_kg': {k: round(v, 2) for k, v in seg_mass.items()},
             'mass_ratio_to_wearer': round(m_suit / m_w, 2),
             'note': 'everything except the undersuit, balaclava and inner gloves stands on the boot soles through the frame'},
    'joint_torque': tq, 'muscles_eha': eh, 'elbow_tendon': elbow, 'shoulder_spring': shoulder, 'assist_ratio': ASSIST,
    'power': {'mechanical_avg_W': round(mech_avg, 0), 'electrical_avg_W': {k: round(v, 1) for k, v in elec.items()},
              'electrical_total_W': round(P_avg, 0), 'eha_efficiency': eta_eha, 'peak_W': round(sum(e['motor_W'] for e in eh.values()) * 2 * 0.6 + 120, 0)},
    'battery': {'energy_kWh': round(E_pack, 2), 'panels': 2, 'cells_per_panel': cells_per_panel, 'cell': CELL,
                'cell_Wh': round(cell_Wh, 1), 'cell_g': round(cell_g, 1), 'bus': '14s, 48 V class, two panels ideal-diode OR',
                'panel_area_m2_each': round(area_each, 4), 'runtime_mixed_h': round(runtime, 1), 'evaporant_runtime_h': round(water_h, 1),
                'swap': 'hot swap one panel at a time, 6 Wh buffer holds 90 s',
                'note': '2036 cell energy density is the one declared exception (Doha brief)'},
    'tether': {'needed_for': ['charging (dock or cable, ~50 min to 90 %)', 'chill line only when the ambient wet bulb exceeds ~26 C (hot and humid)',
                              'bring-up and diagnostics in the assembly cell'], 'not_needed_for': ['walking, lifting, tool work up to ~3 h']},
    'thermal': {'metabolic_W': 330, 'lcg_W': LCG_Q, 'lcg_flow_L_min': round(lcg_flow * 60, 2), 'lcg_inlet_C': round(T_IN, 1),
                'lcg_tube_m': round(tube_m, 1), 'lcg_circuits': n_circ, 'lcg_cover_m2': round(cover_m2, 2),
                'lcg_reynolds': round(re), 'lcg_dp_kPa': round(dp_total / 1000, 1), 'coolant_pump_W': round(pump_W, 1),
                'gill': gill, 'ambient_C': AMB_C, 'ambient_RH': AMB_RH, 'heat_to_air_W': round(q_air), 'air_dT_K': 12,
                'airflow_L_s': round(air_L_s, 1), 'fans': 6, 'pcm_kJ': pcm_kJ,
                'louvres': ['flank L/R (behind the vents drawn in the reference): membrane gills', 'upper back L/R: spine core, electronics']},
    'life_support': {'papr': papr, 'VO2_L_min': round(VO2, 2), 'VCO2_L_min': round(VCO2, 2), 'hydration_L': 0.5,
                     'emergency_release': 'one sternum handle, cable-actuated, no power needed',
                     'vitals': ['ECG 3-lead', 'SpO2 + HR (forehead PPG)', 'core temperature estimate (dual heat flux)', 'respiration', 'sweat'],
                     'derate': 'joint power limited when core temperature > 38.5 C'},
    'neural': {'emg_channels': emg_ch, 'emg_grids': emg_grids, 'emg_grid_muscles': list(EMG_GRIDS), 'emg_bipolar': emg_bip,
               'emg_nodes': emg_nodes, 'emg_fs_Hz': 2048, 'emg_raw_Mbit_s': round(emg_ch * 2048 * 24 / 1e6, 1),
               'eeg_channels': eeg_ch, 'eeg_fs_Hz': 500, 'latency_ms': latency, 'latency_total_ms': lat_ms,
               'human_electromechanical_delay_ms': [30, 100],
               'muscle_model': 'Hill-type, personalised from muscles.json (Fmax, optimal fibre length, pennation)',
               'muscle_model_examples': {k: {f: MUS[k][f] for f in ('ko', 'fmax_N', 'fibre_length_cm', 'pennation_deg')} for k in ('vaslat', 'recfem', 'gasmed', 'BIC')}},
    'provisional': PI['status'],
    'rom_deg': {'neck_flex_ext_rot': [40, 45, 70], 'trunk_flex_ext_lat_rot': [60, 20, 25, 35], 'shoulder_flex_abd_ext': [160, 150, 45],
                'elbow': [0, 135], 'wrist_flex_ext': [65, 60], 'hip_flex_ext_abd': [110, 20, 35], 'knee': [0, 125], 'ankle_dorsi_plantar': [15, 40]},
    'bom_summary': {'total_parts': B['total_parts'], 'robot_ops': B['robot_ops'],
                    'by_system': {k: {'parts': v.get('parts', 0), 'mass_kg': v.get('mass_kg', 0)} for k, v in B['systems'].items()},
                    'by_stage': {k: {'name_en': v['name_en'], 'parts': v.get('parts', 0), 'modules': v.get('modules', 0)} for k, v in B['stages'].items()}},
}
json.dump(out, open(os.path.join(R, 'engineering.json'), 'w'), indent=1, ensure_ascii=False)
json.dump(B, open(os.path.join(R, 'bom.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps({k: out[k] for k in ('suit', 'joint_torque', 'battery', 'power')}, indent=1, ensure_ascii=False))
for j, e in eh.items():
    print(j, e)
print('elbow', elbow, 'shoulder', shoulder)
print('thermal', {k: out['thermal'][k] for k in ('lcg_tube_m', 'lcg_dp_kPa', 'coolant_pump_W', 'gill', 'heat_to_air_W', 'airflow_L_s', 'lcg_reynolds')})
print('papr', papr, 'latency', lat_ms)
for k, v in B['systems'].items(): print(f"{k:9s} parts {v.get('parts',0):5d}  mass {v.get('mass_kg',0):6.2f} kg")
for k, v in B['stages'].items(): print(k, v['name_en'], v.get('parts'), v.get('modules'))
print('TOTAL parts', B['total_parts'], 'mass', B['total_mass_kg'], 'robot ops', B['robot_ops'])
