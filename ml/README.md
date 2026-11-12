# ML environment setup

Repository: https://github.com/Coding-gurukul-8/crop-disease-detection

Status: Updated for this repository; not verified in a live Google Colab
session.

Use Python 3.10 or 3.11 for this environment. Python 3.12 and newer are not
supported because of compatibility with the pinned TensorFlow version.

## macOS and Linux (bash/zsh)

From the `ml/` directory, create and activate the virtual environment, then
install the ML dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Windows PowerShell

From the `ml/` directory, create and activate the virtual environment, then
install the ML dependencies:

```powershell
python3 -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
