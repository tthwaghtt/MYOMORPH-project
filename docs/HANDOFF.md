# MYOMORPH-project — 새 세션 인계 문서

> **작성** Claude · 2026-10-03 · 계획서 v3.0 기준
> **목적**: 새 세션이 이 문서 하나만 읽고 바로 이어서 일할 수 있게 한다. 계획 전체는 [`PLAN.md`](PLAN.md), 레퍼런스 처리 순서는 [`INTAKE.md`](INTAKE.md).
> **새 세션의 Claude에게**: 이 문서를 처음부터 끝까지 읽고, §4 규칙을 지킨다. 그다음 [`PLAN.md`](PLAN.md) §0~§2, §5, §16과 [`INTAKE.md`](INTAKE.md)를 읽는다.

---

## 0. 30초 요약

| 항목 | 내용 |
|---|---|
| 프로젝트 | MYOMORPH-MK. 1(실제로 작동 가능한 근골격 티타늄 슈트)이 한 사람의 몸 위에 조립되는 과정을 보여 주는 스크롤형 인터랙티브 3D 웹 경험. Blender(bpy)로 만들고 three.js로 보여 준다 |
| 의뢰인 | 도하. 디자인 원천이자 착용자(178 cm, 65 kg). 보고는 **한국어** |
| 지금 단계 | P0 완료 · P1 R1·R2 완료 · **P1 R3: 레퍼런스 기반 전환 준비 완료** |
| 기다리는 것 | **도하의 새 레퍼런스**(팔 안쪽, 다리 안쪽까지 모든 면이 들어간 상세 도면). 2026-10-03 기준 1~2일 안에 도착 예정 |
| 다음 할 일 | 레퍼런스가 오면 [`INTAKE.md`](INTAKE.md) 1단계(받기와 검토)부터. 1단계를 마치면 질문 목록과 계획을 도하에게 보고하고 동의를 받는다 |
| 브랜치 | `claude/dazzling-newton-19zxf5` (GitHub에 있는 유일한 브랜치. 2026-10-03에 기록을 정리하고 강제 푸시했다) |

**가장 중요한 결정 (2026-10-03, 도하)**
1. 마네킹 기반 슈트 디자인은 폐기했다. 슈트 외형은 **도하의 레퍼런스 그대로** 만든다. 모든 선을 분석해 판 하나하나를 독립된 3D 판으로 만든다.
2. "근육처럼 보여야 한다" 같은 해석은 더하지 않는다. 비율만 도하 몸에 맞게 조금 조정하고, 조정한 곳은 보고한다.
3. **헬멧과 얼굴(PERSONA)도 도하가 디자인한다.**
4. 유지: 의도와 분위기, 몸 치수, 동작 원리, 배터리, 레이싱 슈트형 신경 언더슈트, 공학, 슈트 기능, 색, 웹 페이지 디자인, 도구(Blender, three.js).
5. 스토리보드 아티팩트는 도하가 마음에 들어 한다. 아이디어가 바뀔 수 있으니 한 번에 완성하지 않고 조금씩 고친다.

---

## 1. 새 세션 여는 법 (도하용)

### 1.1 레퍼런스 올리기
1. [`reference/GUIDE.md`](reference/GUIDE.md)대로 그린다. 밑그림은 [`reference/template/`](reference/template/)에 있다.
2. 파일 이름은 `MK1_ref_v1_front.svg`, `MK1_ref_v1_side.svg`처럼 붙인다.
3. 올리는 방법은 둘 중 하나다.
   - **GitHub 웹**(파일이 많거나 SVG일 때 권장): 저장소 `tthwaghtt/MYOMORPH-project` → 브랜치 `claude/dazzling-newton-19zxf5` → `docs/reference/incoming/` 폴더 → **Add file → Upload files** → "Commit directly to the `claude/dazzling-newton-19zxf5` branch"로 커밋.
   - **대화창 첨부**(PNG, WebP 몇 장일 때): 새 세션의 첫 메시지에 붙인다. Claude가 `docs/reference/incoming/`에 저장하고 커밋한다.

