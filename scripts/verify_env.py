"""Check that the running ArangoDB supports everything the cookbook needs, before any data code.

1. vector index + APPROX_NEAR_COSINE, and the query plan really uses the index
2. the same vector query with a FILTER in front (current-version filtering) still uses the index
   and still returns a full top-k
3. ArangoSearch view + BM25
4. how text_en tokenizes a form code such as NW-POA-2 (why the cookbook keeps codes in their own field)

Runs in a throwaway database that is dropped at the end. Exit code 0 = OK.
Run: python scripts/verify_env.py   (or: make verify)
"""
import importlib.metadata
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cookbook.db import ARANGO_URL, get_db  # noqa: E402

SCRATCH_DB = "verify_env_scratch"
DIM = 8
N_DOCS = 30  # about the size of the knowledge base


def main() -> int:
    sys_db = get_db("_system")
    sys_db.delete_database(SCRATCH_DB, ignore_missing=True)  # leftovers from an interrupted run
    db = get_db(SCRATCH_DB)
    print(f"server        {ARANGO_URL}  ArangoDB {db.version()}")
    print(f"python-arango {importlib.metadata.version('python-arango')}")
    try:
        check_vector(db)
        check_bm25(db)
        check_code_tokens(db)
    finally:
        sys_db.delete_database(SCRATCH_DB, ignore_missing=True)
    print("OK")
    return 0


def check_vector(db) -> None:
    rng = random.Random(42)
    docs = [{"_key": f"v{i}", "current": i % 2 == 0, "embedding": [rng.uniform(-1, 1) for _ in range(DIM)]}
            for i in range(N_DOCS)]
    col = db.create_collection("vec_check")
    col.import_bulk(docs)  # the index trains its clusters on existing vectors, so load first
    col.add_index({"type": "vector", "name": "vec_check_cosine", "fields": ["embedding"],
                   "params": {"metric": "cosine", "dimension": DIM, "nLists": 2, "defaultNProbe": 2}})

    plain = """
    FOR d IN vec_check
      LET s = APPROX_NEAR_COSINE(d.embedding, @qv)
      SORT s DESC LIMIT 5
      RETURN d._key
    """
    filtered = """
    FOR d IN vec_check
      FILTER d.current == true
      LET s = APPROX_NEAR_COSINE(d.embedding, @qv)
      SORT s DESC LIMIT 5
      RETURN d._key
    """
    bind = {"qv": docs[7]["embedding"]}  # v7 is not current
    for label, query, first in [("vector", plain, "v7"), ("vector+FILTER", filtered, None)]:
        keys = list(db.aql.execute(query, bind_vars=bind))
        nodes = [n["type"] for n in db.aql.explain(query, bind_vars=bind)["nodes"]]
        uses_index = "EnumerateNearVectorNode" in nodes
        print(f"{label:14} top-5 {keys}  uses vector index: {uses_index}")
        assert uses_index, f"{label}: plan does not use the vector index"
        assert len(keys) == 5, f"{label}: expected 5 results, got {len(keys)}"
        if first:
            assert keys[0] == first, f"{label}: expected {first} first"
        else:
            assert all(int(k[1:]) % 2 == 0 for k in keys), "filtered query returned a non-current doc"


def check_bm25(db) -> None:
    col = db.create_collection("text_check")
    col.import_bulk([
        {"_key": "loan", "text": "Your lender holds the title while the loan is open."},
        {"_key": "lease", "text": "The leasing company owns a leased car."},
        {"_key": "keys", "text": "Bring all keys and remotes to the appointment."},
    ])
    db.create_arangosearch_view("text_check_view", properties={
        "links": {"text_check": {"fields": {"text": {"analyzers": ["text_en"]}}}}})
    query = """
    FOR d IN text_check_view
      SEARCH ANALYZER(d.text IN TOKENS(@q, "text_en"), "text_en")
      OPTIONS { waitForSync: true }
      SORT BM25(d) DESC LIMIT 3
      RETURN d._key
    """
    for q, expected in [("who holds my title during the loan", "loan"), ("leasing company", "lease")]:
        top = list(db.aql.execute(query, bind_vars={"q": q}))
        print(f"BM25 {q!r:38} -> {top}")
        assert top and top[0] == expected, f"expected {expected} first for {q!r}"


def check_code_tokens(db) -> None:
    tokens = list(db.aql.execute('RETURN TOKENS("Use form NW-POA-2, not NW-POA-1.", "text_en")'))[0]
    print(f"text_en tokens for 'Use form NW-POA-2, not NW-POA-1.': {tokens}")
    # The two codes differ by a single token ("2" vs "1"), so plain BM25 can barely tell them apart.
    assert "nw" in tokens and "poa" in tokens


if __name__ == "__main__":
    sys.exit(main())
