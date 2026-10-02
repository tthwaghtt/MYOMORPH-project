"""MYOMORPH-MK. 1 engineering bible v1 -> engineering.json (every number on the site comes from this file).

Inputs: Doha's CORPUS profile (docs/research/corpus), the fitted mannequin (previs/wearer_fit.json) and the
previs shell area (previs/suit_stats.json). Assumptions are listed next to each block; the single declared
exception to present-day engineering is the battery energy density (2036 assumption, Doha's brief).
Run: python engineering/calc.py
"""
import json, math, os

R = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(R, '..')
J = lambda *p: json.load(open(os.path.join(ROOT, *p)))
BC = J('docs', 'research', 'corpus', 'bodycomp.json'); A = J('docs', 'research', 'corpus', 'anthro.json')['measurements']
FIT = J('previs', 'wearer_fit.json')['measurements']; SS = J('previs', 'suit_stats.json')
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

# ---------------------------------------------------------------- suit mass budget
area = SS['area_m2']                                  # outer shell area of the previs (incl. helmet, hands, boots)
t_panel, rho_ti = 0.0009, 4430.0                       # Ti-6Al-4V 0.8-1.2 mm, mean 0.9 mm
panels = area * t_panel * rho_ti * 1.12                # + hems, flanges, press beads
budget = {
    'panels (MYO, Ti-6Al-4V 0.9 mm, +12 % hems)': panels,
    'frame (OS: LPBF nodes, drawn tubes, bearings)': 7.0,
    'hydraulics (COR + 8 cylinders, lines, fluid)': 12.5,
    'electric drives (shoulder 2, wrist/finger 4)': 4.0,
    'battery (ENERGIA 2 x 1.2 kWh, 2036 pack 450 Wh/kg)': 2.4 * 1000 / 450,
    'electronics, sensors, cooling (NERVUS, BRANCHIA)': 2.5,
    'liner, fasteners, misc (FASCIA, FIX)': 2.5,
    'PERSONA (shell, visor, blowers)': 1.4,
}
m_suit = sum(budget.values())

# ---------------------------------------------------------------- joint torque requirements
# peak net joint moments of healthy adults (N·m per kg body mass) for the hardest everyday task per joint
# (stair ascent / sit-to-stand for hip and knee, walking push-off for the ankle). The suit carries 100 % of its own
# mass and adds 40 % of the wearer's own requirement (assist).
PEAK = {'hip': 1.2, 'knee': 1.3, 'ankle': 1.5}
assist = 0.40
tq = {}
for j, k in PEAK.items():
    suit_share = k * m_suit; wearer_share = assist * k * m_w
    tq[j] = {'peak_Nm': round(suit_share + wearer_share, 1), 'suit_self_Nm': round(suit_share, 1), 'assist_Nm': round(wearer_share, 1)}
# arms: hold the arm horizontal with a 5 kg tool (static), suit arm masses from the budget split
m_arm_suit = (panels * 0.11 + 2.0)                     # one arm: ~11 % of panel mass + cylinder, motors, frame share
arm_len = L['upper_arm'] + L['forearm'] + L['hand'] * 0.5
m_arm_w = (DELEVA['upper_arm'][0] + DELEVA['forearm'][0] + DELEVA['hand'][0]) * m_w
sh_static = g * ((m_arm_suit + assist * m_arm_w) * arm_len * 0.45 + 5.0 * arm_len)
el_static = g * ((m_arm_suit * 0.45 + assist * (DELEVA['forearm'][0] + DELEVA['hand'][0]) * m_w) * (L['forearm'] * 0.55) + 5.0 * (L['forearm'] + L['hand'] * 0.5))
tq['shoulder'] = {'peak_Nm': round(sh_static, 1), 'case': 'arm horizontal, 5 kg tool'}
tq['elbow'] = {'peak_Nm': round(el_static, 1), 'case': 'forearm horizontal, 5 kg tool'}

