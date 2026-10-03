"""Engineering-drawing HUD (the site's L2 overlay, previewed in post). Its per-frame layouts were written for the retired
R2 styleframes F01-F11; the style (leader lines, mono labels, numbers from the JSON) carries over to the new frames.

Thin leader lines, Geist-like mono labels (DejaVu Sans Mono here), Korean in WenQuanYi Zen Hei; every number from the
JSON sources. `python hud.py IN_DIR OUT_DIR` -> OUT_DIR/F??_*.webp
"""
import os, sys, json, math
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
J = lambda *p: json.load(open(os.path.join(ROOT, *p)))
MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
KO = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
INK = (214, 222, 228); DIM = (140, 152, 160); CY = (120, 214, 240); OR = (255, 122, 48)


def F(size, ko=False):
    try:
        return ImageFont.truetype(KO if ko else MONO, size)
    except Exception:
        return ImageFont.load_default()


class Hud:
    def __init__(self, path):
        self.im = Image.open(path).convert('RGB'); self.W, self.H = self.im.size
        self.s = self.W / 1920.0
        self.d = ImageDraw.Draw(self.im, 'RGBA')

    def px(self, x, y):
        return (x * self.W, y * self.H)

    def text(self, xy, t, size=15, col=INK, ko=False, anchor='la'):
        self.d.text(xy, t, font=F(int(size * self.s), ko), fill=col, anchor=anchor)

    def line(self, pts, col=INK, w=1):
        self.d.line(pts, fill=col, width=max(1, int(w * self.s)))

    def dot(self, xy, r=3, col=INK, ring=False):
        r *= self.s; x, y = xy
        if ring:
            self.d.ellipse([x - r, y - r, x + r, y + r], outline=col, width=max(1, int(self.s)))
        else:
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=col)

    def block(self, xy, title, lines, w=520):
        x, y = xy; s = self.s
        self.d.rectangle([x, y, x + w * s, y + (34 + 22 * len(lines)) * s], fill=(8, 10, 12, 170), outline=(90, 100, 108, 255), width=1)
        self.text((x + 12 * s, y + 9 * s), title, 16, INK)
        for k, l in enumerate(lines):
            self.text((x + 12 * s, y + (34 + 22 * k) * s), l, 13, DIM)

    def callout(self, p, label_xy, text, sub=None, col=INK, sub_ko=False):
        x0, y0 = p; x1, y1 = label_xy
        elbow = (x1 - (14 * self.s if x1 > x0 else -14 * self.s), y1)
        self.dot((x0, y0), 3, col); self.line([(x0, y0), elbow, (x1, y1)], col)
        anchor = 'ls' if x1 > x0 else 'rs'
        self.text((x1 + (4 if x1 > x0 else -4) * self.s, y1 - 3 * self.s), text, 13, col, anchor=anchor)
        if sub:
            self.text((x1 + (4 if x1 > x0 else -4) * self.s, y1 + 15 * self.s), sub, 13, DIM, ko=sub_ko, anchor=anchor)

    def save(self, out):
        self.im.save(out, quality=88)


def spread(ys, gap):
    """push label y positions apart so they do not overlap (keeps order)."""
    o = sorted(range(len(ys)), key=lambda i: ys[i]); out = list(ys)
    for a, b in zip(o, o[1:]):
        if out[b] - out[a] < gap: out[b] = out[a] + gap
    return out


