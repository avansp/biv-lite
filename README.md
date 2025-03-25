Biventricular Lite
----

<p align="center">
<img height="300" src="screenshots/biv_banner.png">
</p>

This package contains simple command line tools to load, visualise, and some quick processing of a biventricular model.

Note: there is no fitting functionality in this package. The input is a fitting model, where there are 388 control points in 3D format. An example of a fitted model is given in `tests/fitted_model.txt`.

### 🚀 Installation

```bash
# clone project
git clone https://github.kcl.ac.uk/YoungLab/biv-lite
cd biv-lite

# create conda environment
conda create -n biv-lite python=3.11
conda activate biv-lite

# install requirements
pip install -r requirements.txt

# install the tool
pip install --editable .
```

### 🫀 Using the `BivMesh` class

The `BivMesh` is the main class for the biventricular modelling and it only accepts a fitted model, which consists of 388 control points. An example of a fitted model is given in [tests/fitted_model.txt](tests/fitted_model.txt) file.

#### Load a fitted model and print some of its properties
```python
from biv_lite import BivMesh

biv = BivMesh.from_fitted_model("tests/fitted_model.txt")
print(biv)
```

will output
```text
<BivMesh> object
  Label: biv_mesh
  Control points: (388, 3), dtype: float64
  Vertices: (5810, 3), dtype: float64
  Faces: (11920, 3), dtype: int64
  Components: AORTA_VALVE, AORTA_VALVE_CUT, LV_ENDOCARDIAL, LV_EPICARDIAL, MITRAL_VALVE, MITRAL_VALVE_CUT, PULMONARY_VALVE, PULMONARY_VALVE_CUT, RV_EPICARDIAL, RV_FREEWALL, RV_SEPTUM, THRU_WALL, TRICUSPID_VALVE, TRICUSPID_VALVE_CUT
```

More examples and explanations are given in the [notebooks folder](notebooks).

### 🏃🏽 CLI tools

There are some tools that you can call directly from the command-line interface, either using `main.py` file:
```shell
python src/biv_lite/main.py --help
```

or `biv-lite` command:
```shell
biv-lite --help
```

Some CLI examples

<details>
<summary><b>Load a fitted model as a `Mesh` object and print its structure</b></summary>

There is an example fitted model file in the `tests` folder:
```bash
biv-lite load tests/fitted_model.txt
```

Output:
```text
There are 388 control points
After subdivision, here is the mesh structure:
{
    'name': 'Mesh',
    'number_of_nodes': 5810,
    'node_basis': 4,
    'nodes': [(5810, 3), dtype('float64')],
    'number_of_elements': 11760,
    'elements': [(11760, 3), dtype('int64')],
    'materials': [(11760,), dtype('float64')]
}
```

</details>


<details>
<summary><b>A quick plot of surface points</b></summary>

```shell
biv-lite plot points tests/fitted_model.txt
```
![](screenshots/plot_points.png)

</details>

<details>
<summary><b>A quick plot of surface mesh</b></summary>

```shell
biv-lite plot mesh tests/fitted_model.txt
```
![](screenshots/plot_mesh.png)

</details>

<details>
<summary><b>A quick plot of the LV & RV meshes</b></summary>

```shell
biv-lite plot biv tests/fitted_model.txt
```
![](screenshots/plot_biv.png)

</details>

<details>
<summary><b>Volume and mass calculation</b></summary>

```shell
biv-lite volumes tests/fitted_model.txt
```

```text
2025-03-06 19:33:39.918 | INFO     | biv_measures:compute_volume:22 - Computing volumes and masses of tests/fitted_model.txt
{
    'lv_vol': 253.280039260176,
    'rv_vol': 260.47160066078743,
    'lv_epi_vol': 469.0292227955365,
    'rv_epi_vol': 324.1358505950869,
    'lv_mass': 226.53664271212853,
    'rv_mass': 66.84746243101442
}
```

</details>

### 🕹️ Developer notes

This tool uses `typer` library to create commands and subcommands. It's an amazing library that saves
your time to build an app. You can read more about Typer here: https://typer.tiangolo.com/

You can add more commands in the `main.py` file, or create sub-commands as I have made skeleton in the `biv_plots.py` file. 

*Have fun !!*
