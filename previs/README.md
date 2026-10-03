# previs — 유지하는 도구

> 2026-10-03 정리: 마네킹을 부풀린 셸로 만든 슈트 디자인(R1·R2)은 폐기했다. 슈트는 도하의 새 상세 레퍼런스에서 판 단위로 다시 만든다(`docs/INTAKE.md`). 여기 남은 것은 슈트 외형과 무관하게 계속 쓰는 도구다.

실행은 Blender 5.2.1 Python 모듈(bpy) 가상환경에서 한다. 설치 방법은 `docs/HANDOFF.md` §3.

| 파일 | 무엇 | 쓰임 |
|---|---|---|
| `body.py` | MakeHuman/MPFB2 기본 메시(CC0) + 타깃(`vendor/mpfb/`), 자세, 랜드마크, 치수 | 도하의 몸(CORPUS) |
| `fit_corpus.py` | CORPUS 치수에 마네킹을 맞춤 → `wearer_fit.json` | 도하의 몸 |
| `lib.py` | 장면, 조명, 카메라, 기본 재질, `load_wearer()`(도하 몸, 자세 지정) | 공통 |
| `materials.py` | 판 재질(무광 티타늄 + 약한 마모, TiN 골드, PVD, 아노다이즈, 바이저). 속성 계약은 파일 머리말 | 재질 방향(유지) |
| `undersuit.py` | 신경 언더슈트: SENIAM 근전도 40곳, 뇌파 10-10, 노드, 은사 배선, 냉각복, 바라클라바 → `engineering/undersuit.json` | 언더슈트(유지) |
| `cell.py` | 조립 셀: 천장 격자, 갠트리, 드래그 체인, 트레이, 덕트, 스캐너 링, 탯줄, 천장 로봇(망원 마스트 6축), 주변 장비, 모니터 | 무대(유지) |
| `props.py` | 보, 원기둥, 케이블 도우미(`cell.py`가 씀) | 공통 |
| `hud.py` | 엔지니어링 도면풍 오버레이 미리보기 | HUD 스타일(유지) |
| `reference_template.py` | 레퍼런스 작성용 도하 신체 정사영 템플릿 → `docs/reference/template/` | 레퍼런스 준비 |
| `render_corpus.py`, `test_undersuit.py` | 확인 렌더 | |
