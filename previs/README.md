# previs — P1 preproduction (throwaway blockout tooling)

Not the production pipeline (MYOFORGE, P2+). Mood frames and analysis only. Run everything with the Blender 5.2.1
Python venv (bpy + numpy, scipy, pandas, statsmodels, pillow).

| file | what |
|---|---|
| `body.py` | Doha's body without bpy: MakeHuman/MPFB2 base mesh (CC0) + targets (`vendor/mpfb/targets/`), posing, ANSUR-style landmarks and measurements |
| `fit_corpus.py` | MAP fit of the mannequin to the CORPUS profile (`docs/research/corpus/`) → `wearer_fit.json` |
| `lib.py` | `load_wearer()` (fitted body in the drawing's A-pose), materials, studio helpers |
| `blueprint.py` | reads Doha's blueprint: lines, silhouette, symmetry, panel regions, PERSONA face drawn into the face oval → `blueprint/` (derived maps regenerate on demand) |
| `suit.py` | blueprint suit shell: registration with arm/crotch fit corrections, silhouette fit, panel seams from the drawing, lofted PERSONA helmet, temporal hubs, panel materials |
| `suit_stats.py` | builds the shell without rendering → `suit_stats.json` (area for the engineering budget) |
| `props.py` | yellow 6-axis robot arm with nutrunner, blockout internals (frame, cylinders, HPU, batteries) |
| `macro.py` | clean macro set pieces (panel with rolled hem, Torx fastener, etch, heat-tinted louvres) |
| `styleframes.py` | SF1–SF8: `python styleframes.py OUT [SF1 SF2 ...]` |
| `render_corpus.py`, `test_suit.py` | check renders |
