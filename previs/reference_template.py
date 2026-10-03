"""Drawing template for Doha's next MYOMORPH-MK. 1 reference (2026-10-03).

Doha's own body (CORPUS fit, previs/wearer_fit.json) in orthographic views at 1 unit = 1 mm: landmark heights, joint
centres, the minimum outer-surface line (skin + 12 mm) and the depth the internal modules need (current engineering
estimate). It is an underlay that keeps the drawing's proportions and fit right - not a design.

Sheets (SVG with layers + PNG):
  1 body   FRONT / SIDE (left side, figure faces left, arms removed - their outline dashed) / BACK
  2 limbs  left arm straightened (FRONT / BACK / OUTER / INNER), left leg INNER side, TOP of the whole body
  3 head   FRONT / SIDE / BACK / TOP
Template colours (gray, teal, magenta, orange) stay clear of the drawing colours in docs/reference/GUIDE.md.

python reference_template.py OUTDIR
"""
import os, sys, math, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
import contourpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib, body

ARM_DEG, ELBOW_DEG = 30.0, 5.0         # recommended reference pose: upper arms 30 deg from vertical, elbows straight
INSOLE = 0.035                          # boot sole: the body stands 35 mm above the floor line
ENVELOPE = 0.012                        # minimum skin -> outer panel surface (layer stack 8.6 mm + margin)
HEAD_STEMS = ('head', 'jaw', 'eye', 'levator', 'oculi', 'orbicularis', 'oris', 'risorius', 'special', 'temporalis', 'tongue')
COL = dict(body='#e6ebf2', body_line='#8c99aa', ghost='#9aa6b5', env='#009c9c', land='#c9cfd8', land_txt='#7d8794',
           joint='#c0399f', zone='#e07b00', text='#333a44', grid='#eef1f5', grid5='#dde2ea')
FONT_KR = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
# depth the internal modules need, skin -> outer surface (module thickness + 8.6 mm layer stack), R2 engineering estimate
ZONES = {
    'back_upper': ('등 상부 ≥ 27 mm', '배터리 등판 + 척추 연산부'),
    'back_lumbar': ('허리 뒤 ≥ 31 mm', '배전 · 버퍼 · 냉각 펌프'),
    'glute': ('엉덩이 뒤 ≥ 27 mm', '고관절 근육 (EHA)'),
    'thigh_front': ('허벅지 앞 ≥ 29 mm', '무릎 근육 (EHA)'),
    'calf_back': ('종아리 뒤 ≥ 27 mm', '발목 근육 (EHA)'),
    'knee_side': ('무릎 바깥 ≥ 15 mm', '교차 4절 링크 + 디스크'),
    'hip_side': ('고관절 옆 ≥ 35 mm', '고관절 3축'),
    'flank': ('옆구리 ≥ 23 mm', '막 아가미 + 루버 팬'),
    'chest': ('가슴 ≥ 21 mm', '비상 해제 손잡이 · 생체 센서'),
    'shoulder_top': ('어깨 위 ≥ 39 mm', '어깨 중력보상 스프링'),
    'neck_side': ('목 옆 ≥ 23 mm', '팬 박스 (흡·배기)'),
    'upperarm_back': ('위팔 뒤 ≥ 23 mm', '팔꿈치 힘줄 구동'),
    'forearm_palm': ('전완 손바닥 쪽 ≥ 25 mm', '보조 손 (접힘)'),
    'forearm_out': ('오른 전완 바깥 ≥ 37 mm / 왼 ≥ 31 mm', '툴 베이 / 교체 포트'),
}


