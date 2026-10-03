# MYOMORPH-MK. 1 — 시스템 카탈로그 (부품표 v2)

> 자동 생성: `engineering/report.py` ← `bom.json` v2 (R2, 2026-10-03). 손으로 고치지 않는다.
> **부품 5,819개** · 사전 조립 모듈 41개 · 질량 35.13 kg(유체 제외) · 사람이 입는 것 1.92 kg
> 세는 법: one part = one separately made or bought item that is assembled (a PCB assembly, a bearing, a cell, a screw each count 1; a sewn pattern piece counts 1; a moulded or printed one-piece item counts 1).

각 모듈의 "원리"는 사이트 시스템 카드의 본문이다. 부품표는 그 카드의 분해도에 붙는 이름표다.

## 시스템 요약

| 코드 | 이름 | 한 줄 | 부품 | 질량 kg |
|---|---|---|---:|---:|
| **FASCIA** | NEURAL WEAR · 신경 언더슈트 | 피부에 닿는 층. 근전도·뇌파 센서와 냉각 튜브가 들어 있는 레이싱 슈트형 옷 | 208 | 1.92 |
| **PES** | GROUND · 발 | 땅과 만나는 곳. 슈트의 무게가 내려가는 끝 | 102 | 2.28 |
| **OS** | SKELETON · 골격 | 몸 바깥의 뼈대. 슈트 무게를 땅으로 내리고 힘을 몸에 전달하는 프레임과 커프 | 599 | 6.53 |
| **MUSCULUS** | MUSCLE · 근육 | 전기로 움직이는 밀폐형 유압 근육(EHA) 6개 | 450 | 4.47 |
| **TENDO** | TENDON · 힘줄 | 케이블로 힘을 전하는 팔꿈치 구동기와 어깨 중력보상 스프링 | 140 | 0.83 |
| **ENERGIA** | ENERGY · 에너지 | 외부 패널이 곧 배터리. 48 V 배전과 하네스 | 281 | 2.88 |
| **BRANCHIA** | THERMAL · 아가미 | 막 아가미(증발 냉각기), 냉각수 회로, 팬, 열리는 루버 | 151 | 1.57 |
| **VITA** | LIFE SUPPORT · 생명유지 | 헬멧 송풍 정화, 가스 감시, 수분 공급, 비상 해제 | 58 | 0.50 |
| **NERVUS** | NERVOUS SYSTEM · 신경계 | 척추 연산부, 실시간 버스, 상태광 | 259 | 0.48 |
| **PERSONA** | HELMET · 얼굴 | 헬멧, 눈 슬릿 카메라, 시야 디스플레이 | 88 | 0.82 |
| **FUNCTIO** | FUNCTION · 기능 | 툴 베이, 보조 손, 교체 포트 | 96 | 0.53 |
| **MYO** | PANELS · 근육 패널 | 도하의 청사진 판 477장과 패널 캐리어 | 561 | 11.35 |
| **FIX** | FASTENERS · 체결 | 설치 볼트, 패널 체결구, 방진 그로밋 | 2,826 | 0.97 |

## 조립 단계 (로봇 작업 순서)

| 단계 | 이름 | 내용 | 부품 | 모듈 |
|---|---|---|---:|---:|
| 0 | WEAR · 착용 | 도하가 언더슈트, 바라클라바, 이너 장갑을 입고 셀에 들어온다(사람이 입는다) | 208 | 4 |
| 1 | GROUND · 발 | 부츠에 발을 넣고 로봇이 바인딩을 조인다 | 102 | 2 |
| 2 | SKELETON · 골격 | 다리 프레임 → 골반 → 척추와 하네스 → 팔 프레임, 커프 조임 | 599 | 6 |
| 3 | MUSCLE · 근육 | EHA 6개 핀 결합, 팔꿈치 힘줄 구동기, 어깨 스프링, 힘줄 장력 | 590 | 10 |
| 4 | SYSTEMS · 내장 시스템 | 배전, 버퍼, 냉동기, 냉각수 회로, 팬, 연산부, 생명유지, 언더슈트 연결, 천장 탯줄 연결 | 403 | 15 |
| 5 | PANELS · 패널 | 청사진 판 477장(배터리 패널, 루버, 툴 베이 패널 포함) | 3,801 | 8 |
| 6 | PERSONA · 헬멧 | 후두 셸 → 측두 허브 → 안면판 → 락 | 116 | 2 |
| 7 | BRING-UP · 기동 | 신경 보정, 자가 진단, 탯줄 분리, 배터리 단독 구동 | 0 | 0 |

로봇 작업 합계: 모듈 설치 41회, 판 픽 168회, 나사 1,458개, 쿼터턴 16개, 커넥터 76개.

## FASCIA — NEURAL WEAR · 신경 언더슈트

피부에 닿는 층. 근전도·뇌파 센서와 냉각 튜브가 들어 있는 레이싱 슈트형 옷

### FAS-SUIT · NEURAL UNDERSUIT · 신경 언더슈트

- **수량** 1 (C) · **위치** whole body · **조립 단계** 0 WEAR
- **부품** 개당 151개 · 합계 151개 · **질량** 개당 1.726 kg · 합계 1.726 kg
- **사양** emg_channels 784 · tube_m 77.50 · lcg_flow_L_min 1.43
- **설치** by: wearer, connect: waist L/R coolant + data → nape data

**원리** MYO(근육)를 읽는 옷. 근육이 수축하기 30~100 ms 전에 척수의 운동신경이 근섬유에 전기 신호를 보낸다. 피부 위 고밀도 전극 격자가 이 신호를 받아 운동단위 하나하나의 발화로 분해하면, 슈트는 몸이 움직이기 전에 얼마나 힘을 쓰려는지 안다. 같은 원단 속 3.2 mm 튜브에는 냉각수가 흘러 몸의 열을 직접 뺀다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| 3-layer knit pattern piece (aramid/elastane spacer, 1.1 mm) | 28 | aramid | 21 |
| two-way front zip | 1 | PA/steel | 18 |
| cooling tube circuit, PU 3.2 OD / 1.6 ID (total 77 m) | 24 | PU | 23.24 |
| tube distribution manifold, 6-port | 4 | PEEK | 9 |
| dry-break quick disconnect, garment half | 4 | Ti64/FKM | 11 |
| HD-sEMG grid, 32 ch printed on knit (4 x 8, 10 mm) | 24 | Ag/AgCl-knit | 6 |
| bipolar dry EMG electrode pair | 16 | Ag/AgCl | 3 |
| biopotential node, 64 ch, overmoulded pod | 22 | FR4/TPU | 7 |
| dry ECG electrode | 3 | Ag-knit | 2 |
| heat-flux / skin temperature sensor | 6 | FR4 | 1.5 |
| respiration strain band | 1 | TPU | 8 |
| sweat conductance sensor | 1 | FR4 | 2 |
| embroidered data bus run (Ag yarn, TPU laminate) | 14 | Ag/TPU | 6 |
| sealed trunk connector, 24-pin (nape, waist L/R) | 3 | mixed | 9 |

### FAS-BALA · EEG BALACLAVA · 뇌파 바라클라바

- **수량** 1 (C) · **위치** head · **조립 단계** 0 WEAR
- **부품** 개당 41개 · 합계 41개 · **질량** 개당 0.134 kg · 합계 0.134 kg
- **사양** eeg_channels 32 · sample_Hz 500
- **설치** by: wearer

