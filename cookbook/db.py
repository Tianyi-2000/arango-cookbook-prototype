"""Connect to ArangoDB and run AQL so that every query is printed before it runs.

Settings come from the environment (or a .env file); the defaults match docker-compose.yml.
"""
import os

from arango import ArangoClient
from dotenv import load_dotenv

load_dotenv()

ARANGO_URL = os.getenv("ARANGO_URL", "http://127.0.0.1:8535")
ARANGO_USER = os.getenv("ARANGO_USER", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD", "cookbook-local-only")
DB_NAME = os.getenv("ARANGO_DB", "northwind_kb")


def get_db(name: str = DB_NAME):
    """Return a handle to database `name`, creating it on first use (the root user can)."""
    client = ArangoClient(hosts=ARANGO_URL)
    sys_db = client.db("_system", username=ARANGO_USER, password=ARANGO_PASSWORD)
    if name != "_system" and not sys_db.has_database(name):
        sys_db.create_database(name)
    return client.db(name, username=ARANGO_USER, password=ARANGO_PASSWORD)


def run(db, aql: str, bind_vars: dict | None = None, show: bool = True) -> list:
    """Print the AQL (and its bind variables, with long vectors shortened), run it, return the rows."""
    if show:
        print("AQL>", aql.strip().replace("\n", "\n     "))
        if bind_vars:
            shown = {k: (f"<{len(v)} floats>" if isinstance(v, list) and len(v) > 8 else v)
                     for k, v in bind_vars.items()}
            print("bind:", shown)
    return list(db.aql.execute(aql, bind_vars=bind_vars or {}))
