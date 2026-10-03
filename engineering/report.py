"""Generate the human-readable engineering documents from the JSON sources (no hand-copied numbers).

docs/design/systems.md   every system and pre-assembled module: principle (system-card copy), specs, parts table
docs/design/_plan_tables.md   tables included in PLAN §5 (BOM tree, EHA sizing, packaging, sensor sites, stages)
Run after calc.py (and previs/modules.py, previs/undersuit.py): python engineering/report.py
"""
import json, os

R = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(R, '..')
J = lambda *p: json.load(open(os.path.join(ROOT, *p)))
E = J('engineering', 'engineering.json'); B = J('engineering', 'bom.json')
PK = J('engineering', 'packaging.json'); U = J('engineering', 'undersuit.json')
OUT = os.path.join(ROOT, 'docs', 'design'); os.makedirs(OUT, exist_ok=True)
fmt = lambda x: f'{x:,}' if isinstance(x, int) else (f'{x:,.2f}' if isinstance(x, float) else str(x))


def systems_md():
    L = ['# MYOMORPH-MK. 1 — 시스템 카탈로그 (부품표 v2)', '',
         f"> 자동 생성: `engineering/report.py` ← `bom.json` {B['version']}. 손으로 고치지 않는다.",
         f"> **부품 {B['total_parts']:,}개** · 사전 조립 모듈 {B['pre_assembled_modules']}개 · 질량 {B['total_mass_kg']:.2f} kg(유체 제외) · 사람이 입는 것 {B['worn_mass_kg']:.2f} kg",
         f"> 세는 법: {B['counting_rule']}", '',
         '각 모듈의 "원리"는 사이트 시스템 카드의 본문이다. 부품표는 그 카드의 분해도에 붙는 이름표다.', '',
         '## 시스템 요약', '', '| 코드 | 이름 | 한 줄 | 부품 | 질량 kg |', '|---|---|---|---:|---:|']
    for k, s in B['systems'].items():
        L.append(f"| **{k}** | {s['name_en']} · {s['name_ko']} | {s['summary_ko']} | {s.get('parts', 0):,} | {s.get('mass_kg', 0):.2f} |")
    L += ['', '## 조립 단계 (로봇 작업 순서)', '', '| 단계 | 이름 | 내용 | 부품 | 모듈 |', '|---|---|---|---:|---:|']
    for k, s in B['stages'].items():
        L.append(f"| {k} | {s['name_en']} · {s['name_ko']} | {s['what_ko']} | {s.get('parts', 0) or 0:,} | {s.get('modules', 0) or 0} |")
    ro = B['robot_ops']
    L += ['', f"로봇 작업 합계: 모듈 설치 {ro['modules_installed']}회, 판 픽 {ro['panel_picks']}회, 나사 {ro['screws_driven']:,}개, 쿼터턴 {ro['quarter_turns']}개, 커넥터 {ro['connectors_mated']}개.", '']
    for sysk, s in B['systems'].items():
        mods = [m for m in B['modules'] if m['system'] == sysk]
        if not mods: continue
        L += [f"## {sysk} — {s['name_en']} · {s['name_ko']}", '', s['summary_ko'], '']
        for m in mods:
            L += [f"### {m['id']} · {m['name_en']} · {m['name_ko']}", '']
            L += [f"- **수량** {m['units']} ({m['sides']}) · **위치** {m['zone']} · **조립 단계** {m['stage']} {B['stages'][str(m['stage'])]['name_en']}",
                  f"- **부품** 개당 {m['parts_per_unit']}개 · 합계 {m['parts_total']}개 · **질량** 개당 {m['mass_g_per_unit'] / 1000:.3f} kg · 합계 {m['mass_kg_total']:.3f} kg"]
            if m.get('envelope_mm'): L.append(f"- **외형** {' × '.join(str(round(x)) for x in m['envelope_mm'])} mm (길이 × 폭 × 두께)")
            if m['specs']: L.append('- **사양** ' + ' · '.join(f'{k} {fmt(v)}' for k, v in m['specs'].items()))
            if m['install']: L.append('- **설치** ' + ', '.join(f"{k}: {v if not isinstance(v, list) else ' → '.join(v)}" for k, v in m['install'].items()))
            if m['moves']: L.append('- **독립적 움직임** ' + ' / '.join(m['moves']))
            L += ['', f"**원리** {m['principle_ko']}", '', '| 부품 | 수량 | 재료 | g/개 |', '|---|---:|---|---:|']
            for p in m['parts']:
                L.append(f"| {p['name']} | {p['qty']} | {p['material']} | {p['g_each']:g} |")
            L.append('')
    open(os.path.join(OUT, 'systems.md'), 'w').write('\n'.join(L))


