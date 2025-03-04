Biventricular Lite
----

This package contains simple command line tools to load, visualise, and some quick processing of a biventricular model.

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
```

### ⚡ Run the tools

Always use `--help` from the `main.py` to see how to use the tools:
```shell
python src/main.py --help
```

If there are sub-commands, you can always call `--help` to show more information about that command
and what available options are.

For example, there is `load` command:
```shell
python src/main.py load --help
```

*and so on....*

### 🏃 Examples

<details>
<summary><b>Load a fitted model as a `Mesh` object and print its structure</b></summary>

There is an example fitted model file in the `tests` folder:
```bash
python src/main.py load tests/fitted_model.txt
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
python src/main.py plot points tests/fitted_model.txt
```
![](screenshots/plot_points.png)

</details>

<details>
<summary><b>A quick plot of surface mesh</b></summary>

```shell
python src/main.py plot mesh tests/fitted_model.txt
```
![](screenshots/plot_mesh.png)

</details>


### Developer notes

This tool uses `typer` library to create commands and subcommands. It's an amazing library that saves
your time to build an app. You can read more about Typer here: https://typer.tiangolo.com/

You can add more commands in the `main.py` file, or create sub-commands as I have made skeleton in the `biv_plots.py` file. 

*Have fun !!*
