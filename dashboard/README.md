### Setup the environment

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pip-tools
pip-compile requirements.in
pip install -r requirements.txt
---
