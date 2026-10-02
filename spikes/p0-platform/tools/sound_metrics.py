# Objective checks: tonality (spectral peak prominence) and roughness proxy (envelope modulation energy 20-150 Hz).
import sys, wave, numpy as np
def load(fn):
    w = wave.open(fn); return np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32768.0, w.getframerate()
for fn in sys.argv[1:]:
    y, sr = load(fn)
    act = np.abs(y) > 0.02 * np.abs(y).max(); seg = y[np.argmax(act): len(y) - np.argmax(act[::-1])]
    F = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))); fr = np.fft.rfftfreq(len(seg), 1 / sr)
    band = (fr > 300) & (fr < 4000)
    # tonality: peak vs median magnitude within 300-4000 Hz (dB)
    tonal = 20 * np.log10(F[band].max() / (np.median(F[band]) + 1e-12))
    # roughness proxy: modulation spectrum of the 1-6 kHz envelope
    from numpy.fft import rfft, rfftfreq
    k = int(sr * 0.002); env = np.convolve(np.abs(seg), np.ones(k) / k, 'same')[::8]; esr = sr / 8
    M = np.abs(rfft((env - env.mean()) * np.hanning(len(env)))); mf = rfftfreq(len(env), 1 / esr)
    rough = M[(mf > 20) & (mf < 150)].sum() / (M[(mf > 1) & (mf < 400)].sum() + 1e-12)
    print(f"{fn.split('/')[-1]:22s} tonal peak {tonal:5.1f} dB | roughness band share {rough:.2f}")