**원리** 뇌는 움직이기 0.5~1.5초 전부터 운동피질에서 준비 신호(운동관련 전위, 뮤·베타 리듬 감소)를 낸다. 헬멧 라이너가 누르는 32개 건식 전극이 이 신호를 읽어 동작 모드(걷기, 계단, 들기, 공구)를 고르고, 슈트가 의도와 다르게 움직였을 때 뇌가 내는 오류 전위로 즉시 멈춘다. 연속 제어는 근전도, 판단은 뇌파가 맡는다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| knit hood | 1 | aramid | 45 |
| dry comb EEG electrode, spring-loaded | 32 | Ag/AgCl | 1.6 |
| EEG node, 32 ch | 1 | FR4/TPU | 9 |
| forehead PPG (SpO2, HR) | 1 | FR4 | 2 |
| bone-conduction transducer | 2 | mixed | 6 |
| bone-conduction mic | 1 | mixed | 3 |
| nape connector | 1 | mixed | 6 |
| embroidered bus run | 2 | Ag/TPU | 3 |

### FAS-GLOVE · INNER GLOVE · 이너 장갑

- **수량** 2 (LR) · **위치** hand · **조립 단계** 0 WEAR
- **부품** 개당 8개 · 합계 16개 · **질량** 개당 0.029 kg · 합계 0.059 kg
- **설치** by: wearer

**원리** 손끝 압력을 읽어 보조 손과 공구의 힘을 맞춘다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| knit glove | 1 | aramid | 22 |
| fingertip pressure sensor | 5 | FR4 | 0.5 |
| wrist connector | 1 | mixed | 3 |
| embroidered bus run | 1 | Ag/TPU | 2 |

## PES — GROUND · 발

땅과 만나는 곳. 슈트의 무게가 내려가는 끝

### PES-BOOT · BOOT · 부츠

- **수량** 2 (LR) · **위치** foot · **조립 단계** 1 GROUND
- **부품** 개당 51개 · 합계 102개 · **질량** 개당 1.142 kg · 합계 2.284 kg
- **외형** 290 × 115 × 95 mm (길이 × 폭 × 두께)
- **사양** load_cells 4 · pressure_zones 16
- **설치** by: wearer + robot, ops: close binding (BOA)

**원리** 슈트 무게는 사람 몸이 아니라 프레임을 따라 이 발판으로 내려간다. 발판 아래 하중 센서 4개와 16구역 압력 깔창이 무게중심과 보행 단계(뒤꿈치 닿음 → 발바닥 → 밀기)를 1 kHz로 읽는다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| sole plate, CFRP | 1 | CFRP | 250 |
| heel node, LPBF | 1 | Ti64 | 95 |
| outsole, lugged | 1 | NBR | 180 |
| midsole | 1 | TPU foam | 85 |
| pressure insole, 16-zone capacitive | 1 | mixed | 45 |
| shear-beam load cell | 4 | steel | 18 |
| heel lever (Achilles link anchor), LPBF | 1 | Ti64 | 70 |
| ankle hinge yoke | 2 | Ti64 | 38 |
| thin-section bearing | 4 | steel | 6 |
| hinge axle | 2 | Ti64 | 9 |
| circlip | 4 | steel | 0.4 |
| instep shell | 1 | CFRP | 60 |
| heel cup | 1 | CFRP | 55 |
| BOA dial | 1 | PA | 18 |
| BOA lace | 1 | steel | 2 |
| foot node (load-cell amp + IMU) | 1 | FR4 | 8 |
| sealed connector | 1 | mixed | 5 |
| inner bootie | 1 | EVA | 60 |
| internal screw M3, Ti | 22 | Ti64 | 0.8 |

## OS — SKELETON · 골격

몸 바깥의 뼈대. 슈트 무게를 땅으로 내리고 힘을 몸에 전달하는 프레임과 커프

### OS-LEG · LEG FRAME · 다리 프레임

- **수량** 2 (LR) · **위치** thigh + shank · **조립 단계** 2 SKELETON
- **부품** 개당 111개 · 합계 222개 · **질량** 개당 1.287 kg · 합계 2.575 kg
- **외형** 820 × 150 × 150 mm (길이 × 폭 × 두께)
- **사양** knee_rom_deg [0, 125] · icr_tracking 1
- **설치** by: robot, ops: dock to boot ankle hinge → pin hip → tighten 2 cuffs, bolts: 8

**원리** 허벅지와 정강이 양옆을 지나는 탄소섬유 지주. 무릎은 단순 경첩이 아니라 교차 4절 링크라서 사람 무릎처럼 굽힐수록 회전중심이 뒤로 이동한다(순간회전중심 추종). 그래서 슈트 무릎이 사람 무릎을 비틀지 않는다. 커프는 힘을 몸에 전하는 유일한 접점이고, 나머지는 몸에서 떠 있다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| thigh strut, lateral (CFRP / Ti end fittings) | 1 | CFRP/Ti | 170 |
| thigh strut, medial | 1 | CFRP/Ti | 130 |
| shank strut, lateral | 1 | CFRP/Ti | 110 |
| shank strut, medial | 1 | CFRP/Ti | 100 |
| knee crossed four-bar link | 4 | Ti64 | 26 |
| knee joint plate | 4 | Ti64 | 22 |
| needle roller bearing | 8 | steel | 2.5 |
| knee pin | 8 | Ti64 | 4 |
| circlip | 16 | steel | 0.4 |
| knee hard stop + bumper | 2 | Ti/PU | 6 |
| knee absolute encoder | 1 | FR4 | 5 |
| encoder magnet | 1 | NdFeB | 1 |
| ankle bracket, LPBF | 2 | Ti64 | 40 |
| EHA clevis node, thigh, LPBF | 1 | Ti64 | 45 |
| EHA clevis node, shank, LPBF | 1 | Ti64 | 38 |
| thigh cuff shell | 1 | CFRP | 95 |
| thigh cuff liner (EPP + gel) | 1 | EPP/silicone | 30 |
| thigh cuff strap | 2 | PA | 12 |
| thigh cuff BOA dial | 1 | PA | 18 |
| shank cuff shell | 1 | CFRP | 70 |
| shank cuff liner (EPP + gel) | 1 | EPP/silicone | 25 |
| shank cuff strap | 1 | PA | 12 |
| shank cuff BOA dial | 1 | PA | 18 |
| strain gauge bridge | 2 | FR4 | 2 |
| IMU node | 2 | FR4 | 4 |
| harness clip | 6 | PA | 1 |
| internal screw M4, Ti | 40 | Ti64 | 0.9 |

### OS-PELVIS · PELVIS + HIP JOINTS · 골반과 고관절

- **수량** 1 (C) · **위치** pelvis · **조립 단계** 2 SKELETON
- **부품** 개당 83개 · 합계 83개 · **질량** 개당 1.353 kg · 합계 1.353 kg
- **외형** 360 × 220 × 120 mm (길이 × 폭 × 두께)
- **사양** hip_rom_deg {'flex': 110, 'ext': 20, 'abd': 35, 'rot': 25}
- **설치** by: robot, ops: pin both leg frames → close belt, bolts: 12

**원리** 고관절은 세 축이다. 굽힘·폄은 EHA가 밀고, 벌림과 돌림은 스프링으로 가운데를 찾는 수동 축이라 사람이 다리를 벌리거나 돌릴 때 막지 않는다. 축마다 하드 스톱이 사람의 가동 범위 안에서 기계적으로 막는다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| pelvic arch, LPBF lattice + CFRP | 1 | Ti64/CFRP | 320 |
| lateral hip arm | 2 | Ti64 | 110 |
| crossed roller bearing (hip flexion axis) | 2 | steel | 45 |
| hip output flange | 2 | Ti64 | 40 |
| hip housing | 2 | Al7075 | 60 |
| abduction hinge yoke (passive) | 2 | Ti64 | 35 |
| abduction bearing | 4 | steel | 6 |
| abduction axle | 2 | Ti64 | 8 |
| abduction centring spring | 2 | steel | 10 |
| rotation ring bearing (passive, +/-25 deg) | 2 | steel | 30 |
| hip encoder (flex, abd, rot) | 6 | FR4 | 5 |
| hip hard stop | 6 | Ti/PU | 6 |
| pelvic belt, padded | 1 | PA/EPP | 140 |
| belt buckle | 1 | Al7075 | 22 |
| belt BOA dial | 2 | PA | 18 |
| IMU node (pelvis) | 1 | FR4 | 4 |
| PDU / buffer bracket | 1 | Ti64 | 25 |
| internal screw M4, Ti | 44 | Ti64 | 0.9 |