### 1.2 첫 메시지 (복사해서 쓰기)

```
MYOMORPH-project를 이어서 진행해줘.
1. docs/HANDOFF.md를 먼저 끝까지 읽고 그 규칙대로 해.
2. claude/dazzling-newton-19zxf5 브랜치의 최신 내용에서 시작해. 세션 브랜치가 다르면 HANDOFF §2대로 가져와.
3. 새 레퍼런스를 docs/reference/incoming/에 올렸어(또는 이 메시지에 첨부했어).
4. docs/INTAKE.md 1단계(받기와 검토)만 먼저 하고, 빠진 뷰와 질문 목록, 다음 계획을 보고해줘. 내가 동의하면 다음 단계로 가.
```

레퍼런스 없이 다른 일(예: 스토리보드 수정)을 시킬 때는 3, 4번을 그 일로 바꾼다.

---

## 2. 브랜치와 git

- **작업 브랜치**: `claude/dazzling-newton-19zxf5`. GitHub에는 이 브랜치 하나뿐이고, 기본 브랜치도 이것이다.
- **새 세션이 다른 브랜치를 배정받으면**: 배정받은 브랜치에서 일하되, 내용은 이 브랜치에서 가져온다.
  ```bash
  git fetch origin claude/dazzling-newton-19zxf5
  # 배정 브랜치에 고유 커밋이 없으면(새 브랜치):
  git checkout -B <배정-브랜치> origin/claude/dazzling-newton-19zxf5
  # 배정 브랜치에 이미 커밋이 있으면:
  git checkout <배정-브랜치> && git merge origin/claude/dazzling-newton-19zxf5
  ```
- **푸시**: `git push -u origin <브랜치>`. 네트워크 오류일 때만 2, 4, 8, 16초 간격으로 4번까지 다시 시도한다.
- **커밋 서명**: 커밋 메시지 끝에는 세션 시스템 안내가 주는 서명 줄(trailer)을 그대로 붙인다.
- **PR은 도하가 요청할 때만** 만든다.
- **기록 정리 (2026-10-03)**: 폐기한 슈트 디자인 파일을 git 기록 전체에서 지우고 강제 푸시했다(§8.1 목록). 예전 커밋 해시는 GitHub가 정리할 때까지 해시로만 남아 있을 수 있다. 예전에 받은 복제본이 있다면 `git fetch origin && git reset --hard origin/claude/dazzling-newton-19zxf5`로 맞춘다.
- **턴 끝 검사**: 이 환경은 커밋하지 않은 변경이 있으면 턴 끝에 커밋과 푸시를 요구한다. 작업을 멈출 때는 WIP 커밋을 남긴다.

---

## 3. 환경 다시 만들기

컨테이너는 휘발성이다. 새 세션에서는 아래를 다시 설치한다(이전 세션의 가상환경은 사라진다).

| 항목 | 상태 (2026-10-03 확인) |
|---|---|
| Python | `/usr/bin/python3.13` 있음(3.10~3.13 설치됨). `uv` 0.8.x 있음 |
| Blender | **PyPI `bpy` 5.2.1**(Python 3.13 전용 휠). `download.blender.org`는 네트워크 정책으로 403 → 우회하지 않는다 |
| GPU | 없음. CPU 4코어, RAM 15 GB. Cycles CPU + OIDN |
| Node | npm 레지스트리 접근 가능(three, vite, gltf-transform) |
| 브라우저 | Chromium + Playwright 설치됨(`playwright install` 금지) |
| 기타 | ffmpeg 있음 |

**bpy 가상환경**

