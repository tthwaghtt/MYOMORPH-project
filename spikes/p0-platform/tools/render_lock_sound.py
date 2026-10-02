# Offline render of the same modal "lock" as the worklet (Ti panel 0.16 x 0.10 x 0.001 m + steel latch),
# saved as WAV + spectrogram PNG for inspection.
import numpy as np, wave
from PIL import Image
sr = 48000; E, rho, nu = 113.8e9, 4430, 0.34
def modes(a, b, h):
    D = E*h**3/(12*(1-nu**2)); k = (np.pi/2)*np.sqrt(D/(rho*h)); out = []
    for m in range(1, 5):
        for n in range(1, 5):
            f = k*((m/a)**2 + (n/b)**2)
            if f < 12000: out.append((f, 0.5/(m*n), 0.06*(800/f)**0.6))
    return out
rng = np.random.default_rng(1)
def strike(md, noise, gain, delay, life, y):
    t = np.arange(int(life*sr))/sr; s = np.zeros_like(t)
    for f, a, tau in md: s += a*np.exp(-t/tau)*np.sin(2*np.pi*f*t + rng.uniform(0, 6.28))
    nb = int(0.002*sr); s[:nb] += (rng.uniform(-1, 1, nb))*noise*(1-np.arange(nb)/nb)
    i = int(delay*sr); y[i:i+len(s)] += s*gain
pm = modes(0.16, 0.10, 0.001); print('panel modes Hz:', [round(f) for f, _, _ in sorted(pm)][:8])
y = np.zeros(int(0.9*sr))
strike(pm, 0.35, 0.5, 0.05, 0.6, y)
strike([(4200, .25, .012), (6900, .125, .012), (9100, .083, .012)], 0.15, 0.35, 0.08, 0.1, y)
y = np.tanh(y*1.2)/np.tanh(1.2); peak = np.abs(y).max()
with wave.open('build_tmp/lock.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((y/peak*0.9*32767).astype(np.int16).tobytes())
# spectrogram
n, hop = 2048, 128; win = np.hanning(n)
frames = np.array([np.abs(np.fft.rfft(win*y[i:i+n])) for i in range(0, len(y)-n, hop)])
db = 20*np.log10(frames.T + 1e-6); db = np.clip((db - db.max() + 80)/80, 0, 1)
fmax_bin = int(12000/(sr/2)*db.shape[0]); img = (np.flipud(db[:fmax_bin])*255).astype(np.uint8)
Image.fromarray(img).resize((900, 420)).save('build_tmp/lock_spectrogram.png')
env = np.abs(y); t60 = None
pk = np.argmax(env); thr = env[pk]*10**(-60/20)
print('peak at ms', round(pk/sr*1000,1), '| attack(10%->90%) ms', round((np.argmax(env>0.9*env[pk]) - np.argmax(env>0.1*env[pk]))/sr*1000, 2))
