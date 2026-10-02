# CORPUS data scripts

Run with the Blender venv Python (numpy, scipy, pandas, statsmodels). Raw data is not committed; fetch it into a scratch dir:

| file | source (public mirror used; original host blocked in the build environment) |
|---|---|
| `DEMO_G.xpt`, `BMX_G.xpt`, `DXX_G.xpt` | NHANES 2011-2012, CDC (public domain). Mirror: `raw.githubusercontent.com/zoolutanwar/body-fat-prediction-nhanes/main/data/` |
| `ANSUR_II_MALE_Public.csv` | ANSUR II 2012, US Army (public domain). Mirror: `raw.githubusercontent.com/hfelabs-boop/AnthropometricRepo/main/data/ansur-ii-2012/` |
| `Rajagopal2016.osim` | `raw.githubusercontent.com/opensim-org/opensim-models/master/Models/Rajagopal/` |
| `mobl41.osim` | `raw.githubusercontent.com/CEINMS-RT/UpperLimbModel/master/MOBL_ARMS_41.osim` (Apache-2.0) |

```
python bodycomp.py <dir>   # -> bodycomp.json
python anthro.py <dir>/ANSUR_II_MALE_Public.csv   # -> anthro.json
python muscles.py <dir>    # -> muscles.json
python ../../../previs/fit_corpus.py   # -> previs/wearer_fit.json
```
Report: [`../wearer-anatomy.md`](../wearer-anatomy.md)