```bash
SP=<scratchpad 경로>            # 세션마다 다르다. 시스템 안내의 scratchpad 디렉터리를 쓴다
uv venv --python 3.13 $SP/bpy52
uv pip install --python $SP/bpy52/bin/python bpy==5.2.1 numpy scipy pillow matplotlib contourpy pandas statsmodels
# 선택(색 연구 스크립트): colour-science opencolorio
$SP/bpy52/bin/python -c "import bpy; print(bpy.app.version_string)"   # → 5.2.1 LTS
```

**자주 쓰는 명령**

| 무엇 | 명령 | 시간 |
|---|---|---|
| 공학 수치 다시 계산 | `python3 engineering/calc.py && python3 engineering/report.py` (시스템 python3로 된다) | 몇 초 |
| 레퍼런스 템플릿 다시 만들기 | `cd previs && $SP/bpy52/bin/python reference_template.py ../docs/reference/template` | 약 15초 |
| 언더슈트 데이터 | `cd previs && $SP/bpy52/bin/python undersuit.py [OUT.webp]` → `engineering/undersuit.json` (OUT을 주면 센서 지도도 렌더) | |
| 착용자 몸 다시 맞추기 | [`research/corpus/README.md`](research/corpus/README.md) (원자료는 공개 미러에서 받는다) | |
| P0 플랫폼 스파이크 | `cd spikes/p0-platform && npm ci && npm run build` | |
| 사용량 기록 | `python3 tools/session_usage.py --append "<라벨>"` → `docs/usage-log.md` | 몇 초 |

---

## 4. 작업 규칙 (도하와 합의한 것)

1. **보고는 한국어**로, 쉬운 말로 한다.
2. **큰 방향 전환이나 해석이 필요한 결정은 먼저 내 생각을 말하고 도하의 동의를 받은 뒤 실행**한다(2026-10-03 도하 지시).
3. 도하가 멈추라고 하면 하던 일을 안전하게 멈추고 기다린다. 도하가 일을 끊고 피드백을 주면, 하던 일을 마칠지 피드백을 먼저 할지 판단해서 유연하게 한다.
4. **레퍼런스는 해석하지 않는다.** 선 그대로 판을 만든다. 레퍼런스에 없는 면은 묻고, 임시로 채운 곳은 표시한다. 비율 조정은 % 표로 보고하고, 5 %를 넘으면 먼저 묻는다.
5. **저장소에 올리는 파일에는 모델 이름을 쓰지 않는다**(커밋 메시지 본문, 문서, 코드 주석, 아티팩트).
6. 네트워크 정책에 막힌 호스트(403)는 우회하지 않고 보고한다.
7. 결정은 [`PLAN.md`](PLAN.md) §16과 §17에, 교훈은 이 문서 §8에 기록한다. 대화가 길어지면 문맥이 흐려지므로 md 파일에 남기는 것이 원칙이다.
8. 만든 것은 **렌더하거나 캡처해서 이미지를 직접 보고** 비평한 뒤 고친다(PLAN §12.2).
9. 게이트를 마칠 때마다 사용량을 기록한다(`tools/session_usage.py`). 같은 세션은 마지막 값만 유효하고, 세션이 여러 개면 세션별 마지막 값을 더한다.
10. 아티팩트는 기존 URL로 갱신한다. 새 세션에서는 먼저 `Artifact read`로 읽고, 그 내용 위에 고친다(§6).

---

## 5. 문서 지도

