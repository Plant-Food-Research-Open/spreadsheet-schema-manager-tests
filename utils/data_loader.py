import json
from pathlib import Path

TEST_DATA_DIR = Path(__file__).resolve().parent.parent / "test-data"


def load_json(filename: str):
    with open(TEST_DATA_DIR / filename) as f:
        return json.load(f)


def data_file_path(filename: str) -> str:
    return str(TEST_DATA_DIR / filename)