### OS-SPINE · SPINE + HARNESS · 척추와 하네스

- **수량** 1 (C) · **위치** back · **조립 단계** 2 SKELETON
- **부품** 개당 152개 · 합계 152개 · **질량** 개당 1.373 kg · 합계 1.373 kg
- **외형** 520 × 330 × 40 mm (길이 × 폭 × 두께)
- **사양** lumbar_flex_deg 60 · scapular_travel_mm 38
- **설치** by: robot, ops: dock to pelvis → close harness, bolts: 10

**원리** 허리는 티타늄 판스프링 6장이 쌓인 척추다. 앞으로 숙이면 판스프링이 에너지를 저장했다가 일어설 때 돌려준다(전원 불필요). 어깨뼈(견갑골)는 팔을 들 때 가슴 위를 미끄러지는데, 레일 위 캐리지가 그 움직임을 따라가 슈트 어깨 축이 사람 어깨 중심에서 벗어나지 않는다. 외골격의 가장 어려운 문제를 기구로 푼다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| lumbar vertebra block, LPBF | 5 | Ti64 | 38 |
| lumbar leaf flexure 0.8 mm | 6 | Ti64 | 14 |
| flexure guide rail | 2 | Ti64 | 22 |
| flexure preload screw | 6 | Ti64 | 2 |
| thoracic frame, LPBF lattice | 1 | Ti64 | 380 |
| chest harness shell | 2 | CFRP | 65 |
| harness foam | 3 | EPP | 15 |
| harness strap | 4 | PA | 14 |
| harness buckle | 2 | Al7075 | 22 |
| harness BOA dial | 2 | PA | 18 |
| scapular tracking rail | 2 | Ti64 | 30 |
| scapular carriage | 2 | Ti64 | 25 |
| carriage bearing | 8 | steel | 3 |
| scapular linkage | 6 | Ti64 | 12 |
| linkage pin | 12 | Ti64 | 2 |
| scapular return spring | 4 | steel | 6 |
| scapular encoder | 4 | FR4 | 5 |
| IMU node (thorax) | 1 | FR4 | 4 |
| harness channel clip | 20 | PA | 1 |
| internal screw M4, Ti | 60 | Ti64 | 0.9 |

### OS-ARM · ARM FRAME · 팔 프레임

- **수량** 2 (LR) · **위치** upper arm + forearm · **조립 단계** 2 SKELETON
- **부품** 개당 71개 · 합계 142개 · **질량** 개당 0.612 kg · 합계 1.224 kg
- **외형** 560 × 90 × 60 mm (길이 × 폭 × 두께)
- **사양** elbow_rom_deg [0, 135]
- **설치** by: robot, ops: dock to scapular carriage → tighten 2 cuffs, bolts: 6

**원리** 팔 바깥쪽 지주와 팔꿈치 경첩. 손목은 구동하지 않는 2축 짐벌이라 손은 완전히 자유롭다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| upper arm strut, lateral | 1 | CFRP/Ti | 95 |
| shoulder linkage arm | 3 | Ti64 | 22 |
| shoulder linkage bearing | 6 | steel | 3 |
| shoulder linkage pin | 3 | Ti64 | 3 |
| elbow yoke | 2 | Ti64 | 24 |
| elbow bearing | 2 | steel | 5 |
| elbow axle | 1 | Ti64 | 7 |
| circlip | 2 | steel | 0.4 |
| elbow hard stop | 2 | Ti/PU | 4 |
| elbow encoder | 1 | FR4 | 5 |
| encoder magnet | 1 | NdFeB | 1 |
| forearm strut, radial | 1 | CFRP/Ti | 80 |
| wrist gimbal ring | 2 | Ti64 | 18 |
| gimbal bearing | 4 | steel | 2 |
| gimbal axle | 2 | Ti64 | 3 |
| upper arm cuff shell | 1 | CFRP | 50 |
| upper arm cuff liner (EPP + gel) | 1 | EPP/silicone | 15 |
| upper arm cuff strap | 1 | PA | 12 |
| upper arm cuff BOA dial | 1 | PA | 18 |
| forearm cuff shell | 1 | CFRP | 45 |
| forearm cuff liner (EPP + gel) | 1 | EPP/silicone | 14 |
| forearm cuff strap | 1 | PA | 12 |
| forearm cuff BOA dial | 1 | PA | 18 |
| IMU node | 2 | FR4 | 4 |
| internal screw M3, Ti | 28 | Ti64 | 0.8 |

## MUSCULUS — MUSCLE · 근육

전기로 움직이는 밀폐형 유압 근육(EHA) 6개

### MUS-EHA-HIP · HIP MUSCLE (EHA) · 고관절 근육

- **수량** 2 (LR) · **위치** gluteal / posterior pelvis · **조립 단계** 3 MUSCLE
- **부품** 개당 75개 · 합계 150개 · **질량** 개당 0.694 kg · 합계 1.389 kg
- **외형** 215 × 44 × 18 mm (길이 × 폭 × 두께)
- **사양** bore_mm 12.00 · rod_mm 6.00 · stroke_mm 72.50 · force_kN 2.01 · design_torque_Nm 80.20 · motor_W 159.00 · pressure_MPa 21
- **설치** by: robot, ops: pin rod eye → pin base clevis → circlips → plug bus + power → test stroke, bolts: 2
- **독립적 움직임** kinetic bulge of the covering panel as the cylinder extends

**원리** 모터, 양방향 기어 펌프, 밸브 블록, 실린더를 하나로 밀봉한 전기유압 액추에이터(EHA). 중앙 유압 펌프와 긴 고압 배관이 없다. 모터가 정방향으로 돌면 펌프가 기름을 실린더 한쪽으로 밀어 늘어나고, 역방향이면 줄어든다. 밸브로 압력을 버리지 않고 모터 회전으로 직접 제어하니 효율이 높다. 다리를 흔드는 구간에서는 바이패스 밸브가 열려 저항 없이 따라온다(자유 스윙). 고장 나면 이 밸브가 기본으로 열려 사람을 가두지 않는다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| BLDC stator assembly, frameless 12-slot | 1 | Cu/Si-steel | 142.31 |
| rotor assembly, 14-pole NdFeB | 1 | NdFeB/steel | 77.62 |
| motor bearing, deep groove 6701 | 2 | steel | 3 |
| motor housing | 1 | Al7075 | 44.57 |
| motor end cap | 1 | Al7075 | 10.29 |
| hall + 17-bit absolute encoder PCB | 1 | FR4 | 4 |
| pump gear, drive / idler (internal gear set) | 2 | steel DLC | 7.71 |
| pump body | 1 | Al7075 | 37.71 |
| pump side plate | 2 | bronze | 6 |
| shaft seal | 1 | PTFE | 0.6 |
| valve manifold, LPBF | 1 | Ti64 | 81.43 |
| pilot-operated check valve | 2 | steel | 6 |
| pressure relief valve 25 MPa | 2 | steel | 7 |
| free-swing bypass solenoid valve | 1 | steel/Cu | 16 |
| pressure transducer | 2 | steel | 5 |
| oil temperature sensor | 1 | steel | 1.5 |
| bootstrap accumulator body | 1 | Ti64 | 29.14 |
| accumulator piston | 1 | Al7075 | 4.29 |
| accumulator end cap | 1 | Ti64 | 5.14 |
| cylinder barrel, bore 12 mm | 1 | Ti64 | 35.27 |
| piston | 1 | Ti64 | 6.86 |
| piston rod 6 mm, DLC | 1 | Ti64 | 12.84 |
| piston seal | 2 | PTFE/bronze | 0.8 |
| rod seal | 1 | PU | 0.6 |
| wiper | 1 | PU | 0.4 |
| rod gland | 1 | Ti64 | 7.71 |
| rod eye | 1 | Ti64 | 9.43 |
| magnetostrictive position sensor | 1 | steel | 9 |
| spherical plain bearing | 2 | steel | 4 |
| clevis pin | 2 | Ti64 | 4 |
| circlip | 4 | steel | 0.3 |
| motor driver + MCU, EtherCAT slave | 1 | FR4 | 14 |
| thermal pad | 1 | silicone | 1.5 |
| driver cover | 1 | Al7075 | 9 |
| sealed connector, power + bus | 2 | mixed | 4 |
| O-ring | 8 | FKM | 0.2 |
| fill / bleed screw | 2 | steel | 1 |
| hydraulic fluid, synthetic ester (ml) | 1 | ester | 22.12 |
| internal screw M3, Ti | 16 | Ti64 | 0.7 |