def run(src, dst):
    os.makedirs(dst, exist_ok=True)
    E = J('engineering', 'engineering.json'); B = J('engineering', 'bom.json'); U = J('engineering', 'undersuit.json')
    P = B['total_parts']
    for fn in sorted(os.listdir(src)):
        if not fn.endswith('.png'): continue
        name = fn[:-4]; h = Hud(os.path.join(src, fn)); s = h.s; W, H = h.W, h.H
        mk_path = os.path.join(src, name + '_marks.json'); marks = json.load(open(mk_path)) if os.path.exists(mk_path) else []
        if name.startswith('F01'):
            h.text((W / 2, H * 0.90), 'HOLD TO ENGAGE', 15, INK, anchor='ma'); h.text((W / 2, H * 0.925), '길게 눌러 기동', 13, DIM, ko=True, anchor='ma')
            h.text((W / 2, H * 0.965), f'PARTS STAGED 0000 / {P:,}', 12, DIM, anchor='ma')
        elif name.startswith('F02'):
            h.text((28 * s, 26 * s), 'CELL 01 · BUILD 0001 · OPERATOR: DOHA', 14, DIM)
            h.text((W - 28 * s, H - 30 * s), f'PARTS STAGED {P:,} / {P:,}', 13, DIM, anchor='ra')
        elif name.startswith('F03'):
            h.block((28 * s, 26 * s), 'NEURAL WEAR', [f"EMG {E['neural']['emg_channels']} ch · {U['totals']['hd_grids']} HD grids + {U['totals']['bipolar']} bipolar · 2048 Hz",
                                                        f"EEG {E['neural']['eeg_channels']} ch dry · 10-10 · intent + error",
                                                        f"COOLING {E['thermal']['lcg_tube_m']} m · {E['thermal']['lcg_circuits']} circuits · {E['thermal']['lcg_flow_L_min']} L/min",
                                                        f"DECODE {E['neural']['latency_total_ms']} ms  <  human EMD 30-100 ms"], w=560)
            vis = [m for m in marks if m['type'] == 'HD32' and m.get('facing', 1) > 0.15 and 0.05 < m['x'] < 0.95 and 0.05 < m['y'] < 0.97]
            right = [m for m in vis if m['x'] >= 0.5]; left = [m for m in vis if m['x'] < 0.5]
            for grp, xl in ((right, 0.80), (left, 0.20)):
                ys = spread([m['y'] for m in grp], 0.052)
                for m, yy in zip(sorted(grp, key=lambda m: m['y']), sorted(ys)):
                    h.callout(h.px(m['x'], m['y']), h.px(xl, yy), m['label'], f"{m['ko']}  ·  HD 32 ch", CY if xl > 0.5 else INK, sub_ko=True)
            ee = [m for m in marks if m['type'] == 'EEG']
            if ee:
                top = min(ee, key=lambda m: m['y'])
                h.callout(h.px(top['x'], top['y']), h.px(0.64, 0.06), 'EEG CROWN · 32 DRY ELECTRODES', '바라클라바 속 · 운동피질 위 촘촘', CY, sub_ko=True)
        elif name.startswith('F04'):
            st = B['stages']['2']; h.block((28 * s, 26 * s), 'STAGE 2 · SKELETON', [f"{st['parts']} parts · {st['modules']} modules · carbon struts, crossed four-bar knees", 'leg frames -> pelvis -> spine + harness -> arms, 10 cuffs'], w=600)
        elif name.startswith('F05'):
            e = E['muscles_eha']['knee']
            h.block((28 * s, 26 * s), 'STAGE 3 · MUSCLE', [f"MUS-EHA-KNEE-R · bore {e['bore_mm']:.0f} mm · {e['force_kN']} kN · 21 MPa", f"motor {e['motor_W']:.0f} W · stroke {e['stroke_mm']} mm · free-swing bypass"], w=600)
        elif name.startswith('F06'):
            mod = next(x for x in B['modules'] if x['id'] == 'MUS-EHA-KNEE')
            h.block((28 * s, 26 * s), f"SYSTEM CARD · {mod['name_en']}", [f"{mod['id']} · {mod['parts_per_unit']} parts · {mod['mass_g_per_unit'] / 1000:.2f} kg · 21 MPa",
                                                                        '모터가 정방향이면 늘어나고, 역방향이면 줄어든다.'], w=640)
            h.text((40 * s, 26 * s + 34 * s + 22 * s * 1), '', 13)
            top = [m for m in marks if m['y'] < 0.5]; bot = [m for m in marks if m['y'] >= 0.5]
            for k, m in enumerate(sorted(top, key=lambda m: m['x'])):
                yy = 0.30 - (k % 2) * 0.05
                h.callout(h.px(m['x'], m['y']), h.px(m['x'] + 0.012, yy), f"{m['k']}  {m['label']}", None, INK)
            for k, m in enumerate(sorted(bot, key=lambda m: m['x'])):
                yy = 0.80 + (k % 2) * 0.05
                h.callout(h.px(m['x'], m['y']), h.px(m['x'] + 0.012, yy), f"{m['k']}  {m['label']}", None, INK if 'ASSEMBLED' not in m['label'] else OR)
        elif name.startswith('F07'):
            st = B['stages']['4']; h.block((28 * s, 26 * s), 'STAGE 4 · SYSTEMS', [f"{st['parts']} parts · spine core, PDU, buffer, membrane gills, fans, harness", 'battery panel R sliding on its rails · 4 quarter-turns'], w=640)
        elif name.startswith('F08'):
            frac = 0.40; st = B['stages']
            done = sum((st[k].get('parts') or 0) for k in ('0', '1', '2', '3', '4')) + frac * (st['5'].get('parts') or 0)
            mass = sum((st[k].get('mass_kg') or 0) for k in ('0', '1', '2', '3', '4')) + frac * (st['5'].get('mass_kg') or 0)
            sc_ = int(frac * B['robot_ops']['screws_driven'])
            h.d.rectangle([0, H - 54 * s, W, H], fill=(8, 10, 12, 190))
            h.text((28 * s, H - 36 * s), f"PARTS {int(done):,} / {P:,}     SCREWS {sc_:,} / {B['robot_ops']['screws_driven']:,}     MASS {mass:.1f} / {E['suit']['mass_total_kg']} kg", 15, INK)
            h.text((W - 28 * s, H - 36 * s), 'MYOMORPH · 477 PANELS', 15, DIM, anchor='ra')
        elif name.startswith('F09'):
            h.text((28 * s, H - 40 * s), 'PERSONA · EYE SLITS 7 mm · 11° · CAMERAS BEHIND', 14, DIM)
        elif name.startswith('F10'):
            h.text((W - 28 * s, 26 * s), f"UNTETHERED · BATT 100 % · {E['battery']['energy_kWh']} kWh · {E['battery']['runtime_mixed_h']} h", 14, DIM, anchor='ra')
        elif name.startswith('F11'):
            h.block((28 * s, 22 * s), f"KNOLL · {P:,} PARTS", [f"{B['pre_assembled_modules']} modules · 13 systems · {E['suit']['mass_total_kg']} kg"], w=420)
            for m in marks:
                h.text((m['x'] * W, m['y'] * H - 22 * s), f"{m['label']}", 13, INK, anchor='ls')
                h.text((m['x'] * W, m['y'] * H - 4 * s), f"{m['ko']} · {m['n']:,}", 12, DIM, ko=True, anchor='ls')
        h.save(os.path.join(dst, name + '.webp'))
        print('hud', name)


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])