| 파일 | 무엇 |
|---|---|
| [`PLAN.md`](PLAN.md) | 마스터 플랜 v3.0. 의도, 콘셉트, 공학 바이블, 렌더, 인터랙션, 사운드, 로드맵, 결정 |
| [`INTAKE.md`](INTAKE.md) | 레퍼런스 처리 9단계와 바뀔 것 미리 보기 |
| [`plan-page.html`](plan-page.html) | 계획 웹페이지 원본(§6 아티팩트) |
| [`brief/`](brief/) | 도하의 브리프, 재질 레퍼런스 이미지 5장 |
| [`reference/`](reference/) | 작성 가이드(GUIDE.md), 템플릿, 받는 곳(incoming/), 이전 도면(previous/) |
| [`storyboard/`](storyboard/) | STORYBOARD(장면), COPY(카피), BIBLES(아트·모션·사운드 규칙). ⏳ 표시 = 레퍼런스 대기 |
| [`design/systems.md`](design/systems.md) | 시스템 13개, 모듈 41개의 원리와 부품표(자동 생성) |
| [`research/`](research/) | 블렌더 방법론(G0), MBS 규약, 착용자 분석(CORPUS) |
| [`reviews/P0-platform.md`](reviews/P0-platform.md) | P0 플랫폼·사운드 검증 기록 |
| [`usage-log.md`](usage-log.md) | 토큰·시간·비용 기록 |
| [`../engineering/`](../engineering/) | calc.py, bom.py, report.py → engineering.json, bom.json, undersuit.json, provisional_inputs.json(잠정) |
| [`../previs/`](../previs/) | 유지하는 bpy 도구(README.md에 파일별 설명) |
| [`../spikes/p0-platform/`](../spikes/p0-platform/) | P0 웹 플랫폼과 사운드(`src/sfx.js`, 승인된 소리) |

---

## 6. 아티팩트

| 무엇 | 주소 | 원본 | 갱신 방법 |
|---|---|---|---|
| **계획 웹페이지** | <https://claude.ai/artifact/QnzTZbHN28DMHAfNfeEDYE> | `docs/plan-page.html` | 파일을 고친 뒤 이 URL로 발행. 새 세션에서는 먼저 read |
| **스토리보드** | <https://claude.ai/artifact/Tadg6ntS8yYW9kcgCKVr8o> | 레포에 없음(발행본이 원본) | `Artifact read`로 HTML을 받아 고친 뒤 같은 URL로 발행. 지금 발행본은 v1이라 이전 스타일프레임과 폐기한 '근육 자리의 기계' 서사가 남아 있다. 도하가 마음에 들어 하니 지우지 말고, STORYBOARD.md를 기준으로 조금씩 고친다 |
| P0 시험 페이지 | <https://claude.ai/artifact/Wa1z7DTgUuU494rC1RSfVT> | `spikes/p0-platform/` | 필요할 때만 |

---

## 7. 유지한 결정 (요약)

| 영역 | 내용 | 자세히 |
|---|---|---|
| 메시지 | "NOT ARMOR. ANATOMY." 몸 위에 짓는 두 번째 몸 | PLAN §3 |
| 서사 | 어둠 속 조립 셀 → 사람(언더슈트, 바라클라바) → 도하의 도면 → 몸 측정 → 신경 연결 → 로봇 4대가 몸 바깥에 조립 → 탯줄 분리와 첫 공개 → 움직임 → 기능 → 부품 놀링 → 자유 탐색. 3막, 정점 3개, 약 290초 | STORYBOARD |
| 구조 | 모든 기계는 몸 바깥. 층: 피부 → 신경 언더슈트 → 커프 → 프레임 → EHA와 힘줄 → 배터리·아가미·연산부 → 판 → 헬멧. 시스템 13개, 사전 조립 모듈 41개 | PLAN §3.2, §5 |
| 구동 | EHA 6개(고관절·무릎·발목), 팔꿈치 힘줄 구동, 어깨 수동 스프링, 허리 판스프링, 보조 25 % | PLAN §5.4 |
| 에너지 | 배터리 = 등판 2장(0.84 kWh, 약 3.7시간), 2036년 셀 가정만 미래 | PLAN §5.9 |
| 냉각·생명유지 | 냉각복 77.5 m + 막 아가미(압축기 없음) + 팬 6 + 아래로 열리는 루버, 헬멧 송풍 160 L/min, 비상 해제 | PLAN §5.5, §5.12 |
| 신경 | 두 번 읽는다: 뇌파 32 ch + 고밀도 근전도 784 ch, 지연 43.2 ms, SENIAM 센서 위치 | PLAN §5.11, §5.15 |
| 언더슈트 | 겉은 레이싱 슈트, 속은 기능성(센서, 냉각 튜브, 커넥터 일부 노출) | PLAN §5.15 |
| 재질·색 | 무광 티타늄 + 가벼운 마모, TiN 골드 포인트, 블랙 아노다이즈, 탄소. 셀은 산업용 노랑, 로봇은 도장 벗겨짐 | PLAN §3.4, BIBLES A2 |
| 렌더 | 하이브리드: L1 플레이트(Cycles), L1′ 재조명, L2 실시간 레이어, L3 실시간 장면. AgX LUT | PLAN §8 |
| 소리 | 배경음악 없음. 승인된 소리: 체결 '철컥' v3, 로봇 너트러너 v3, 유압 v2 | PLAN §10 |
| 웹 | Vite 빌드 → 여러 파일 Artifact, 영문 라벨 + 한글 본문, 모바일 30 fps, iPhone 스위치 햅틱 | PLAN §9, §11 |