### MUS-EHA-KNEE · KNEE MUSCLE (EHA) · 무릎 근육

- **수량** 2 (LR) · **위치** anterior thigh · **조립 단계** 3 MUSCLE
- **부품** 개당 75개 · 합계 150개 · **질량** 개당 0.738 kg · 합계 1.477 kg
- **외형** 184 × 44 × 20 mm (길이 × 폭 × 두께)
- **사양** bore_mm 14.00 · rod_mm 7.00 · stroke_mm 56.80 · force_kN 2.49 · design_torque_Nm 79.80 · motor_W 158.00 · pressure_MPa 21
- **설치** by: robot, ops: pin rod eye → pin base clevis → circlips → plug bus + power → test stroke, bolts: 2
- **독립적 움직임** kinetic bulge of the covering panel as the cylinder extends

**원리** 모터, 양방향 기어 펌프, 밸브 블록, 실린더를 하나로 밀봉한 전기유압 액추에이터(EHA). 중앙 유압 펌프와 긴 고압 배관이 없다. 모터가 정방향으로 돌면 펌프가 기름을 실린더 한쪽으로 밀어 늘어나고, 역방향이면 줄어든다. 밸브로 압력을 버리지 않고 모터 회전으로 직접 제어하니 효율이 높다. 다리를 흔드는 구간에서는 바이패스 밸브가 열려 저항 없이 따라온다(자유 스윙). 고장 나면 이 밸브가 기본으로 열려 사람을 가두지 않는다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| BLDC stator assembly, frameless 12-slot | 1 | Cu/Si-steel | 141.62 |
| rotor assembly, 14-pole NdFeB | 1 | NdFeB/steel | 77.25 |
| motor bearing, deep groove 6701 | 2 | steel | 3 |
| motor housing | 1 | Al7075 | 52 |
| motor end cap | 1 | Al7075 | 12 |
| hall + 17-bit absolute encoder PCB | 1 | FR4 | 4 |
| pump gear, drive / idler (internal gear set) | 2 | steel DLC | 9 |
| pump body | 1 | Al7075 | 44 |
| pump side plate | 2 | bronze | 7 |
| shaft seal | 1 | PTFE | 0.6 |
| valve manifold, LPBF | 1 | Ti64 | 95 |
| pilot-operated check valve | 2 | steel | 6 |
| pressure relief valve 25 MPa | 2 | steel | 7 |
| free-swing bypass solenoid valve | 1 | steel/Cu | 16 |
| pressure transducer | 2 | steel | 5 |
| oil temperature sensor | 1 | steel | 1.5 |
| bootstrap accumulator body | 1 | Ti64 | 34 |
| accumulator piston | 1 | Al7075 | 5 |
| accumulator end cap | 1 | Ti64 | 6 |
| cylinder barrel, bore 14 mm | 1 | Ti64 | 33.31 |
| piston | 1 | Ti64 | 8 |
| piston rod 7 mm, DLC | 1 | Ti64 | 14.8 |
| piston seal | 2 | PTFE/bronze | 0.8 |
| rod seal | 1 | PU | 0.6 |
| wiper | 1 | PU | 0.4 |
| rod gland | 1 | Ti64 | 9 |
| rod eye | 1 | Ti64 | 11 |
| magnetostrictive position sensor | 1 | steel | 9 |
| spherical plain bearing | 2 | steel | 4 |
| clevis pin | 2 | Ti64 | 4 |
| circlip | 4 | steel | 0.3 |
| motor driver + MCU, EtherCAT slave | 1 | FR4 | 14 |
| thermal pad | 1 | silicone | 1.5 |
| driver cover | 1 | Al7075 | 9 |
| sealed connector, power + bus | 2 | mixed | 4 |
| O-ring | 8 | FKM | 0.2 |
| fill / bleed screw | 2 | steel | 1 |
| hydraulic fluid, synthetic ester (ml) | 1 | ester | 23.22 |
| internal screw M3, Ti | 16 | Ti64 | 0.7 |

### MUS-EHA-ANKLE · ANKLE MUSCLE (EHA) · 발목 근육

- **수량** 2 (LR) · **위치** posterior shank · **조립 단계** 3 MUSCLE
- **부품** 개당 75개 · 합계 150개 · **질량** 개당 0.803 kg · 합계 1.606 kg
- **외형** 153 × 44 × 18 mm (길이 × 폭 × 두께)
- **사양** bore_mm 12.00 · rod_mm 6.00 · stroke_mm 41.60 · force_kN 2.12 · design_torque_Nm 95.20 · motor_W 283.00 · pressure_MPa 21
- **설치** by: robot, ops: pin rod eye → pin base clevis → circlips → plug bus + power → test stroke, bolts: 2
- **독립적 움직임** kinetic bulge of the covering panel as the cylinder extends