# ---------------------------------------------------------------- drawing primitives -> SVG + PNG
class Sheet:
    def __init__(self, w, h, title):
        self.w, self.h, self.title = w, h, title
        self.layers = {}          # name -> list of primitives

    def add(self, layer, kind, **kw):
        self.layers.setdefault(layer, []).append((kind, kw))

    def svg(self, path):
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
               f'width="{self.w}mm" height="{self.h}mm" viewBox="0 0 {self.w} {self.h}">',
               f'<title>{self.title}</title>', f'<rect width="{self.w}" height="{self.h}" fill="#ffffff"/>']
        for li, (name, prims) in enumerate(self.layers.items()):
            lid = 'L%02d' % li
            out.append(f'<g id="{lid}" inkscape:groupmode="layer" inkscape:label="{name}">')
            for kind, kw in prims:
                out.append(self._svg_prim(kind, kw))
            out.append('</g>')
        out.append('</svg>')
        open(path, 'w').write('\n'.join(out))

    @staticmethod
    def _svg_prim(kind, kw):
        f = lambda p: ' '.join(f'{x:.1f},{y:.1f}' for x, y in p)
        if kind == 'poly':
            return f'<polygon points="{f(kw["pts"])}" fill="{kw.get("fill", "none")}" stroke="{kw.get("stroke", "none")}" stroke-width="{kw.get("sw", 0)}"/>'
        if kind == 'line':
            dash = f' stroke-dasharray="{kw["dash"]}"' if kw.get('dash') else ''
            return f'<polyline points="{f(kw["pts"])}" fill="none" stroke="{kw["stroke"]}" stroke-width="{kw["sw"]}"{dash} stroke-linecap="round" stroke-linejoin="round"/>'
        if kind == 'text':
            anchor = {'l': 'start', 'm': 'middle', 'r': 'end'}[kw.get('anchor', 'l')]
            return (f'<text x="{kw["x"]:.1f}" y="{kw["y"]:.1f}" font-size="{kw["size"]}" fill="{kw.get("fill", COL["text"])}" '
                    f'text-anchor="{anchor}" font-family="Noto Sans KR, Apple SD Gothic Neo, Malgun Gothic, sans-serif">{kw["t"]}</text>')
        raise ValueError(kind)

    def png(self, path, ppm=2.0):
        W, H = int(self.w * ppm), int(self.h * ppm)
        im = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(im)
        fonts = {}
        def font(sz):
            k = max(8, int(sz * ppm))
            if k not in fonts: fonts[k] = ImageFont.truetype(FONT_KR, k)
            return fonts[k]
        for name, prims in self.layers.items():
            for kind, kw in prims:
                if kind == 'poly':
                    d.polygon([(x * ppm, y * ppm) for x, y in kw['pts']], fill=kw.get('fill') if kw.get('fill', 'none') != 'none' else None,
                              outline=kw.get('stroke') if kw.get('stroke', 'none') != 'none' else None,
                              width=max(1, int(kw.get('sw', 0) * ppm)))
                elif kind == 'line':
                    pts = [(x * ppm, y * ppm) for x, y in kw['pts']]; w = max(1, int(round(kw['sw'] * ppm)))
                    if kw.get('dash'):
                        on, off = [float(v) * ppm for v in kw['dash'].split(',')]
                        for a, b in zip(pts[:-1], pts[1:]):
                            L = math.dist(a, b); t = 0.0
                            while t < L:
                                t1 = min(t + on, L); u0, u1 = t / L, t1 / L
                                d.line([(a[0] + (b[0] - a[0]) * u0, a[1] + (b[1] - a[1]) * u0), (a[0] + (b[0] - a[0]) * u1, a[1] + (b[1] - a[1]) * u1)], fill=kw['stroke'], width=w)
                                t = t1 + off
                    else:
                        d.line(pts, fill=kw['stroke'], width=w, joint='curve')
                elif kind == 'text':
                    anc = {'l': 'ls', 'm': 'ms', 'r': 'rs'}[kw.get('anchor', 'l')]
                    d.text((kw['x'] * ppm, kw['y'] * ppm), kw['t'], font=font(kw['size']), fill=kw.get('fill', COL['text']), anchor=anc)
        im.save(path, optimize=True)


def rdp(P, eps):
    """Ramer-Douglas-Peucker polyline simplification (closed polylines keep their ends)."""
    if len(P) < 3: return P
    a, b = P[0], P[-1]; ab = b - a; n = np.linalg.norm(ab)
    d = np.abs(ab[0] * (P[:, 1] - a[1]) - ab[1] * (P[:, 0] - a[0])) / n if n > 1e-9 else np.linalg.norm(P - a, axis=1)
    i = int(np.argmax(d))
    if d[i] > eps:
        return np.vstack([rdp(P[:i + 1], eps)[:-1], rdp(P[i:], eps)])
    return np.vstack([a, b])


