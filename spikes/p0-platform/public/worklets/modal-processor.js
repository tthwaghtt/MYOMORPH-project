// Modal synthesis of a titanium panel "lock": a bank of exponentially damped sinusoids
// (plate bending modes) excited by a short contact transient, plus a steel latch click.
// Mode frequencies come from the main thread (computed from panel size, thickness and Ti properties).
class ModalProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.voices = [];
    this.port.onmessage = (e) => {
      if (e.data.type === 'strike') this.voices.push({ ...e.data, t: 0 });
    };
  }
  process(_inputs, outputs) {
    const out = outputs[0][0];
    const sr = sampleRate;
    out.fill(0);
    for (const v of this.voices) {
      for (let i = 0; i < out.length; i++) {
        const t = (v.t + i) / sr;
        if (t < v.delay) continue;
        const tt = t - v.delay;
        let s = 0;
        for (let m = 0; m < v.modes.length; m++) {
          const md = v.modes[m];
          s += md.a * Math.exp(-tt / md.tau) * Math.sin(2 * Math.PI * md.f * tt + md.ph);
        }
        // contact transient: 2 ms noise burst
        if (tt < 0.002) s += (Math.random() * 2 - 1) * v.noise * (1 - tt / 0.002);
        out[i] += s * v.gain;
      }
      v.t += out.length;
    }
    this.voices = this.voices.filter((v) => v.t / sr < v.delay + v.life);
    for (let ch = 1; ch < outputs[0].length; ch++) outputs[0][ch].set(out);
    return true;
  }
}
registerProcessor('modal-processor', ModalProcessor);
