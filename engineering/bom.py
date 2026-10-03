"""MYOMORPH-MK. 1 bill of materials v2 (R2, 2026-10-03).

Architecture v2 (Doha feedback 2026-10-03): every machine sits OUTSIDE the wearer, layered over a functional
undersuit and covered by (or built into) the blueprint panels. Robot arms install pre-assembled modules (LRUs);
the parts inside each module are counted here so the site can say how many parts the suit really has.

Counting rule: one part = one separately made or bought item that is assembled (a PCB assembly, a bearing, a cell,
a screw each count 1; a sewn pattern piece counts 1; a moulded or printed one-piece item counts 1).
Units: grams, millimetres. Text: name_en is the on-screen label, principle_ko is the system-card body copy.
Used by calc.py (mass budget, fixed point with the sizing); writes nothing on its own.
"""
import math

RHO = {'Ti64': 4.43, 'CFRP': 1.55, 'Al7075': 2.81, 'PEEK': 1.32, 'steel': 7.9, 'PU': 1.2, 'NdFeB': 7.5}


def P(name, qty, mat, g, note=''):
    return {'name': name, 'qty': int(qty), 'material': mat, 'g_each': round(float(g), 2), 'note': note}


def M(mid, sys_, name_en, name_ko, stage, zone, sides, parts, principle_ko, specs=None, envelope=None, install=None,
      moves=None):
    return {'id': mid, 'system': sys_, 'name_en': name_en, 'name_ko': name_ko, 'stage': stage, 'zone': zone,
            'sides': sides, 'parts': parts, 'principle_ko': principle_ko, 'specs': specs or {},
            'envelope_mm': envelope, 'install': install or {}, 'moves': moves or []}


SYSTEMS = {
    'FASCIA': ('NEURAL WEAR', '신경 언더슈트', '피부에 닿는 층. 근전도·뇌파 센서와 냉각 튜브가 들어 있는 레이싱 슈트형 옷'),
    'PES': ('GROUND', '발', '땅과 만나는 곳. 슈트의 무게가 내려가는 끝'),
    'OS': ('SKELETON', '골격', '몸 바깥의 뼈대. 슈트 무게를 땅으로 내리고 힘을 몸에 전달하는 프레임과 커프'),
    'MUSCULUS': ('MUSCLE', '근육', '전기로 움직이는 밀폐형 유압 근육(EHA) 6개'),
    'TENDO': ('TENDON', '힘줄', '케이블로 힘을 전하는 팔꿈치 구동기와 어깨 중력보상 스프링'),
    'ENERGIA': ('ENERGY', '에너지', '외부 패널이 곧 배터리. 48 V 배전과 하네스'),
    'BRANCHIA': ('THERMAL', '아가미', '막 아가미(증발 냉각기), 냉각수 회로, 팬, 열리는 루버'),
    'VITA': ('LIFE SUPPORT', '생명유지', '헬멧 송풍 정화, 가스 감시, 수분 공급, 비상 해제'),
    'NERVUS': ('NERVOUS SYSTEM', '신경계', '척추 연산부, 실시간 버스, 상태광'),
    'PERSONA': ('HELMET', '얼굴', '헬멧, 눈 슬릿 카메라, 시야 디스플레이'),
    'FUNCTIO': ('FUNCTION', '기능', '툴 베이, 보조 손, 교체 포트'),
    'MYO': ('PANELS', '근육 패널', '도하의 청사진 판 477장과 패널 캐리어'),
    'FIX': ('FASTENERS', '체결', '설치 볼트, 패널 체결구, 방진 그로밋'),
}

STAGES = {
    0: ('WEAR', '착용', '도하가 언더슈트, 바라클라바, 이너 장갑을 입고 셀에 들어온다(사람이 입는다)'),
    1: ('GROUND', '발', '부츠에 발을 넣고 로봇이 바인딩을 조인다'),
    2: ('SKELETON', '골격', '다리 프레임 → 골반 → 척추와 하네스 → 팔 프레임, 커프 조임'),
    3: ('MUSCLE', '근육', 'EHA 6개 핀 결합, 팔꿈치 힘줄 구동기, 어깨 스프링, 힘줄 장력'),
    4: ('SYSTEMS', '내장 시스템', '배전, 버퍼, 막 아가미, 냉각수 회로, 팬, 연산부, 생명유지, 언더슈트 연결, 천장 탯줄 연결'),
    5: ('PANELS', '패널', '청사진 판 477장(배터리 패널, 루버, 툴 베이 패널 포함)'),
    6: ('PERSONA', '헬멧', '후두 셸 → 측두 허브 → 안면판 → 락'),
    7: ('BRING-UP', '기동', '신경 보정, 자가 진단, 탯줄 분리, 배터리 단독 구동'),
}


def eha(joint, bore, stroke, rod, motor_W):
    """Electro-hydrostatic actuator: motor + reversible gear pump + valve manifold + cylinder in one sealed unit."""
    k = bore / 14.0
    barrel_g = math.pi * ((bore / 2 + 2.0) ** 2 - (bore / 2) ** 2) * (stroke + 18) * RHO['Ti64'] / 1000
    motor_g = 1.25 * motor_W + 60                     # frameless BLDC ~1 kW/kg peak incl. back iron
    parts = [
        P('BLDC stator assembly, frameless 12-slot', 1, 'Cu/Si-steel', motor_g * 0.55),
        P('rotor assembly, 14-pole NdFeB', 1, 'NdFeB/steel', motor_g * 0.30),
        P('motor bearing, deep groove 6701', 2, 'steel', 3.0),
        P('motor housing', 1, 'Al7075', 52 * k), P('motor end cap', 1, 'Al7075', 12 * k),
        P('hall + 17-bit absolute encoder PCB', 1, 'FR4', 4),
        P('pump gear, drive / idler (internal gear set)', 2, 'steel DLC', 9 * k),
        P('pump body', 1, 'Al7075', 44 * k), P('pump side plate', 2, 'bronze', 7 * k), P('shaft seal', 1, 'PTFE', 0.6),
        P('valve manifold, LPBF', 1, 'Ti64', 95 * k),
        P('pilot-operated check valve', 2, 'steel', 6), P('pressure relief valve 25 MPa', 2, 'steel', 7),
        P('free-swing bypass solenoid valve', 1, 'steel/Cu', 16),
        P('pressure transducer', 2, 'steel', 5), P('oil temperature sensor', 1, 'steel', 1.5),
        P('bootstrap accumulator body', 1, 'Ti64', 34 * k), P('accumulator piston', 1, 'Al7075', 5 * k),
        P('accumulator end cap', 1, 'Ti64', 6 * k),
        P(f'cylinder barrel, bore {bore:g} mm', 1, 'Ti64', barrel_g), P('piston', 1, 'Ti64', 8 * k),
        P(f'piston rod {rod:g} mm, DLC', 1, 'Ti64', math.pi * (rod / 2) ** 2 * (stroke + 30) * RHO['Ti64'] / 1000),
        P('piston seal', 2, 'PTFE/bronze', 0.8), P('rod seal', 1, 'PU', 0.6), P('wiper', 1, 'PU', 0.4),
        P('rod gland', 1, 'Ti64', 9 * k), P('rod eye', 1, 'Ti64', 11 * k),
        P('magnetostrictive position sensor', 1, 'steel', 9),
        P('spherical plain bearing', 2, 'steel', 4), P('clevis pin', 2, 'Ti64', 4), P('circlip', 4, 'steel', 0.3),
        P('motor driver + MCU, EtherCAT slave', 1, 'FR4', 14), P('thermal pad', 1, 'silicone', 1.5),
        P('driver cover', 1, 'Al7075', 9), P('sealed connector, power + bus', 2, 'mixed', 4),
        P('O-ring', 8, 'FKM', 0.2), P('fill / bleed screw', 2, 'steel', 1.0),
        P('hydraulic fluid, synthetic ester (ml)', 1, 'ester', 0.92 * (math.pi * (bore / 2) ** 2 * stroke / 1000 * 2.2 + 6),
          'counted as one fill'),
        P('internal screw M3, Ti', 16, 'Ti64', 0.7),
    ]
    return parts


