"""Load the knowledge base into ArangoDB: documents, edges parsed from the data, a named graph,
a search view (BM25) and a vector index. Everything is rebuilt from data/ on every run.

Run: python -m cookbook.build   (or: make load)

Nothing in the graph is written by hand. Each edge comes from something already in the data:
  links_to      article -> article   `[label](kb:<doc_id>)` in the text (to every version of the target)
  supersedes    article -> article   newer version -> the version it replaced (same doc_id)
  uses_form     article -> form      an `NW-XXX-n` code in the text
  replaced_by   form -> form         forms.replaced_by
  applies_in    article -> state     articles.states (empty = every state, so no edge)
  about_lender  article -> lender    the lender's full name in the text
  about_lessor  article -> lessor    the lessor's full name in the text
  cites         ticket -> article    tickets.cites
"""
import time
from collections import defaultdict

from cookbook.db import DB_NAME, get_db, run
from cookbook.embed import DIM, article_text, embed
from cookbook.load import load_kb, load_tickets

DOCS = ["articles", "tickets", "forms", "states", "lenders", "lessors", "stores"]
EDGES = {  # edge collection: (from collections, to collections)
    "links_to": (["articles"], ["articles"]),
    "supersedes": (["articles"], ["articles"]),
    "uses_form": (["articles"], ["forms"]),
    "replaced_by": (["forms"], ["forms"]),
    "applies_in": (["articles"], ["states"]),
    "about_lender": (["articles"], ["lenders"]),
    "about_lessor": (["articles"], ["lessors"]),
    "cites": (["tickets"], ["articles"]),
}
GRAPH = "kb_graph"
VIEW = "kb_view"
VECTOR_INDEX = "articles_embedding_cosine"
N_LISTS = 4  # tiny corpus; defaultNProbe = nLists, so every list is searched (exact top-k)


def article_edges(a: dict, kb: dict, by_doc: dict) -> dict[str, list[dict]]:
    """The outgoing edges of one article version, parsed from its own fields and text."""
    src = f"articles/{a['_key']}"
    forms = {f["_key"] for f in kb["forms"]}
    e = defaultdict(list)
    for doc_id in sorted(set(a["links"])):
        for b in by_doc.get(doc_id, []):  # a link to a missing article (a known KB issue) makes no edge
            e["links_to"].append({"_from": src, "_to": f"articles/{b['_key']}", "doc_id": doc_id})
    for code in a["codes"]:
        if code in forms:
            e["uses_form"].append({"_from": src, "_to": f"forms/{code}"})
    for s in a["states"]:
        e["applies_in"].append({"_from": src, "_to": f"states/{s}"})
    for l in kb["lenders"]:
        if l["name"] in a["text"]:
            e["about_lender"].append({"_from": src, "_to": f"lenders/{l['_key']}"})
    for l in kb["lessors"]:
        if l["name"] in a["text"]:
            e["about_lessor"].append({"_from": src, "_to": f"lessors/{l['_key']}"})
    return e


def parse_edges(kb: dict, tickets: list[dict]) -> dict[str, list[dict]]:
    """Every edge, parsed from the data. Returns {edge collection: [edge documents]}."""
    arts = kb["articles"]
    by_doc = defaultdict(list)
    for a in arts:
        by_doc[a["doc_id"]].append(a)
    e = defaultdict(list)
    for a in arts:
        for name, rows in article_edges(a, kb, by_doc).items():
            e[name] += rows
    for versions in by_doc.values():
        versions.sort(key=lambda v: v["effective_from"])
        for old, new in zip(versions, versions[1:]):
            e["supersedes"].append({"_from": f"articles/{new['_key']}", "_to": f"articles/{old['_key']}",
                                    "on": new["effective_from"]})
    for f in kb["forms"]:
        if f.get("replaced_by"):
            e["replaced_by"].append({"_from": f"forms/{f['_key']}", "_to": f"forms/{f['replaced_by']}"})
    for t in tickets:
        for k in t["cites"]:
            e["cites"].append({"_from": f"tickets/{t['_key']}", "_to": f"articles/{k}"})
    return dict(e)


def build(db_name: str = DB_NAME, verbose: bool = True) -> dict:
    """Drop and rebuild database `db_name` from data/. Returns the counts."""
    t0 = time.time()
    sys_db = get_db("_system")
    sys_db.delete_database(db_name, ignore_missing=True)
    db = get_db(db_name)
    kb, tickets = load_kb(), load_tickets()

    # 1. documents (articles carry their embedding; the vector index trains on existing vectors, so load first)
    arts = [dict(a) for a in kb["articles"]]
    for a, v in zip(arts, embed([article_text(a) for a in arts])):
        a["embedding"] = v
        a.pop("links", None)  # links become edges; `codes` stays (the exact-match search field)
    rows = {"articles": arts, "tickets": tickets, **{k: kb[k] for k in ["forms", "states", "lenders", "lessors", "stores"]}}
    for name in DOCS:
        db.create_collection(name).import_bulk(rows[name], on_duplicate="error")

    # 2. edges and the named graph
    edges = parse_edges(kb, tickets)
    for name in EDGES:
        db.create_collection(name, edge=True).import_bulk(edges.get(name, []), on_duplicate="error")
    db.create_graph(GRAPH, edge_definitions=[
        {"edge_collection": name, "from_vertex_collections": f, "to_vertex_collections": t}
        for name, (f, t) in EDGES.items()])

    # 3. search view: BM25 over title and text; codes matched exactly (text_en splits NW-POA-2, I-002)
    db.create_arangosearch_view(VIEW, properties={"links": {"articles": {"fields": {
        "title": {"analyzers": ["text_en"]},
        "text": {"analyzers": ["text_en"]},
        "codes": {"analyzers": ["identity"]},
    }}}})

    # 4. vector index on the article embeddings
    db.collection("articles").add_index({"type": "vector", "name": VECTOR_INDEX, "fields": ["embedding"],
                                         "params": {"metric": "cosine", "dimension": DIM,
                                                    "nLists": N_LISTS, "defaultNProbe": N_LISTS}})
    counts = {n: db.collection(n).count() for n in DOCS + list(EDGES)}
    if verbose:
        print(f"database {db_name}: built in {time.time() - t0:.1f}s")
        for n in DOCS + list(EDGES):
            print(f"  {n:13} {counts[n]:4}  {'edge' if n in EDGES else 'document'}")
        print(f"  graph {GRAPH}, view {VIEW}, vector index {VECTOR_INDEX} (nLists={N_LISTS})\n")
    return counts


SHOW_KB_PROBLEMS = """
FOR a IN articles
  FILTER a.effective_to == null                      // current versions only
  FOR f IN 1 OUTBOUND a uses_form
    FILTER f.status == "retired"
    FILTER f.replaced_by NOT IN a.codes              // cites the old form without its replacement
    RETURN {article: a._key, cites: f._key, replaced_by: f.replaced_by}
"""


def main() -> None:
    build()
    db = get_db()
    print("Graph query: current articles that still point readers at a retired form")
    for r in run(db, SHOW_KB_PROBLEMS):
        print("  ", r)


if __name__ == "__main__":
    main()