# ---------------------------------------------------------------- body
def load():
    V, F, J = lib.load_wearer(height_m=1.78, arm_deg=ARM_DEG, elbow_deg=ELBOW_DEG)
    V = V + [0, 0, INSOLE]; J = {k: v + [0, 0, INSOLE] for k, v in J.items()}
    B = body.Base.get(); M = body.region_masks(B)
    W = B.Wbody; names = B.bone_names
    wsum = lambda stems: W[:, [i for i, n in enumerate(names) if n.split('.')[0].rstrip('0123456789-') in stems]].sum(1)
    head = wsum(HEAD_STEMS) > 0.5; neck = (wsum(('neck',)) > 0.5) & ~head
    armL = B.arm_w['l'][B.body] > 0.5; armR = B.arm_w['r'][B.body] > 0.5
    legL = M['leg_l'][B.body]; legR = M['leg_r'][B.body]
    part = np.full(len(V), 'torso', object)
    part[neck] = 'neck'; part[head] = 'head'; part[legL] = 'leg_l'; part[legR] = 'leg_r'; part[armL] = 'arm_l'; part[armR] = 'arm_r'
    F = [list(f) for f in F]
    fpart = np.array([part[f[0]] for f in F])
    return V, F, J, part, fpart


PROJ = {  # view -> (u, v) in mm, v down the sheet
    'front': lambda P: (P[:, 0] * 1000, -P[:, 2] * 1000),
    'back': lambda P: (-P[:, 0] * 1000, -P[:, 2] * 1000),
    'side': lambda P: (P[:, 1] * 1000, -P[:, 2] * 1000),          # left side, the figure faces left
    'inner': lambda P: (-P[:, 1] * 1000, -P[:, 2] * 1000),        # seen from the wearer's right (left leg's inner side)
    'top': lambda P: (P[:, 0] * 1000, -P[:, 1] * 1000),           # from above, front edge toward the bottom
}


class View:
    """one orthographic view: mask raster (2 px/mm) of selected faces, contours, envelope, helpers."""
    PX = 2.0

    def __init__(self, V, F, sel_faces, proj, ox, oy, pad=40):
        u, v = proj(V)
        idx = np.unique(np.concatenate([F[i] for i in sel_faces]))
        self.u0, self.u1 = u[idx].min() - pad, u[idx].max() + pad
        self.v0, self.v1 = v[idx].min() - pad, v[idx].max() + pad
        W = int((self.u1 - self.u0) * self.PX) + 1; H = int((self.v1 - self.v0) * self.PX) + 1
        im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
        for i in sel_faces:
            f = F[i]; d.polygon([((u[k] - self.u0) * self.PX, (v[k] - self.v0) * self.PX) for k in f], fill=255)
        self.mask = np.asarray(im) > 0
        self.mask = ndi.binary_closing(self.mask, iterations=2)
        self.ox, self.oy = ox - self.u0, oy - self.v0             # sheet offset: sheet = (u + ox, v + oy)
        self.u, self.v = u, v

    def sheet(self, u, v):
        return u + self.ox, v + self.oy

    def contours(self, mask=None, eps=0.3):
        m = self.mask if mask is None else mask
        gen = contourpy.contour_generator(z=np.pad(m, 1).astype(float))
        out = []
        for seg in gen.lines(0.5):
            P = (seg - 1) / self.PX + [self.u0, self.v0]
            P = rdp(P, eps)
            if len(P) > 3:
                out.append([(x + self.ox, y + self.oy) for x, y in P])
        return out

    def envelope(self, mm):
        dist = ndi.distance_transform_edt(~self.mask)
        return self.contours(dist <= mm * self.PX, eps=0.5)

    def edge(self, v_mm, which):
        """sheet point on the silhouette at height v (sheet-free coords): which = 'min' or 'max' u."""
        r = int(round((v_mm - self.v0) * self.PX)); r = min(max(r, 0), self.mask.shape[0] - 1)
        xs = np.nonzero(self.mask[r])[0]
        if not len(xs): return None
        x = xs.min() if which == 'min' else xs.max()
        return self.sheet(x / self.PX + self.u0, v_mm)

    def top_edge(self, u_mm):
        c = int(round((u_mm - self.u0) * self.PX)); c = min(max(c, 0), self.mask.shape[1] - 1)
        ys = np.nonzero(self.mask[:, c])[0]
        if not len(ys): return None
        return self.sheet(u_mm, ys.min() / self.PX + self.v0)