**원리** 모터, 양방향 기어 펌프, 밸브 블록, 실린더를 하나로 밀봉한 전기유압 액추에이터(EHA). 중앙 유압 펌프와 긴 고압 배관이 없다. 모터가 정방향으로 돌면 펌프가 기름을 실린더 한쪽으로 밀어 늘어나고, 역방향이면 줄어든다. 밸브로 압력을 버리지 않고 모터 회전으로 직접 제어하니 효율이 높다. 다리를 흔드는 구간에서는 바이패스 밸브가 열려 저항 없이 따라온다(자유 스윙). 고장 나면 이 밸브가 기본으로 열려 사람을 가두지 않는다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| BLDC stator assembly, frameless 12-slot | 1 | Cu/Si-steel | 227.56 |
| rotor assembly, 14-pole NdFeB | 1 | NdFeB/steel | 124.12 |
| motor bearing, deep groove 6701 | 2 | steel | 3 |
| motor housing | 1 | Al7075 | 44.57 |
| motor end cap | 1 | Al7075 | 10.29 |
| hall + 17-bit absolute encoder PCB | 1 | FR4 | 4 |
| pump gear, drive / idler (internal gear set) | 2 | steel DLC | 7.71 |
| pump body | 1 | Al7075 | 37.71 |
| pump side plate | 2 | bronze | 6 |
| shaft seal | 1 | PTFE | 0.6 |
| valve manifold, LPBF | 1 | Ti64 | 81.43 |
| pilot-operated check valve | 2 | steel | 6 |
| pressure relief valve 25 MPa | 2 | steel | 7 |
| free-swing bypass solenoid valve | 1 | steel/Cu | 16 |
| pressure transducer | 2 | steel | 5 |
| oil temperature sensor | 1 | steel | 1.5 |
| bootstrap accumulator body | 1 | Ti64 | 29.14 |
| accumulator piston | 1 | Al7075 | 4.29 |
| accumulator end cap | 1 | Ti64 | 5.14 |
| cylinder barrel, bore 12 mm | 1 | Ti64 | 23.23 |
| piston | 1 | Ti64 | 6.86 |
| piston rod 6 mm, DLC | 1 | Ti64 | 8.97 |
| piston seal | 2 | PTFE/bronze | 0.8 |
| rod seal | 1 | PU | 0.6 |
| wiper | 1 | PU | 0.4 |
| rod gland | 1 | Ti64 | 7.71 |
| rod eye | 1 | Ti64 | 9.43 |
| magnetostrictive position sensor | 1 | steel | 9 |
| spherical plain bearing | 2 | steel | 4 |
| clevis pin | 2 | Ti64 | 4 |
| circlip | 4 | steel | 0.3 |
| motor driver + MCU, EtherCAT slave | 1 | FR4 | 14 |
| thermal pad | 1 | silicone | 1.5 |
| driver cover | 1 | Al7075 | 9 |
| sealed connector, power + bus | 2 | mixed | 4 |
| O-ring | 8 | FKM | 0.2 |
| fill / bleed screw | 2 | steel | 1 |
| hydraulic fluid, synthetic ester (ml) | 1 | ester | 15.04 |
| internal screw M3, Ti | 16 | Ti64 | 0.7 |

## TENDO — TENDON · 힘줄

케이블로 힘을 전하는 팔꿈치 구동기와 어깨 중력보상 스프링

### TEN-ELBOW · ELBOW TENDON DRIVE · 팔꿈치 힘줄 구동기

- **수량** 2 (LR) · **위치** posterior upper arm · **조립 단계** 3 MUSCLE
- **부품** 개당 43개 · 합계 86개 · **질량** 개당 0.217 kg · 합계 0.434 kg
- **외형** 90 × 60 × 16 mm (길이 × 폭 × 두께)
- **사양** design_torque_Nm 5.00 · tendon_N 230.00 · reduction 23.80
- **설치** by: robot, ops: clip to upper arm strut → route tendon → tension 120 N preload, bolts: 3

**원리** 사람 손가락을 움직이는 근육이 팔뚝에 있고 힘줄로 당기듯, 위팔 뒤의 납작한 모터가 초고분자량 폴리에틸렌 힘줄로 팔꿈치 앞의 풀리를 당긴다. 무거운 모터를 관절에서 멀리 두어 팔 끝이 가볍다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| flat BLDC stator | 1 | Cu/Si-steel | 48 |
| flat BLDC rotor | 1 | NdFeB/steel | 26 |
| motor bearing | 2 | steel | 2.5 |
| motor housing half | 2 | Al7075 | 14 |
| capstan drum | 1 | Al7075 | 12 |
| cable reduction pulley | 3 | Al7075 | 6 |
| pulley bearing | 6 | steel | 1.5 |
| pulley axle | 3 | Ti64 | 2 |
| UHMWPE tendon 2 mm | 1 | Dyneema | 3 |
| PTFE-lined Bowden sheath | 1 | PTFE/steel | 14 |
| sheath ferrule | 2 | Ti64 | 1.5 |
| tendon tensioner | 1 | Ti64 | 6 |
| elbow output pulley | 1 | Al7075 | 14 |
| output pulley bearing | 2 | steel | 2.5 |
| tendon load cell | 1 | steel | 4 |
| motor driver + MCU | 1 | FR4 | 9 |
| internal screw M2.5, Ti | 14 | Ti64 | 0.5 |

### TEN-SHOULDER · SHOULDER SPRING CASSETTE · 어깨 중력보상 스프링

- **수량** 2 (LR) · **위치** shoulder top / upper back · **조립 단계** 3 MUSCLE
- **부품** 개당 27개 · 합계 54개 · **질량** 개당 0.198 kg · 합계 0.395 kg
- **외형** 120 × 70 × 30 mm (길이 × 폭 × 두께)
- **사양** compensated_Nm_at_90deg 13.90 · spring_energy_J 13.90
- **설치** by: robot, ops: seat on thoracic frame → hook cable to upper arm strut, bolts: 4

**원리** 팔을 들고 있는 힘의 대부분은 팔 무게를 버티는 힘이다. 사인 곡선 캠이 스프링 힘을 팔 각도에 맞춰 바꿔 주어 어느 각도에서나 팔이 떠 있는 것처럼 가볍다. 전원 없이 작동하고, 작은 모터는 공구 무게가 바뀔 때 예압만 조정한다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| coil spring | 2 | steel | 42 |
| cam (sin-profile) | 1 | Ti64 | 18 |
| spring cable | 1 | Dyneema | 2 |
| pulley | 2 | Al7075 | 6 |
| pulley bearing | 4 | steel | 1.5 |
| trim worm | 1 | steel | 4 |
| trim worm wheel | 1 | PEEK | 3 |
| trim micro motor | 1 | mixed | 14 |
| ratchet | 1 | steel | 4 |
| pawl | 1 | steel | 1.5 |
| cassette housing half | 2 | Al7075 | 22 |
| internal screw M2.5, Ti | 10 | Ti64 | 0.5 |

## ENERGIA — ENERGY · 에너지

외부 패널이 곧 배터리. 48 V 배전과 하네스

### ENE-PDU · POWER DISTRIBUTION · 배전 장치

- **수량** 1 (C) · **위치** pelvis (posterior) · **조립 단계** 4 SYSTEMS
- **부품** 개당 26개 · 합계 26개 · **질량** 개당 0.200 kg · 합계 0.200 kg
- **외형** 110 × 80 × 22 mm (길이 × 폭 × 두께)
- **사양** bus_V 48
- **설치** by: robot, bolts: 4

**원리** 두 배터리 패널의 48 V를 받아 관절 18곳과 시스템 40여 곳에 나눠 준다. 회로마다 전자 퓨즈가 있어 한 곳이 단락돼도 나머지는 산다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| PDU board (eFuse array, 48 V bus) | 1 | FR4 | 38 |
| PDU housing half | 2 | Al7075 | 30 |
| DC-DC converter 48/12, 48/5, 48/3.3 V | 3 | mixed | 12 |
| sealed power connector | 12 | mixed | 5 |
| internal screw M3, Ti | 8 | Ti64 | 0.7 |

### ENE-BUF · HOT-SWAP BUFFER · 교체 버퍼

- **수량** 1 (C) · **위치** pelvis (posterior) · **조립 단계** 4 SYSTEMS
- **부품** 개당 9개 · 합계 9개 · **질량** 개당 0.114 kg · 합계 0.114 kg
- **외형** 90 × 50 × 18 mm (길이 × 폭 × 두께)
- **사양** Wh 6 · hold_s 90
- **설치** by: robot, bolts: 2

**원리** 배터리 패널 하나를 빼는 90초 동안 슈트가 꺼지지 않게 버틴다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| hybrid capacitor cell | 6 | mixed | 14 |
| buffer BMS | 1 | FR4 | 6 |
| buffer housing half | 2 | Al7075 | 12 |

### ENE-HARN · HARNESS · 하네스

- **수량** 1 (C) · **위치** spine + limbs · **조립 단계** 4 SYSTEMS
- **부품** 개당 152개 · 합계 152개 · **질량** 개당 0.664 kg · 합계 0.664 kg
- **설치** by: robot, ops: route → clip → mate 48 connectors

