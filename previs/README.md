# previs — P1 preproduction (throwaway blockout tooling)

Not the production pipeline (MYOFORGE, P2+). Mood frames and analysis only. Run everything with the Blender 5.2.1
Python venv (bpy + numpy, scipy, pandas, statsmodels, pillow, matplotlib).

| file | what |
|---|---|
| `body.py` | Doha's body without bpy: MakeHuman/MPFB2 base mesh (CC0) + targets (`vendor/mpfb/targets/`), posing, ANSUR-style landmarks and measurements |
| `fit_corpus.py` | MAP fit of the mannequin to the CORPUS profile (`docs/research/corpus/`) → `wearer_fit.json` |
| `lib.py` | `load_wearer()` (fitted body in the drawing's A-pose), materials, studio helpers |
| `blueprint.py` | reads Doha's blueprint: lines, silhouette, symmetry, panel regions, PERSONA face drawn into the face oval, eye-slit variants `SLITS` (R2) → `blueprint/` (derived maps regenerate on demand) |
| `suit.py` | blueprint suit shell: registration with arm/crotch fit corrections, silhouette fit, R2 depth table + knee allowance, panel seams from the drawing, lofted PERSONA helmet with eye slits, matte worn panel material (`set_wear`, `set_slit_glow`) |
| `suit_stats.py` | builds the shell without rendering → `suit_stats.json` (area for the engineering budget) |
| **R2** `clearance.py` | skin → outer panel distance per body zone and facing → `engineering/packaging.json` (zones) + heat-map sheet |
| **R2** `modules.py` | every pre-assembled module anchored to the body and checked against the space under the shell (53/53) → `packaging.json` (modules) + space-claim sheet |
| **R2** `undersuit.py` | neural undersuit: SENIAM EMG sites from the muscle research, EEG 10-10, nodes, embroidered bus, cooling-garment runs, knit with seams, epaulettes, balaclava → `engineering/undersuit.json` + previs objects (`xray_left` for 03 NEURAL) |
| **R2** `cell.py` | the assembly cell: ceiling grid, gantry rails, energy chains, trays, duct, scanner ring, umbilical; telescopic-mast ceiling robots (`robot_ceiling`, tools: nutrunner / gripper / vacuum); periphery (bench, carts, panel rack, blueprint light table, telemetry screens drawn from the JSON) |
| **R2** `assembly.py` | build stages 0-6 on Doha: module blockouts from `packaging.json`, cuffs, harness, shell trimmed to the installed panels, kits on the carts |
| **R2** `styleframes2.py` | F01-F11: `python styleframes2.py OUT [F01 F02 ...] [--draft]` |
| **R2** `hud.py` | engineering-drawing overlay (the site's real-time layer, previewed): `python hud.py IN OUT` |
| **R2** `render_slits.py` | PERSONA eye-slit variants A / B / C |
| `props.py` | P1 floor robot arm, cables, beams |
| `macro.py`, `styleframes.py`, `material_sheet.py`, `render_persona.py` | P1 frames (superseded by R2 for the story) |
| `render_corpus.py`, `test_suit.py`, `test_undersuit.py` | check renders |