**숫자 빠른 참조** (판에 따라 바뀌는 값은 잠정)
- 도하: 키 178.0 cm, 팔 너비 182.0 cm, 65 kg, 체지방 10 %, 가슴 93.1 cm, 허리 71.0 cm, 어깨(삼각근) 너비 47.0 cm.
- 템플릿 높이(바닥에서 mm): 정수리 1,815 · 눈 1,702 · 턱 1,572 · 견봉 1,497 · 가슴 1,334 · 팔꿈치 1,215 · 허리 1,104 · 손목 985 · 가랑이 884 · 무릎 527 · 복사뼈 97 · 발바닥 35.
- 슈트: 36.6 kg(사람이 입는 것 1.92 kg), 부품 5,819(체결구 2,826), 판 477(이전 청사진 기준), 고관절 64 · 무릎 64 · 발목 76 N·m, 평균 213 W.
- 가동 범위: 무릎 0~125°, 팔꿈치 0~135°, 어깨 굽힘 160° · 벌림 150°, 고관절 굽힘 110°, 목 회전 ±70° · 숙임 40°, 허리 숙임 60°.

---

## 8. 버린 것과 교훈

### 8.1 버린 것 (git 기록에서도 삭제)
- 슈트 외형 코드: `previs/suit.py`, `helmet.py`, `blueprint.py`와 `blueprint/`, `clearance.py`, `modules.py`, `assembly.py`, `macro.py`, `material_sheet.py`, `render_persona.py`, `render_slits.py`, `styleframes.py`, `styleframes2.py`, `suit_stats.py`, `suit_stats.json`, `test_suit.py`
- 결과물: 스타일프레임 SF1~SF8, F01~F11, PERSONA 렌더, 재질 시트, 청사진 판 지도, 공간 분석 지도(`docs/reviews/P1/`, `P1r2/`), P1 리뷰 문서 2개, 청사진 실측 오버레이, 스토리보드 페이지 v2 초안, `engineering/packaging.json`
- 남긴 것: 도하의 이전 도면 2장(`reference/previous/`), 착용자 분석 이미지(`research/corpus/`), 재질 시스템(`previs/materials.py`로 분리), 조립 셀, 언더슈트, 몸 도구.

