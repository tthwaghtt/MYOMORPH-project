"""CORPUS-3: muscle table of the wearer for the storyboard (CORPUS chapter callouts) and the engineering bible.

Not used for the suit's panel layout (Doha 2026-10-02: panels follow the MYOMORPH-MK. 1 blueprint).
Sources (architecture data, not redistributed here):
  lower limb  Rajagopal et al. 2016 (IEEE TBME) model, PCSA from Handsfield et al. 2014 MRI volumes, sigma = 60 N/cm^2
  upper limb  MoBL-ARMS, Saul et al. 2015 (CMBBE), forces from Holzbaur et al. 2005, sigma = 140 N/cm^2 (shoulder, elbow)
              and 45 N/cm^2 (forearm, hand)
Volume = Fmax * Lopt / sigma (PCSA * optimal fibre length). Scaled to the wearer by height x mass (Handsfield 2014:
muscle volumes scale with h*m) and a leanness factor (fat-free fraction of the wearer vs a ~17 % fat reference).
Run: python muscles.py <dir with Rajagopal2016.osim, mobl41.osim> -> muscles.json
"""
import json, os, re, sys

D = sys.argv[1] if len(sys.argv) > 1 else '.'
HERE = os.path.dirname(os.path.abspath(__file__))
BC = json.load(open(os.path.join(HERE, 'bodycomp.json')))
H, M = 1.78, 65.0
FFM_FRAC = 1 - 0.11
LEAN = FFM_FRAC / 0.83

FOREARM_HAND = {'ANC', 'SUP', 'BRD', 'ECRL', 'ECRB', 'ECU', 'FCR', 'FCU', 'PL', 'PT', 'PQ', 'FDSL', 'FDSR', 'FDSM', 'FDSI', 'FDPL',
                'FDPR', 'FDPM', 'FDPI', 'EDCL', 'EDCR', 'EDCM', 'EDCI', 'EDM', 'EIP', 'EPL', 'EPB', 'FPL', 'APL'}