def plan_tables():
    T = []
    T += ['<!-- BOM -->', '| 시스템 | 이름 | 부품 | 질량 kg | 대표 모듈 |', '|---|---|---:|---:|---|']
    for k, s in B['systems'].items():
        mods = [m for m in B['modules'] if m['system'] == k]
        T.append(f"| **{k}** | {s['name_ko']} | {s.get('parts', 0):,} | {s.get('mass_kg', 0):.2f} | {', '.join(m['name_en'] for m in mods[:4])}{' …' if len(mods) > 4 else ''} |")
    T.append(f"| | **합계** | **{B['total_parts']:,}** | **{B['total_mass_kg']:.2f}** + 유체 {E['suit']['mass_by_system_kg'].get('fluids (coolant loop + garment, drinking 0.5 L, evaporant 0.6 L)', 0):.2f} = **{E['suit']['mass_total_kg']} kg** | |")
    T += ['', '<!-- EHA -->', '| 관절 | 위치 | 피크 토크 (자중 + 보조) | 설계 토크 | 모멘트암 | 내경 / 로드 | 스트로크 | 추력 | 모터 | 외형 L×W×T |', '|---|---|---|---:|---:|---|---:|---:|---:|---|']
    where = {'hip': '둔부 뒤(골반 아치 → 대퇴 지주)', 'knee': '대퇴 앞(→ 4절 링크)', 'ankle': '종아리 뒤(→ 아킬레스 링크 → 뒤꿈치 레버)'}
    for j, e in E['muscles_eha'].items():
        t = E['joint_torque'][j]
        T.append(f"| {j} | {where[j]} | {t['peak_Nm']} N·m ({t['suit_self_Nm']} + {t['assist_Nm']}) | {e['design_torque_Nm']} N·m | {e['moment_arm_mm']:.0f} mm | {e['bore_mm']:.0f} / {e['rod_mm']:.0f} mm | {e['stroke_mm']} mm | {e['force_kN']} kN | {e['motor_W']:.0f} W | {' × '.join(str(x) for x in e['envelope_mm'])} mm |")
    T += ['', '<!-- PACK -->', '| 모듈 | 두께 mm | 사용 가능 mm | 여유 mm | 판정 |', '|---|---:|---:|---:|---|']
    seen = set()
    for r in PK['modules']:
        key = (r['module'], r['label'])
        if key in seen: continue
        seen.add(key)
        T.append(f"| {r['label']} ({r['module']}) | {r['envelope_mm'][2]} | {r['available_T_mm']} | {r['margin_mm']:+.1f} | {'✅' if r['fits'] else '❌'} |")
    T += ['', '<!-- ZONES -->', '| 부위 | 앞 | 옆 | 뒤 | 안쪽 |', '|---|---:|---:|---:|---:|']
    for z, rec in PK['zones'].items():
        if z in ('helmet',): continue
        c = lambda f: f"{rec[f]['offs_p50']:.0f}" if f in rec else '-'
        T.append(f"| {z} | {c('front')} | {c('lateral')} | {c('back')} | {c('medial')} |")
    T += ['', '<!-- SITES -->', '| 부위 | 근육 | 종류 | 부착 규칙 | 근육 표 (최대 힘 / 섬유 길이 / 깃각) |', '|---|---|---|---|---|']
    for s in U['emg_sites']:
        if not s['site'].endswith('-L'): continue
        mt = f"{s['fmax_N']:.0f} N / {s['fibre_length_cm']} cm / {s['pennation_deg']}°" if 'fmax_N' in s else '(몸통 근육: 공개 모델 없음)'
        T.append(f"| {s['site'][:-2]} | {s['ko']} · {s['latin']} | {'HD 32 ch' if s['type'] == 'HD32' else '양극'} | {s['rule']} | {mt} |")
    T += ['', '<!-- STAGES -->', '| 단계 | 이름 | 로봇이 하는 일 | 부품 |', '|---|---|---|---:|']
    for k, s in B['stages'].items():
        T.append(f"| {k} | {s['name_en']} | {s['what_ko']} | {s.get('parts', 0) or 0:,} |")
    open(os.path.join(OUT, '_plan_tables.md'), 'w').write('\n'.join(T))
    return T


if __name__ == '__main__':
    systems_md(); plan_tables()
    print('wrote docs/design/systems.md, docs/design/_plan_tables.md')
