# MYOMORPH-MK. 1 — 카피 덱 v1.0

> 규칙: **EN 라벨**(대문자, 엔지니어링 문법) + **KO 본문**(한 챕터 한두 문장, 숫자는 단위와 함께). 이름 'MYOMORPH-MK. 1'은 08 NERVUS 전에는 화면에 쓰지 않는다.

| # | EN 라벨 | KO 본문 | 데이터 출처 |
|---|---|---|---|
| P | `HOLD TO ENGAGE` · `ENTER SILENT` | 길게 눌러 기동 · 무음으로 입장 | |
| P | `PARTS STAGED 0000 / 4,200` | | engineering.json |
| 00 | `SHEET 01 / 13 · SCALE 1:1` | (카피 없음) | |
| 01 | `SCHEMA` | 모든 판은 도하가 손으로 그린 한 장의 청사진에서 시작한다. 선 하나, 판 하나를 그대로 읽어 3D로 옮겼다. | blueprint/*.json |
| 01 | `211 PANELS · FRONT VIEW` · `FIT CORRECTION: ARM +7.7 / CROTCH +8.2` | 도하의 비율은 지키고, 몸에 맞게 두 곳만 고쳤다. | suit_stats.json |
| 01 | `DESIGNED BY DOHA` | 원본 드로잉 | |
| 02 | `CORPUS` | 착용자: 스무 살 초반, 키 178, 윙스팬 182, 몸무게 65, 체지방 10 %. 미국 CDC 체성분 데이터와 미 육군 인체 측정 6천 명의 데이터로 몸 전체 93개 치수를 계산했다. 이 슈트는 그 숫자에 맞춰 만든다. | corpus/*.json |
| 02 | `STATURE 178.0 · SPAN 182.0 · MASS 65.0 kg · WAIST 71.0 · BIDELTOID 47.0 · CHEST 93.1` | | anthro.json, wearer_fit.json |
| 02 | `VASTUS LATERALIS 827 cm³` 외 | 가쪽넓은근 외 (라틴어 + 한글 병기) | muscles.json |
| 03 | `FASCIA` | 피부와 금속 사이, 숨 쉬는 층. | |
| 04 | `OS` | 무게는 사람의 뼈가 아니라 슈트의 뼈로 땅에 내려간다. | engineering.json |
| 05 | `TENDO · MUSCULUS` | 기계의 근육은 사람의 근육이 있던 자리에 있다. 같은 자리에서, 같은 일을 한다. | |
| 06 | `COR · VASA · 21 MPa` | 21 MPa의 심장. 배터리 에너지 밀도는 2036년 기준 가정치다(유일한 미래 가정). | engineering.json |
| 07 | `MYOMORPH` · `PANELS 000/480 · FASTENERS 0000/3,000 · MASS 00.0 kg` | 480장의 판. 하나도 빠짐없이 도하의 청사진에 있던 판이다. | engineering.json |
| 07 | `PERSONA` | 얼굴은 근육의 지도다. 눈둘레근은 바이저가, 관자근은 측두 허브가 되었다. | |
| 08 | `NERVUS` · `MYOMORPH-MK. 1 · SN 0001` | 당신의 근육이 신호를 보내면, 기계의 근육이 답한다. | |
| 09 | `MOTUS` · `KNEE 0–125° · ELBOW 0–135°` | 사람이 할 수 있는 동작의 대부분을 막지 않는다. | engineering.json |
| 10 | `FUNCTIO` · `TOOL BAY · ASSIST HAND · SWAP · BRANCHIA` | 도하가 그린 옆구리의 슬롯은 처음부터 숨구멍이었다. | |
| 11 | `DOSSIER` | 이 페이지의 모든 숫자는 하나의 계산서에서 나온다. | engineering.json |
| 12 | `AWAKENING` · `INSPECT` | (카피 없음. 슈트가 고개를 든다) | |
| 12 | 표제란 · 출처 목록 | STORYBOARD §5 | |

**톤**: 설명하지 않고 보여 준다. 형용사보다 숫자. 한 문장이 길면 둘로 나눈다. 감탄사 금지.