**원리** 척추를 따라 내려가는 주 간선과 사지 분기. 커넥터는 모두 방수 밀봉, 피복은 내마모 불소수지.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| harness trunk segment (power + EtherCAT) | 24 | Cu/FEP | 18 |
| sealed connector | 48 | mixed | 3 |
| P-clamp | 60 | PA | 0.8 |
| spiral wrap | 20 | PA | 2 |

### ENE-BATT · BATTERY PANEL · 배터리 패널

- **수량** 2 (LR) · **위치** latissimus (back) L/R · **조립 단계** 5 PANELS
- **부품** 개당 47개 · 합계 94개 · **질량** 개당 0.949 kg · 합계 1.898 kg
- **외형** 328 × 205 × 9 mm (길이 × 폭 × 두께)
- **사양** kWh_each 0.42 · cells 14 · thickness_mm 9 · area_m2_each 0.07
- **설치** by: robot, ops: slide on guide pins → 4 quarter-turns, bolts: 0
- **독립적 움직임** panel releases and slides out (swap)

**원리** 배터리를 따로 매달지 않는다. 등의 넓은등근 판 두 장이 곧 배터리 팩이다. 바깥은 청사진의 티타늄 판, 안쪽 9 mm에 셀이 들어 있다. 쿼터턴 래치 4개를 풀면 판째로 빠지고, 버퍼가 버티는 동안 새 판을 꽂는다(유일한 미래 가정: 셀 에너지 밀도).

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| solid-state pouch cell (2036 assumption) | 14 | Li-metal SSB | 50 |
| structural cell carrier (Ti honeycomb) | 1 | Ti64 | 60 |
| graphite heat spreader | 4 | graphite | 6 |
| BMS board | 1 | FR4 | 14 |
| cell voltage tap flex | 1 | PI/Cu | 6 |
| busbar | 8 | Cu | 3 |
| thermistor | 6 | FR4 | 0.3 |
| pack fuse | 1 | mixed | 4 |
| solid-state contactor | 1 | mixed | 9 |
| blind-mate power / data connector | 1 | mixed | 12 |
| guide pin | 2 | Ti64 | 2 |
| quarter-turn latch | 4 | Ti64 | 3 |
| pack gasket | 1 | silicone | 6 |
| pressure relief vent | 1 | mixed | 2 |
| pack base housing | 1 | Ti64 | 70 |

## BRANCHIA — THERMAL · 아가미

막 아가미(증발 냉각기), 냉각수 회로, 팬, 열리는 루버

### BRA-GILL · MEMBRANE GILL · 막 아가미 (증발 냉각기)

- **수량** 1 (C) · **위치** flank L/R, behind the abdominal side slots · **조립 단계** 4 SYSTEMS
- **부품** 개당 35개 · 합계 35개 · **질량** 개당 0.410 kg · 합계 0.410 kg
- **외형** 160 × 70 × 14 mm (길이 × 폭 × 두께)
- **사양** cooling_W 150.00 · water_out_C_at_30C_40RH 23.40 · evaporant_L_per_h 0.22 · reservoir_L 0.60 · limit ambient wet bulb > 26 C -> chill line
- **설치** by: robot, ops: seat behind flank louvres → mate coolant + evaporant lines, bolts: 4

**원리** 땀이 증발하며 몸을 식히듯, 냉각수가 속이 빈 섬유 1,800가닥 안을 흐르고 그 바깥으로 루버의 공기가 지나가면 물의 일부가 막을 통해 증발하면서 나머지 물을 습구온도 가까이 식힌다. 30 °C, 습도 40 %에서도 냉각수가 23 °C까지 내려간다. 압축기가 없어 얇고(14 mm) 전력은 팬 몫뿐이다. 시간당 물 0.22 L를 쓴다. 덥고 습해서 습구온도가 26 °C를 넘는 날에는 이 원리가 한계에 닿고, 그때만 도크의 냉각 라인(탯줄)을 꽂는다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| hollow-fibre membrane module (PP, ~1,800 fibres, 0.25 m2) | 2 | PP | 95 |
| gill module housing | 2 | Ti64 | 40 |
| evaporant bladder 0.6 L | 1 | TPU | 35 |
| micro diaphragm dosing pump | 1 | mixed | 25 |
| evaporant solenoid valve | 2 | steel | 8 |
| evaporant level sensor | 1 | FR4 | 3 |
| air RH / temperature sensor (in, out) | 4 | FR4 | 1 |
| evaporant line | 6 | PU | 5 |
| fill port quick disconnect | 1 | PP | 8 |
| drain valve | 1 | PP | 5 |
| wicking pre-filter | 2 | PET | 4 |
| internal screw M2.5, Ti | 12 | Ti64 | 0.5 |

### BRA-LOOP · COOLANT LOOP · 냉각수 회로

- **수량** 1 (C) · **위치** back · **조립 단계** 4 SYSTEMS
- **부품** 개당 32개 · 합계 32개 · **질량** 개당 0.689 kg · 합계 0.689 kg
- **사양** flow_L_min 1.43 · pcm_kJ 84
- **설치** by: robot, ops: mate 4 QDs to undersuit

**원리** 냉각수가 분당 1.4 L씩 막 아가미와 언더슈트 튜브 사이를 돈다. 상변화 팩(24 °C에서 녹는 염수화물)은 순간 발열이 클 때 열을 잠시 저장한다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| maglev centrifugal pump | 1 | mixed | 45 |
| expansion bladder / reservoir | 1 | silicone | 20 |
| loop manifold | 1 | PEEK | 30 |
| flow sensor | 1 | mixed | 8 |
| coolant temperature sensor | 4 | FR4 | 1 |
| coolant line | 12 | PU | 6 |
| dry-break quick disconnect, suit half | 4 | Ti64/FKM | 11 |
| phase-change pack (salt hydrate, 24 C) | 6 | mixed | 70 |
| loop filter | 1 | PP | 6 |
| spine core cold plate | 1 | Al | 40 |

### BRA-FAN · LOUVRE FAN UNIT · 루버 팬 유닛

- **수량** 6 (x6) · **위치** flank L/R (2 each) + upper back L/R · **조립 단계** 4 SYSTEMS
- **부품** 개당 14개 · 합계 84개 · **질량** 개당 0.079 kg · 합계 0.474 kg
- **외형** 60 × 55 × 14 mm (길이 × 폭 × 두께)
- **사양** airflow_L_s_each 4.50
- **설치** by: robot, bolts: 2
- **독립적 움직임** louvre slats open downward in sequence

**원리** 도하가 그린 복부 옆 슬롯은 숨구멍이 됐다. 팬이 패널 안쪽 틈의 습한 공기를 빨아 막 아가미와 전자부를 지나 아래로 뿜고, 열이 쌓이면 작은 리니어 액추에이터가 링크 바 하나로 루버 슬랫 전체를 차례로 연다(패널의 독립적 움직임).

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| flat blower 50 mm | 1 | mixed | 38 |
| blower shroud | 1 | PA | 12 |
| finger-proof mesh | 1 | Ti64 | 6 |
| louvre micro linear actuator | 1 | mixed | 14 |
| louvre link bar | 1 | Ti64 | 4 |
| link pin | 4 | Ti64 | 0.5 |
| air temperature sensor | 1 | FR4 | 1 |
| internal screw M2.5, Ti | 4 | Ti64 | 0.5 |

## VITA — LIFE SUPPORT · 생명유지

헬멧 송풍 정화, 가스 감시, 수분 공급, 비상 해제

### VIT-AER · HELMET AIR (PAPR) · 헬멧 송풍 정화

- **수량** 1 (C) · **위치** helmet · **조립 단계** 6 PERSONA
- **부품** 개당 28개 · 합계 28개 · **질량** 개당 0.236 kg · 합계 0.236 kg
- **사양** flow_L_min 160 · inspired_CO2_pct 0.14 · power_W 3.00
- **설치** by: robot (with helmet)