def draw_view(S, vw, label, ghost=None, env=True):
    for P in vw.contours():
        S.add('01 body (Doha, CORPUS fit) - lock', 'poly', pts=P, fill=COL['body'], stroke=COL['body_line'], sw=0.8)
    if ghost is not None:
        for P in vw.contours(ghost):
            S.add('01 body (Doha, CORPUS fit) - lock', 'line', pts=P + [P[0]], stroke=COL['ghost'], sw=0.8, dash='6,5')
    if env:
        for P in vw.envelope(ENVELOPE * 1000):
            S.add('02 min outer surface (skin + 12 mm) - lock', 'line', pts=P + [P[0]], stroke=COL['env'], sw=1.0, dash='10,6')
    cx = (vw.u0 + vw.u1) / 2 + vw.ox
    S.add('06 labels - lock', 'text', x=cx, y=vw.v0 + vw.oy - 10, t=label, size=26, anchor='m')


def joint_mark(S, x, y, r=9):
    S.add('04 joint centres - lock', 'line', pts=[(x - r, y), (x + r, y)], stroke=COL['joint'], sw=1.0)
    S.add('04 joint centres - lock', 'line', pts=[(x, y - r), (x, y + r)], stroke=COL['joint'], sw=1.0)


def zone(S, p, dx, dy, key, anchor='l'):
    if p is None: return
    t1, t2 = ZONES[key]; x, y = p
    S.add('05 depth needed by internal modules (estimate) - lock', 'line', pts=[(x, y), (x + dx, y + dy)], stroke=COL['zone'], sw=1.0)
    S.add('05 depth needed by internal modules (estimate) - lock', 'line', pts=[(x - 3, y - 3), (x + 3, y + 3)], stroke=COL['zone'], sw=1.4)
    S.add('05 depth needed by internal modules (estimate) - lock', 'text', x=x + dx + (6 if anchor == 'l' else -6), y=y + dy - 4, t=t1, size=17, fill=COL['zone'], anchor=anchor)
    S.add('05 depth needed by internal modules (estimate) - lock', 'text', x=x + dx + (6 if anchor == 'l' else -6), y=y + dy + 16, t=t2, size=13, fill=COL['zone'], anchor=anchor)


def empty_draw_layers(S):
    for name in ('10 DRAW panel edges - black thick', '11 DRAW creases inside a panel - blue thin',
                 '12 DRAW hidden or overlapped edges - red dashed', '13 DRAW features (screws, vents, lights) - green',
                 '14 DRAW panel IDs (optional)', '15 DRAW notes'):
        S.layers.setdefault(name, [])


def grid(S, x0, y0, x1, y1):
    for k, x in enumerate(np.arange(x0, x1 + 1, 10)):
        S.add('00 grid 10 mm - lock', 'line', pts=[(x, y0), (x, y1)], stroke=COL['grid5'] if k % 10 == 0 else COL['grid'], sw=0.5 if k % 10 == 0 else 0.3)
    for k, y in enumerate(np.arange(y1, y0 - 1, -10)):
        S.add('00 grid 10 mm - lock', 'line', pts=[(x0, y), (x1, y)], stroke=COL['grid5'] if k % 10 == 0 else COL['grid'], sw=0.5 if k % 10 == 0 else 0.3)


def title_block(S, x, y, lines):
    S.add('06 labels - lock', 'text', x=x, y=y, t=lines[0], size=40)
    for i, t in enumerate(lines[1:]):
        S.add('06 labels - lock', 'text', x=x, y=y + 34 + i * 26, t=t, size=19, fill=COL['land_txt'])


# ---------------------------------------------------------------- sheets
def pick(V, sel, z, axis, sign, band=0.012):
    """3D point of the selected vertices at height z with the extreme coordinate along axis (sign +1 max, -1 min)."""
    m = sel & (np.abs(V[:, 2] - z) < band)
    if not m.any(): return None
    k = np.nonzero(m)[0][np.argmax(sign * V[m, axis])]
    return V[k]


def at(vw, proj, p):
    if p is None: return None
    u, v = proj(np.asarray(p)[None]); return vw.sheet(u[0], v[0])


