"""Four retrieval methods, one AQL query each. Each step adds exactly one thing (D-025):

  M1  BM25            keyword search over every article version (title + text; form codes matched exactly)
  M2  Vector          nearest neighbours over every article version
  M3  Vector + filter M2, but only versions in effect on the question's `as_of` date that apply to its state
  M4  Graph: structural  M3's top hits are entry points into kb_graph; linked articles are pulled in
                          through links, shared forms, lenders and lessors (parsed from the KB)
  M5  Graph: semantic     the same walk over concepts Claude extracted (article > concept < article)
  M6  Graph: both         the same walk over both layers
M4, M5 and M6 are one query; only the edge collections it may walk differ (bind variable @edges).

M1 and M2 search every version on purpose: a plain RAG index holds every copy of a policy ever written,
which is how an assistant ends up quoting an outdated one. stale@k measures that.
"""
from functools import lru_cache

from cookbook.db import run
from cookbook.embed import embed_one
from cookbook.load import CODE_RE

K = 10           # every method returns its top 10; metrics look at the top 5 and top 10
N_ENTRY = 5      # M4: entry points into the graph (D-025, fixed before any run)
DECAY = 0.8      # M4: a neighbour inherits parent score x 0.8 per hop (D-025, fixed before any run)
MAX_DF = 10      # M5/M6: a concept named by more than 10 articles is too generic to walk through (D-030)
GRAPH_EDGES = ["links_to", "uses_form", "replaced_by", "about_lender", "about_lessor"]   # structural (M4)
SEMANTIC_EDGES = ["mentions", "relates"]                                                  # semantic (M5)
EDGE_SETS = {"M4": GRAPH_EDGES, "M5": SEMANTIC_EDGES, "M6": GRAPH_EDGES + SEMANTIC_EDGES}

M1_BM25 = """
FOR d IN kb_view
  SEARCH ANALYZER(d.title IN TOKENS(@q, "text_en") OR d.text IN TOKENS(@q, "text_en"), "text_en")
      OR ANALYZER(d.codes IN @codes, "identity")
  OPTIONS { waitForSync: true }
  LET score = BM25(d)
  SORT score DESC, d._key ASC
  LIMIT @k
  RETURN { key: d._key, score }
"""

M2_VECTOR = """
FOR d IN articles
  LET score = APPROX_NEAR_COSINE(d.embedding, @qv)
  SORT score DESC
  LIMIT @k
  RETURN { key: d._key, score }
"""

# The filter: in effect on as_of, and either for every state or for the customer's state.
# Keep it ONE FILTER statement: with two, vector search fails with ERR 1554 once the second can't be
# folded away by the optimizer (it can when @state is null). Checked on 3.12.13 (I-020).
_FRESH = """d.effective_from <= @as_of AND (d.effective_to == null OR d.effective_to >= @as_of)
      AND (@state == null OR LENGTH(d.states) == 0 OR @state IN d.states)"""

M3_VECTOR_FILTER = f"""
FOR d IN articles
  FILTER {_FRESH}
  LET score = APPROX_NEAR_COSINE(d.embedding, @qv)
  SORT score DESC
  LIMIT @k
  RETURN {{ key: d._key, score }}
"""

GRAPH_QUERY = M4_GRAPH = f"""
// 1. M3's top 10 are the candidates; the first {N_ENTRY} are entry points
LET cands = (
  FOR d IN articles
    FILTER {_FRESH}
    LET approx = APPROX_NEAR_COSINE(d.embedding, @qv)
    SORT approx DESC
    LIMIT @k
    // rank with the index, score with the exact cosine (the two differ by ~1e-8, I-019)
    RETURN {{ key: d._key, id: d._id, score: COSINE_SIMILARITY(d.embedding, @qv), via: null }}
)
// 2. walk the graph from each entry over the allowed edges (@edges): to a linked article (1 hop), or
//    through a shared form, lender, lessor or concept (2-3 hops). PRUNE stops at the first article, so no
//    path goes through one, and at a concept so generic that it would connect everything.
LET neighbours = (
  FOR entry IN SLICE(cands, 0, @n_entry)
    FOR v, edge, p IN 1..3 ANY entry.id GRAPH "kb_graph"
      PRUNE (IS_SAME_COLLECTION("articles", v) AND v._id != entry.id)
         OR (IS_SAME_COLLECTION("concepts", v) AND v.n_articles > @max_df)
      OPTIONS {{ uniqueVertices: "path", edgeCollections: @edges }}
      FILTER IS_SAME_COLLECTION("articles", v) AND v._id != entry.id
      LET d = v
      FILTER {_FRESH}
      LET own = COSINE_SIMILARITY(v.embedding, @qv)
      LET inherited = entry.score * POW(@decay, LENGTH(p.edges))
      RETURN {{ key: v._key, id: v._id, score: MAX([own, inherited]),
               via: inherited > own ? CONCAT_SEPARATOR(" > ", p.vertices[*]._key) : null }}
)
// 3. one row per article, best score wins (the graph can raise a score, never lower it)
FOR c IN APPEND(cands, neighbours)
  COLLECT key = c.key INTO grp = c
  LET best = FIRST(FOR x IN grp SORT x.score DESC, x.via ASC RETURN x)
  SORT best.score DESC, key ASC        // neighbours often inherit the same score: break ties by key (I-021)
  LIMIT @k
  RETURN {{ key, score: best.score, via: best.via }}
"""

METHODS = {
    "M1": ("BM25", M1_BM25),
    "M2": ("Vector", M2_VECTOR),
    "M3": ("Vector + filter", M3_VECTOR_FILTER),
    "M4": ("Graph: structural", M4_GRAPH),
    "M5": ("Graph: semantic", M4_GRAPH),
    "M6": ("Graph: both layers", M4_GRAPH),
}


@lru_cache(maxsize=512)
def _qv(text: str) -> tuple:
    return tuple(embed_one(text))


def bind_vars(method: str, q: dict, k: int = K) -> dict:
    """Bind variables for one question. `q` needs `question`, `as_of` and `state` (as in the gold set)."""
    if method == "M1":
        return {"q": q["question"], "codes": sorted(set(CODE_RE.findall(q["question"].upper()))), "k": k}
    b = {"qv": list(_qv(q["question"])), "k": k}
    if method != "M2":
        b.update({"as_of": q["as_of"], "state": q.get("state")})
    if method in EDGE_SETS:
        b.update({"n_entry": N_ENTRY, "decay": DECAY, "edges": EDGE_SETS[method], "max_df": MAX_DF})
    return b


def retrieve(db, method: str, q: dict, k: int = K, show: bool = False) -> list[dict]:
    """Top-k article versions for question `q`: [{key, score, (via)}], best first."""
    return run(db, METHODS[method][1], bind_vars(method, q, k), show=show)
