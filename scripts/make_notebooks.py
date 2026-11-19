"""Write the six chapter notebooks in notebooks/ (thin wrappers over cookbook/*.py). `make nb` runs them.

The prose cells are DRAFT placeholders; the author will rewrite them. Code lives in cookbook/ and scripts/,
so the notebooks stay short and every AQL query is printed by cookbook.db.run before it runs.
"""
from pathlib import Path

import nbformat as nbf

NB = Path(__file__).resolve().parents[1] / "notebooks"
DRAFT = "<!-- DRAFT: placeholder prose; the author will rewrite this. -->\n"
SETUP = ("import sys, os, warnings\nwarnings.filterwarnings('ignore')\nos.environ['TOKENIZERS_PARALLELISM'] = 'false'\n"
         "sys.path.insert(0, '..'); sys.path.insert(0, '../scripts')\n")


def md(s):
    return nbf.v4.new_markdown_cell(DRAFT + s)


def code(s):
    return nbf.v4.new_code_cell(s)


CHAPTERS = {
    "01_setup.ipynb": [
        md("# 01 · Setup\n**You'll learn:** how to run ArangoDB 3.12 Community Edition with the vector index on, and how to "
           "check that vector search, filtered vector search and BM25 work before writing any data code.\n\nStart ArangoDB 3.12 Community Edition with the vector index enabled (`docker compose up -d`; "
           "`--vector-index true` is set in `docker-compose.yml`), then check that every feature the cookbook uses works: "
           "the vector index, a filtered vector search, BM25 through an ArangoSearch view, and a document inserted after "
           "the index was built being found right away."),
        code(SETUP + "import verify_env\nverify_env.main()"),
    ],
    "02_data_model.ipynb": [
        md("# 02 · Data model\n**You'll learn:** how to keep documents, edges, a named graph, a BM25 view and a vector index "
           "in one database, and how to build a graph from structure already in your data (links, codes, versions, names).\n\nOne database holds documents (articles with their versions and embeddings, tickets, forms, "
           "states, lenders, lessors, stores, concepts) and edges. The **structural** edges are parsed from the knowledge base "
           "itself (links, form codes, version chains, names). The **semantic** edges come from concepts Claude extracted "
           "from each article (cached in `data/kb/semantic/`). Nothing in the graph is written by hand."),
        code(SETUP + "from cookbook.build import build, SHOW_KB_PROBLEMS\nfrom cookbook.db import get_db, run\n"
             "counts = build()\ndb = get_db()"),
        md("A graph query a support team can use: current articles that still point readers at a retired form."),
        code("run(db, SHOW_KB_PROBLEMS)"),
        md("Everything one article connects to, in both layers."),
        code('run(db, """\nFOR v, e IN 1..1 ANY "articles/inherited_car__2026" GRAPH "kb_graph"\n'
             '  OPTIONS { edgeCollections: ["links_to", "uses_form", "mentions"] }\n'
             '  COLLECT edge = PARSE_IDENTIFIER(e._id).collection INTO targets = v._key\n'
             '  RETURN { edge, targets }\n""")'),
    ],
    "03_freshness.ipynb": [
        md("# 03 · Keeping answers current\n**You'll learn:** how to version documents so a policy change reaches the next "
           "answer with no re-indexing: one stream transaction, a date filter, and a `supersedes` edge for the history.\n\nA policy changes. In one stream transaction we insert its new version "
           "(with its embedding and parsed edges), close the old one, and add a `supersedes` edge. The next query already "
           "answers from the new version: nothing is re-indexed. This runs in a copy of the database (`northwind_kb_demo`)."),
        code(SETUP + "import fresh_demo\nfresh_demo.main()"),
    ],
    "04_retrieval.ipynb": [
        md("# 04 · Retrieval: six methods, one AQL query each\n**You'll learn:** how BM25, vector search, a date/state "
           "filter and a graph walk combine in single AQL queries, and how to read a graph hit's path.\n\nM1 BM25 · M2 vector · M3 vector + date/state filter · "
           "M4–M6 the same graph query over structural, semantic or both edge sets. Two questions from the gold set: "
           "q22, where the graph adds the second article a customer needs, and q42, where it pushes a correct one out."),
        code(SETUP + "from cookbook.db import get_db\nfrom cookbook.load import load_gold\nfrom cookbook.retrieve import METHODS, retrieve\n"
             "db = get_db()\ngold = {q['id']: q for q in load_gold()}\n"
             "def show(qid, k=5):\n    q = gold[qid]\n    print(q['question'], '\\ngold:', q['gold_keys'], '\\n')\n"
             "    for m, (name, _) in METHODS.items():\n        rows = retrieve(db, m, q, k=k)\n"
             "        print(f'{m} {name:22}', [r['key'] + (' *' if r['key'] in q['gold_keys'] else '') for r in rows])\n"
             "        for r in rows:\n            if r.get('via') and r['key'] in q['gold_keys']:\n"
             "                print('      reached through', r['via'])"),
        md("The graph query itself (printed with its bind variables):"),
        code("retrieve(db, 'M4', gold['q22'], k=5, show=True)[:2]"),
        code("show('q22')"),
        code("show('q42')"),
    ],
    "05_evaluation.ipynb": [
        md("# 05 · Evaluation\n**You'll learn:** how to measure retrieval and answers honestly: a frozen gold set, "
           "trap articles, stale-version hits, an independent LLM judge and run-to-run variance.\n\nRetrieval scores on the frozen 30 questions (`make eval`), then answer scores: Claude Opus 5.5 "
           "answers from each method's top 5, Claude Fable 5.2 judges each required fact by meaning, three runs "
           "(`make answers-run`, `make answers-report`). Tables are read from `data/eval/scores/`."),
        code(SETUP + "from IPython.display import Markdown\nfrom pathlib import Path\n"
             "Markdown(Path('../data/eval/scores/latest.md').read_text())"),
        code("Markdown(Path('../data/eval/scores/answers.md').read_text())"),
    ],
    "06_graph_questions.ipynb": [
        md("# 06 · Questions that need a graph\n**You'll learn:** three ways to put a graph to work when vector search isn't "
           "enough: enter the graph from names in the question (M7), retrieve wide and rank narrow with a cross-encoder (M8), "
           "and give an answering agent graph tools (M9). Measured on gold v2 (12 chain + 8 list questions, frozen before "
           "any method ran on them). Agent answers are read from the cache, so this chapter makes no API calls."),
        code(SETUP + "import json\nfrom pathlib import Path\nfrom cookbook.db import get_db\nfrom cookbook.load import load_gold_v2\n"
             "from cookbook.entities import link_entities\nfrom cookbook import retrieve as R\n"
             "db = get_db()\ngold = {q['id']: q for q in load_gold_v2()}\nq = gold['v2c01']\n"
             "print(q['question'])\nprint('names found:', link_entities(q['question']))"),
        md("**M7**: the lender's name is an entry point into the graph. The article it reaches carries the path."),
        code("for r in R.retrieve(db, 'M7', q, k=5):\n    print(r['key'], round(r['score'], 3), r.get('via') or '')"),
        md("**M8, wide**: one AQL query collects candidates from BM25, vector search, graph neighbours and named entities, "
           "each tagged with where it came from."),
        code("pool = R.pool(db, 'M8', q, show=True)\nfor c in pool:\n    print(c['key'], c['sources'])"),
        md("**M8, narrow**: a cross-encoder reads (question, article) pairs and ranks the pool."),
        code("for r in R.retrieve(db, 'M8', q, k=5):\n    print(r['key'], r['score'], r['sources'], '*' if r['key'] in q['gold_keys'] else '')"),
        md("**M9's tools** are fixed AQL templates. The model chooses which to call; it never writes AQL."),
        code("from cookbook.tools import execute\nout, _ = execute(db, 'lookup', {'kind': 'form', 'name': 'NW-POA-1'}, q, show=True)\nprint(out)"),
        code("out, _ = execute(db, 'list_records', {'kind': 'lender', 'field': 'epayoff_network', 'value': 'false'}, q, show=True)\n"
             "print([r['name'] for r in json.loads(out)])"),
        md("A list question, answered by the agent with graph tools (M9) and with search only (M9s), from the cached run 1."),
        code("for m in ['M9s', 'M9']:\n    r = json.loads(Path(f'../data/eval/answers_v2/run1/{m}/v2s04.json').read_text())\n"
             "    print(m, [(t['tool'], t['input']) for t in r['agent_meta']['trace']])\n    print('  items:', r['items'])\n"
             "    print('  answer:', r['answer'][:300], '\\n')"),
        md("Scores on gold v2: retrieval (`make eval-v2`) and answers (`make answers-v2-report`)."),
        code("from IPython.display import Markdown\nMarkdown(Path('../data/eval/scores/v2_latest.md').read_text().split('### Per question')[0])"),
        code("Markdown(Path('../data/eval/scores/v2_answers.md').read_text())"),
    ],
}


def main() -> None:
    NB.mkdir(exist_ok=True)
    for name, cells in CHAPTERS.items():
        nb = nbf.v4.new_notebook()
        nb["cells"] = cells
        nb["metadata"]["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
        nbf.write(nb, NB / name)
        print("wrote", NB / name)


if __name__ == "__main__":
    main()