# (group key) -> Latin, English, Korean
NAMES = {
    'glmax': ('gluteus maximus', 'gluteus maximus', '큰볼기근'), 'glmed': ('gluteus medius', 'gluteus medius', '중간볼기근'),
    'glmin': ('gluteus minimus', 'gluteus minimus', '작은볼기근'), 'recfem': ('rectus femoris', 'rectus femoris', '넙다리곧은근'),
    'vaslat': ('vastus lateralis', 'vastus lateralis', '가쪽넓은근'), 'vasmed': ('vastus medialis', 'vastus medialis', '안쪽넓은근'),
    'vasint': ('vastus intermedius', 'vastus intermedius', '중간넓은근'), 'sart': ('sartorius', 'sartorius', '넙다리빗근'),
    'tfl': ('tensor fasciae latae', 'tensor fasciae latae', '넙다리근막긴장근'), 'grac': ('gracilis', 'gracilis', '두덩정강근'),
    'addmag': ('adductor magnus', 'adductor magnus', '큰모음근'), 'addlong': ('adductor longus', 'adductor longus', '긴모음근'),
    'addbrev': ('adductor brevis', 'adductor brevis', '짧은모음근'), 'bflh': ('biceps femoris (long)', 'biceps femoris long head', '넙다리두갈래근 긴갈래'),
    'bfsh': ('biceps femoris (short)', 'biceps femoris short head', '넙다리두갈래근 짧은갈래'), 'semimem': ('semimembranosus', 'semimembranosus', '반막근'),
    'semiten': ('semitendinosus', 'semitendinosus', '반힘줄근'), 'gasmed': ('gastrocnemius (medial)', 'gastrocnemius medial head', '장딴지근 안쪽갈래'),
    'gaslat': ('gastrocnemius (lateral)', 'gastrocnemius lateral head', '장딴지근 가쪽갈래'), 'soleus': ('soleus', 'soleus', '가자미근'),
    'tibant': ('tibialis anterior', 'tibialis anterior', '앞정강근'), 'tibpost': ('tibialis posterior', 'tibialis posterior', '뒤정강근'),
    'perlong': ('fibularis longus', 'peroneus longus', '긴종아리근'), 'perbrev': ('fibularis brevis', 'peroneus brevis', '짧은종아리근'),
    'edl': ('extensor digitorum longus', 'extensor digitorum longus', '긴발가락폄근'), 'ehl': ('extensor hallucis longus', 'extensor hallucis longus', '긴엄지폄근'),
    'fdl': ('flexor digitorum longus', 'flexor digitorum longus', '긴발가락굽힘근'), 'fhl': ('flexor hallucis longus', 'flexor hallucis longus', '긴엄지굽힘근'),
    'iliacus': ('iliacus', 'iliacus', '엉덩근'), 'psoas': ('psoas major', 'psoas major', '큰허리근'), 'piri': ('piriformis', 'piriformis', '궁둥구멍근'),
    'DELT1': ('deltoideus (pars clavicularis)', 'anterior deltoid', '어깨세모근 앞부분'), 'DELT2': ('deltoideus (pars acromialis)', 'middle deltoid', '어깨세모근 중간부분'),
    'DELT3': ('deltoideus (pars spinalis)', 'posterior deltoid', '어깨세모근 뒷부분'), 'SUPSP': ('supraspinatus', 'supraspinatus', '가시위근'),
    'INFSP': ('infraspinatus', 'infraspinatus', '가시아래근'), 'SUBSC': ('subscapularis', 'subscapularis', '어깨밑근'), 'TMIN': ('teres minor', 'teres minor', '작은원근'),
    'TMAJ': ('teres major', 'teres major', '큰원근'), 'PECM': ('pectoralis major', 'pectoralis major', '큰가슴근'), 'LAT': ('latissimus dorsi', 'latissimus dorsi', '넓은등근'),
    'CORB': ('coracobrachialis', 'coracobrachialis', '부리위팔근'), 'TRI': ('triceps brachii', 'triceps brachii', '위팔세갈래근'),
    'BIC': ('biceps brachii', 'biceps brachii', '위팔두갈래근'), 'BRA': ('brachialis', 'brachialis', '위팔근'), 'BRD': ('brachioradialis', 'brachioradialis', '위팔노근'),
    'ANC': ('anconeus', 'anconeus', '팔꿈치근'), 'SUP': ('supinator', 'supinator', '손뒤침근'), 'ECR': ('extensor carpi radialis', 'extensor carpi radialis', '노쪽손목폄근'),
    'ECU': ('extensor carpi ulnaris', 'extensor carpi ulnaris', '자쪽손목폄근'), 'FCR': ('flexor carpi radialis', 'flexor carpi radialis', '노쪽손목굽힘근'),
    'FCU': ('flexor carpi ulnaris', 'flexor carpi ulnaris', '자쪽손목굽힘근'), 'PL': ('palmaris longus', 'palmaris longus', '긴손바닥근'),
    'PT': ('pronator teres', 'pronator teres', '원엎침근'), 'PQ': ('pronator quadratus', 'pronator quadratus', '네모엎침근'),
    'FDS': ('flexor digitorum superficialis', 'flexor digitorum superficialis', '얕은손가락굽힘근'), 'FDP': ('flexor digitorum profundus', 'flexor digitorum profundus', '깊은손가락굽힘근'),
    'EDC': ('extensor digitorum', 'extensor digitorum', '손가락폄근'), 'EDM': ('extensor digiti minimi', 'extensor digiti minimi', '새끼폄근'),
    'EIP': ('extensor indicis', 'extensor indicis', '집게폄근'), 'EPL': ('extensor pollicis longus', 'extensor pollicis longus', '긴엄지폄근'),
    'EPB': ('extensor pollicis brevis', 'extensor pollicis brevis', '짧은엄지폄근'), 'FPL': ('flexor pollicis longus', 'flexor pollicis longus', '긴엄지굽힘근'),
    'APL': ('abductor pollicis longus', 'abductor pollicis longus', '긴엄지벌림근'),
}


def group_key(name, model):
    if model == 'raj':
        n = name[:-2]
        return re.sub(r'(\d+|Dist|Isch|Mid|Prox)$', '', n)
    for k in ('DELT1', 'DELT2', 'DELT3', 'PECM', 'LAT', 'TRI', 'BIC', 'FDS', 'FDP', 'EDC', 'ECR'):
        if name.startswith(k):
            return k
    return name