def build(S):
    """S: sizing from calc.py. Returns the BOM dict (modules, per-module totals, per-system and per-stage tallies)."""
    mods = []
    # ------------------------------------------------------------------ 0 NEURAL WEAR
    tube_m = S['lcg_tube_m']; n_circ = S['lcg_circuits']
    mods.append(M('FAS-SUIT', 'FASCIA', 'NEURAL UNDERSUIT', '신경 언더슈트', 0, 'whole body', 'C', [
        P('3-layer knit pattern piece (aramid/elastane spacer, 1.1 mm)', 28, 'aramid', 21),
        P('two-way front zip', 1, 'PA/steel', 18),
        P(f'cooling tube circuit, PU 3.2 OD / 1.6 ID (total {tube_m:.0f} m)', n_circ, 'PU', tube_m / n_circ * 7.2),
        P('tube distribution manifold, 6-port', 4, 'PEEK', 9),
        P('dry-break quick disconnect, garment half', 4, 'Ti64/FKM', 11),
        P('HD-sEMG grid, 32 ch printed on knit (4 x 8, 10 mm)', S['emg_grids'], 'Ag/AgCl-knit', 6),
        P('bipolar dry EMG electrode pair', S['emg_bipolar'], 'Ag/AgCl', 3),
        P('biopotential node, 64 ch, overmoulded pod', S['emg_nodes'], 'FR4/TPU', 7, 'the visible sensor pods'),
        P('dry ECG electrode', 3, 'Ag-knit', 2), P('heat-flux / skin temperature sensor', 6, 'FR4', 1.5),
        P('respiration strain band', 1, 'TPU', 8), P('sweat conductance sensor', 1, 'FR4', 2),
        P('embroidered data bus run (Ag yarn, TPU laminate)', 14, 'Ag/TPU', 6),
        P('sealed trunk connector, 24-pin (nape, waist L/R)', 3, 'mixed', 9),
    ], 'MYO(근육)를 읽는 옷. 근육이 수축하기 30~100 ms 전에 척수의 운동신경이 근섬유에 전기 신호를 보낸다. '
       '피부 위 고밀도 전극 격자가 이 신호를 받아 운동단위 하나하나의 발화로 분해하면, 슈트는 몸이 움직이기 전에 '
       '얼마나 힘을 쓰려는지 안다. 같은 원단 속 3.2 mm 튜브에는 냉각수가 흘러 몸의 열을 직접 뺀다.',
       {'emg_channels': S['emg_channels'], 'tube_m': round(tube_m, 1), 'lcg_flow_L_min': S['lcg_flow_L_min']},
       envelope=None, install={'by': 'wearer', 'connect': ['waist L/R coolant + data', 'nape data']}))
    mods.append(M('FAS-BALA', 'FASCIA', 'EEG BALACLAVA', '뇌파 바라클라바', 0, 'head', 'C', [
        P('knit hood', 1, 'aramid', 45),
        P('dry comb EEG electrode, spring-loaded', S['eeg_ch'], 'Ag/AgCl', 1.6),
        P('EEG node, 32 ch', 1, 'FR4/TPU', 9), P('forehead PPG (SpO2, HR)', 1, 'FR4', 2),
        P('bone-conduction transducer', 2, 'mixed', 6), P('bone-conduction mic', 1, 'mixed', 3),
        P('nape connector', 1, 'mixed', 6), P('embroidered bus run', 2, 'Ag/TPU', 3),
    ], '뇌는 움직이기 0.5~1.5초 전부터 운동피질에서 준비 신호(운동관련 전위, 뮤·베타 리듬 감소)를 낸다. '
       '헬멧 라이너가 누르는 32개 건식 전극이 이 신호를 읽어 동작 모드(걷기, 계단, 들기, 공구)를 고르고, '
       '슈트가 의도와 다르게 움직였을 때 뇌가 내는 오류 전위로 즉시 멈춘다. 연속 제어는 근전도, 판단은 뇌파가 맡는다.',
       {'eeg_channels': S['eeg_ch'], 'sample_Hz': 500}, install={'by': 'wearer'}))
    mods.append(M('FAS-GLOVE', 'FASCIA', 'INNER GLOVE', '이너 장갑', 0, 'hand', 'LR', [
        P('knit glove', 1, 'aramid', 22), P('fingertip pressure sensor', 5, 'FR4', 0.5),
        P('wrist connector', 1, 'mixed', 3), P('embroidered bus run', 1, 'Ag/TPU', 2),
    ], '손끝 압력을 읽어 보조 손과 공구의 힘을 맞춘다.', install={'by': 'wearer'}))
    # ------------------------------------------------------------------ 1 GROUND
    mods.append(M('PES-BOOT', 'PES', 'BOOT', '부츠', 1, 'foot', 'LR', [
        P('sole plate, CFRP', 1, 'CFRP', 250), P('heel node, LPBF', 1, 'Ti64', 95),
        P('outsole, lugged', 1, 'NBR', 180), P('midsole', 1, 'TPU foam', 85),
        P('pressure insole, 16-zone capacitive', 1, 'mixed', 45), P('shear-beam load cell', 4, 'steel', 18),
        P('heel lever (Achilles link anchor), LPBF', 1, 'Ti64', 70), P('ankle hinge yoke', 2, 'Ti64', 38),
        P('thin-section bearing', 4, 'steel', 6), P('hinge axle', 2, 'Ti64', 9), P('circlip', 4, 'steel', 0.4),
        P('instep shell', 1, 'CFRP', 60), P('heel cup', 1, 'CFRP', 55), P('BOA dial', 1, 'PA', 18),
        P('BOA lace', 1, 'steel', 2), P('foot node (load-cell amp + IMU)', 1, 'FR4', 8),
        P('sealed connector', 1, 'mixed', 5), P('inner bootie', 1, 'EVA', 60), P('internal screw M3, Ti', 22, 'Ti64', 0.8),
    ], '슈트 무게는 사람 몸이 아니라 프레임을 따라 이 발판으로 내려간다. 발판 아래 하중 센서 4개와 16구역 압력 깔창이 '
       '무게중심과 보행 단계(뒤꿈치 닿음 → 발바닥 → 밀기)를 1 kHz로 읽는다.',
       {'load_cells': 4, 'pressure_zones': 16}, envelope=(290, 115, 95), install={'by': 'wearer + robot', 'ops': ['close binding (BOA)']}))
    # ------------------------------------------------------------------ 2 SKELETON
    cuff = lambda seg, shell, liner, straps: [P(f'{seg} cuff shell', 1, 'CFRP', shell), P(f'{seg} cuff liner (EPP + gel)', 1, 'EPP/silicone', liner),
                                             P(f'{seg} cuff strap', straps, 'PA', 12), P(f'{seg} cuff BOA dial', 1, 'PA', 18)]
    mods.append(M('OS-LEG', 'OS', 'LEG FRAME', '다리 프레임', 2, 'thigh + shank', 'LR', [
        P('thigh strut, lateral (CFRP / Ti end fittings)', 1, 'CFRP/Ti', 170), P('thigh strut, medial', 1, 'CFRP/Ti', 130),
        P('shank strut, lateral', 1, 'CFRP/Ti', 110), P('shank strut, medial', 1, 'CFRP/Ti', 100),
        P('knee crossed four-bar link', 4, 'Ti64', 26), P('knee joint plate', 4, 'Ti64', 22),
        P('needle roller bearing', 8, 'steel', 2.5), P('knee pin', 8, 'Ti64', 4), P('circlip', 16, 'steel', 0.4),
        P('knee hard stop + bumper', 2, 'Ti/PU', 6), P('knee absolute encoder', 1, 'FR4', 5), P('encoder magnet', 1, 'NdFeB', 1),
        P('ankle bracket, LPBF', 2, 'Ti64', 40), P('EHA clevis node, thigh, LPBF', 1, 'Ti64', 45), P('EHA clevis node, shank, LPBF', 1, 'Ti64', 38),
        *cuff('thigh', 95, 30, 2), *cuff('shank', 70, 25, 1),
        P('strain gauge bridge', 2, 'FR4', 2), P('IMU node', 2, 'FR4', 4), P('harness clip', 6, 'PA', 1),
        P('internal screw M4, Ti', 40, 'Ti64', 0.9),
    ], '허벅지와 정강이 양옆을 지나는 탄소섬유 지주. 무릎은 단순 경첩이 아니라 교차 4절 링크라서 사람 무릎처럼 '
       '굽힐수록 회전중심이 뒤로 이동한다(순간회전중심 추종). 그래서 슈트 무릎이 사람 무릎을 비틀지 않는다. '
       '커프는 힘을 몸에 전하는 유일한 접점이고, 나머지는 몸에서 떠 있다.',
       {'knee_rom_deg': [0, 125], 'icr_tracking': True}, envelope=(820, 150, 150),
       install={'by': 'robot', 'ops': ['dock to boot ankle hinge', 'pin hip', 'tighten 2 cuffs'], 'bolts': 8}))
    mods.append(M('OS-PELVIS', 'OS', 'PELVIS + HIP JOINTS', '골반과 고관절', 2, 'pelvis', 'C', [
        P('pelvic arch, LPBF lattice + CFRP', 1, 'Ti64/CFRP', 320), P('lateral hip arm', 2, 'Ti64', 110),
        P('crossed roller bearing (hip flexion axis)', 2, 'steel', 45), P('hip output flange', 2, 'Ti64', 40), P('hip housing', 2, 'Al7075', 60),
        P('abduction hinge yoke (passive)', 2, 'Ti64', 35), P('abduction bearing', 4, 'steel', 6), P('abduction axle', 2, 'Ti64', 8),
        P('abduction centring spring', 2, 'steel', 10), P('rotation ring bearing (passive, +/-25 deg)', 2, 'steel', 30),
        P('hip encoder (flex, abd, rot)', 6, 'FR4', 5), P('hip hard stop', 6, 'Ti/PU', 6),
        P('pelvic belt, padded', 1, 'PA/EPP', 140), P('belt buckle', 1, 'Al7075', 22), P('belt BOA dial', 2, 'PA', 18),
        P('IMU node (pelvis)', 1, 'FR4', 4), P('PDU / buffer bracket', 1, 'Ti64', 25), P('internal screw M4, Ti', 44, 'Ti64', 0.9),
    ], '고관절은 세 축이다. 굽힘·폄은 EHA가 밀고, 벌림과 돌림은 스프링으로 가운데를 찾는 수동 축이라 '
       '사람이 다리를 벌리거나 돌릴 때 막지 않는다. 축마다 하드 스톱이 사람의 가동 범위 안에서 기계적으로 막는다.',
       {'hip_rom_deg': {'flex': 110, 'ext': 20, 'abd': 35, 'rot': 25}}, envelope=(360, 220, 120),
       install={'by': 'robot', 'ops': ['pin both leg frames', 'close belt'], 'bolts': 12}))
    mods.append(M('OS-SPINE', 'OS', 'SPINE + HARNESS', '척추와 하네스', 2, 'back', 'C', [
        P('lumbar vertebra block, LPBF', 5, 'Ti64', 38), P('lumbar leaf flexure 0.8 mm', 6, 'Ti64', 14),
        P('flexure guide rail', 2, 'Ti64', 22), P('flexure preload screw', 6, 'Ti64', 2),
        P('thoracic frame, LPBF lattice', 1, 'Ti64', 380),
        P('chest harness shell', 2, 'CFRP', 65), P('harness foam', 3, 'EPP', 15), P('harness strap', 4, 'PA', 14),
        P('harness buckle', 2, 'Al7075', 22), P('harness BOA dial', 2, 'PA', 18),
        P('scapular tracking rail', 2, 'Ti64', 30), P('scapular carriage', 2, 'Ti64', 25), P('carriage bearing', 8, 'steel', 3),
        P('scapular linkage', 6, 'Ti64', 12), P('linkage pin', 12, 'Ti64', 2), P('scapular return spring', 4, 'steel', 6),
        P('scapular encoder', 4, 'FR4', 5), P('IMU node (thorax)', 1, 'FR4', 4), P('harness channel clip', 20, 'PA', 1),
        P('internal screw M4, Ti', 60, 'Ti64', 0.9),
    ], '허리는 티타늄 판스프링 6장이 쌓인 척추다. 앞으로 숙이면 판스프링이 에너지를 저장했다가 일어설 때 돌려준다(전원 불필요). '
       '어깨뼈(견갑골)는 팔을 들 때 가슴 위를 미끄러지는데, 레일 위 캐리지가 그 움직임을 따라가 슈트 어깨 축이 '
       '사람 어깨 중심에서 벗어나지 않는다. 외골격의 가장 어려운 문제를 기구로 푼다.',
       {'lumbar_flex_deg': 60, 'scapular_travel_mm': 38}, envelope=(520, 330, 40),
       install={'by': 'robot', 'ops': ['dock to pelvis', 'close harness'], 'bolts': 10}))
    mods.append(M('OS-ARM', 'OS', 'ARM FRAME', '팔 프레임', 2, 'upper arm + forearm', 'LR', [
        P('upper arm strut, lateral', 1, 'CFRP/Ti', 95), P('shoulder linkage arm', 3, 'Ti64', 22), P('shoulder linkage bearing', 6, 'steel', 3),
        P('shoulder linkage pin', 3, 'Ti64', 3),
        P('elbow yoke', 2, 'Ti64', 24), P('elbow bearing', 2, 'steel', 5), P('elbow axle', 1, 'Ti64', 7), P('circlip', 2, 'steel', 0.4),
        P('elbow hard stop', 2, 'Ti/PU', 4), P('elbow encoder', 1, 'FR4', 5), P('encoder magnet', 1, 'NdFeB', 1),
        P('forearm strut, radial', 1, 'CFRP/Ti', 80), P('wrist gimbal ring', 2, 'Ti64', 18), P('gimbal bearing', 4, 'steel', 2), P('gimbal axle', 2, 'Ti64', 3),
        *cuff('upper arm', 50, 15, 1), *cuff('forearm', 45, 14, 1),
        P('IMU node', 2, 'FR4', 4), P('internal screw M3, Ti', 28, 'Ti64', 0.8),
    ], '팔 바깥쪽 지주와 팔꿈치 경첩. 손목은 구동하지 않는 2축 짐벌이라 손은 완전히 자유롭다.',
       {'elbow_rom_deg': [0, 135]}, envelope=(560, 90, 60),
       install={'by': 'robot', 'ops': ['dock to scapular carriage', 'tighten 2 cuffs'], 'bolts': 6}))
    # ------------------------------------------------------------------ 3 MUSCLE
    for j in ('hip', 'knee', 'ankle'):
        e = S['eha'][j]
        mods.append(M(f'MUS-EHA-{j.upper()}', 'MUSCULUS', f'{j.upper()} MUSCLE (EHA)', {'hip': '고관절 근육', 'knee': '무릎 근육', 'ankle': '발목 근육'}[j],
                      3, {'hip': 'gluteal / posterior pelvis', 'knee': 'anterior thigh', 'ankle': 'posterior shank'}[j], 'LR',
                      eha(j, e['bore_mm'], e['stroke_mm'], e['rod_mm'], e['motor_W']),
                      '모터, 양방향 기어 펌프, 밸브 블록, 실린더를 하나로 밀봉한 전기유압 액추에이터(EHA). 중앙 유압 펌프와 긴 고압 배관이 없다. '
                      '모터가 정방향으로 돌면 펌프가 기름을 실린더 한쪽으로 밀어 늘어나고, 역방향이면 줄어든다. 밸브로 압력을 버리지 않고 '
                      '모터 회전으로 직접 제어하니 효율이 높다. 다리를 흔드는 구간에서는 바이패스 밸브가 열려 저항 없이 따라온다(자유 스윙). '
                      '고장 나면 이 밸브가 기본으로 열려 사람을 가두지 않는다.',
                      {k: e[k] for k in ('bore_mm', 'rod_mm', 'stroke_mm', 'force_kN', 'design_torque_Nm', 'motor_W', 'pressure_MPa')},
                      envelope=e['envelope_mm'], install={'by': 'robot', 'ops': ['pin rod eye', 'pin base clevis', 'circlips', 'plug bus + power', 'test stroke'], 'bolts': 2},
                      moves=['kinetic bulge of the covering panel as the cylinder extends']))
    t = S['elbow']
    mods.append(M('TEN-ELBOW', 'TENDO', 'ELBOW TENDON DRIVE', '팔꿈치 힘줄 구동기', 3, 'posterior upper arm', 'LR', [
        P('flat BLDC stator', 1, 'Cu/Si-steel', 48), P('flat BLDC rotor', 1, 'NdFeB/steel', 26), P('motor bearing', 2, 'steel', 2.5),
        P('motor housing half', 2, 'Al7075', 14), P('capstan drum', 1, 'Al7075', 12),
        P('cable reduction pulley', 3, 'Al7075', 6), P('pulley bearing', 6, 'steel', 1.5), P('pulley axle', 3, 'Ti64', 2),
        P('UHMWPE tendon 2 mm', 1, 'Dyneema', 3), P('PTFE-lined Bowden sheath', 1, 'PTFE/steel', 14), P('sheath ferrule', 2, 'Ti64', 1.5),
        P('tendon tensioner', 1, 'Ti64', 6), P('elbow output pulley', 1, 'Al7075', 14), P('output pulley bearing', 2, 'steel', 2.5),
        P('tendon load cell', 1, 'steel', 4), P('motor driver + MCU', 1, 'FR4', 9), P('internal screw M2.5, Ti', 14, 'Ti64', 0.5),
    ], '사람 손가락을 움직이는 근육이 팔뚝에 있고 힘줄로 당기듯, 위팔 뒤의 납작한 모터가 초고분자량 폴리에틸렌 힘줄로 '
       '팔꿈치 앞의 풀리를 당긴다. 무거운 모터를 관절에서 멀리 두어 팔 끝이 가볍다.',
       {'design_torque_Nm': t['design_torque_Nm'], 'tendon_N': t['tendon_N'], 'reduction': t['reduction']}, envelope=(90, 60, 16),
       install={'by': 'robot', 'ops': ['clip to upper arm strut', 'route tendon', 'tension 120 N preload'], 'bolts': 3}))
    sp = S['shoulder']
    mods.append(M('TEN-SHOULDER', 'TENDO', 'SHOULDER SPRING CASSETTE', '어깨 중력보상 스프링', 3, 'shoulder top / upper back', 'LR', [
        P('coil spring', 2, 'steel', 42), P('cam (sin-profile)', 1, 'Ti64', 18), P('spring cable', 1, 'Dyneema', 2),
        P('pulley', 2, 'Al7075', 6), P('pulley bearing', 4, 'steel', 1.5), P('trim worm', 1, 'steel', 4), P('trim worm wheel', 1, 'PEEK', 3),
        P('trim micro motor', 1, 'mixed', 14), P('ratchet', 1, 'steel', 4), P('pawl', 1, 'steel', 1.5),
        P('cassette housing half', 2, 'Al7075', 22), P('internal screw M2.5, Ti', 10, 'Ti64', 0.5),
    ], '팔을 들고 있는 힘의 대부분은 팔 무게를 버티는 힘이다. 사인 곡선 캠이 스프링 힘을 팔 각도에 맞춰 바꿔 주어 '
       '어느 각도에서나 팔이 떠 있는 것처럼 가볍다. 전원 없이 작동하고, 작은 모터는 공구 무게가 바뀔 때 예압만 조정한다.',
       {'compensated_Nm_at_90deg': sp['comp_Nm'], 'spring_energy_J': sp['energy_J']}, envelope=(120, 70, 30),
       install={'by': 'robot', 'ops': ['seat on thoracic frame', 'hook cable to upper arm strut'], 'bolts': 4}))
    # ------------------------------------------------------------------ 4 SYSTEMS
    b = S['battery']
    mods.append(M('ENE-PDU', 'ENERGIA', 'POWER DISTRIBUTION', '배전 장치', 4, 'pelvis (posterior)', 'C', [
        P('PDU board (eFuse array, 48 V bus)', 1, 'FR4', 38), P('PDU housing half', 2, 'Al7075', 30),
        P('DC-DC converter 48/12, 48/5, 48/3.3 V', 3, 'mixed', 12), P('sealed power connector', 12, 'mixed', 5),
        P('internal screw M3, Ti', 8, 'Ti64', 0.7),
    ], '두 배터리 패널의 48 V를 받아 관절 18곳과 시스템 40여 곳에 나눠 준다. 회로마다 전자 퓨즈가 있어 한 곳이 단락돼도 나머지는 산다.',
       {'bus_V': 48}, envelope=(110, 80, 22), install={'by': 'robot', 'bolts': 4}))
    mods.append(M('ENE-BUF', 'ENERGIA', 'HOT-SWAP BUFFER', '교체 버퍼', 4, 'pelvis (posterior)', 'C', [
        P('hybrid capacitor cell', 6, 'mixed', 14), P('buffer BMS', 1, 'FR4', 6), P('buffer housing half', 2, 'Al7075', 12),
    ], '배터리 패널 하나를 빼는 90초 동안 슈트가 꺼지지 않게 버틴다.', {'Wh': b['buffer_Wh'], 'hold_s': 90}, envelope=(90, 50, 18),
        install={'by': 'robot', 'bolts': 2}))
    mods.append(M('ENE-HARN', 'ENERGIA', 'HARNESS', '하네스', 4, 'spine + limbs', 'C', [
        P('harness trunk segment (power + EtherCAT)', 24, 'Cu/FEP', 18), P('sealed connector', 48, 'mixed', 3),
        P('P-clamp', 60, 'PA', 0.8), P('spiral wrap', 20, 'PA', 2),
    ], '척추를 따라 내려가는 주 간선과 사지 분기. 커넥터는 모두 방수 밀봉, 피복은 내마모 불소수지.', install={'by': 'robot', 'ops': ['route', 'clip', 'mate 48 connectors']}))
    gl = S['gill']
    mods.append(M('BRA-GILL', 'BRANCHIA', 'MEMBRANE GILL', '막 아가미 (증발 냉각기)', 4, 'flank L/R, behind the abdominal side slots', 'C', [
        P('hollow-fibre membrane module (PP, ~1,800 fibres, 0.25 m2)', 2, 'PP', 95), P('gill module housing', 2, 'Ti64', 40),
        P('evaporant bladder 0.6 L', 1, 'TPU', 35), P('micro diaphragm dosing pump', 1, 'mixed', 25),
        P('evaporant solenoid valve', 2, 'steel', 8), P('evaporant level sensor', 1, 'FR4', 3),
        P('air RH / temperature sensor (in, out)', 4, 'FR4', 1), P('evaporant line', 6, 'PU', 5),
        P('fill port quick disconnect', 1, 'PP', 8), P('drain valve', 1, 'PP', 5), P('wicking pre-filter', 2, 'PET', 4),
        P('internal screw M2.5, Ti', 12, 'Ti64', 0.5),
    ], '땀이 증발하며 몸을 식히듯, 냉각수가 속이 빈 섬유 1,800가닥 안을 흐르고 그 바깥으로 루버의 공기가 지나가면 물의 일부가 '
       '막을 통해 증발하면서 나머지 물을 습구온도 가까이 식힌다. 30 °C, 습도 40 %에서도 냉각수가 '
       f"{gl['water_out_C']:.0f} °C까지 내려간다. 압축기가 없어 얇고(14 mm) 전력은 팬 몫뿐이다. 시간당 물 {gl['L_per_h']:.2f} L를 쓴다. "
       '덥고 습해서 습구온도가 26 °C를 넘는 날에는 이 원리가 한계에 닿고, 그때만 도크의 냉각 라인(탯줄)을 꽂는다.',
       {'cooling_W': gl['cooling_W'], 'water_out_C_at_30C_40RH': gl['water_out_C'], 'evaporant_L_per_h': gl['L_per_h'],
        'reservoir_L': 0.6, 'limit': 'ambient wet bulb > 26 C -> chill line'}, envelope=(160, 70, 14),
       install={'by': 'robot', 'ops': ['seat behind flank louvres', 'mate coolant + evaporant lines'], 'bolts': 4}))
    mods.append(M('BRA-LOOP', 'BRANCHIA', 'COOLANT LOOP', '냉각수 회로', 4, 'back', 'C', [
        P('maglev centrifugal pump', 1, 'mixed', 45), P('expansion bladder / reservoir', 1, 'silicone', 20),
        P('loop manifold', 1, 'PEEK', 30), P('flow sensor', 1, 'mixed', 8), P('coolant temperature sensor', 4, 'FR4', 1),
        P('coolant line', 12, 'PU', 6), P('dry-break quick disconnect, suit half', 4, 'Ti64/FKM', 11),
        P('phase-change pack (salt hydrate, 24 C)', 6, 'mixed', 70), P('loop filter', 1, 'PP', 6), P('spine core cold plate', 1, 'Al', 40),
    ], f"냉각수가 분당 {S['lcg_flow_L_min']:.1f} L씩 막 아가미와 언더슈트 튜브 사이를 돈다. 상변화 팩(24 °C에서 녹는 염수화물)은 순간 발열이 클 때 열을 잠시 저장한다.",
       {'flow_L_min': S['lcg_flow_L_min'], 'pcm_kJ': S['pcm_kJ']}, install={'by': 'robot', 'ops': ['mate 4 QDs to undersuit']}))
    mods.append(M('BRA-FAN', 'BRANCHIA', 'LOUVRE FAN UNIT', '루버 팬 유닛', 4, 'flank L/R (2 each) + upper back L/R', 'x6', [
        P('flat blower 50 mm', 1, 'mixed', 38), P('blower shroud', 1, 'PA', 12), P('finger-proof mesh', 1, 'Ti64', 6),
        P('louvre micro linear actuator', 1, 'mixed', 14), P('louvre link bar', 1, 'Ti64', 4), P('link pin', 4, 'Ti64', 0.5),
        P('air temperature sensor', 1, 'FR4', 1), P('internal screw M2.5, Ti', 4, 'Ti64', 0.5),
    ], '도하가 그린 복부 옆 슬롯은 숨구멍이 됐다. 팬이 패널 안쪽 틈의 습한 공기를 빨아 막 아가미와 전자부를 지나 아래로 뿜고, 열이 쌓이면 '
       '작은 리니어 액추에이터가 링크 바 하나로 루버 슬랫 전체를 차례로 연다(패널의 독립적 움직임).',
       {'airflow_L_s_each': S['fan_L_s_each']}, envelope=(60, 55, 14), install={'by': 'robot', 'bolts': 2},
       moves=['louvre slats open downward in sequence']))
    a = S['papr']
    mods.append(M('VIT-AER', 'VITA', 'HELMET AIR (PAPR)', '헬멧 송풍 정화', 6, 'helmet', 'C', [
        P('helmet blower', 2, 'mixed', 28), P('P3 + carbon filter cartridge (in temporal hub)', 2, 'mixed', 42),
        P('intake check valve', 2, 'silicone', 2), P('exhalation valve', 2, 'silicone', 8), P('oro-nasal cup', 1, 'silicone', 35),
        P('slit anti-fog air knife duct', 2, 'PA', 6), P('CO2 sensor (NDIR)', 1, 'mixed', 4), P('O2 sensor', 1, 'mixed', 6),
        P('temperature / humidity sensor', 1, 'FR4', 1), P('air board', 1, 'FR4', 6), P('air tube', 3, 'silicone', 3),
        P('internal screw M2, Ti', 10, 'Ti64', 0.3),
    ], '헬멧 안은 바깥보다 압력이 조금 높다. 송풍기가 측두 허브의 필터로 바깥 공기를 걸러 넣으니 먼지와 연기가 새어 들지 않고, '
       '눈 슬릿 안쪽으로 공기 칼날이 흘러 김이 서리지 않는다. 날숨은 입 앞 컵에서 바로 배기 밸브로 나가 CO2가 쌓이지 않는다.',
       {'flow_L_min': a['flow_L_min'], 'inspired_CO2_pct': a['inspired_CO2_pct'], 'power_W': a['power_W']}, install={'by': 'robot (with helmet)'}))
    mods.append(M('VIT-HYDRA', 'VITA', 'HYDRATION', '수분 공급', 4, 'upper back', 'C', [
        P('bladder 0.5 L', 1, 'TPU', 40), P('drink tube', 1, 'silicone', 10), P('bite valve', 1, 'silicone', 4),
        P('bladder pocket', 1, 'aramid', 25), P('helmet pass-through QD', 1, 'PP', 6),
    ], '헬멧을 벗지 않고 마신다. 냉각복이 땀을 줄여도 1시간에 0.3~0.5 L는 잃는다.', {'volume_L': 0.5}, install={'by': 'robot'}))
    mods.append(M('VIT-SALUS', 'VITA', 'EMERGENCY + VITALS', '비상과 생체 감시', 4, 'sternum + spine', 'C', [
        P('emergency release handle', 1, 'Ti64', 22), P('release Bowden cable', 4, 'steel/PTFE', 8),
        P('latch release actuator', 6, 'mixed', 12), P('SOS beacon (GNSS + satellite)', 1, 'mixed', 30),
        P('vitals hub board', 1, 'FR4', 8), P('haptic alert motor', 2, 'mixed', 3), P('internal screw M2.5, Ti', 10, 'Ti64', 0.5),
    ], '흉골 손잡이 하나를 당기면 헬멧과 가슴 셸, 다리 커프가 기계식으로 풀린다(전원 불필요). 심전도, 산소포화도, 심부체온 추정, '
       '호흡을 계속 보고 열 스트레스가 오면 출력을 먼저 줄인다. 넘어짐을 감지하면 위치를 자동 송신한다.',
       {'core_temp_derate_C': 38.5}, install={'by': 'robot', 'bolts': 4}))
    mods.append(M('NER-CORE', 'NERVUS', 'SPINE CORE', '척추 연산부', 4, 'upper back, between scapulae', 'C', [
        P('compute module (edge AI SoC)', 1, 'mixed', 25), P('carrier board (lockstep safety MCU, EtherCAT master)', 1, 'FR4', 40),
        P('NVMe storage', 1, 'mixed', 6), P('core housing half', 2, 'Al7075', 30), P('sealed connector', 8, 'mixed', 5),
        P('internal screw M3, Ti', 10, 'Ti64', 0.7),
    ], '근전도 800채널과 뇌파 32채널을 실시간으로 해독하고, 도하의 근육 표(최대 힘, 섬유 길이, 깃각)로 만든 근골격 모델로 '
       '관절마다 필요한 토크를 계산해 1 kHz로 근육(EHA)에 보낸다. 근육 신호가 오고 힘이 나기까지 50~100 ms, 슈트는 40 ms 안에 답한다.',
       {'control_Hz': 1000, 'latency_ms': S['latency_ms'], 'power_W': 15}, envelope=(120, 90, 20), install={'by': 'robot', 'bolts': 4}))
    mods.append(M('NER-NET', 'NERVUS', 'BUS HUBS', '버스 허브', 4, 'spine', 'C', [
        P('EtherCAT junction hub', 4, 'FR4', 12), P('internal screw M2.5, Ti', 8, 'Ti64', 0.5)],
        '관절, 센서 노드, 시스템을 하나의 결정론적 버스(250 µs 주기)로 묶는다.', install={'by': 'robot'}))
    mods.append(M('NER-LUX', 'NERVUS', 'STATUS LIGHT PIPES', '상태광', 5, 'panel seams', 'C', [
        P('light pipe segment (PC, frosted)', S['lightpipes'], 'PC', 1.2), P('side-emitting LED strip', 32, 'FR4', 2),
        P('LED driver', 8, 'FR4', 3), P('light pipe clip', 60, 'PA', 0.3),
    ], '패널 이음선 홈 속의 광섬유처럼 빛나는 막대. 근섬유 방향으로 흐르며 부하가 클수록 빠르고 밝다.', install={'by': 'robot (with panels)'}))
    # ------------------------------------------------------------------ 5 FUNCTION (under forearm panels) + battery panels
    mods.append(M('ENE-BATT', 'ENERGIA', 'BATTERY PANEL', '배터리 패널', 5, 'latissimus (back) L/R', 'LR', [
        P('solid-state pouch cell (2036 assumption)', b['cells_per_panel'], 'Li-metal SSB', b['cell_g']),
        P('structural cell carrier (Ti honeycomb)', 1, 'Ti64', 60), P('graphite heat spreader', 4, 'graphite', 6),
        P('BMS board', 1, 'FR4', 14), P('cell voltage tap flex', 1, 'PI/Cu', 6), P('busbar', 8, 'Cu', 3), P('thermistor', 6, 'FR4', 0.3),
        P('pack fuse', 1, 'mixed', 4), P('solid-state contactor', 1, 'mixed', 9), P('blind-mate power / data connector', 1, 'mixed', 12),
        P('guide pin', 2, 'Ti64', 2), P('quarter-turn latch', 4, 'Ti64', 3), P('pack gasket', 1, 'silicone', 6),
        P('pressure relief vent', 1, 'mixed', 2), P('pack base housing', 1, 'Ti64', 70),
    ], '배터리를 따로 매달지 않는다. 등의 넓은등근 판 두 장이 곧 배터리 팩이다. 바깥은 청사진의 티타늄 판, 안쪽 9 mm에 '
       '셀이 들어 있다. 쿼터턴 래치 4개를 풀면 판째로 빠지고, 버퍼가 버티는 동안 새 판을 꽂는다(유일한 미래 가정: 셀 에너지 밀도).',
       {'kWh_each': b['kWh_each'], 'cells': b['cells_per_panel'], 'thickness_mm': b['thickness_mm'], 'area_m2_each': b['area_m2_each']},
       envelope=b['envelope_mm'], install={'by': 'robot', 'ops': ['slide on guide pins', '4 quarter-turns'], 'bolts': 0},
       moves=['panel releases and slides out (swap)']))
    mods.append(M('FUN-TOOLBAY', 'FUNCTIO', 'TOOL BAY', '툴 베이', 5, 'right forearm, dorsal', 'R', [
        P('rail carriage', 1, 'Ti64', 18), P('slide rail', 2, 'Ti64', 10), P('pivot hinge', 1, 'Ti64', 8),
        P('panel micro linear actuator', 1, 'mixed', 16), P('cartridge tray', 1, 'PEEK', 20), P('work light, high-CRI LED 2 W', 1, 'mixed', 12),
        P('articulating borescope camera 5.5 mm', 1, 'mixed', 25), P('1/4 in bit driver (micro gearmotor)', 1, 'mixed', 45),
        P('driver bit', 6, 'steel', 2), P('tray latch', 2, 'Ti64', 3), P('tool bay board', 1, 'FR4', 6), P('internal screw M2, Ti', 12, 'Ti64', 0.3),
    ], '전완 판이 원위 방향으로 6 mm 미끄러진 뒤 피벗해 열린다. 작업등, 관절형 점검 카메라, 비트 드라이버.',
       {'stroke_mm': 6, 'open_deg': 38}, envelope=(180, 55, 28), install={'by': 'robot (with forearm panels)'},
       moves=['forearm panel slides 6 mm then pivots 38 deg']))
    mods.append(M('FUN-HAND', 'FUNCTIO', 'ASSIST HAND', '보조 손', 5, 'right forearm, ventral', 'R', [
        P('palm base', 1, 'Ti64', 40), P('finger link', 6, 'Ti64', 8), P('thumb link', 3, 'Ti64', 8), P('joint pin', 12, 'Ti64', 1),
        P('finger tendon cable', 3, 'Dyneema', 1), P('micro BLDC + reducer', 2, 'mixed', 35), P('silicone pad', 3, 'silicone', 3),
        P('telescoping rail', 2, 'Ti64', 10), P('pad rotation mechanism', 1, 'Ti64', 12), P('pad force sensor', 3, 'FR4', 1),
        P('hand board', 1, 'FR4', 6), P('internal screw M2, Ti', 14, 'Ti64', 0.3),
    ], '전완 아래에 접혀 있다가 펼쳐지는 두 손가락 + 마주 보는 엄지 그리퍼. 정밀 모드는 M2 나사를, 와이드 모드는 파이프를 잡는다.',
       {'grip_N': 40}, envelope=(160, 50, 18), install={'by': 'robot (with forearm panels)'}, moves=['unfolds from under the forearm']))
    mods.append(M('FUN-PORT', 'FUNCTIO', 'SWAP PORT + SENSOR CARTRIDGE', '교체 포트', 5, 'left forearm, dorsal', 'L', [
        P('MYO-PORT socket (8 pogo pins + rails)', 1, 'Ti64/mixed', 25), P('quarter-turn latch', 2, 'Ti64', 3),
        P('cartridge housing', 1, 'Ti64', 30), P('thermal camera core', 1, 'mixed', 8), P('4-gas sensor', 1, 'mixed', 12),
        P('cartridge board', 1, 'FR4', 5), P('internal screw M2, Ti', 8, 'Ti64', 0.3),
    ], '공통 규격 포트. 지금은 열화상 카메라와 가스 센서 카트리지가 꽂혀 있다.', install={'by': 'robot (with forearm panels)'}))
    # panels: counts per blueprint group (PLAN §5.3), mount points per panel from its size class
    groups = S['panel_groups']
    t_mm = S['panel_t_mm']
    n_pan = sum(g['n'] for g in groups.values())
    area_pan = S['panel_area_m2']
    pan_g = area_pan * t_mm * RHO['Ti64'] * 1000 * 1.10 / n_pan
    mounts = sum(g['n'] * g['mounts'] for g in groups.values())
    mods.append(M('MYO-PANELS', 'MYO', 'BLUEPRINT PANELS', '청사진 판', 5, 'whole body', 'C', [
        *[P(f'panel, {k} (Ti-6Al-4V {t_mm} mm, SPIF)', g['n'], 'Ti64', pan_g * g['size']) for k, g in groups.items()],
        P('panel carrier (CFRP sub-frame)', 36, 'CFRP', 40), P('sliding panel guide (PEEK)', 48, 'PEEK', 3),
    ], '도하가 손으로 그린 판 그대로. 0.6 mm 티타늄 판을 점진 성형(SPIF)으로 곡면을 만들고 가장자리를 말아 강성을 낸다. '
       '판은 몸에 닿지 않고 탄소섬유 캐리어 위에 방진 그로밋으로 떠 있어서, 관절이 움직일 때 겹치고 미끄러진다.',
       {'panels': n_pan, 'thickness_mm': t_mm, 'area_m2': round(area_pan, 2), 'mount_points': mounts},
       install={'by': 'robot', 'ops': ['place', 'nutrunner'], 'picks': S['panel_picks']},
       moves=['deltoid caps slide in layers', 'abdominal bands telescope', 'knee cop slides over the knee', 'neck lamellae fan']))
    # ------------------------------------------------------------------ 6 PERSONA
    mods.append(M('PER-HELMET', 'PERSONA', 'PERSONA HELMET', '페르소나 헬멧', 6, 'head', 'C', [
        P('occipital shell, SPIF', 1, 'Ti64', 180), P('crown shell', 1, 'Ti64', 120), P('face plate carrier', 1, 'CFRP', 60),
        P('face plate hinge', 2, 'Ti64', 8), P('hinge pin', 2, 'Ti64', 2), P('face plate latch', 2, 'Ti64', 6), P('latch actuator', 1, 'mixed', 14),
        P('eye slit window, laminated PC, smoked', 2, 'PC', 6), P('global-shutter camera (behind slit)', 2, 'mixed', 4),
        P('ToF depth sensor', 1, 'mixed', 3), P('micro-OLED display', 2, 'mixed', 3), P('pancake optic', 2, 'PMMA', 12),
        P('temporal hub ring', 2, 'Ti64', 22), P('temporal hub cap (TiN)', 2, 'Ti64', 14), P('hub servo', 2, 'mixed', 6), P('hub bearing', 2, 'steel', 4),
        P('helmet liner', 1, 'EPP', 110), P('comfort pad', 6, 'foam', 6), P('EEG pressure pad (spring)', 8, 'mixed', 3),
        P('neck seal', 1, 'silicone', 45), P('chin cup', 1, 'silicone', 20),
        P('helmet board', 1, 'FR4', 12), P('IMU node (head)', 1, 'FR4', 4), P('helmet cable', 2, 'Cu/FEP', 5),
        P('internal screw M2, Ti', 40, 'Ti64', 0.3),
    ], '눈 슬릿은 얇다(높이 7 mm). 대신 슬릿 뒤 두 카메라와 깊이 센서가 넓은 시야를 찍어 눈앞 디스플레이에 보여 준다. '
       '슬릿으로 직접 보는 시야는 전원이 나가도 남는 예비 시야다. 귀 자리의 측두 허브는 송풍기 필터 캡이고, 돌아가며 흡기구를 연다.',
       {'slit_height_mm': 7, 'fov_deg_display': 110}, envelope=(250, 175, 270),
       install={'by': 'robot', 'ops': ['occipital shell', 'temporal hubs', 'face plate lowers', 'lock']},
       moves=['temporal hub rings rotate to open the intakes', 'face plate lowers and locks']))
    # ------------------------------------------------------------------ installation hardware (FIX)
    bolts = 0
    for m_ in mods:
        bolts += m_['install'].get('bolts', 0) * (2 if m_['sides'] == 'LR' else 6 if m_['sides'] == 'x6' else 1)
    quarter = 2 * 4 + 2 * 2 + 4                                       # battery panels, swap port, tool bay
    mods.append(M('FIX-INSTALL', 'FIX', 'INSTALLATION HARDWARE', '설치 체결구', 5, 'whole body', 'C', [
        P('panel screw, Ti Torx M2.5 countersunk', mounts, 'Ti64', 0.35),
        P('panel isolator grommet', mounts, 'EPDM', 0.15),
        P('quarter-turn stud + receptacle', quarter, 'Ti64', 2.2),
        P('module bolt, Ti M4/M5', bolts, 'Ti64', 2.4),
    ], '나사 하나하나가 토크 사양을 가진다(M2.5 티타늄 0.45 N·m). 로봇 끝의 너트러너가 클러치가 끊기는 순간까지 조인다.',
       {'panel_screw_torque_Nm': 0.45, 'module_bolt_torque_Nm': 2.9}, install={'by': 'robot (nutrunner)'}))
    # ------------------------------------------------------------------ tallies
    mult = lambda m_: 2 if m_['sides'] == 'LR' else 6 if m_['sides'] == 'x6' else 1
    for m_ in mods:
        n = sum(p['qty'] for p in m_['parts']); g = sum(p['qty'] * p['g_each'] for p in m_['parts'])
        m_['parts_per_unit'] = n; m_['mass_g_per_unit'] = round(g, 1); m_['units'] = mult(m_)
        m_['parts_total'] = n * mult(m_); m_['mass_kg_total'] = round(g * mult(m_) / 1000, 3)
    sysT, stgT = {}, {}
    for m_ in mods:
        s_ = sysT.setdefault(m_['system'], {'parts': 0, 'mass_kg': 0.0, 'units': 0})
        s_['parts'] += m_['parts_total']; s_['mass_kg'] += m_['mass_kg_total']; s_['units'] += m_['units']
        st = stgT.setdefault(m_['stage'], {'parts': 0, 'modules': 0, 'mass_kg': 0.0})
        st['parts'] += m_['parts_total']; st['modules'] += m_['units']; st['mass_kg'] += m_['mass_kg_total']
    for d in list(sysT.values()) + list(stgT.values()):
        d['mass_kg'] = round(d['mass_kg'], 2)
    total_parts = sum(m_['parts_total'] for m_ in mods)
    total_mass = sum(m_['mass_kg_total'] for m_ in mods)
    worn = sum(m_['mass_kg_total'] for m_ in mods if m_['stage'] == 0)
    lru = sum(m_['units'] for m_ in mods if m_['system'] not in ('MYO', 'FIX', 'FASCIA'))
    robot_ops = {'modules_installed': lru, 'panel_picks': S['panel_picks'], 'screws_driven': mounts + bolts,
                 'quarter_turns': quarter, 'connectors_mated': 48 + 8 + 12 + 4 + 4}
    return {'version': 'v2 (R2, 2026-10-03)', 'counting_rule': __doc__.split('Counting rule: ')[1].split('\n')[0] + ' ' + __doc__.split('Counting rule: ')[1].split('\n')[1].strip(),
            'systems': {k: {'name_en': v[0], 'name_ko': v[1], 'summary_ko': v[2], **sysT.get(k, {})} for k, v in SYSTEMS.items()},
            'stages': {k: {'name_en': v[0], 'name_ko': v[1], 'what_ko': v[2], **stgT.get(k, {})} for k, v in STAGES.items()},
            'modules': mods, 'total_parts': total_parts, 'total_mass_kg': round(total_mass, 2),
            'worn_mass_kg': round(worn, 2), 'robot_ops': robot_ops,
            'pre_assembled_modules': lru}
