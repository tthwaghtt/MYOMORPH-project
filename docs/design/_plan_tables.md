<!-- BOM -->
| 시스템 | 이름 | 부품 | 질량 kg | 대표 모듈 |
|---|---|---:|---:|---|
| **FASCIA** | 신경 언더슈트 | 208 | 1.92 | NEURAL UNDERSUIT, EEG BALACLAVA, INNER GLOVE |
| **PES** | 발 | 102 | 2.28 | BOOT |
| **OS** | 골격 | 599 | 6.53 | LEG FRAME, PELVIS + HIP JOINTS, SPINE + HARNESS, ARM FRAME |
| **MUSCULUS** | 근육 | 450 | 4.47 | HIP MUSCLE (EHA), KNEE MUSCLE (EHA), ANKLE MUSCLE (EHA) |
| **TENDO** | 힘줄 | 140 | 0.83 | ELBOW TENDON DRIVE, SHOULDER SPRING CASSETTE |
| **ENERGIA** | 에너지 | 281 | 2.88 | POWER DISTRIBUTION, HOT-SWAP BUFFER, HARNESS, BATTERY PANEL |
| **BRANCHIA** | 아가미 | 151 | 1.57 | MEMBRANE GILL, COOLANT LOOP, LOUVRE FAN UNIT |
| **VITA** | 생명유지 | 58 | 0.50 | HELMET AIR (PAPR), HYDRATION, EMERGENCY + VITALS |
| **NERVUS** | 신경계 | 259 | 0.48 | SPINE CORE, BUS HUBS, STATUS LIGHT PIPES |
| **PERSONA** | 얼굴 | 88 | 0.82 | PERSONA HELMET |
| **FUNCTIO** | 기능 | 96 | 0.53 | TOOL BAY, ASSIST HAND, SWAP PORT + SENSOR CARTRIDGE |
| **MYO** | 외부 패널 | 561 | 11.35 | SUIT PANELS |
| **FIX** | 체결 | 2,826 | 0.97 | INSTALLATION HARDWARE |
| | **합계** | **5,819** | **35.13** + 유체 1.50 = **36.6 kg** | |

<!-- EHA -->
| 관절 | 위치 | 피크 토크 (자중 + 보조) | 설계 토크 | 모멘트암 | 내경 / 로드 | 스트로크 | 추력 | 모터 | 외형 L×W×T |
|---|---|---|---:|---:|---|---:|---:|---:|---|
| hip | 둔부 뒤(골반 아치 → 대퇴 지주) | 64.2 N·m (44.7 + 19.5) | 80.2 N·m | 40 mm | 12 / 6 mm | 72.5 mm | 2.01 kN | 159 W | 215 × 44 × 18 mm |
| knee | 대퇴 앞(→ 4절 링크) | 63.8 N·m (42.6 + 21.1) | 79.8 N·m | 32 mm | 14 / 7 mm | 56.8 mm | 2.49 kN | 158 W | 184 × 44 × 20 mm |
| ankle | 종아리 뒤(→ 아킬레스 링크 → 뒤꿈치 레버) | 76.2 N·m (51.8 + 24.4) | 95.2 N·m | 45 mm | 12 / 6 mm | 41.6 mm | 2.12 kN | 283 W | 153 × 44 × 18 mm |