def sheet_body(V, F, J, part, fpart, meas, out):
    allf = np.arange(len(F))
    noarm = np.nonzero(~np.isin(fpart, ['arm_l', 'arm_r']))[0]
    arms = np.nonzero(np.isin(fpart, ['arm_l', 'arm_r']))[0]
    floor_y = 2280.0                                                # sheet y of the floor line (z = 0)
    S = Sheet(3400, 2400, 'MYOMORPH-MK. 1 reference template - body')
    # front | side | back on one floor line (z = 0 -> floor_y); landmark labels in the left margin
    vF = View(V, F, allf, PROJ['front'], 360, 0); vF.oy = floor_y
    vS = View(V, F, noarm, PROJ['side'], 0, 0); vS.oy = floor_y; vS.ox += (vF.u1 + vF.ox + 190) - (vS.u0 + vS.ox)
    vB = View(V, F, allf, PROJ['back'], 0, 0); vB.oy = floor_y; vB.ox += (vS.u1 + vS.ox + 190) - (vB.u0 + vB.ox)
    x_end = vB.u1 + vB.ox + 40
    S.w = int(x_end + 70)
    grid(S, 60, 300, x_end, floor_y + 10)
    gh = View(V, F, arms, PROJ['side'], 0, 0)                       # arms, dashed, on the side view's frame
    ghost = np.zeros_like(vS.mask)
    du = int(round((gh.u0 - vS.u0) * View.PX)); dv = int(round((gh.v0 - vS.v0) * View.PX))
    ys, xs = np.nonzero(gh.mask); ys = ys + dv; xs = xs + du
    ok = (ys >= 0) & (ys < ghost.shape[0]) & (xs >= 0) & (xs < ghost.shape[1]); ghost[ys[ok], xs[ok]] = True
    draw_view(S, vF, 'FRONT 정면'); draw_view(S, vS, 'SIDE 측면 (왼쪽 · 팔 없이, 팔 위치는 점선)', ghost=ghost)
    draw_view(S, vB, 'BACK 후면')
    L = [('바닥 floor', 0.0), ('발바닥 insole (부츠 밑창 위)', INSOLE),
         ('복사뼈 ankle', meas['lateralmalleolusheight'] / 1000 + INSOLE), ('무릎 knee (mid-patella)', meas['kneeheightmidpatella'] / 1000 + INSOLE),
         ('가랑이 crotch', meas['crotchheight'] / 1000 + INSOLE), ('손목 wrist (30° A자세)', J['joint-l-hand'][2]),
         ('허리 waist (배꼽 높이)', meas['waistheightomphalion'] / 1000 + INSOLE), ('팔꿈치 elbow', J['joint-l-elbow'][2]),
         ('가슴 chest', meas['chestheight'] / 1000 + INSOLE), ('어깨 acromion', meas['acromialheight'] / 1000 + INSOLE),
         ('턱 chin', float(V[part == 'head', 2].min())), ('눈 eyes', J['joint-l-eye'][2]), ('정수리 crown', float(V[:, 2].max()))]
    for name, z in L:
        y = floor_y - z * 1000
        S.add('03 landmark heights - lock', 'line', pts=[(60, y), (x_end, y)], stroke=COL['land'], sw=0.6)
        S.add('03 landmark heights - lock', 'text', x=64, y=y - 4, t=f'{name}  {z * 1000:,.0f}', size=14, fill=COL['land_txt'])
    for side in 'lr':
        for jn in ('shoulder', 'elbow', 'hand', 'upper-leg', 'knee', 'ankle'):
            p = J[f'joint-{side}-{jn}']
            joint_mark(S, *at(vF, PROJ['front'], p)); joint_mark(S, *at(vB, PROJ['back'], p))
    for jn in ('upper-leg', 'knee', 'ankle'):
        joint_mark(S, *at(vS, PROJ['side'], J[f'joint-l-{jn}']))
    trunk = np.isin(part, ['torso', 'neck', 'leg_l', 'leg_r']); torso = part == 'torso'; legL = part == 'leg_l'
    Pside = lambda z, sgn, sel=trunk: at(vS, PROJ['side'], pick(V, sel, z, 1, sgn))
    zone(S, Pside(1.32, +1), 80, -30, 'back_upper'); zone(S, Pside(1.08, +1), 90, 0, 'back_lumbar')
    zone(S, Pside(0.93, +1), 90, 25, 'glute'); zone(S, Pside(0.70, -1), -80, 0, 'thigh_front', 'r')
    zone(S, Pside(0.36, +1), 90, 0, 'calf_back'); zone(S, Pside(1.36, -1, torso), -80, -15, 'chest', 'r')
    shx = abs(J['joint-l-shoulder'][0]); upper = np.isin(part, ['torso', 'neck', 'arm_l', 'arm_r'])
    def top_at(x0):
        m = upper & (np.abs(V[:, 0] - x0) < 0.008)
        return V[np.nonzero(m)[0][np.argmax(V[m, 2])]] if m.any() else None
    sgnL = 1 if J['joint-l-shoulder'][0] > 0 else -1
    zone(S, at(vF, PROJ['front'], top_at(sgnL * (shx + 0.02))), 70, -70, 'shoulder_top' if sgnL * vF.sheet(1, 0)[0] > 0 else 'shoulder_top')
    zone(S, at(vF, PROJ['front'], top_at(-sgnL * shx * 0.45)), -70, -110, 'neck_side', 'r')
    zone(S, at(vB, PROJ['back'], pick(V, torso, 1.12, 0, sgnL)), -60, 50, 'flank', 'r')
    zone(S, at(vB, PROJ['back'], pick(V, legL, 0.92, 0, sgnL)), -70, 40, 'hip_side', 'r')
    zone(S, at(vB, PROJ['back'], pick(V, legL, J['joint-l-knee'][2], 0, sgnL)), -70, 10, 'knee_side', 'r')
    title_block(S, 360, 110, ['MYOMORPH-MK. 1 · 레퍼런스 템플릿 1 / 3 · 몸',
                 f'도하의 몸 (CORPUS 피팅) · 1 단위 = 1 mm · 팔 {ARM_DEG:.0f}° A자세, 팔꿈치 곧게 · 발바닥 {INSOLE * 1000:.0f} mm 위 (부츠 밑창)',
                 '청록 점선 = 판 바깥면 최소선 (피부 + 12 mm) · 자홍 + = 관절 중심 · 주황 = 내부 장치가 필요한 깊이 (공학 추정, 잠정)',
                 '잠긴 레이어(00~06) 위, 10~15 레이어에 그린다 · 그리는 규칙: docs/reference/GUIDE.md'])
    empty_draw_layers(S)
    S.svg(os.path.join(out, 'template_1_body.svg')); S.png(os.path.join(out, 'template_1_body.png'), ppm=2.0)