# ---------------------------------------------------------------- hydraulic sizing (double-acting, 21 MPa)
p_sys = 21e6
cyl = {}
for j, arm_r, omega in (('knee', 0.035, 6.0), ('hip', 0.040, 4.0), ('ankle', 0.045, 5.0), ('elbow', 0.030, 6.0)):
    T = tq[j]['peak_Nm'] * 1.25                        # 25 % margin
    F = T / arm_r; A_need = F / p_sys
    bore = 2 * math.sqrt(A_need / math.pi)
    bore_std = next(b for b in (0.010, 0.012, 0.016, 0.020, 0.025, 0.032) if b >= bore)
    A_cap = math.pi * bore_std ** 2 / 4; rod = bore_std / 2
    v = omega * arm_r; Q = A_cap * v
    cyl[j] = {'moment_arm_mm': arm_r * 1000, 'design_torque_Nm': round(T, 1), 'force_kN': round(F / 1000, 2),
              'bore_mm': bore_std * 1000, 'rod_mm': rod * 1000, 'thrust_at_21MPa_kN': round(A_cap * p_sys / 1000, 2),
              'peak_speed_m_s': round(v, 3), 'peak_flow_L_min': round(Q * 60000, 2), 'peak_hydraulic_W': round(p_sys * Q, 0)}

# ---------------------------------------------------------------- power, battery (2036), heat
# mixed use (walking, stairs, standing work): ~1.6 W of net positive joint work per kg carried or assisted;
# valve-controlled hydraulics with accumulator ~38 % wall-to-joint efficiency
mech_avg = 1.6 * (m_suit + assist * m_w)
eta_hyd = 0.38
elec = {'actuation': mech_avg / eta_hyd, 'electronics + sensors': 60.0, 'cooling blowers': 30.0, 'standby drives': 25.0}
P_avg = sum(elec.values())
E_pack = 2.4                                            # kWh, two latissimus modules
runtime_h = E_pack * 1000 / P_avg
heat = P_avg - mech_avg
dT = 20.0
air_kg_s = heat / (1005 * dT); air_L_s = air_kg_s / 1.2 * 1000

out = {
    'version': 'v1 (P1, 2026-10-02)',
    'wearer': {'stature_m': H, 'span_m': 1.82, 'mass_kg': m_w, 'body_fat_bia_pct': 10, 'body_fat_dxa_adopted_pct': 11,
               'ffm_kg': round(m_w * 0.89, 1), 'ffmi': round(m_w * 0.89 / H ** 2, 2),
               'waist_omphalion_cm': round(mm('waistcircumference') / 10, 1), 'bideltoid_cm': round(mm('bideltoidbreadth') / 10, 1),
               'chest_cm': round(mm('chestcircumference') / 10, 1), 'crotch_height_cm': round(mm('crotchheight') / 10, 1),
               'segments': seg},
    'suit': {'height_m': 1.837, 'shell_area_m2': area, 'panel_count_est': 480,
             'mass_budget_kg': {k: round(v, 2) for k, v in budget.items()}, 'mass_total_kg': round(m_suit, 1),
             'mass_ratio_to_wearer': round(m_suit / m_w, 2),
             'note': 'suit weight is carried by the OS frame to the boot soles, not by the wearer'},
    'joint_torque': tq, 'hydraulic_cylinders': cyl, 'system_pressure_MPa': 21,
    'power': {'mechanical_avg_W': round(mech_avg, 0), 'electrical_avg_W': {k: round(v, 0) for k, v in elec.items()},
              'electrical_total_W': round(P_avg, 0), 'hydraulic_efficiency': eta_hyd},
    'battery': {'energy_kWh': E_pack, 'modules': 2, 'pack_Wh_per_kg_2036': 450, 'cell_Wh_per_kg_2036': 600,
                'pack_mass_kg': round(E_pack * 1000 / 450, 2), 'runtime_mixed_h': round(runtime_h, 1),
                'note': '2036 energy density is the one declared exception (Doha brief)'},
    'thermal': {'heat_W': round(heat, 0), 'air_dT_K': dT, 'airflow_L_s': round(air_L_s, 1), 'airflow_CFM': round(air_L_s * 2.119, 0),
                'louvres': ['pectoral (shoulder motors)', 'trapezius boxes (electronics)', 'abdominal side vents (battery, HPU intake)', 'gluteal (HPU exhaust)']},
    'rom_deg': {'neck_flex_ext_rot': [40, 45, 70], 'trunk_flex_ext_lat_rot': [60, 20, 25, 35], 'shoulder_flex_abd_ext': [160, 150, 45],
                'elbow': [0, 135], 'wrist_flex_ext': [65, 60], 'hip_flex_ext_abd': [110, 20, 35], 'knee': [0, 125], 'ankle_dorsi_plantar': [15, 40]},
}
json.dump(out, open(os.path.join(R, 'engineering.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps({k: out[k] for k in ('suit', 'joint_torque', 'battery', 'thermal')}, indent=1, ensure_ascii=False))
for j, c in cyl.items():
    print(j, c)
