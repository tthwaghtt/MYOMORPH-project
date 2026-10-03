# MYOMORPH-MK. 1 — 카피 덱 v2.0

> 규칙
> - **EN 라벨**: 대문자, 엔지니어링 문법.
> - **KO 본문**: 한 챕터에 한두 문장, 숫자는 단위와 함께.
> - 이름 'MYOMORPH-MK. 1'은 10 NERVUS 전에는 화면에 쓰지 않는다.
> - 모든 숫자는 `engineering/engineering.json`, `bom.json`, `undersuit.json`, `docs/research/corpus/*.json`에서 빌드 시 주입한다(손으로 쓰지 않는다).

| # | EN 라벨 | KO 본문 | 데이터 출처 |
|---|---|---|---|
| P | `HOLD TO ENGAGE` · `ENTER SILENT` | 길게 눌러 기동 · 무음으로 입장 | |
| P | `PARTS STAGED 0000 / 5,819` | | bom.json `total_parts` |
| 00 | `CELL 01 · BUILD 0001 · OPERATOR: DOHA` | (카피 없음) | |
| 01 | `SCHEMA · 477 PANELS` | 모든 판은 도하가 손으로 그린 한 장의 청사진에서 시작한다. 정면에서 보이는 모습은 도하의 선 그대로다. | blueprint/*.json, engineering.json `suit.panels` |
| 01 | `FIT: ARM AXIS · PELVIC V-PLATE · KNEE +5 mm` | 도하의 비율은 지키고, 몸에 맞게 두 곳을 고쳤다. 무릎 바깥 5 mm는 무릎 링크가 들어갈 자리다. | suit_stats.json, packaging.json |
| 01 | `DESIGNED BY DOHA` | 원본 드로잉 | |
| 02 | `CORPUS` | 이 슈트는 한 사람의 몸에서 잰다. 93개 치수, 64개 근육. | corpus/*.json |
| 02 | `STATURE 178.0 · SPAN 182.0 · MASS 65.0 kg · WAIST 71.0 · BIDELTOID 47.0 · CHEST 93.1` | | anthro.json, wearer_fit.json |
| 03 | `NEURAL WEAR · EMG 784 ch · EEG 32 ch · COOLING 77.5 m` | 뇌가 마음먹는 순간을 뇌파로, 척수가 근육에 내리는 명령을 근전도로 읽는다. 슈트는 당신이 움직이기 43 ms 전에 안다. | undersuit.json, engineering.json `neural` |
| 03 | `VL · VASTUS LATERALIS · SENIAM 2/3 ASIS–PATELLA` 외 24곳 | 가쪽넓은근 외. 센서 위치는 근육마다 국제 표준 규칙으로 도하의 몸에서 계산했다. | undersuit.json `emg_sites` |
| 03 | `LINK: COOLANT + DATA` | 천장의 탯줄이 허리에 꽂힌다. 냉각수가 흐르기 시작한다. | |
| 04 | `GROUND · 4 LOAD CELLS · 16 ZONES` | 슈트 무게 36.6 kg은 사람이 아니라 이 발판이 받는다. | bom.json `PES-BOOT` |
| 05 | `SKELETON · 599 PARTS` | 무게는 사람의 뼈가 아니라 슈트의 뼈를 따라 땅으로 내려간다. 사람과 닿는 곳은 커프 10개뿐이다. | bom.json `OS` |
| 05 | `KNEE · CROSSED FOUR-BAR · ICR TRACKING` | 무릎은 경첩이 아니다. 굽힐수록 회전중심이 뒤로 간다, 사람 무릎처럼. | |
| 06 | `MUSCLE · 6 EHA · 21 MPa · KNEE 64 N·m` | 중앙 펌프도, 긴 고압 배관도 없다. 근육마다 모터와 펌프와 실린더가 한 몸이다. | engineering.json `muscles_eha` |
| 06 | `EHA · 75 PARTS` (카드) | 모터가 정방향이면 늘어나고, 역방향이면 줄어든다. 고장 나면 바이패스가 열려 사람을 가두지 않는다. | bom.json `MUS-EHA-KNEE` |
| 07 | `SYSTEMS · 403 PARTS` | 배터리, 냉각, 생명유지, 신경계. 모두 몸 바깥에, 판 아래에. | bom.json stage 4 |
| 07 | `MEMBRANE GILL · 23.4 °C @ 30 °C / 40 %` (카드) | 땀처럼 증발해 식힌다. 압축기가 없다. | engineering.json `thermal.gill` |
| 07 | `SPINE CORE · 1 kHz · 43 ms` (카드) | 도하의 근육 표로 만든 근골격 모델이 관절마다 필요한 힘을 계산한다. | engineering.json `neural` |
| 08 | `MYOMORPH · 477 PANELS` · `PARTS 0000/5,819 · SCREWS 0000/1,458 · MASS 00.0/36.6 kg` | 477장. 하나도 빠짐없이 도하의 청사진에 있던 판이다. 등판 두 장은 배터리다. | bom.json, engineering.json |
| 09 | `PERSONA` | 눈은 얇게. 넓은 시야는 슬릿 뒤의 카메라 두 대가 본다. 슬릿은 전원이 꺼져도 남는 예비 시야다. | bom.json `PER-HELMET` |
| 10 | `NERVUS` · `MYOMORPH-MK. 1 · SN 0001` | 당신의 근육이 신호를 보내면, 기계의 근육이 답한다. | |
| 11 | `UNTETHERED · 0.84 kWh · 3.7 h` | 이제 케이블 없이 선다. 충전할 때와 덥고 습한 날만 다시 연결한다. | engineering.json `battery`, `tether` |
| 12 | `MOTUS · KNEE 0–125° · ELBOW 0–135°` | 판은 몸에 닿지 않는다. 그래서 겹치고, 미끄러지고, 비켜 준다. | engineering.json `rom_deg` |
| 13 | `FUNCTIO · TOOL BAY · ASSIST HAND · BATTERY SWAP · BRANCHIA` | 도하가 그린 옆구리의 슬롯은 처음부터 숨구멍이었다. | |
| 14 | `KNOLL · 5,819 PARTS · 41 MODULES · 13 SYSTEMS` | 이 페이지의 모든 숫자는 하나의 계산서와 하나의 부품표에서 나온다. | bom.json |
| 15 | `AWAKENING` · `INSPECT` | (카피 없음. 슈트가 고개를 든다) | |
| 15 | 표제란 · 출처 목록 | STORYBOARD §6 | |

**톤**: 설명하지 않고 보여 준다. 형용사보다 숫자를 쓴다. 한 문장이 길면 둘로 나눈다. 감탄사는 쓰지 않는다. 원리를 말할 때는 비유를 하나만 쓴다(땀, 힘줄, 냉장고).
