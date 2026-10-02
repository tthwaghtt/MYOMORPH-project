import sys, wave, numpy as np
from PIL import Image, ImageDraw
files = sys.argv[1:]; tiles = []
for fn in files:
    w = wave.open(fn); sr = w.getframerate(); y = np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32768.0
    n, hop = 1024, 64; win = np.hanning(n); y = np.pad(y, (0, n))
    S = np.array([np.abs(np.fft.rfft(win * y[i:i+n])) for i in range(0, len(y) - n, hop)]).T
    db = 20 * np.log10(S + 1e-7); db = np.clip((db - db.max() + 70) / 70, 0, 1)
    top = int(16000 / (sr / 2) * S.shape[0]); img = Image.fromarray((np.flipud(db[:top]) * 255).astype(np.uint8)).resize((640, 220)).convert('RGB')
    env = np.abs(y); 
    d = ImageDraw.Draw(img); d.text((6, 4), fn.split('/')[-1] + f'  {len(y)/sr*1000:.0f} ms  (0-16 kHz)', fill=(255, 200, 80))
    for k in (2, 4, 8): yy = int(220 * (1 - k * 1000 / 16000)); d.line([(0, yy), (12, yy)], fill=(120, 180, 255)); d.text((14, yy - 6), f'{k}k', fill=(120, 180, 255))
    # spectral centroid in first 120 ms
    seg = y[:int(0.12 * sr) + n]; F = np.abs(np.fft.rfft(seg)); fr = np.fft.rfftfreq(len(seg), 1 / sr)
    print(fn.split('/')[-1], 'centroid(0-120ms) Hz', int((F * fr).sum() / F.sum()), '| energy<500Hz %', round(100 * (F[fr < 500] ** 2).sum() / (F ** 2).sum(), 1))
    tiles.append(img)
out = Image.new('RGB', (640, 220 * len(tiles)))
for i, t in enumerate(tiles): out.paste(t, (0, 220 * i))
out.save('build_tmp/sfx/spectrograms.png')
