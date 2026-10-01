# G0 보고서: 블렌더 방법론 심층 조사 (깊이 10/10)

> **작성** Claude · 2026-10-01 · **대상 버전** Blender **5.2.1 LTS** (bpy, 빌드 `9e2066aef7ef`, 2026-08-25)  
> **상태** 도하 검토 대기 (G0 게이트). 이 보고서가 승인되기 전에는 프로젝트용 블렌더 모델링/렌더를 시작하지 않는다.  
> **연관 문서** [`MBS.md`](MBS.md) (이 조사에서 도출한 작업 규약) · [`scripts/`](scripts/) (실측 재현 스크립트) · [`../PLAN.md`](../PLAN.md)

---

## 목차

0. [결론 요약](#0-결론-요약)
1. [조사 방법과 신뢰도 등급](#1-조사-방법과-신뢰도-등급)
2. [Blender 5.2.1 실행 검증](#2-blender-521-실행-검증)
3. [하드서피스 모델링 방법론 비교](#3-하드서피스-모델링-방법론-비교)
4. [유기 형상 위의 하드서피스 (근육 → 패널)](#4-유기-형상-위의-하드서피스-근육--패널)
5. [토폴로지, 스케일, 명명](#5-토폴로지-스케일-명명)
6. [비파괴 워크플로우와 모디파이어 순서](#6-비파괴-워크플로우와-모디파이어-순서)
7. [지오메트리 노드와 SDF](#7-지오메트리-노드와-sdf)
8. [UV와 텍셀 밀도](#8-uv와-텍셀-밀도)
9. [베이킹](#9-베이킹)
10. [PBR 재질: 측정값과 이방성](#10-pbr-재질-측정값과-이방성)
11. [색 관리: AgX를 웹까지](#11-색-관리-agx를-웹까지)
12. [조명과 HDRI](#12-조명과-hdri)
13. [렌더 엔진: Cycles와 EEVEE](#13-렌더-엔진-cycles와-eevee)
14. [glTF 익스포트와 웹 압축](#14-gltf-익스포트와-웹-압축)
15. [파이프라인 자동화와 버전 관리](#15-파이프라인-자동화와-버전-관리)
16. [리깅: 강체 부품과 분절 라멜](#16-리깅-강체-부품과-분절-라멜)
17. [실시간 최적화](#17-실시간-최적화)
18. [실사화 체크리스트 (업계 합의)](#18-실사화-체크리스트-업계-합의)
19. [업계 사례](#19-업계-사례)
20. [플랜에 반영할 변경 사항](#20-플랜에-반영할-변경-사항)
21. [열린 문제](#21-열린-문제)
22. [출처](#22-출처)

---

## 0. 결론 요약

1. **Blender 5.2.1 LTS는 이 컨테이너에서 정상 실행된다.** PyPI `bpy==5.2.1`(Python 3.13 전용)로 헤드리스 실행, Cycles CPU 렌더, OIDN 디노이즈, AgX, 베이크, QuadriFlow, 지오메트리 노드, glTF 익스포트, .blend 저장까지 전부 실측으로 확인했다. 단 EEVEE는 GPU가 없어 실용적이지 않다(아래 2장).
2. **하드서피스 방법은 '미드폴리 + 가중 노멀'을 주력으로 한다.** 실제 베벨 지오메트리로 실루엣 하이라이트를 만들고, 미세 디테일(각인, 블라스트 질감, 공구 자국)만 노멀/트림으로 처리한다. 하이폴리 → 로우폴리 베이크는 각인 같은 국소 디테일에만 쓴다. AAA 게임 업계(Star Citizen 등)의 주류 방식이며 웹 실시간에 가장 잘 맞는다.
3. **근육 형상은 블렌더 5.2의 네이티브 SDF 노드로 만들 수 있다.** 곡선 → 반지름 프로파일 점 → SDF → 합집합 → 필렛 → 메시까지 실측 0.1초. 플랜 B3(근육 SDF)을 외부 도구 없이 블렌더 안에서 구현할 수 있다.
4. **곡면 패널의 음영은 '원본 곡면 노멀 전사(Data Transfer)'가 핵심이다.** 곡면을 잘라 만든 패널은 원래 곡면의 노멀을 물려받아야 패널 경계를 넘어 하이라이트가 끊기지 않는다(같은 금형에서 찍은 실제 패널처럼).
5. **색은 LUT로 맞춘다. 숫자로 확인했다.** three.js 내장 AgX는 Blender AgX와 컬러차트 평균 **ΔE 3.9**(최대 6.2), 주황/빨강 발광체에서 **최대 ΔE 7**까지 다르다. Blender의 AgX를 log2 셰이퍼 + 65³ LUT로 구우면 three.js 방식(trilinear 보간)으로 **평균 ΔE 0.07, 최대 0.83**으로 재현된다.
6. **재질 수치는 분광 계산으로 확보했다.** 공개 n,k 데이터에서 계산한 티타늄 F0는 (0.441, 0.400, 0.361)로 physicallybased.info DB와 정확히 일치했다. 골드티타늄(TiN) F0는 (0.614, 0.462, 0.233). 다만 **티타늄은 측정 데이터셋에 따라 20~40% 차이**가 나므로 최종값은 스타일프레임 비교 렌더로 정한다.
7. **웹 압축은 블렌더 밖에서 한다.** 5.2.1 익스포터에 meshopt 옵션이 생겼지만 PyPI wheel에는 Draco/meshopt 네이티브 라이브러리가 없어 **조용히 무시된다**(실측). glTF-Transform(npm)으로 후처리한다.
8. **파이프라인은 코드로 만든다.** 업계 관행(Blender Studio의 명명 규칙, 헤드리스 실전 교훈)을 [`MBS.md`](MBS.md)로 정리했고, 이후 모든 스크립트가 자동 검사를 받는다.
9. **착용자 바디는 MakeHuman(MPFB2) CC0 에셋을 쓸 수 있다.** 기본 메시와 타깃이 GitHub에 있고 에셋 라이선스가 CC0이다. 다만 zip 다운로드가 막혀 있어 필요한 파일만 개별로 받아 직접 타깃을 적용한다.
10. **네트워크 제약**: blender.org 전체(매뉴얼, 개발 문서), Polycount, three.js 공식 사이트 등이 이 환경에서 차단돼 있다. 그래서 ① bpy 직접 실측, ② GitHub 원본 소스, ③ 웹 검색 요약을 조합했고, 출처마다 신뢰도를 표기했다.

---

## 1. 조사 방법과 신뢰도 등급

### 1.1 신뢰도 등급

| 등급 | 의미 | 예 |
|---|---|---|
| **A** | 이 컨테이너에서 **직접 실측**하거나 **소스 코드를 읽어** 확인 | bpy 5.2.1 실행, three.js 소스, OCIO 설정 파일, ΔE 계산 |
| **B** | 공식 1차 자료 (매뉴얼, 사양서, 원저 데이터) | Blender 매뉴얼(검색 요약 경유), Khronos 사양, refractiveindex.info 원 데이터 |
| **C** | 업계 실무자 다수 출처의 합의 | Polycount, 80.lv, 아트스테이션 브레이크다운 |
| **D** | 단일 2차 출처, 검증 필요 | 블로그 한 곳, 검색 요약에만 있는 주장 |

### 1.2 조사 환경 제약과 우회

| 대상 | 상태 | 우회 |
|---|---|---|
| docs.blender.org, developer.blender.org, studio.blender.org, projects.blender.org | ❌ 차단 | 웹 검색 요약(B/C) + bpy 실측(A) |
| Polycount 위키, physicallybased.info, threejs.org, gltf-transform.dev, 위키백과, 유튜브 | ❌ 차단 | GitHub 원본 저장소(raw) + 검색 요약 |
| raw.githubusercontent.com | ✅ | three.js 소스, physicallybased DB, refractiveindex DB, MPFB2 |
| GitHub zip/릴리스 다운로드 | ❌ 차단 | 개별 파일 raw 다운로드 |
| PyPI, npm | ✅ | bpy, opencolorio, colour-science, gltf-transform |
| 웹 검색 | ✅ (요약 스니펫) | 실무 관행 탐색용. 핵심 주장은 실측이나 소스로 교차 검증 |

> **검색 요약의 오류 사례**: 검색 요약 하나는 "Blender가 QuadriFlow를 Quad Remesher로 대체했다"고 주장했지만, 5.2.1에서 `object.quadriflow_remesh`가 그대로 존재하고 정상 동작함을 실측했다. Quad Remesher는 상용 애드온일 뿐이다. 이런 이유로 D등급 주장은 반드시 교차 검증했다.

---

## 2. Blender 5.2.1 실행 검증

> 도하 질문: "블렌더 5.2.1 버전으로 실행되는지 확인해봐" → **✅ 실행된다.** 아래는 전부 등급 A(실측).

### 2.1 설치 경로

- PyPI에 `bpy` 5.2.1이 있다. 최신은 **5.2.2**(5.2 LTS 패치). **5.1부터 wheel은 Python 3.13 전용**(`cp313`, `manylinux_2_28_x86_64`, 약 402 MB)이다.
- 처음 Python 3.11로 조회했을 때 5.0.1까지만 보였던 이유가 이것이다. 플랜의 "5.0.1이 최신"은 잘못된 서술이었고 수정했다.
- 컨테이너에 Python 3.13.14와 glibc 2.39가 있어 요구사항(glibc 2.28 이상)을 충족한다.
- blender.org 공식 바이너리는 네트워크 정책으로 받을 수 없다. bpy 모듈이 유일한 경로다.

```
bpy 5.2.1 LTS | build 9e2066aef7ef | 2026-08-25 | Python 3.13.14
```

### 2.2 기능별 실측 결과

| 항목 | 결과 | 비고 |
|---|---|---|
| 헤드리스 import | ✅ | |
| 빌드 옵션 | ✅ Cycles, OSL, OpenColorIO, OpenVDB, OpenSubdiv, USD, Alembic, Freestyle, WebP/EXR/HDR | OpenMP 꺼짐 |
| Cycles 디바이스 | ✅ CPU (Intel Xeon 2.1 GHz, 4스레드) | CUDA/HIP 라이브러리 없음(경고만) |
| Cycles 렌더 | ✅ 320×240, 64spp + OIDN = **1.17초** | |
| Cycles 벤치 | ✅ 1280×720, 128spp 적응형 + OIDN, 단순 장면 = **31.3초** | 복잡한 실제 장면은 수 분 예상 |
| OIDN 디노이저 | ✅ `OPENIMAGEDENOISE` | |
| 색 관리 기본값 | ✅ 디스플레이 sRGB / 뷰 **AgX** / 룩 None | |
| 작업 색공간 | ✅ `bpy.data.colorspace.working_space` = Linear Rec.709 (Rec.2020, ACEScg 선택 가능) | 5.0에서 신설 |
| AO 베이크 | ✅ 0.02초 (128²) | |
| 노멀 베이크 (Selected to Active, 케이지) | ✅ 1K = **1.04초** | |
| QuadriFlow | ✅ 744면 전부 쿼드, 0.35초 | |
| 복셀 리메시 | ✅ 0.03초 | |
| 지오메트리 노드 | ✅ 노드 타입 274종 | SDF 그리드 전 계열 포함 |
| SDF 체인 | ✅ 큐브 → SDF(2 mm) → 필렛 ×3 → 메시 = 61k면 0.29초 | Grid to Mesh 임계값은 0으로 바꿔야 함 |
| glTF 익스포트 | ✅ extras(커스텀 속성), TANGENT, TEXCOORD, NORMAL | |
| glTF meshopt/Draco | ⚠️ 옵션은 있으나 **wheel에 브리지 라이브러리가 없어 압축이 조용히 생략됨** | glTF-Transform으로 후처리 |
| .blend 저장 | ✅ | |
| EEVEE | ⚠️ 기본 상태에선 `libEGL.so.1` 없음으로 **중단**. Mesa(llvmpipe) 설치 후 동작은 하지만 160×120 기본 큐브에 **35초**(셰이더 컴파일) | **실사용 불가 → Cycles 전용** |
| LoopTools | ❌ bpy 모듈에 기본 미포함 | 필요 기능은 bmesh로 구현 |

재현: [`scripts/`](scripts/README.md)

---

## 3. 하드서피스 모델링 방법론 비교

### 3.1 네 가지 주류 방식

| 방식 | 핵심 | 장점 | 단점 | 주 사용처 | 신뢰도 |
|---|---|---|---|---|---|
| **SubD + 서포트 루프** | 저해상도 케이지 + Subdivision Surface, 날카로운 곳에 보조 루프 | 매끈한 곡면, 영화/제품 품질 | 폴리곤 많음, 수정 어려움, 불리언과 상극 | 영화, 하이폴리 원본 | C |
| **미드폴리 (베벨 + 가중 노멀)** | 실제 베벨 지오메트리 + Weighted Normal로 평면은 평평하게, 베벨은 부드럽게 | **베이크 불필요**, 수정 쉬움, 트림/데칼과 궁합 | 가는 삼각형 증가 | AAA 게임 (Star Citizen, Alien Isolation) | C |
| **불리언 + 비파괴 스택** | 원시 도형을 불리언으로 조합, 베벨로 마감 (HardOps/BoxCutter 계열) | 기계 형상을 빠르게 | 토폴로지 지저분, 곡면 음영 문제 | 컨셉, 하드서피스 키트배시 | C |
| **하이 → 로우 베이크** | 하이폴리 디테일을 노멀맵으로 로우폴리에 굽기 | 최소 폴리곤 | 파이프라인이 파괴적, 케이지/탄젠트 관리 | 전통적 게임 에셋 | C |

### 3.2 MYOMORPH의 선택: 하이브리드

| 대상 | 방식 | 이유 |
|---|---|---|
| **패널 외형과 모서리** | **미드폴리**: 실제 베벨(0.3~0.5 mm, 2~3세그먼트) + 가중 노멀 | 실루엣 하이라이트는 노멀맵으로 흉내 낼 수 없다. 조립 애니메이션에서 패널이 뒤집히고 측면이 보이므로 실제 두께와 모서리가 필요하다 |
| **근육 형상(몰드)** | **SDF/복셀** (블렌더 네이티브 그리드 노드) | 수십 개 근육의 매끈한 합집합과 필렛 |
| **패널 곡면** | 쿼드 리메시 + 쉬링크랩 + **노멀 전사** | 곡면 연속성 |
| **미세 디테일** (각인, 블라스트, SPIF 공구 자국, 리벳 머리 주변) | 노멀/트림 시트, 국소 하이→로우 베이크 | 폴리곤 예산 보호 |
| **반복 부품** (체결부품 수천 개) | 인스턴싱 (GN Instance on Points → glTF EXT_mesh_gpu_instancing 또는 런타임 InstancedMesh) | 메모리 |

### 3.3 근거가 되는 실무 원칙 (C등급, 다수 출처 합의)

- 날카로운 90° 모서리는 실시간 조명에서 가짜로 보인다. 실제 제조 부품에는 항상 공구가 남긴 작은 반경이 있다. 대부분의 하드서피스 아티스트가 1~3 mm 베벨을 기본으로 넣는다(우리는 판재 두께가 1 mm 안팎이라 0.3~0.5 mm).
- 가중 노멀(FWN)은 큰 평면의 버텍스 노멀을 면에 수직으로 세워, 음영 변화를 작은 베벨 면에 몰아준다. 평면의 원치 않는 그라데이션이 약 90% 사라진다. UV를 분할하지 않아도 되므로 버텍스 수도 늘지 않는다.
- 단점: 베벨이 길고 가는 삼각형을 만들어 렌더 성능을 깎는다 → 베벨 세그먼트를 최소화하고 LOD에서 베벨을 단순화한다.

---

## 4. 유기 형상 위의 하드서피스 (근육 → 패널)

### 4.1 업계의 수작업 방식 (C등급)

1. 유기 형상을 스컬프트한다.
2. 마스크나 페이스셋으로 패널 영역을 지정해 두께 없이 추출한다.
3. 쿼드 리메셔로 정리한다.
4. 솔리디파이로 두께를 준다.
5. 리토폴로지 메시는 쉬링크랩(Project, Above Surface, 아주 작은 오프셋)으로 원본에 붙인다.

### 4.2 우리의 절차적 변환

| 수작업 단계 | MYOFORGE 자동화 |
|---|---|
| 스컬프트 | 근육 테이블(기시/정지, 근복 프로파일, 섬유 유형) → **SDF 섬유 다발** (7장) |
| 마스크/페이스셋 | **근육 소유권 라벨**: 표면 각 점에서 가장 가까운 근육 → 경계 = 이음선 |
| 쿼드 리메시 | 영역별 **QuadriFlow**(내장, 실측 확인) + 경계 고정 |
| 쉬링크랩 | `TARGET_PROJECT` 또는 `ABOVE_SURFACE` 모드(5.2.1 존재 확인) |
| 솔리디파이 | `NON_MANIFOLD` + 일정 두께(`EVEN`/`CONSTRAINTS`) |
| 음영 정리 | **Data Transfer(CUSTOM_NORMAL)** 로 원본 곡면 노멀 전사 |

### 4.3 실측으로 확인한 함정

- **SDF 샘플링으로 소유권을 정하면 이음선 근처 판정이 불안정하다.** 프로브 결과, 각 근육 SDF가 좁은 대역(narrow band)만 저장하므로 대역 밖 값이 포화되어, 두 근육 거리가 같아지는 이음선 근처 점을 잡지 못했다(A/B 라벨 자체는 12,318 / 8,382로 분리됨). → **이음선은 근육 골격 곡선까지의 명시적 거리(BVH/numpy)로 계산**한다.
- **Points to SDF Grid의 Radius 입력을 연결하지 않으면 기본값이 적용돼 형상이 엉뚱하게 커진다**(실측: 99만 면). 반드시 Radius 노드를 연결한다.

### 4.4 쿼드 리메셔 비교

| 도구 | 라이선스 | 특징 | 우리 사용 |
|---|---|---|---|
| **QuadriFlow** | 블렌더 내장 | Instant Meshes 기반, 특이점(비정규 꼭짓점)이 약 4배 적음. 작은 디테일 정밀도는 낮음 | **1안** (실측 동작) |
| Instant Meshes | BSD | 빠르고 강건, 하드서피스에 유리, 방향장 정렬 | 2안 (소스 빌드 필요) |
| QuadWild (Bi-MDF) | GPL | 특징선 기반, 유기체에 유리, 순수 쿼드 | 3안 (빌드 부담) |
| Quad Remesher | 상용 | 업계 표준급 품질 | 사용 불가 (헤드리스 라이선스) |

### 4.5 곡면 패널 음영: 노멀 전사 (C등급, 핵심 기법)

곡면에 구멍을 내거나 잘라내면 노멀 흐름이 끊겨 핀치, 깨진 반사, 왜곡된 그라데이션이 생긴다. 메시가 틀려서가 아니다. 해결책은 **자르기 전의 매끈한 곡면을 복제해 두고 Data Transfer 모디파이어로 그 노멀을 잘린 메시에 전사**하는 것이다(구멍 안쪽 루프는 제외).

**MYOMORPH 적용**: 각 패널은 근육 외형 몰드(OML)에서 잘려 나온다. 패널 윗면에 OML의 노멀을 전사하면 **인접 패널끼리 하이라이트가 이음선을 넘어 매끄럽게 이어진다.** 같은 금형에서 찍은 실제 판금 패널이 이렇게 보인다. 이것이 '조각들이 모여 하나의 근육으로 읽히는' 핵심이다.

---

## 5. 토폴로지, 스케일, 명명

### 5.1 스케일과 트랜스폼 (B/C)

- **실제 스케일 필수**(1 unit = 1 m). 조명, 물리, 피사계 심도가 모두 스케일에 의존한다. 스케일이 틀리면 비전문가도 위화감을 느낀다.
- 트랜스폼을 적용(Apply)한 뒤 익스포트한다. 회전/스케일이 남아 있으면 노멀 전사, 베벨 폭, 쉬링크랩이 틀어진다.

### 5.2 Blender Studio 명명 규칙 (B, 공식 파이프라인 문서의 검색 요약)

| 규칙 | 내용 |
|---|---|
| 대소문자 | `lower_underscore_case`, 접두사와 접미사는 대문자 |
| 구분자 | 밑줄 = 공백 대체(의미 없음), **대시 = 접두사와 계층 구분** |
| 오브젝트 접두사 | `GEO`(렌더되는 지오메트리), `RIG`(아마추어), `LGT`(조명), `ENV`(환경), `WGT`(본 셰이프), `HLP`(헬퍼, 렌더 안 됨) |
| 에셋 루트 컬렉션 | 유형 접두사 + 이름: `CH-`(캐릭터), `PR-`(리그된 소품), `LI-`, `SE-`, `LG-`(라이트 리그), `CA-`(카메라 리그) |
| 데이터블록 | 모든 데이터블록 이름에 에셋 이름을 포함해 고유성 확보 |
| 파일 | `{유형}-{에셋}-{작업}.blend` |

**우리 적용**: 이 문법 위에 플랜의 부품번호 체계를 얹는다. 예: 오브젝트 `GEO-MM1-CH-PMS-L-03`, 리그 `RIG-MM1`, 헬퍼 `HLP-MM1-joint_knee_L`. 세부는 [`MBS.md`](MBS.md) §2.

### 5.3 5.x API에서 사라지거나 바뀐 것 (A)

- `Mesh.use_auto_smooth` **삭제됨**(4.1부터). 'Smooth by Angle' 모디파이어 또는 `object.shade_auto_smooth`를 쓴다.
- 커뮤니티 보고(D, 검증 예정): `scene.threads_mode` 삭제, 액션이 오브젝트에 바인딩될 때만 `fcurves` 접근 가능(슬롯 액션 체계).

---

## 6. 비파괴 워크플로우와 모디파이어 순서

### 6.1 일반 원칙 (C)

모디파이어는 위에서 아래로 순서대로 평가되고, 대부분의 쌍은 순서를 바꾸면 결과가 달라진다. 합의된 단계:

`① 복제(Mirror, Array) → ② 변형(Lattice, Curve, Shrinkwrap) → ③ 토폴로지(Boolean, Remesh, Decimate) → ④ 두께/디테일(Solidify, Bevel) → ⑤ 매끈함(Subdivision) → ⑥ 음영(Weighted Normal, Data Transfer)`

- 미러는 맨 위(특히 불리언보다 먼저).
- 서브디비전을 불리언 위에 두지 않는다.
- 베벨 → 서브디비전 순서여야 베벨이 유지된다.

### 6.2 베벨 + 가중 노멀 조합 (B/C, 5.2.1 API 확인)

- **방법 1**: Bevel의 `face_strength_mode`(`FSTR_AFFECTED` 등)로 면 강도를 표시 → Weighted Normal의 `use_face_influence` 켜기. 비파괴적이고 유연하다.
- **방법 2**: Bevel의 `harden_normals`. 베벨 안에 내장된 가중 노멀 같은 것으로, 결과가 약간 다르다.
- **우리 선택**: 방법 1. Weighted Normal은 `FACE_AREA_WITH_ANGLE`, `keep_sharp` 켬.

### 6.3 MYOMORPH 패널의 표준 스택

```
1. [GN] 패널 생성 (몰드에서 영역 추출, 경계 정리)        ← 절차 단계는 GN 또는 파이썬
2. Shrinkwrap        (TARGET_PROJECT, 몰드에 밀착)
3. Solidify          (NON_MANIFOLD, 두께 0.8~1.2 mm, 안쪽)
4. [GN] 헴/플랜지     (안쪽으로 접힌 가장자리 2~4 mm)
5. Bevel             (ANGLE 제한, 0.3~0.5 mm, 2~3 세그먼트, face strength = AFFECTED)
6. Data Transfer     (CUSTOM_NORMAL ← 몰드 원본, 윗면 버텍스 그룹만)
7. Weighted Normal   (FACE_AREA_WITH_ANGLE, face influence, keep sharp)
```

6과 7의 영역이 겹치지 않도록 버텍스 그룹으로 나눈다(윗면 = 전사, 모서리/측면 = 가중).

---

## 7. 지오메트리 노드와 SDF

### 7.1 5.2.1에서 쓸 수 있는 SDF/그리드 노드 (A, 실측 목록)

`Points to SDF Grid` · `Mesh to SDF Grid` · `SDF Grid Boolean` · `SDF Grid Fillet` · `SDF Grid Offset` · `SDF Grid Laplacian` · `SDF Grid Mean` · `SDF Grid Mean Curvature` · `SDF Grid Median` · `Grid to Mesh` · `Sample Grid` · `Grid Gradient` · `Field to Grid` · `Grid Voxelize` 외

- **SDF Grid Boolean**: 입력은 `Grid 1` + 다중 입력 `Grid`. 합집합은 다중 입력에 여러 그리드를 연결한다(실측).
- **스무딩 계열**: Mean(빠른 박스 필터), Laplacian(확산), Mean Curvature(형상 보존형, 불리언 후 정리에 효과적), Median(날카로운 특징 보존) (B, 매뉴얼 요약).
- **Offset**: 월드 거리로 팽창/수축 → **착용 여유와 패널 두께 오프셋**에 사용.

### 7.2 근육 SDF 프로브 (A, 실현성 확인)

```
직선 곡선 → Resample(64) → 반지름 = r·sin(πt)^0.6 + 0.25r (근복 프로파일)
→ Curve to Points → Points to SDF Grid (2.5 mm, Radius 연결)
→ 두 가닥 SDF 합집합 → Fillet ×4 → Grid to Mesh (임계값 0)
→ Sample Grid로 근육별 거리 차이 저장 (소유권)
결과: 20,698면, 0.1초, 바운딩 박스 정확
```

### 7.3 디테일 생성 (C)

- 체결부품: 모서리를 따라 일정 간격으로 인스턴스를 배치하는 'Edge Distribution' 패턴(곡선 변환 → 길이 기준 리샘플 → 법선 정렬 → Instance on Points)이 표준이다. 우리는 여기에 '패널 모서리에서 안쪽으로 오프셋, 최소 간격, 코너 회피' 규칙을 더한다.
- Repeat Zone과 For Each Element Zone(5.2.1 존재 확인)으로 근육별, 패널별 반복 처리를 노드 안에서 한다.
- Bake 노드로 무거운 단계를 캐시한다.

---

## 8. UV와 텍셀 밀도

### 8.1 업계 기준 (C)

| 용도 | 텍셀 밀도 |
|---|---|
| 모바일/VR | 256~512 px/m |
| 3인칭 게임 | 512~1,024 px/m |
| 1인칭 게임 | 1,024~2,048 px/m |
| 시네마틱/스크린샷 | 2,048~4,096 px/m |

### 8.2 MYOMORPH 기준

우리는 매크로 클로즈업(100 mm 렌즈, 화면에 패널 하나가 꽉 차는 장면)이 있다. 그렇다고 부품 수천 개에 고유 고해상도 텍스처를 줄 수는 없다. 그래서 **텍셀 밀도를 세 층으로 나눈다**.

| 층 | 내용 | 밀도 |
|---|---|---|
| ① 공유 타일 재질 | 비드블라스트 미세 노멀, 거칠기 브레이크업, 헤어라인 | 트리플래너/UV 타일링으로 사실상 무제한 (4,096 px/m급 체감) |
| ② 트림 시트 | 헴, 각인, 패스너 주변, 라이트파이프 홈 | 2,048 px/m |
| ③ 부품별 베이크 아틀라스 | AO, 곡률, 두께 | 히어로 부품 512 px/m, 일반 256 px/m |

### 8.3 UV 규칙 (A/C)

- 언랩: 5.2.1의 `MINIMUM_STRETCH`(SLIM) 방식 사용 가능(실측). 판금 패널은 거의 전개 가능한 곡면이라 왜곡이 적다.
- **U축 = 근섬유 방향** (플랜 원칙 C). 탄젠트가 섬유를 따라가므로 이방성 방향 맵 없이도 결이 맞는다.
- 하드 에지(노멀이 갈라지는 곳)에서는 UV도 분할한다. 탄젠트 공간 노멀맵 이음선 문제의 가장 흔한 원인이 이것이다.
- 패킹: `pack_islands`(CONCAVE, 회전 허용, 마진 FRACTION).

---

## 9. 베이킹

### 9.1 동기화 워크플로우 (B/C)

- **MikkTSpace가 사실상 표준**이다. 블렌더 기본값이고 Unity/Unreal도 지원한다. glTF는 탄젠트를 포함해 익스포트할 수 있고 three.js는 그 탄젠트를 쓴다.
- 원칙: **굽는 프로그램과 렌더하는 프로그램이 같은 탄젠트 공간을 써야 한다**(synced workflow). → 블렌더에서 MikkTSpace로 굽고, glTF에 TANGENT를 익스포트하고(실측 확인), three.js에서 그 탄젠트를 그대로 쓴다.
- 케이지 = 로우폴리를 부풀린 사본. 복잡한 에셋은 **베이크 그룹**(하이폴리의 어떤 면이 로우폴리의 어떤 면에 대응하는지 지정)이 가장 정밀하다. 우리는 부품 단위로 베이크하므로 자연스럽게 그룹이 나뉜다.

### 9.2 굽는 맵 (MYOMORPH)

| 맵 | 용도 | 방식 |
|---|---|---|
| AO | 패널 간격의 접촉 그림자 | Cycles AO, 부품별 + 이웃 부품 포함 |
| 곡률 | 모서리 폴리시, 엣지 하이라이트 | GN 속성 → 베이크 |
| 두께 | 얇은 부위 표현 | Cycles |
| 노멀 | 각인, 미세 비드 | 국소 하이→로우 |
| ID | 재질 영역 | 정점 색/속성 |

실측 속도: 1K 노멀(케이지) 1.04초. 부품 600종 × 맵 3~4장도 CPU로 감당 가능하다.

---

## 10. PBR 재질: 측정값과 이방성

### 10.1 분광 계산으로 얻은 금속 F0 (A: 직접 계산, 원 데이터 B)

방법: refractiveindex.info 데이터베이스(CC0, GitHub 원본)의 n,k → 수직 입사 프레넬 반사율 → CIE 1931 2° + D65 → 선형 sRGB.  
검증: 같은 방식으로 계산한 Ti(Palm)와 Au(Babar) 값이 physicallybased.info DB(CC0, 2026-09-01 갱신)와 **소수점 셋째 자리까지 일치**했다.

| 재질 | 데이터 | F0 (선형 sRGB) | 82° 반사 (엣지 틴트) |
|---|---|---|---|
| **티타늄** | Palm | **(0.441, 0.400, 0.361)** | (0.610, 0.620, 0.627) |
| 티타늄 | Johnson & Christy | (0.619, 0.579, 0.543) | (0.614, 0.616, 0.623) |
| 티타늄 | 실시간 렌더링 교재 표 (기존 플랜 값) | (0.542, 0.497, 0.449) | |
| **TiN (골드티타늄)** | Pflüger 1984 (EELS, TiN₁.₀ 박막) | **(0.614, 0.462, 0.233)** | (0.716, 0.705, 0.612) |
| 금 (비교) | Babar | (1.059, 0.773, 0.307) | (1.002, 0.896, 0.630) |

**해석**
- 티타늄은 **측정 데이터셋에 따라 20~40% 차이**가 난다(시료 순도, 산화막, 표면 상태). 실제 Ti-6Al-4V는 자연 산화막이 있고, 비드블라스트 표면은 거칠기 때문에 더 밝고 회색으로 보인다.
- **결정**: Palm(DB와 일치, CC0, 출처 명확)을 기준선으로 쓰고 J&C를 상한으로 둔다. **P1 스타일프레임에서 두 값을 나란히 렌더해 도하와 함께 고른다.**
- TiN 데이터는 단일 출처(EELS 측정 박막)라 신뢰도가 상대적으로 낮다. 문헌상 TiN은 청록에서 반사가 낮고 적색에서 급증하는 '금색' 스펙트럼이며, 계산값이 이와 맞는다. 공정 조건에 따라 색이 달라진다는 점도 문헌에 있다.
- 밀도: CP 티타늄 4,540 kg/m³ (DB), Ti-6Al-4V 4,430 kg/m³ (플랜 계산서에 사용).

### 10.2 블렌더와 웹의 재질 매핑 (A)

| 단계 | 블렌더 (레퍼런스 렌더) | 웹 (three.js) |
|---|---|---|
| 금속 반사 | **Metallic BSDF, `PHYSICAL_CONDUCTOR`** 모드에 n,k를 직접 입력 (5.2.1 확인) | `metalness=1`, base color = F0, 엣지 틴트는 커스텀 TSL로 근사 |
| 분포 | `MULTI_GGX` (다중 산란, 거친 금속이 어두워지는 문제 보정) | GGX (three.js는 다중 산란 보정 포함) |
| 이방성 | Principled `Anisotropic` + **Tangent 노드(UV 기반)** | `anisotropy` + 익스포트된 TANGENT |

### 10.3 이방성 파이프라인 (A: 소스 확인)

1. 블렌더: Principled BSDF의 Anisotropic, Anisotropic Rotation, **Tangent 소켓을 Tangent 노드(UV Map 모드)에 연결**한다. 익스포터(`anisotropy.py`)는 이 세 소켓이 모두 있어야 `KHR_materials_anisotropy`를 쓴다.
2. glTF: `anisotropyStrength`, `anisotropyRotation`, (필요하면) `anisotropyTexture`.
3. three.js r187: `GLTFLoader`가 `KHR_materials_anisotropy`를 지원한다. `anisotropyMap`은 **R,G = 탄젠트/바이탄젠트 공간 방향(−1~1), B = 강도(0~1)**, 비색상 데이터.
4. **UV의 U를 섬유 방향에 맞추면 방향 맵이 필요 없다**(방향 = (1, 0) 고정). UV가 섬유와 어긋나는 부위만 방향 맵을 굽는다.

---

## 11. 색 관리: AgX를 웹까지

### 11.1 블렌더 5.x 색 관리 (A: 설정 파일 직접 확인)

- **작업 색공간**(5.0 신설): Linear Rec.709(기본) / Linear Rec.2020 / ACEScg. → **Linear Rec.709 고정**(웹이 sRGB 기반이라 변환 손실이 없다).
- sRGB 디스플레이의 뷰: Standard, ACES 1.3, ACES 2.0, Khronos PBR Neutral, **AgX**, Filmic, Filmic Log, False Color, Raw.
- AgX 룩: Punchy, Greyscale, Very High ~ Very Low Contrast, Base Contrast. → **룩 None 고정**(기준 일치를 위해).
- HDR 디스플레이(Rec.2100-PQ/HLG)와 AgX HDR 뷰도 있다(웹 HDR은 범위 밖).

### 11.2 블렌더 AgX의 정확한 변환 체인 (A: `config.ocio`)

```
장면 선형 (ACES2065-1 경유)
 → Linear FilmLight E-Gamut 로 변환
 → log2 할당: [-12.47393, +12.5260688] (25 stops)
 → AgX_Base_sRGB.cube (57³, 사면체 보간)
     "E-Gamut log2 -10~+15 stops 입력, 이미지 형성은 -10~+6.5 stops, 거듭제곱 2.4로 인코딩"
 → Rec.1886(감마 2.4)로 해석 → sRGB 구간식 인코딩으로 변환
```

### 11.3 three.js 내장 AgX (A: r187dev 소스)

```
선형 sRGB → Rec.2020 → 인셋 행렬(블렌더 AgX Log와 같은 값)
 → log2 [-12.47393, +4.026069] (-10~+6.5 stops)
 → 다항식 시그모이드 근사 (iolite, 평균제곱오차 3.67e-6)
 → 아웃셋 행렬 → 거듭제곱 2.2 → Rec.2020 → sRGB → 클램프
```

차이점: E-Gamut과 LUT 대신 Rec.2020 행렬, 정확한 곡선 대신 다항식, **감마 2.4 대신 2.2**, 게이트 매핑 대신 클램프.

### 11.4 차이 실측 (A: PyOpenColorIO 2.6.0 + 블렌더 5.2.1 설정, colour 0.4.7)

| 테스트 | three.js vs 블렌더 ΔE2000 |
|---|---|
| 그레이 램프 | 최대 **4.91** (중간 회색 −1 stop, three.js가 저중간조에서 더 밝음) |
| 컬러차트 24색, 노출 0 | 평균 **3.91**, 최대 6.2 (빨강) |
| 컬러차트 24색, 노출 +2 | 평균 2.31, 최대 4.87 (주황) |
| 발광 빨강 (상태광) | 최대 **6.97** |
| 발광 시그널 오렌지 (UI 강조색) | 최대 **6.87** |
| 발광 앰버 | 최대 4.89 |
| 발광 시안 | 최대 2.21 |
| 티타늄 알베도 | 1.37 |

ΔE 2를 넘으면 나란히 놓았을 때 구별된다. **특히 우리 브랜드 색(시그널 오렌지)과 경고색(빨강, 앰버)이 가장 많이 틀어진다.**

### 11.5 LUT 재현 정확도 (A)

방법: 선형 Rec.709 입력에 log2 셰이퍼 [−12.47393, 12.5260688] → OCIO로 정확히 계산한 N³ LUT → **three.js와 같은 trilinear 보간**으로 2만 1천 색(−8~+7 stops, 무작위 채도) 재현.

| LUT 크기 | 평균 ΔE | 99% | 최대 | 용량 (RGBA16F) |
|---|---|---|---|---|
| 33³ | 0.188 | 0.593 | 1.399 | 0.29 MB |
| 48³ | 0.104 | 0.380 | 1.100 | 0.88 MB |
| **65³** | **0.068** | **0.273** | **0.832** | 2.2 MB (압축 시 대폭 감소) |

**결정**: 65³(최고 정확도) 또는 48³(용량 절충). 둘 다 플랜 목표(평균 1.5 이하)를 큰 폭으로 만족하고 사람 눈의 식별 한계(약 1) 아래다.

---

## 12. 조명과 HDRI

### 12.1 제품 시각화 조명 원칙 (C)

- **금속은 '받는 빛'이 아니라 '비추는 것'으로 보인다.** 밝기를 올리기 전에 반사될 밝고 어두운 형태를 배치한다. 반사 물체는 밝은 배경 앞에서 사라질 수 있다.
- 스트립 소프트박스 HDRI는 금속과 광택면에 잘 정의된 띠 하이라이트를 준다. 조명이 너무 균일하면 평평해 보이므로 의도적 대비를 만든다.
- 영역 조명(Area Light)이 소프트박스 역할의 기본 선택이다.
- **라이트 링킹**(5.2.1에서 오브젝트 속성 존재 확인)으로 특정 부위에만 하이라이트를 준다.
- HDRI 해상도: 조명 테스트는 1~2K로 충분, 날카로운 근접 반사가 보이는 히어로 렌더는 최대 8K까지 정당화된다.

### 12.2 MYOMORPH 적용

- 블렌더에서 스튜디오 세트(세로 스트립 소프트박스 3~4개, 블랙 플래그, 바닥)를 만들고 **Cycles 등장방형 파노라마로 렌더해 자체 HDRI를 만든다.** 블렌더 레퍼런스와 three.js가 같은 환경광을 공유한다.
- 웹용은 2K~4K + UltraHDR(게인맵 JPEG)로 경량화, 근접 반사는 실시간 RectAreaLight가 담당한다.
- 카메라: 기본 센서 36 mm(5.2.1 기본값 확인), 85/100/35 mm 렌즈, DoF 속성(f-stop, 조리개 날 수, 회전, 비율)으로 실제 렌즈 보케.

---

## 13. 렌더 엔진: Cycles와 EEVEE

### 13.1 결정: Cycles CPU 전용 (A)

EEVEE는 이 컨테이너에서 Mesa 소프트웨어 렌더링으로만 돌고, 기본 큐브 160×120에 35초가 걸렸다(대부분 셰이더 컴파일). Cycles는 같은 일을 1초 안에 한다.

### 13.2 Cycles 설정 기준 (B/C + A로 속성 확인)

| 설정 | 값 | 근거 |
|---|---|---|
| 적응형 샘플링 | 켬, 임계값 0.01, 최소 샘플 기본 | 권장 시작점 |
| 샘플 | 레퍼런스 256~512, 반복 작업 32~64 | |
| 디노이저 | OIDN, 프리필터 Accurate, 알베도+노멀 입력 | CPU 기본 권장 |
| 라이트 트리 | 켬 (`use_light_tree`) | 다중 조명 효율 |
| 경로 가이딩 | 실내형 장면에서만 켬 (`use_guiding`, **CPU 전용 기능**), 학습 샘플 128~256 | 우리는 CPU라 쓸 수 있다 |
| 바운스 | 총 6~8 (금속 상호반사 고려, 기본 12는 과함) | 3~6이 일반적이지만 금속 다중 반사 때문에 약간 높게 |
| 텍스처 | 5.2의 텍스처 캐시 관련 옵션 존재 | 대규모 장면에서 메모리 절감 |

### 13.3 시간 예산 (A 기반 추정)

720p 128spp 단순 장면 31초 → 실제 슈트 장면(부품 4천 개, 금속 다중 반사)은 720p 기준 3~8분, 1080p는 그 2~3배로 예상. 레퍼런스 렌더 수십 장은 감당 가능하지만, 반복 작업은 저해상도로 한다.

---

## 14. glTF 익스포트와 웹 압축

### 14.1 5.2.1 익스포터 (A)

| 옵션 | 상태 |
|---|---|
| `export_extras` | ✅ 커스텀 속성 → 노드 extras (부품 메타데이터 운반) |
| `export_tangents` | ✅ |
| `export_apply` | ✅ 모디파이어 적용 |
| `export_gpu_instances` | ✅ `EXT_mesh_gpu_instancing` (빈 오브젝트 자식으로 한정) |
| `export_image_format` | AUTO / JPEG / **WEBP** / NONE |
| `export_meshopt_compression_enable` + `export_meshopt_extension` | 옵션 존재 (`EXT_meshopt_compression` 또는 `KHR_meshopt_compression`) |
| Draco, meshopt 실제 동작 | ❌ **wheel에 `libbf_intern_draco_bridge.so`, `libbf_intern_meshopt_bridge.so` 없음** → 오류 로그만 남기고 비압축 출력 |
| `export_use_gltfpack` | gltfpack 바이너리가 있으면 사용 가능 |

### 14.2 웹 쪽 지원 (A: three.js r187dev `GLTFLoader` 소스)

`KHR_materials_anisotropy`, `KHR_meshopt_compression`, `EXT_meshopt_compression`, `KHR_texture_basisu`, `EXT_texture_webp`, `EXT_mesh_gpu_instancing`, `KHR_materials_emissive_strength` 등 지원.

### 14.3 압축 전략 (C + A)

- **지오메트리: meshopt**. Draco보다 디코딩이 훨씬 빠르고 애니메이션과 모프 타깃도 압축하며, glTF-Transform `optimize`의 기본값이다. 디코더가 JS에 내장돼 wasm 파일 문제도 없다.
- **텍스처: KTX2**. 노멀/AO/거칠기-금속성(비색상)은 **UASTC**, 베이스 컬러(색상)는 **ETC1S**. GPU별 네이티브 압축 포맷으로 트랜스코딩된다.
- **인코더 확보 문제**: KTX-Software 공식 릴리스 다운로드는 이 환경에서 차단된다. npm `ktx2-encoder`(wasm 기반)와 PyPI `pyktx`가 접근 가능하다 → P0.2에서 시험. 안 되면 WebP로 폴백.

---

## 15. 파이프라인 자동화와 버전 관리

### 15.1 헤드리스 bpy 실전 교훈 (C/D: 커뮤니티 정리 + A: 일부 직접 재현)

1. 노드는 **UI 이름이 아니라 `.type`/`.bl_idname`으로 찾는다**(현지화된 빌드에서 이름이 바뀜). 입력 소켓 이름은 안정적이다.
2. `matrix_world`는 뷰 레이어가 갱신되기 전까지 낡은 값이다 → `view_layer.update()` 후 읽는다.
3. **오퍼레이터보다 `bpy.data` 직접 조작을 우선**한다(컨텍스트 의존성과 신뢰성 문제).
4. 블렌더 로그는 장황하다 → 신호만 필터링한다.
5. **렌더가 종료 코드 0으로 끝나도 내용이 맞다는 보장은 없다** → 결과 이미지를 직접 보고 구체적 질문으로 확인한다(피사체 전체가 프레임 안에 있는가, 정면인가, 특징이 보이는가). 턴테이블은 프레임별 픽셀 표준편차로 빈 프레임을 잡는다.
6. 카메라는 추적 쿼터니언으로 조준하고, 정면 규칙을 하나로 고정한다.
7. 결정론: 시드 고정, 팩토리 설정에서 시작(`read_factory_settings(use_empty=True)`).
8. bpy는 프로세스당 한 번만 import된다 → 단계별로 별도 프로세스를 띄우면 격리와 크래시 내성이 좋아진다(EEVEE 중단 실측 사례).

### 15.2 버전 관리 (B/C)

- Blender Studio는 **SVN**을 쓴다(비압축 .blend의 바이너리 차분 효율, 파일 잠금). 벤치마크에서는 압축 .blend + **Git LFS**가 속도 면에서 우세했다.
- **우리 선택: 파이프라인을 코드로**. 원천은 스크립트와 데이터(YAML/JSON)이고, .blend는 재생성 가능한 중간 산출물이라 커밋하지 않는다. 웹 최종 에셋(압축 glTF, 텍스처)만 커밋한다. 이 방식은 컨테이너 휘발성 문제도 해결한다.

---

## 16. 리깅: 강체 부품과 분절 라멜

### 16.1 원칙 (C)

- 기계 부품은 변형되지 않는다. **각 부품을 별도 오브젝트로 두고 본에 직접 페어런팅**한다(웨이트 페인팅 없음). 금속 패널이 늘어나는 순간 '그림티'가 난다.
- 겹치는 갑옷(허리, 무릎, 팔꿈치)은 제약(constraint)으로 제어한다. 빈 오브젝트 + 드라이버 방식도 쓰인다.

### 16.2 분수 회전 분배 (B/C)

- **Copy Rotation 제약의 영향도(influence)를 0.5로 두면 목표 회전의 절반만 돈다.** 이것을 사슬로 연결하면 회전이 여러 분절에 고르게 나뉜다. Rigify의 척추/목 시스템도 같은 원리(로컬 회전 복사)를 쓴다.
- **MYOMORPH 적용**: 목 라멜 7~9단, 복부 분절, 삼각근 라멜에 영향도 1/n, 2/n, … 을 배정한다. 히어로의 시선 추적(마스크가 커서를 따라 돌 때 목 라멜이 미끄러지는 장면)이 이 원리다.

### 16.3 웹으로 가져가는 방식

- 블렌더 리그는 **검증용**(간섭 검사, ROM 포즈 라이브러리)으로 쓴다.
- 런타임에서는 같은 규칙(분수 회전, 실린더 코사인 법칙, 4절 링크)을 TypeScript로 다시 구현해 **절차적으로 계산**한다. 스크롤 가역성, 용량, 사지 드래그 상호작용 때문이다.
- 블렌더와 런타임이 같은 결과를 내는지 포즈별 부품 행렬을 비교하는 테스트를 둔다.

---

## 17. 실시간 최적화

### 17.1 LOD (C)

- glTF-Transform의 `simplify`는 meshoptimizer를 쓴다. 목표 `ratio`를 향해 단순화하되 오차가 `error` 임계값을 넘으면 멈춘다. 속성 이음선, 경계, 접힘을 보존하려 한다.
- 하드서피스는 실루엣과 베벨 하이라이트가 생명이라 **LOD1에서 베벨 세그먼트를 줄이고, LOD2에서 베벨을 노멀로 대체**하는 방식이 단순 데시메이션보다 낫다 → 블렌더에서 LOD별 모디파이어 파라미터로 따로 생성한다.

### 17.2 three.js BatchedMesh (A: r187dev 소스)

확인한 API: `addGeometry`, `addInstance`, `setMatrixAt`, **`setGeometryIdAt`(인스턴스별 LOD 교체)**, `setVisibleAt`, `setColorAt`, `deleteInstance`, `optimize`, `perObjectFrustumCulled`(기본 켬), `sortObjects`(기본 켬), `setCustomSort`. 플랜의 "재질별 BatchedMesh 하나로 수백 개 부품을 단일 드로우콜 + 부품별 행렬 갱신 + LOD 교체" 설계가 API상 가능하다.

---

## 18. 실사화 체크리스트 (업계 합의)

| # | 원칙 | 출처 등급 | MYOMORPH 반영 |
|---|---|---|---|
| 1 | 실제 스케일로 모델링 (조명, 물리, DoF가 스케일에 의존) | C | MBS-U01 |
| 2 | **모든 모서리에 작은 베벨** (빛을 잡아 '진짜'임을 알림) | C | MBS-M04 |
| 3 | **불완전함을 겹겹이**: 거칠기 변화, 미세 스크래치, 아주 약한 얼룩. 정상 시청 거리에서 거의 안 보일 정도로 | C | PLAN §6.2 |
| 4 | HDRI는 '설정하고 잊는' 것이 아니다. 밝은 영역이 그림자, 하이라이트, 반사를 결정한다 | C | 자체 스튜디오 HDRI |
| 5 | 과도한 후보정 금지 (강한 대비, 발광, 과채도) | C | AgX, 룩 None, 약한 블룸 |
| 6 | 비율과 스케일 불일치는 비전문가도 느낀다 | C | 드로잉 IoU 검증 |
| 7 | 곡면 절단부 음영은 노멀 전사로 | C | §4.5 |
| 8 | 측정 기반 재질값 | A/B | §10 |
| 9 | 렌더 결과를 직접 보고 검증 | C/A | MBS-Q 계열 |

---

## 19. 업계 사례

| 사례 | 시사점 | 등급 |
|---|---|---|
| **Star Citizen, Alien Isolation** | 미드폴리 + 가중 노멀 + 트림 시트 + 데칼, 하이폴리와 베이크 없음. 거대한 하드서피스 에셋을 일관된 품질로 양산 | C |
| **Blender Studio 'Charge'** (14번째 오픈 무비) | 게임 시네마틱과 실시간 데모 형식에서 영감, 실사와 인터랙티브 PBR 워크플로우로 블렌더 한계를 밀어붙인 프로젝트 | B/C |
| **Blender Studio 파이프라인 문서** | 명명 규칙, 에셋 컬렉션 구조, SVN 폴더 구조, 에셋 파이프라인 애드온 | B |
| **MakeHuman / MPFB2** | 인체 기본 메시와 형태 타깃을 CC0로 공개 (출력물에 권리 주장 없음) | A(라이선스 원문 확인) |

---

## 20. 플랜에 반영할 변경 사항

| # | 변경 | 근거 |
|---|---|---|
| 1 | 대상 버전 **Blender 5.2.1 LTS** (Python 3.13 venv) | §2 |
| 2 | 근육 형상(B3)을 **블렌더 네이티브 SDF 노드**로 구현. 이음선은 골격 곡선 거리로 계산 | §4.3, §7 |
| 3 | 패널 음영에 **Data Transfer 노멀 전사** 단계 추가 | §4.5, §6.3 |
| 4 | 렌더 엔진 **Cycles CPU 전용**, EEVEE 사용 안 함 | §13 |
| 5 | 압축은 **glTF-Transform 후처리**, 블렌더 익스포터의 압축 옵션은 쓰지 않음 | §14 |
| 6 | AgX는 **65³(또는 48³) LUT** 확정 (ΔE 실측 근거) | §11 |
| 7 | 티타늄 F0 기준선을 Palm 값으로 바꾸고, P1에서 비교 렌더로 확정 | §10 |
| 8 | 착용자 바디(B2)는 **MPFB2 CC0 기본 메시 + 타깃을 개별 다운로드해 직접 적용** | §19, 21 |
| 9 | 레퍼런스 렌더는 Metallic BSDF의 **물리 도체(n,k) 모드** 사용 | §10.2 |
| 10 | 리그는 블렌더에서 검증, 런타임은 같은 규칙을 TS로 구현하고 행렬 비교 테스트 | §16.3 |

---

## 21. 열린 문제

| # | 문제 | 영향 | 대응 |
|---|---|---|---|
| O1 | **AgX LUT 라이선스**: 블렌더 색 관리 설정(Eary Chow의 AgX, Troy Sobotka의 원 설계)의 라이선스 원문을 이 환경에서 확인하지 못함 | LUT 배포 | 출시 전 확인. 대안: 변환을 실행해 얻은 데이터로 자체 LUT 생성, 또는 Khronos PBR Neutral(블렌더에 포함) |
| O2 | TiN 광학 상수가 단일 출처(EELS 박막) | 골드 마감 색 | 문헌 스펙트럼 형태와 일치함은 확인. 스타일프레임에서 시각 검증 |
| O3 | KTX2 인코더 확보 | 텍스처 용량 | npm `ktx2-encoder`, PyPI `pyktx` 시험 → 실패 시 WebP |
| O4 | MPFB2 전체 설치 불가(zip 차단) | 바디 생성 | 필요한 파일만 개별 다운로드, 타깃 적용은 자체 구현 (형식이 단순한 텍스트) |
| O5 | 블렌더 매뉴얼 원문을 직접 읽을 수 없음 | 세부 확인 | 실측과 소스 코드로 대체. 필요하면 도하가 특정 매뉴얼 페이지를 붙여 줄 수 있음 |
| O6 | **사진 레퍼런스 접근 불가** (이미지 사이트 차단) | 재질 실사감 | 도하가 티타늄/골드티타늄 실물 사진(비드블라스트, 헤어라인, TiN 코팅)을 몇 장 올려 주면 재질 보정 정확도가 크게 오른다 |

---

## 22. 출처

**직접 실측 / 소스 (A)**
- bpy 5.2.1 실측 스크립트와 결과: [`scripts/`](scripts/README.md)
- Blender 5.2.1 `datafiles/colormanagement/config.ocio`, `luts/AgX_Base_sRGB.cube` (wheel 내부)
- Blender 5.2.1 glTF 익스포터 소스 `io_scene_gltf2/blender/exp/material/extensions/anisotropy.py`, `accessors.py` (wheel 내부)
- three.js r187dev: [`tonemapping_pars_fragment.glsl.js`](https://github.com/mrdoob/three.js/blob/dev/src/renderers/shaders/ShaderChunk/tonemapping_pars_fragment.glsl.js), [`GLTFLoader.js`](https://github.com/mrdoob/three.js/blob/dev/examples/jsm/loaders/GLTFLoader.js), [`BatchedMesh.js`](https://github.com/mrdoob/three.js/blob/dev/src/objects/BatchedMesh.js), [`MeshPhysicalMaterial.js`](https://github.com/mrdoob/three.js/blob/dev/src/materials/MeshPhysicalMaterial.js)
- [physically-based-api](https://github.com/AntonPalmqvist/physically-based-api) `deploy/v2/materials.json` (CC0, 2026-09-01)
- [refractiveindex.info-database](https://github.com/polyanskiy/refractiveindex.info-database): TiN/Pfluger, Ti/Palm, Ti/Johnson, Au/Johnson, Au/Babar (CC0)
- [MPFB2](https://github.com/makehumancommunity/mpfb2) `LICENSE.md`, `blender_manifest.toml`, `data/3dobjs/base.obj`
- PyPI [`bpy`](https://pypi.org/project/bpy/) 릴리스 메타데이터

**공식 문서 / 1차 자료 (B, 검색 요약 경유 포함)**
- [Blender 5.2 LTS 출시 정보](https://www.blender.org/download/releases/5-2/), [CG Channel: Blender 5.2 LTS 주요 기능](https://www.cgchannel.com/2026/07/blender-5-2-lts-is-here-discover-its-5-key-features/), [Phoronix](https://www.phoronix.com/news/Blender-5.2-Released)
- [Blender 5.0 색 관리 릴리스 노트](https://developer.blender.org/docs/release_notes/5.0/color_management/), [toodee.de: Blender 5.0 색 관리 변화](https://www.toodee.de/2026/01/big-blender-5-0-color-management-changes/)
- Blender 5.2 매뉴얼: [SDF Grid Boolean](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/volume/operations/sdf_grid_boolean.html), [SDF Grid Mean Curvature](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/volume/operations/sdf_grid_mean_curvature.html), [Bevel Modifier](https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/bevel.html), [Copy Rotation](https://docs.blender.org/manual/en/latest/animation/constraints/transform/copy_rotation.html), [Cycles Sampling](https://docs.blender.org/manual/en/latest/render/cycles/render_settings/sampling.html), [Metallic BSDF](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/metallic.html), [Principled BSDF](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html), [Modifiers Introduction](https://docs.blender.org/manual/en/latest/modeling/modifiers/introduction.html)
- Blender Studio: [Naming Conventions](https://studio.blender.org/tools/naming-conventions/introduction), [Datablock names](https://studio.blender.org/tools/naming-conventions/datablock-names), [Asset Pipeline](https://studio.blender.org/tools/addons/asset_pipeline), [버전 관리 벤치마크](https://studio.blender.org/blog/benchmarking-version-control-git-lfs-svn-mercurial/), [Charge](https://3dvf.com/en/blender-studio-unveils-charge-an-action-packed-open-movie/)
- [QuadriFlow 논문 (SGP 2018)](http://stanford.edu/~jingweih/papers/quadriflow/quadriflow.pdf), [Instant Field-Aligned Meshes](https://www.researchgate.net/publication/283334005_Instant_Field-Aligned_Meshes)
- TiN 광학: [Springer: TiN 박막 광학 특성](https://link.springer.com/article/10.1186/s40712-024-00203-6), [Purdue: TiN 플라즈모닉](https://engineering.purdue.edu/~aeb/pubs/Titanium%20nitride%20as%20a%20plasmonic%20material%20for%20visible%20and%20near-infrared%20wavelengths.pdf)

**업계 실무 (C/D)**
- 하드서피스/미드폴리: [Polycount 위키: Face weighted normals](http://wiki.polycount.com/wiki/Face_weighted_normals), [Polycount: 미드폴리 워크플로우](https://polycount.com/discussion/238054/weighted-normals-mid-poly-workflow-clarification), [Matthias Patscheider: mid-poly](https://matthias-patscheider.artstation.com/blog/ZXnP/quarry-bank-mill-3d-08-the-mid-poly-workflow), [Robert Doman: mid-poly](https://www.robertdoman.com/post/why-you-may-want-to-consider-mid-poly-modeling-smoothed-normals-workflow), [Blacksteinn: MIDPOLY 가이드](https://blacksteinn.artstation.com/blog/7o3WB/midpoly-the-ultimate-guide-with-all-working-nuances), [80.lv: 하드서피스 팁](https://80.lv/articles/hard-surface-modeling-tips-and-tricks), [HardOps 매뉴얼](https://hardops-manual.readthedocs.io/en/latest/subdivision/), [Propgon 가이드](https://propgon.com/en/hard-surface-modeling-blender-game-art-guide/)
- 트림/데칼: [Star Citizen 워크플로우 연구](https://www.artstation.com/artwork/xzdkRR), [Polycount: DECALmachine](https://polycount.com/discussion/comment/2683007)
- 리토폴로지/추출: [Blender Studio: Realistic Human](https://studio.blender.org/training/realistic-human-research/reprojection-sculpt-layers/), [Blender Artists: QuadriFlow 비교](https://blenderartists.org/t/how-good-is-quadriflow-remesh-compared-to-other-auto-retopo-solutions/1547001), [QRemeshify (QuadWild)](https://github.com/ksami/QRemeshify)
- 노멀 전사: [3DSkillUp: 곡면 음영 수정](https://3dskillup.art/how-to-fix-shading-artifacts-on-curved-surfaces-in-blender/), [Francesco Saviano](https://francescos010.artstation.com/blog/bo60w/how-to-fix-shading-artifacts-on-curved-surfaces-in-blender-quick-breakdown), [Yarsa: Normal transfer](https://blog.yarsalabs.com/normal-transfer-in-blender/)
- 텍셀 밀도: [Beyond Extent: Texel Density](https://www.beyondextent.com/deep-dives/deepdive-texeldensity), [StraySpark](https://www.strayspark.studio/blog/texture-resolution-guide-games-512-1k-2k-4k)
- 베이킹: [Polycount 위키: Texture Baking](http://wiki.polycount.com/wiki/Texture_Baking), [Ben Golus: 완벽한 노멀맵](https://bgolus.medium.com/generating-perfect-normal-maps-for-unity-f929e673fc57), [80.lv: 노멀맵 유형과 문제](https://80.lv/articles/tutorial-types-of-normal-maps-common-problems)
- 모디파이어 순서: [Braxton Wise](https://braxtonwise.com/blender-modifier-order-modifier-stack/), [Blender Artists](https://blenderartists.org/t/order-of-modifiers-in-stack/654727)
- 지오메트리 노드: [Procedural Bolts](https://superhivemarket.com/products/procedural-bolts), [Scatter on edges](https://3dbystedt.gumroad.com/l/scatter_on_edges), [StraySpark: 5.1 SDF 노드](https://www.strayspark.studio/blog/blender-51-sdf-volume-nodes-game-assets)
- 조명: [3DSkillUp: 금속 조명](https://3dskillup.art/light-metal-objects-blender/), [Lightmap: 스튜디오 조명](https://www.lightmap.co.uk/learning/blender-tutorial-02/), [Vagon: 제품 조명](https://vagon.io/blog/mastering-product-lighting-in-blender-techniques-for-stunning-3d-renders)
- 실사화: [Renderistic](https://www.renderistic.com/post/why-3d-renders-look-fake), [360 Render](https://www.360render.com/3d-rendering/why-your-3d-product-renders-look-fake-5-common-lighting-and-material-mistakes/), [Yelzkizi](https://yelzkizi.org/blender-photorealism-make-renders-real/)
- Cycles: [SuperRenders: 렌더 설정](https://superrendersfarm.com/article/blender-render-settings-optimization-guide), [Gachoki: 속도 팁](https://gachoki.com/how-to-speed-up-cycles-render-in-blender/)
- 압축: [glTF-Transform](https://github.com/donmccurdy/glTF-Transform), [utsubo: three.js 팁](https://www.utsubo.com/blog/threejs-best-practices-100-tips), [gltf-transform simplify](https://gltf-transform.dev/modules/functions/functions/simplify), [meshoptimizer](https://meshoptimizer.org/)
- 헤드리스/파이프라인: [blender-headless-bpy 교훈](https://github.com/kitapoe-ops/blender-headless-bpy), [blender-pipeline-integration](https://github.com/paulgolter/blender-pipeline-integration)
- 리깅: [Blender Artists: 판금 갑옷 리깅](https://blenderartists.org/t/how-to-rig-plate-armor-joints/629546), [Blender Artists: 기계 부품 리깅](https://blenderartists.org/t/beginner-rigging-with-armatures-for-mechanical-parts/634888)