def fpart_vertices(F, fpart, name):
    return np.unique(np.concatenate([F[i] for i in np.nonzero(fpart == name)[0]]))


def straighten_arm(V, J, side):
    """rotate the arm about the shoulder in the frontal plane until shoulder -> wrist points straight down."""
    S_ = J[f'joint-{side}-shoulder']; a = J[f'joint-{side}-hand'] - S_
    ang = math.atan2(a[0], -a[2])                                    # deviation from straight down, frontal plane
    c, s = math.cos(-ang), math.sin(-ang)
    R = np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]])
    P = (V - S_) @ R.T + S_
    if abs((R @ a)[0]) > 1e-3:                                       # wrong sign convention: rotate the other way
        R = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]); P = (V - S_) @ R.T + S_
    return P, R


def sheet_limbs(V, F, J, fpart, out):
    S = Sheet(2500, 1950, 'MYOMORPH-MK. 1 reference template - limbs')
    legf = np.nonzero(fpart == 'leg_l')[0]
    Pa, R = straighten_arm(V, J, 'l')
    zs_ = (J['joint-l-shoulder'] - J['joint-l-shoulder'])[2] + J['joint-l-shoulder'][2] + 0.045     # cut 45 mm above the joint
    armf = np.array([i for i in np.nonzero(fpart == 'arm_l')[0] if Pa[F[i], 2].mean() < zs_])
    jl = {k: (J[f'joint-l-{k}'] - J['joint-l-shoulder']) @ R.T + J['joint-l-shoulder'] for k in ('shoulder', 'elbow', 'hand')}
    ytop = 260.0
    views = [('front', 'ARM FRONT 팔 앞'), ('back', 'ARM BACK 팔 뒤'), ('side', 'ARM OUTER 팔 바깥'), ('inner', 'ARM INNER 팔 안쪽')]
    x = 120.0; vws = {}
    for key, label in views:
        vw = View(Pa, F, armf, PROJ[key], 0, 0)
        vw.ox += x - (vw.u0 + vw.ox); vw.oy = ytop - vw.v0
        draw_view(S, vw, label); vws[key] = vw
        for k, p in jl.items():
            u, v = PROJ[key](p[None]); joint_mark(S, *vw.sheet(u[0], v[0]))
        x = vw.u1 + vw.ox + 190
    el = jl['elbow'][2]; sh = jl['shoulder'][2]; wr = jl['hand'][2]
    zv = lambda z: -z * 1000
    zone(S, vws['back'].edge(zv((sh + el) / 2), 'max'), 60, 0, 'upperarm_back')
    zone(S, vws['inner'].edge(zv((el + wr) / 2), 'max'), 60, 30, 'forearm_palm')
    zone(S, vws['side'].edge(zv((el + wr) / 2), 'min'), -60, 40, 'forearm_out', 'r')
    vl = View(V, F, legf, PROJ['inner'], 0, 0); vl.ox += x + 40 - (vl.u0 + vl.ox); vl.oy = 1880 - vl.v1
    draw_view(S, vl, 'LEG INNER 다리 안쪽 (왼다리, 오른쪽에서 봄)')
    for jn in ('upper-leg', 'knee', 'ankle'):
        u, v = PROJ['inner'](J[f'joint-l-{jn}'][None]); joint_mark(S, *vl.sheet(u[0], v[0]))
    allf = np.arange(len(F))
    vT = View(V, F, allf, PROJ['top'], 0, 0); vT.ox += 120 - (vT.u0 + vT.ox); vT.oy = 1880 - vT.v1
    draw_view(S, vT, 'TOP 윗면 (몸 전체, 앞쪽이 아래)')
    S.w = int(max(vl.u1 + vl.ox, vT.u1 + vT.ox) + 260)
    grid(S, 60, 60, S.w - 30, 1900)
    title_block(S, 120, 120, ['MYOMORPH-MK. 1 · 레퍼런스 템플릿 2 / 3 · 팔, 다리 안쪽, 윗면',
                 '왼팔을 어깨 중심으로 돌려 곧게 세웠다 (A자세 팔과 같은 길이, 어깨 관절 45 mm 위에서 자름) · 1 단위 = 1 mm · 청록 점선 = 피부 + 12 mm',
                 '오른팔은 왼팔의 거울상으로 본다 (툴 베이는 오른 전완, 교체 포트는 왼 전완)'])
    empty_draw_layers(S)
    S.svg(os.path.join(out, 'template_2_limbs.svg')); S.png(os.path.join(out, 'template_2_limbs.png'), ppm=2.0)