def muscles(path, model):
    s = open(path).read()
    out = []
    for m in re.finditer(r'<(\w*Muscle\w*) name="([^"]+)">(.*?)</\1>', s, re.S):
        name, body = m.group(2), m.group(3)
        if name == 'default' or (model == 'raj' and not name.endswith('_r')):
            continue
        g = lambda t: float(re.search(rf'<{t}>([^<]+)<', body).group(1))
        F, L, pen = g('max_isometric_force'), g('optimal_fiber_length'), g('pennation_angle_at_optimal')
        sigma = 60.0 if model == 'raj' else (45.0 if name in FOREARM_HAND else 140.0)
        out.append(dict(name=name, F=F, L=L, pen=pen, sigma=sigma, V=F * L / (sigma * 1e4) * 1e6))   # cm^3
    return out


raj = muscles(os.path.join(D, 'Rajagopal2016.osim'), 'raj')
mob = muscles(os.path.join(D, 'mobl41.osim'), 'mob')
k_low = (H * M) / (1.70 * 75.3) * LEAN          # Rajagopal generic subject (Handsfield cohort scale)
k_up = (H * M) / (1.75 * 77.0) * LEAN           # Holzbaur 50th-percentile male (assumed mass 77 kg)
table = {}
for rows, k, model in ((raj, k_low, 'raj'), (mob, k_up, 'mob')):
    for r in rows:
        key = group_key(r['name'], model)
        t = table.setdefault(key, dict(region='lower limb' if model == 'raj' else 'upper limb', V=0.0, PCSA=0.0, F=0.0, Lw=0.0,
                                       pen=0.0, parts=0, names=NAMES.get(key, (key, key, ''))))
        V = r['V'] * k; pcsa = V / (r['L'] * 100)
        t['V'] += V; t['PCSA'] += pcsa; t['F'] += pcsa * r['sigma']
        t['Lw'] += r['L'] * V; t['pen'] += r['pen'] * V; t['parts'] += 1
out = []
for key, t in table.items():
    out.append({'key': key, 'latin': t['names'][0], 'en': t['names'][1], 'ko': t['names'][2], 'region': t['region'],
                'volume_cm3_per_side': round(t['V'], 1), 'mass_g_per_side': round(t['V'] * 1.056, 0),
                'pcsa_cm2': round(t['PCSA'], 2), 'fmax_N': round(t['F'], 0), 'fibre_length_cm': round(t['Lw'] / t['V'] * 100, 1),
                'pennation_deg': round(t['pen'] / t['V'] * 57.2958, 1), 'model_parts': t['parts']})
out.sort(key=lambda r: -r['volume_cm3_per_side'])
tot_low = sum(r['volume_cm3_per_side'] for r in out if r['region'] == 'lower limb')
tot_up = sum(r['volume_cm3_per_side'] for r in out if r['region'] == 'upper limb')
res = {'scale_lower': round(k_low, 3), 'scale_upper': round(k_up, 3),
       'total_volume_cm3_per_side': {'lower_limb_and_hip': round(tot_low), 'shoulder_and_upper_limb': round(tot_up)},
       'cross_check': {'dxa_leg_lean_kg_both': BC['composition']['low']['LEG_L_kg']['mean'],
                       'model_lower_limb_muscle_kg_both': round(2 * tot_low * 1.056 / 1000, 2),
                       'smm_kim2002_kg': BC['composition']['low']['SMM_kim2002_kg']},
       'not_modelled': 'trunk muscles (pectoralis minor, trapezius, serratus anterior, rectus abdominis, obliques, erector '
                       'spinae, sternocleidomastoid): no open model reachable from this environment (SimTK blocked); the '
                       'storyboard labels them by name only',
       'muscles': out}
json.dump(res, open(os.path.join(HERE, 'muscles.json'), 'w'), indent=1, ensure_ascii=False)
print({k: v for k, v in res.items() if k != 'muscles'})
for r in out[:40]:
    print(f"{r['en']:32s} {r['ko']:14s} V {r['volume_cm3_per_side']:7.1f} cm3  PCSA {r['pcsa_cm2']:6.1f}  Lf {r['fibre_length_cm']:5.1f}  pen {r['pennation_deg']:4.1f}")
