"""M9's tools (D-034): four generic graph operations, each a fixed AQL template. The model picks a tool and its
arguments; it never writes AQL. Every call is printed with its AQL when `show=True`.

  search_help_center(query)            M8 (wide -> narrow) for the question's date and state, top 5 articles
  read_article(doc_id)                 the version in effect, its links (missing targets marked), forms, states
  lookup(kind, name)                   one form / lender / lessor / state, its record, and the current articles
                                       connected to it in kb_graph; for a form, what it replaced or was replaced by
  list_records(kind, field?, value?)   every record of a kind, optionally where one field equals a value

M9s gets only search_help_center, so M9 - M9s is what the graph tools add beyond searching more than once.
"""
import json

from cookbook import retrieve as R
from cookbook.db import run
from cookbook.entities import item_key
from cookbook.load import LINK_RE, plain

KINDS = {"form": "forms", "lender": "lenders", "lessor": "lessors", "state": "states"}
FRESH = R._FRESH

SEARCH = {
    "name": "search_help_center",
    "description": "Search the help center. Returns up to 5 articles in effect today that apply to the customer's "
                   "state, best first: key, title, text. Search again with other words if the first results miss something.",
    "input_schema": {"type": "object", "properties": {"query": {"type": "string", "description": "What to look for, in plain words."}},
                     "required": ["query"], "additionalProperties": False},
}
READ = {
    "name": "read_article",
    "description": "Read one help-center article by its doc_id (a key without the '__version' suffix, e.g. 'co_owners'). "
                   "Returns the version in effect today: title, text, the articles it links to (with a flag if the target "
                   "doesn't exist), the forms it names (with each form's status) and the states it applies to.",
    "input_schema": {"type": "object", "properties": {"doc_id": {"type": "string"}}, "required": ["doc_id"], "additionalProperties": False},
}
LOOKUP = {
    "name": "lookup",
    "description": "Look up one record by name or code: a form (e.g. 'NW-POA-2'), a lender, a leasing company (kind 'lessor') "
                   "or a state. Returns the record's fields, the current help-center articles connected to it in the "
                   "knowledge graph, and for a form the form it replaced or was replaced by.",
    "input_schema": {"type": "object", "properties": {"kind": {"type": "string", "enum": list(KINDS)}, "name": {"type": "string"}},
                     "required": ["kind", "name"], "additionalProperties": False},
}
LIST = {
    "name": "list_records",
    "description": "List every record of one kind (form, lender, lessor = leasing company, state) with all its fields. "
                   "Optionally keep only records where one top-level field equals a value, e.g. field 'status', value "
                   "'retired' (values compare as text, case-insensitive: 'false' matches false).",
    "input_schema": {"type": "object", "properties": {"kind": {"type": "string", "enum": list(KINDS)},
                                                      "field": {"type": "string"}, "value": {"type": "string"}},
                     "required": ["kind"], "additionalProperties": False},
}
GRAPH_TOOLS = [SEARCH, READ, LOOKUP, LIST]   # M9
SEARCH_ONLY = [SEARCH]                       # M9s

READ_AQL = f"""
FOR d IN articles
  FILTER d.doc_id == @doc_id AND {FRESH}
  LET links = (FOR v IN 1 OUTBOUND d links_to FILTER v.effective_to == null OR v.effective_to >= @as_of RETURN DISTINCT v.doc_id)
  LET forms = (FOR f IN 1 OUTBOUND d uses_form RETURN {{ code: f._key, name: f.name, status: f.status, replaced_by: f.replaced_by }})
  RETURN {{ key: d._key, title: d.title, text: d.text, linked_doc_ids: links, forms, states: d.states }}
"""
LOOKUP_AQL = """
LET r = DOCUMENT(@id)
LET articles = (
  FOR v IN 1 INBOUND r uses_form, about_lender, about_lessor, applies_in
    FILTER v.effective_from <= @as_of AND (v.effective_to == null OR v.effective_to >= @as_of)
    SORT v._key
    RETURN DISTINCT { key: v._key, title: v.title })
LET replaced_by = (FOR f IN 1 OUTBOUND r replaced_by RETURN f._key)
LET replaces = (FOR f IN 1 INBOUND r replaced_by RETURN f._key)
RETURN MERGE(UNSET(r, "_id", "_rev"), { current_articles: articles, replaced_by_form: replaced_by, replaces_form: replaces })
"""
LIST_AQL = """
FOR r IN @@coll
  FILTER @field == null OR LOWER(TO_STRING(r[@field])) == LOWER(@value)
  SORT r._key
  RETURN UNSET(r, "_id", "_rev")
"""


AUTHOR_NOTES = {"lenders"}  # lender `note`s are the data author's remarks ("close to Harbor Leasing on purpose"): hidden


def _dump(x) -> str:
    return json.dumps(x, ensure_ascii=False)


def _clean(coll: str, row: dict) -> dict:
    return {k: v for k, v in row.items() if not (coll in AUTHOR_NOTES and k == "note")}


def execute(db, name: str, args: dict, q: dict, show: bool = False) -> tuple[str, bool]:
    """Run one tool call for question `q` (its as_of and state). Returns (result text, is_error)."""
    as_of, state = q["as_of"], q.get("state")
    try:
        if name == "search_help_center":
            rows = R.retrieve(db, "M8", {"question": args["query"], "as_of": as_of, "state": state}, k=5, show=show)
            docs = {d["_key"]: d for d in db.collection("articles").get_many([r["key"] for r in rows])}
            return _dump([{"key": r["key"], "title": docs[r["key"]]["title"], "text": plain(docs[r["key"]]["text"])}
                          for r in rows]), False
        if name == "read_article":
            doc_id = args["doc_id"].split("__")[0].strip()
            rows = run(db, READ_AQL, {"doc_id": doc_id, "as_of": as_of, "state": state}, show=show)
            if not rows:
                return f"No article '{doc_id}' is in effect on {as_of} for this customer.", True
            a = rows[0]
            named = [m.group(2) for m in LINK_RE.finditer(a["text"])]
            a["links"] = [{"doc_id": t, "exists": t in a["linked_doc_ids"]} for t in dict.fromkeys(named)]
            del a["linked_doc_ids"]
            a["text"] = plain(a["text"])
            return _dump(a), False
        if name in {"lookup", "list_records"}:
            kind = args.get("kind")
            if kind not in KINDS:
                return f"kind must be one of {list(KINDS)}", True
            if name == "lookup":
                key = item_key(kind, args.get("name", ""))
                if key is None:
                    return f"No {kind} matches '{args.get('name')}'. Try list_records(kind='{kind}').", True
                row = run(db, LOOKUP_AQL, {"id": f"{KINDS[kind]}/{key}", "as_of": as_of}, show=show)[0]
                return _dump(_clean(KINDS[kind], row)), False
            field, value = args.get("field"), args.get("value")
            if (field is None) != (value is None):
                return "Give both field and value, or neither.", True
            rows = run(db, LIST_AQL, {"@coll": KINDS[kind], "field": field, "value": value}, show=show)
            return _dump([_clean(KINDS[kind], r) for r in rows]), False
        return f"Unknown tool {name}", True
    except KeyError as e:
        return f"Missing argument {e}", True