**원리** 헬멧 안은 바깥보다 압력이 조금 높다. 송풍기가 측두 허브의 필터로 바깥 공기를 걸러 넣으니 먼지와 연기가 새어 들지 않고, 눈 슬릿 안쪽으로 공기 칼날이 흘러 김이 서리지 않는다. 날숨은 입 앞 컵에서 바로 배기 밸브로 나가 CO2가 쌓이지 않는다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| helmet blower | 2 | mixed | 28 |
| P3 + carbon filter cartridge (in temporal hub) | 2 | mixed | 42 |
| intake check valve | 2 | silicone | 2 |
| exhalation valve | 2 | silicone | 8 |
| oro-nasal cup | 1 | silicone | 35 |
| slit anti-fog air knife duct | 2 | PA | 6 |
| CO2 sensor (NDIR) | 1 | mixed | 4 |
| O2 sensor | 1 | mixed | 6 |
| temperature / humidity sensor | 1 | FR4 | 1 |
| air board | 1 | FR4 | 6 |
| air tube | 3 | silicone | 3 |
| internal screw M2, Ti | 10 | Ti64 | 0.3 |

### VIT-HYDRA · HYDRATION · 수분 공급

- **수량** 1 (C) · **위치** upper back · **조립 단계** 4 SYSTEMS
- **부품** 개당 5개 · 합계 5개 · **질량** 개당 0.085 kg · 합계 0.085 kg
- **사양** volume_L 0.50
- **설치** by: robot

**원리** 헬멧을 벗지 않고 마신다. 냉각복이 땀을 줄여도 1시간에 0.3~0.5 L는 잃는다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| bladder 0.5 L | 1 | TPU | 40 |
| drink tube | 1 | silicone | 10 |
| bite valve | 1 | silicone | 4 |
| bladder pocket | 1 | aramid | 25 |
| helmet pass-through QD | 1 | PP | 6 |

### VIT-SALUS · EMERGENCY + VITALS · 비상과 생체 감시

- **수량** 1 (C) · **위치** sternum + spine · **조립 단계** 4 SYSTEMS
- **부품** 개당 25개 · 합계 25개 · **질량** 개당 0.175 kg · 합계 0.175 kg
- **사양** core_temp_derate_C 38.50
- **설치** by: robot, bolts: 4

**원리** 흉골 손잡이 하나를 당기면 헬멧과 가슴 셸, 다리 커프가 기계식으로 풀린다(전원 불필요). 심전도, 산소포화도, 심부체온 추정, 호흡을 계속 보고 열 스트레스가 오면 출력을 먼저 줄인다. 넘어짐을 감지하면 위치를 자동 송신한다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| emergency release handle | 1 | Ti64 | 22 |
| release Bowden cable | 4 | steel/PTFE | 8 |
| latch release actuator | 6 | mixed | 12 |
| SOS beacon (GNSS + satellite) | 1 | mixed | 30 |
| vitals hub board | 1 | FR4 | 8 |
| haptic alert motor | 2 | mixed | 3 |
| internal screw M2.5, Ti | 10 | Ti64 | 0.5 |

## NERVUS — NERVOUS SYSTEM · 신경계

척추 연산부, 실시간 버스, 상태광

### NER-CORE · SPINE CORE · 척추 연산부

- **수량** 1 (C) · **위치** upper back, between scapulae · **조립 단계** 4 SYSTEMS
- **부품** 개당 23개 · 합계 23개 · **질량** 개당 0.178 kg · 합계 0.178 kg
- **외형** 120 × 90 × 20 mm (길이 × 폭 × 두께)
- **사양** control_Hz 1,000 · latency_ms 43.20 · power_W 15
- **설치** by: robot, bolts: 4

**원리** 근전도 800채널과 뇌파 32채널을 실시간으로 해독하고, 도하의 근육 표(최대 힘, 섬유 길이, 깃각)로 만든 근골격 모델로 관절마다 필요한 토크를 계산해 1 kHz로 근육(EHA)에 보낸다. 근육 신호가 오고 힘이 나기까지 50~100 ms, 슈트는 40 ms 안에 답한다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| compute module (edge AI SoC) | 1 | mixed | 25 |
| carrier board (lockstep safety MCU, EtherCAT master) | 1 | FR4 | 40 |
| NVMe storage | 1 | mixed | 6 |
| core housing half | 2 | Al7075 | 30 |
| sealed connector | 8 | mixed | 5 |
| internal screw M3, Ti | 10 | Ti64 | 0.7 |

### NER-NET · BUS HUBS · 버스 허브

- **수량** 1 (C) · **위치** spine · **조립 단계** 4 SYSTEMS
- **부품** 개당 12개 · 합계 12개 · **질량** 개당 0.052 kg · 합계 0.052 kg
- **설치** by: robot

**원리** 관절, 센서 노드, 시스템을 하나의 결정론적 버스(250 µs 주기)로 묶는다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| EtherCAT junction hub | 4 | FR4 | 12 |
| internal screw M2.5, Ti | 8 | Ti64 | 0.5 |

### NER-LUX · STATUS LIGHT PIPES · 상태광

- **수량** 1 (C) · **위치** panel seams · **조립 단계** 5 PANELS
- **부품** 개당 224개 · 합계 224개 · **질량** 개당 0.255 kg · 합계 0.255 kg
- **설치** by: robot (with panels)

**원리** 패널 이음선 홈 속의 광섬유처럼 빛나는 막대. 근섬유 방향으로 흐르며 부하가 클수록 빠르고 밝다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| light pipe segment (PC, frosted) | 124 | PC | 1.2 |
| side-emitting LED strip | 32 | FR4 | 2 |
| LED driver | 8 | FR4 | 3 |
| light pipe clip | 60 | PA | 0.3 |

## PERSONA — HELMET · 얼굴

헬멧, 눈 슬릿 카메라, 시야 디스플레이

### PER-HELMET · PERSONA HELMET · 페르소나 헬멧

- **수량** 1 (C) · **위치** head · **조립 단계** 6 PERSONA
- **부품** 개당 88개 · 합계 88개 · **질량** 개당 0.824 kg · 합계 0.824 kg
- **외형** 250 × 175 × 270 mm (길이 × 폭 × 두께)
- **사양** slit_height_mm 7 · fov_deg_display 110
- **설치** by: robot, ops: occipital shell → temporal hubs → face plate lowers → lock
- **독립적 움직임** temporal hub rings rotate to open the intakes / face plate lowers and locks

**원리** 눈 슬릿은 얇다(높이 7 mm). 대신 슬릿 뒤 두 카메라와 깊이 센서가 넓은 시야를 찍어 눈앞 디스플레이에 보여 준다. 슬릿으로 직접 보는 시야는 전원이 나가도 남는 예비 시야다. 귀 자리의 측두 허브는 송풍기 필터 캡이고, 돌아가며 흡기구를 연다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| occipital shell, SPIF | 1 | Ti64 | 180 |
| crown shell | 1 | Ti64 | 120 |
| face plate carrier | 1 | CFRP | 60 |
| face plate hinge | 2 | Ti64 | 8 |
| hinge pin | 2 | Ti64 | 2 |
| face plate latch | 2 | Ti64 | 6 |
| latch actuator | 1 | mixed | 14 |
| eye slit window, laminated PC, smoked | 2 | PC | 6 |
| global-shutter camera (behind slit) | 2 | mixed | 4 |
| ToF depth sensor | 1 | mixed | 3 |
| micro-OLED display | 2 | mixed | 3 |
| pancake optic | 2 | PMMA | 12 |
| temporal hub ring | 2 | Ti64 | 22 |
| temporal hub cap (TiN) | 2 | Ti64 | 14 |
| hub servo | 2 | mixed | 6 |
| hub bearing | 2 | steel | 4 |
| helmet liner | 1 | EPP | 110 |
| comfort pad | 6 | foam | 6 |
| EEG pressure pad (spring) | 8 | mixed | 3 |
| neck seal | 1 | silicone | 45 |
| chin cup | 1 | silicone | 20 |
| helmet board | 1 | FR4 | 12 |
| IMU node (head) | 1 | FR4 | 4 |
| helmet cable | 2 | Cu/FEP | 5 |
| internal screw M2, Ti | 40 | Ti64 | 0.3 |