<!-- SITES -->
| 부위 | 근육 | 종류 | 부착 규칙 | 근육 표 (최대 힘 / 섬유 길이 / 깃각) |
|---|---|---|---|---|
| VL | 가쪽넓은근 · vastus lateralis | HD 32 ch | SENIAM: 2/3 on the line from the anterior superior iliac spine to the lateral side of the patella | 4990 N / 9.9 cm / 14.5° |
| VM | 안쪽넓은근 · vastus medialis | HD 32 ch | SENIAM: 80 % on the line between the ASIS and the joint space in front of the medial ligament | 2663 N / 9.7 cm / 24.2° |
| RF | 넙다리곧은근 · rectus femoris | HD 32 ch | SENIAM: 50 % on the line from the ASIS to the superior part of the patella | 2124 N / 7.6 cm / 12.4° |
| BF | 넙다리두갈래근 긴갈래 · biceps femoris (long) | HD 32 ch | SENIAM: 50 % on the line between the ischial tuberosity and the lateral epicondyle of the tibia | 1273 N / 9.8 cm / 10.1° |
| ST | 반힘줄근 · semitendinosus | HD 32 ch | SENIAM: 50 % on the line between the ischial tuberosity and the medial epicondyle of the tibia | 573 N / 19.3 cm / 13.8° |
| GMAX | 큰볼기근 · gluteus maximus | HD 32 ch | SENIAM: 50 % on the line between the sacral vertebrae and the greater trochanter | 3235 N / 15.7 cm / 21.1° |
| GM | 장딴지근 안쪽갈래 · gastrocnemius (medial) | HD 32 ch | SENIAM: on the most prominent bulge of the medial head | 3019 N / 5.1 cm / 9.5° |
| GL | 장딴지근 가쪽갈래 · gastrocnemius (lateral) | HD 32 ch | SENIAM: 1/3 of the line between the head of the fibula and the heel | 1527 N / 5.9 cm / 12.0° |
| SOL | 가자미근 · soleus | HD 32 ch | SENIAM: 2/3 of the line between the medial femoral condyle and the medial malleolus | 6004 N / 4.4 cm / 21.9° |
| TA | 앞정강근 · tibialis anterior | HD 32 ch | SENIAM: 1/3 on the line between the tip of the fibula and the tip of the medial malleolus | 1190 N / 6.8 cm / 11.2° |
| BB | 위팔두갈래근 · biceps brachii | HD 32 ch | SENIAM: on the line between the medial acromion and the fossa cubiti at 1/3 from the fossa cubiti | 775 N / 12.2 cm / 0.0° |
| TB | 위팔세갈래근 · triceps brachii | HD 32 ch | SENIAM: 50 % on the line between the posterior crista of the acromion and the olecranon (grid spans both heads) | 2032 N / 12.2 cm / 10.2° |
| DA | 어깨세모근 앞부분 · deltoideus (pars clavicularis) | 양극 | SENIAM: one finger width distal and anterior to the acromion | 1122 N / 9.8 cm / 22.0° |
| DM | 어깨세모근 중간부분 · deltoideus (pars acromialis) | 양극 | SENIAM: on the line acromion - lateral epicondyle, at the greatest bulge | 1016 N / 10.8 cm / 15.0° |
| TRAP | 등세모근 위부분 · trapezius pars descendens | 양극 | SENIAM: 50 % on the line from the acromion to the spine of C7 | (몸통 근육: 공개 모델 없음) |
| PM | 큰가슴근 · pectoralis major | 양극 | literature: sternal head, between the nipple and the anterior axillary fold | 1474 N / 14.0 cm / 23.1° |
| LD | 넓은등근 · latissimus dorsi | 양극 | literature: ~4 cm below the inferior angle of the scapula, midway to the lateral border | 734 N / 25.3 cm / 21.7° |
| ES | 척주세움근(가장긴근) · erector spinae | 양극 | SENIAM: two finger widths lateral to the spinous process of L1 | (몸통 근육: 공개 모델 없음) |
| FCR | 노쪽손목굽힘근 · flexor carpi radialis | 양극 | literature: proximal third of the line medial epicondyle - radial styloid | 376 N / 6.3 cm / 3.0° |
| ECR | 노쪽손목폄근 · extensor carpi radialis | 양극 | literature: proximal fifth of the line lateral epicondyle - radial styloid | 543 N / 7.3 cm / 3.2° |

<!-- STAGES -->
| 단계 | 이름 | 로봇이 하는 일 | 부품 |
|---|---|---|---:|
| 0 | WEAR | 도하가 언더슈트, 바라클라바, 이너 장갑을 입고 셀에 들어온다(사람이 입는다) | 208 |
| 1 | GROUND | 부츠에 발을 넣고 로봇이 바인딩을 조인다 | 102 |
| 2 | SKELETON | 다리 프레임 → 골반 → 척추와 하네스 → 팔 프레임, 커프 조임 | 599 |
| 3 | MUSCLE | EHA 6개 핀 결합, 팔꿈치 힘줄 구동기, 어깨 스프링, 힘줄 장력 | 590 |
| 4 | SYSTEMS | 배전, 버퍼, 막 아가미, 냉각수 회로, 팬, 연산부, 생명유지, 언더슈트 연결, 천장 탯줄 연결 | 403 |
| 5 | PANELS | 레퍼런스 판 전체(잠정 477장, 배터리 패널, 루버, 툴 베이 패널 포함) | 3,801 |
| 6 | PERSONA | 헬멧 셸 → 안면판 → 락(순서는 도하의 헬멧 디자인에 맞춘다) | 116 |
| 7 | BRING-UP | 신경 보정, 자가 진단, 탯줄 분리, 배터리 단독 구동 | 0 |