### 8.2 왜 실패했나 (반복하지 말 것)
1. **2D 선을 부풀린 마네킹 껍데기에 투영하면 판이 생기지 않는다.** 해칭과 두 줄 선이 모두 이음선이 되고, 판은 한 장의 껍데기에 낸 홈일 뿐이었다. 이번에는 판마다 독립 솔리드로 만든다.
2. **홈 너비가 메시 간격보다 좁으면 이음선이 점선처럼 끊긴다.** 서브디비전 2단계에서 메시 간격이 약 4 mm였다. 손그림 획 굵기를 그대로 홈 너비로 쓰면 금이 간 것처럼 보인다. 틈은 공학 규칙(1.5 mm 등)으로 정하고, 선은 위치로만 쓴다.
3. **래스터 경계는 계단이 된다.** 벡터 레퍼런스를 받고, 래스터는 세선화 → 폴리라인 → 단순화를 거친다.
4. **실루엣 두 장으로 헬멧을 로프트하면 덩어리가 된다.** 헬멧은 4면과 단면이 필요하다(이번에는 도하가 디자인).
5. **뷰가 부족하면 추측하게 된다.** 정면과 측면 한 장씩으로는 팔 안쪽, 옆구리, 다리 안쪽을 알 수 없었다.

### 8.3 렌더와 도구 교훈
- **조명**: 1.1 m 거리 면광원 합계 약 78 W에서 새틴 티타늄이 하얀 석고처럼 보였다. 약 9~13 W가 맞았다. 어두운 바닥의 4 % 반사는 Specular IOR Level 약 0.08로 낮춘다.
- **렌더 시간(실측)**: 768 × 432, 16 spp 경로추적이 9.4~21.9초. 1600 × 900, 64 spp는 장당 약 165~380초로, 플레이트 2,640장이면 CPU로 약 120~280시간, GPU로 약 6~28시간이다(PLAN §8.8). 이전 파이프라인은 장면 생성에 장당 90~200초를 더 썼다.
- **기다리기**: `pgrep -f 이름`은 자기 자신의 bash 명령줄과도 맞아서 끝나지 않는 대기 루프가 된다. PID로 기다린다.
- **numpy 2**: 2차원 벡터에 `np.cross`를 쓰면 오류가 난다. 식을 직접 쓴다.
- **scipy cKDTree**: NaN 점이 있으면 실패한다. 유한한 점만 넣는다.
- **JSON 덮어쓰기**: 한 스크립트가 다른 스크립트의 키까지 지우며 파일을 덮어쓴 적이 있다(`clearance.py` → `packaging.json`). 자기 키만 고친다.
- **긴 세션**: 수정이 거듭되면 문맥이 오염된다. 결정과 교훈은 md에 남기고 새 세션에서 시작한다.

### 8.4 도하 피드백 흐름 (취향 참고용, 지금은 레퍼런스가 우선)
- 2026-10-02 R1: 패널 디자인은 도하의 청사진 그대로. 착용자 정밀 분석.
- 2026-10-03 R2: 완성품을 처음에 보여 주지 않기, 사람이 먼저, 기계는 몸 바깥, 슬림 유지, 무광 + 마모, 얇은 눈 슬릿, 셀을 빈 곳 없이, 하이브리드 렌더.
- R2 이후: 눈 구멍을 시원하게 길게, 판이 너무 매끈하지 않게, 직선미와 적당한 남성미(눈썹뼈 판이나 코는 붙이지 않기), 턱은 슬림하게.
- 그다음: 근육 유선형 해석은 하지 말 것 → **마네킹 기반 디자인 폐기, 도하의 상세 레퍼런스 그대로**(R3). 위 R2 이후 취향은 도하의 레퍼런스에 담길 것이므로 따로 적용하지 않는다.

---

## 9. 레퍼런스를 기다리는 동안 할 수 있는 일 (도하가 원할 때만)

- 인수 도구 미리 만들기: SVG 레이어 읽기, PNG 레이어 세선화와 선 추적, 템플릿 좌표 정합, 확인 이미지 출력(INTAKE 2~3단계). 템플릿 위에 시험용 판 몇 장을 그려 도구를 검증한다.
- 스토리보드 아티팩트를 STORYBOARD.md v2 방향으로 조금씩 고치기. 슈트 외형이 보이는 장면은 ⏳로 둔다.
- P2 준비: 모션 캡처 소스 라이선스 조사, 하이브리드 플레이트 재생 스파이크(WebCodecs).
