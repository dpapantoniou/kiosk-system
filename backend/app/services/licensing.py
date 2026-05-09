import json
from pathlib import Path

CONFIG_PATH = Path("backend/config/licensing_config.json")

def load_licensing_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)