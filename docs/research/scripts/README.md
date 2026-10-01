# G0 검증 스크립트

`docs/research/blender-methodology.md`의 실측 수치를 재현하는 스크립트. 모두 연구용 검증이며 프로젝트 에셋을 만들지 않는다.

## 환경

```bash
uv venv -p python3.13 .venv-bpy          # bpy 5.1+ wheel은 cp313 전용
uv pip install -p .venv-bpy/bin/python bpy==5.2.1 opencolorio colour-science
```

## 실행

| 스크립트 | 내용 |
|---|---|
| `01_capabilities.py` | 빌드 옵션, 색 관리, 모디파이어, GN 노드, glTF 옵션, 디바이스 |
| `02_cycles_smoke.py` | Cycles CPU + OIDN + AgX 렌더, .blend 저장 |
| `03_remesh_gn_smoke.py` | QuadriFlow, 복셀 리메시, GN SDF 왕복 |
| `04_bake_gltf_smoke.py` | AO 베이크, glTF(extras, tangents, meshopt 옵션) |
| `05_eevee_headless.py` | EEVEE 헤드리스 (libEGL + Mesa 필요) |
| `06_bake_render_bench.py` | 노멀 베이크 1K, 720p 128spp 벤치 |
| `07_api_facts.py`, `08_cycles_camera_light_api.py` | API 사실 확인 |
| `10_agx_three_vs_blender.py` | three.js AgX vs Blender AgX ΔE2000 |
| `11_agx_lut_accuracy.py` | log2 셰이퍼 + 3D LUT(33/48/65³) 재현 오차 |
| `12_spectral_f0.py` | n,k 분광 데이터 → F0 (선형 sRGB) |
| `13_sdf_strand_probe.py` | 곡선 → SDF → 합집합 → 메시 → 소유권 라벨 실현성 |

```bash
.venv-bpy/bin/python 01_capabilities.py
```
