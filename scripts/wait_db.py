"""Wait until ArangoDB answers (after `docker compose up -d` it needs a few seconds). Exit 1 after 90 s."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cookbook.db import ARANGO_URL, get_db  # noqa: E402

for i in range(90):
    try:
        print("ArangoDB", get_db("_system").version(), "at", ARANGO_URL)
        sys.exit(0)
    except Exception:  # noqa: BLE001 - not up yet
        if i == 0:
            print("waiting for ArangoDB at", ARANGO_URL, "...")
        time.sleep(1)
sys.exit(f"ArangoDB didn't answer at {ARANGO_URL} within 90 s (docker compose ps / docker compose logs)")
