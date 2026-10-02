# P0 환경 시험 보고 (2026-10-02)

시험 페이지: https://claude.ai/artifact/Wa1z7DTgUuU494rC1RSfVT (비공개, v4) · 소스: [`spikes/p0-platform/`](../../spikes/p0-platform/)  
결과 저장: 아티팩트 DB `p0_runs` (도하 기기에서 열 때마다 1건)

## 1. 결과 요약

| 항목 | 결과 | 근거 |
|---|---|---|
| Vite 다중 파일 아티팩트 발행 | ✅ | v1~v4 발행. 빌드 결과에서 doctype/head/body를 걷어내는 후처리 필요 (`tools/to-artifact.mjs`) |
| WebGPU (도하 Mac, Claude 앱) | ✅ | Apple M4, metal-3, Chrome 152 엔진, three.js r186 WebGPU 백엔드로 실행 |
| WebGL2 자동 폴백 | ✅ | 구버전 브라우저(Chromium 141)에서 WebGPU 실패 → 같은 코드가 WebGL2로 재시작 |
| wasm 파일 배포 | ✅ | `application/wasm`, 컴파일 성공 (Basis 트랜스코더) |
| **`.glb`, `.bin` 파일** | ⚠️ → ✅ | **아티팩트 서버가 거부하는 형식.** 허용 형식(`application/wasm`)으로 올리면 서버에서 받은 파일이 원본과 SHA-256 일치, 페이지에서 정상 로드 |
| meshopt 지오메트리 | ✅ | 메시 7개, 부품 메타데이터(extras) 7개 전달 |
| **GLB 내장 텍스처** | ❌ → 수정 | 아티팩트 CSP가 `blob:` 주소 fetch를 막아 three.js 기본 로더가 텍스처를 못 읽음 (도하 기기 v2 로그로 확인). 버퍼에서 직접 디코딩하는 플러그인(`src/gltf-noblob.js`)으로 해결, 엄격한 CSP 로컬 재현에서 통과 |
| KTX2 (UASTC) 텍스처 | ✅ (로컬) | GPU 포맷 ASTC 4×4로 트랜스코딩. 도하 기기 재확인 필요 |
| 이방성 재질 (KHR_materials_anisotropy) | ✅ | 블렌더 → glTF → three.js까지 0.55 전달 |
| Blender AgX LUT (48³) | ✅ | 884 KB 로드, 셰이퍼 + `lut3D` 파이프라인 동작 |
| 렌더 성능 | ⏳ | 자동 미리보기가 4초 만에 닫혀 미측정. 도하 기기에서 15초 이상 열어야 기록됨 |
| 소리 / 진동 / 햅틱 / 포인터 잠금 / 전체 화면 / 기울기 | ⏳ | 사용자 제스처가 필요한 시험이라 도하의 직접 실행 대기 |

## 2. 에셋 파이프라인 실측

| 단계 | 크기 |
|---|---|
| 블렌더 5.2.1 GLB (곡면 패널 + 체결부품 6개) | 119.8 KB |
| meshopt + 양자화 후 지오메트리 | 약 24 KB (−80%) |
| AO 텍스처 PNG 512² | 185.5 KB |
| → KTX2 UASTC (비색상용) | 124.9 KB |
| → KTX2 ETC1S (색상용) | 28.5 KB |
| 최종 GLB (meshopt + KTX2) | 149.0 KB |

- **KTX2 인코더 확보 (R13 해결)**: npm `basisu` 1.16.3 바이너리가 이 환경에서 동작 (`-ktx2 -uastc`).
- glTF-Transform 4.5.1의 `dedup`이 동일 체결부품 메시를 하나로 합쳤다 → 인스턴싱의 기초.

## 3. 소리 엔진 (P0.4)

- AudioWorklet 모달 합성: 티타늄 판(0.16 × 0.10 × 0.001 m) 굽힘 모드를 물성(E 113.8 GPa, ρ 4,430, ν 0.34)에서 계산 → 340, 626, 1073, 1104, 1359, 1772 Hz … + 강철 래치 클릭(4.2/6.9/9.1 kHz).
- 오프라인 렌더 분석: 어택 0.73 ms(금속 클릭 기준 2 ms 미만 충족), 저역 모드가 가장 오래 울림.
- 스펙트로그램에서 **음성 수명 절단 잡음** 발견 → 수명을 감쇠 상수의 8배로 바꿔 수정(v4).
- 340 Hz 모드가 '종소리'처럼 길게 남을 수 있음 → 아이솔레이터 감쇠값은 도하 청음 후 조정.

## 4. 플랜에 반영할 사항

1. **에셋 형식 규칙**: `.glb`/`.ktx2`/`.bin`은 `contentType: application/wasm`으로 발행한다 (오버헤드 0). 대안: base64 JSON(+33%).
2. **blob 금지 규칙**: 모든 텍스처는 버퍼에서 직접 디코딩 (`gltf-noblob` 플러그인을 P5 로더 기본값으로).
3. **WebGPU 실패 시 WebGL2 재시작**은 필수 (three.js r186 WebGPU가 구버전 브라우저의 텍스처 swizzle 미지원에서 실패).
4. 로컬 시험 서버는 아티팩트와 같은 CSP를 흉내 내야 한다 (`connect-src 'self'`).

## 5. 도하 기기 결과 (대기)

도하가 데스크톱과 휴대폰에서 시험 페이지를 열고 버튼 시험을 하면 이 절을 채운다.
