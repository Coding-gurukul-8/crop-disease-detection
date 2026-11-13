# ML Environment Setup

All ML work (preprocessing, training, evaluation) runs inside an isolated virtual environment at `ml/venv/`, so package versions stay identical across teammates and match what the FastAPI backend later loads.

## Required Python version

**Python 3.10 or 3.11 only.** Do **not** use Python 3.12 or newer: the pinned TensorFlow range (`>=2.15,<2.17`) does not install reliably on them (Python 3.13 has no compatible TensorFlow wheels at all).

Check your version first:

```bash
python3 --version   # must print 3.10.x or 3.11.x
```

If it prints something else, install Python 3.11 (e.g. `brew install python@3.11` on macOS, `sudo apt install python3.11 python3.11-venv` on Ubuntu, or the installer from python.org on Windows) and use `python3.11` in place of `python3` below.

## macOS / Linux (bash / zsh)

Run from inside the `ml/` folder:

```bash
cd ml
python3 -m venv venv
source venv/bin/activate
python --version        # confirm 3.10.x or 3.11.x inside the venv
pip install --upgrade pip
pip install -r requirements.txt
```

## Windows (PowerShell)

Run from inside the `ml\` folder:

```powershell
cd ml
python3 -m venv venv
venv\Scripts\Activate.ps1
python --version
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Notes for Windows:

- If `python3` is not recognised, use the Python launcher instead: `py -3.11 -m venv venv`.
- If activation fails with "running scripts is disabled", run this once, then activate again:
  `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

## Verify the install

With the venv active:

```bash
python -c "import tensorflow as tf; print(tf.__version__)"
```

## Leaving / recreating the environment

- Leave the venv: `deactivate`
- Start clean: delete `ml/venv/` and repeat the steps above. `ml/venv/` is git-ignored and must never be committed.

## Training on Google Colab instead

Open `notebooks/00_colab_setup.ipynb` in Colab and edit the single `PROJECT_PATH` line at the top. Colab provides its own Python and GPU, so no venv is needed there.

## Dataset download and exploration

1. Create a Kaggle API token (Kaggle account -> Settings -> API -> **Create New Token**) and save it as `~/.kaggle/kaggle.json` (`chmod 600` on macOS/Linux). It is git-ignored; never commit it.
2. With the venv active, from the project root:

```bash
python ml/dataset/download_dataset.py           # downloads + extracts into ml/dataset/raw/<class_name>/*.jpg
python ml/dataset/download_dataset.py --force   # wipe raw/ and re-download
```

Running it again without `--force` does nothing if `raw/` already has data. On any failure it prints an actionable error, exits non-zero and leaves `raw/` untouched.

3. Open `ml/notebooks/01_dataset_exploration.ipynb` (start Jupyter from inside the project folder, or open it in Colab from Drive). It prints the per-class counts table, flags empty classes, and saves `ml/evaluation/class_distribution.png`. Its path setup comes from `ml/notebooks/project_setup.py`.
