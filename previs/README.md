# previs — P1 storyboard styleframes (throwaway blockout tooling)

Not the production pipeline (MYOFORGE, P2+). Mood frames only.

- `lib.py` — wearer mannequin (MakeHuman/MPFB2 CC0 base mesh + macro and shape targets, arms posed to 17° with rig skin weights, 178 cm), measurement (`measure()`), materials, studio helpers.
- `suit.py` — previs suit shell (Voronoi panels on skin-weight segments, seam field cut in Geometry Nodes), helmet blockout, joint rings.
- `fit_wearer.py` — fits shape-target weights to requested girths (2026-10-02: waist +5 cm, shoulder −4 cm).
- `vendor/mpfb/` — CC0 assets from MPFB2 (`LICENSE.ASSETS.md`): base mesh, targets, derived weight arrays. `weights.default.json` is not committed (regenerable from the MPFB2 repo).

Run with the Blender 5.2.1 Python venv: `.venv-bpy/bin/python previs/compare_mannequin.py after`.