## FUNCTIO — FUNCTION · 기능

툴 베이, 보조 손, 교체 포트

### FUN-TOOLBAY · TOOL BAY · 툴 베이

- **수량** 1 (R) · **위치** right forearm, dorsal · **조립 단계** 5 PANELS
- **부품** 개당 30개 · 합계 30개 · **질량** 개당 0.192 kg · 합계 0.192 kg
- **외형** 180 × 55 × 28 mm (길이 × 폭 × 두께)
- **사양** stroke_mm 6 · open_deg 38
- **설치** by: robot (with forearm panels)
- **독립적 움직임** forearm panel slides 6 mm then pivots 38 deg

**원리** 전완 판이 원위 방향으로 6 mm 미끄러진 뒤 피벗해 열린다. 작업등, 관절형 점검 카메라, 비트 드라이버.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| rail carriage | 1 | Ti64 | 18 |
| slide rail | 2 | Ti64 | 10 |
| pivot hinge | 1 | Ti64 | 8 |
| panel micro linear actuator | 1 | mixed | 16 |
| cartridge tray | 1 | PEEK | 20 |
| work light, high-CRI LED 2 W | 1 | mixed | 12 |
| articulating borescope camera 5.5 mm | 1 | mixed | 25 |
| 1/4 in bit driver (micro gearmotor) | 1 | mixed | 45 |
| driver bit | 6 | steel | 2 |
| tray latch | 2 | Ti64 | 3 |
| tool bay board | 1 | FR4 | 6 |
| internal screw M2, Ti | 12 | Ti64 | 0.3 |

### FUN-HAND · ASSIST HAND · 보조 손

- **수량** 1 (R) · **위치** right forearm, ventral · **조립 단계** 5 PANELS
- **부품** 개당 51개 · 합계 51개 · **질량** 개당 0.251 kg · 합계 0.251 kg
- **외형** 160 × 50 × 18 mm (길이 × 폭 × 두께)
- **사양** grip_N 40
- **설치** by: robot (with forearm panels)
- **독립적 움직임** unfolds from under the forearm

**원리** 전완 아래에 접혀 있다가 펼쳐지는 두 손가락 + 마주 보는 엄지 그리퍼. 정밀 모드는 M2 나사를, 와이드 모드는 파이프를 잡는다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| palm base | 1 | Ti64 | 40 |
| finger link | 6 | Ti64 | 8 |
| thumb link | 3 | Ti64 | 8 |
| joint pin | 12 | Ti64 | 1 |
| finger tendon cable | 3 | Dyneema | 1 |
| micro BLDC + reducer | 2 | mixed | 35 |
| silicone pad | 3 | silicone | 3 |
| telescoping rail | 2 | Ti64 | 10 |
| pad rotation mechanism | 1 | Ti64 | 12 |
| pad force sensor | 3 | FR4 | 1 |
| hand board | 1 | FR4 | 6 |
| internal screw M2, Ti | 14 | Ti64 | 0.3 |

### FUN-PORT · SWAP PORT + SENSOR CARTRIDGE · 교체 포트

- **수량** 1 (L) · **위치** left forearm, dorsal · **조립 단계** 5 PANELS
- **부품** 개당 15개 · 합계 15개 · **질량** 개당 0.088 kg · 합계 0.088 kg
- **설치** by: robot (with forearm panels)

**원리** 공통 규격 포트. 지금은 열화상 카메라와 가스 센서 카트리지가 꽂혀 있다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| MYO-PORT socket (8 pogo pins + rails) | 1 | Ti64/mixed | 25 |
| quarter-turn latch | 2 | Ti64 | 3 |
| cartridge housing | 1 | Ti64 | 30 |
| thermal camera core | 1 | mixed | 8 |
| 4-gas sensor | 1 | mixed | 12 |
| cartridge board | 1 | FR4 | 5 |
| internal screw M2, Ti | 8 | Ti64 | 0.3 |

## MYO — PANELS · 근육 패널

도하의 청사진 판 477장과 패널 캐리어

### MYO-PANELS · BLUEPRINT PANELS · 청사진 판

- **수량** 1 (C) · **위치** whole body · **조립 단계** 5 PANELS
- **부품** 개당 561개 · 합계 561개 · **질량** 개당 11.347 kg · 합계 11.347 kg
- **사양** panels 477 · thickness_mm 0.60 · area_m2 3.34 · mount_points 1,352
- **설치** by: robot, ops: place → nutrunner, picks: 168
- **독립적 움직임** deltoid caps slide in layers / abdominal bands telescope / knee cop slides over the knee / neck lamellae fan

**원리** 도하가 손으로 그린 판 그대로. 0.6 mm 티타늄 판을 점진 성형(SPIF)으로 곡면을 만들고 가장자리를 말아 강성을 낸다. 판은 몸에 닿지 않고 탄소섬유 캐리어 위에 방진 그로밋으로 떠 있어서, 관절이 움직일 때 겹치고 미끄러진다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| panel, torso + limbs front (blueprint front view) (Ti-6Al-4V 0.6 mm, SPIF) | 208 | Ti64 | 22.12 |
| panel, back (blueprint rear inset) (Ti-6Al-4V 0.6 mm, SPIF) | 102 | Ti64 | 27.65 |
| panel, limb backs (Ti-6Al-4V 0.6 mm, SPIF) | 44 | Ti64 | 33.18 |
| panel, helmet (PERSONA + side detail, both sides) (Ti-6Al-4V 0.6 mm, SPIF) | 40 | Ti64 | 9.95 |
| panel, hand plates (Ti-6Al-4V 0.6 mm, SPIF) | 38 | Ti64 | 4.87 |
| panel, louvre slats + neck lamellae (Ti-6Al-4V 0.6 mm, SPIF) | 45 | Ti64 | 6.64 |
| panel carrier (CFRP sub-frame) | 36 | CFRP | 40 |
| sliding panel guide (PEEK) | 48 | PEEK | 3 |

## FIX — FASTENERS · 체결

설치 볼트, 패널 체결구, 방진 그로밋

### FIX-INSTALL · INSTALLATION HARDWARE · 설치 체결구

- **수량** 1 (C) · **위치** whole body · **조립 단계** 5 PANELS
- **부품** 개당 2826개 · 합계 2826개 · **질량** 개당 0.966 kg · 합계 0.966 kg
- **사양** panel_screw_torque_Nm 0.45 · module_bolt_torque_Nm 2.90
- **설치** by: robot (nutrunner)

**원리** 나사 하나하나가 토크 사양을 가진다(M2.5 티타늄 0.45 N·m). 로봇 끝의 너트러너가 클러치가 끊기는 순간까지 조인다.

| 부품 | 수량 | 재료 | g/개 |
|---|---:|---|---:|
| panel screw, Ti Torx M2.5 countersunk | 1352 | Ti64 | 0.35 |
| panel isolator grommet | 1352 | EPDM | 0.15 |
| quarter-turn stud + receptacle | 16 | Ti64 | 2.2 |
| module bolt, Ti M4/M5 | 106 | Ti64 | 2.4 |