def sheet_head(V, F, J, fpart, out):
    S = Sheet(1250, 560, 'MYOMORPH-MK. 1 reference template - head')
    zc = float(V[np.unique(np.concatenate([F[i] for i in np.nonzero(fpart == 'head')[0]])), 2].min())
    hf = np.array([i for i in np.nonzero(np.isin(fpart, ['head', 'neck']))[0] if V[F[i], 2].mean() > zc - 0.075])
    x = 70.0; ybase = 500.0; vws = {}
    for key, label in (('front', 'HEAD FRONT'), ('side', 'HEAD SIDE (왼쪽)'), ('back', 'HEAD BACK'), ('top', 'HEAD TOP (앞쪽이 아래)')):
        vw = View(V, F, hf, PROJ[key], 0, 0, pad=25)
        vw.ox += x - (vw.u0 + vw.ox); vw.oy = ybase - vw.v1
        draw_view(S, vw, label); vws[key] = vw
        x = vw.u1 + vw.ox + 60
    eye = J['joint-l-eye'][2]
    for key in ('front', 'side', 'back'):
        vw = vws[key]; y = vw.sheet(0, -eye * 1000)[1]
        S.add('03 landmark heights - lock', 'line', pts=[(vw.u0 + vw.ox, y), (vw.u1 + vw.ox, y)], stroke=COL['land'], sw=0.6)
    S.add('06 labels - lock', 'text', x=70, y=60, t='MYOMORPH-MK. 1 · 레퍼런스 템플릿 3 / 3 · 머리 (헬멧 · PERSONA)', size=26)
    S.add('06 labels - lock', 'text', x=70, y=88, t='청록 점선 = 피부 + 12 mm (헬멧 안쪽 최소 여유, 권장 20~25 mm, 코끝 앞 12 mm 이상) · 회색 선 = 눈높이 · 목 회전 ±70°, 숙임 40° / 젖힘 45°', size=13, fill=COL['land_txt'])
    empty_draw_layers(S)
    S.svg(os.path.join(out, 'template_3_head.svg')); S.png(os.path.join(out, 'template_3_head.png'), ppm=4.0)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    meas = {k: v['fit_mm'] for k, v in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wearer_fit.json')))['measurements'].items()}
    V, F, J, part, fpart = load()
    sheet_body(V, F, J, part, fpart, meas, out)
    sheet_limbs(V, F, J, fpart, out)
    sheet_head(V, F, J, fpart, out)
    print('wrote', sorted(os.listdir(out)))
