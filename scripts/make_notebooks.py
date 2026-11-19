"""Write the five chapter notebooks in notebooks/ (thin wrappers over cookbook/*.py). `make nb` runs them.

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
        md("# 01 · Setup\nStart ArangoDB 3.12 Community Edition with the vector index enabled (`docker compose up -d`; "
           "`--vector-index true` is set in `docker-compose.yml`), then check that every feature the cookbook uses works: "
           "the vector index, a filtered vector search, BM25 through an ArangoSearch view, and a document inserted after "
           "the index was built being found right away."),
        code(SETUP + "import verify_env\nverify_env.main()"),
    ],
    "02_data_model.ipynb": [
        md("# 02 · Data model\nOne database holds documents (articles with their versions and embeddings, tickets, forms, "
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
        md("# 03 · Keeping answers current\nA policy changes. In one stream transaction we insert its new version "
           "(with its embedding and parsed edges), close the old one, and add a `supersedes` edge. The next query already "
           "answers from the new version: nothing is re-indexed. This runs in a copy of the database (`northwind_kb_demo`)."),
        code(SETUP + "import fresh_demo\nfresh_demo.main()"),
    ],
    "04_retrieval.ipynb": [
        md("# 04 · Retrieval: six methods, one AQL query each\nM1 BM25 · M2 vector · M3 vector + date/state filter · "
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
        md("# 05 · Evaluation\nRetrieval scores on the frozen 30 questions (`make eval`), then answer scores: Claude Opus 5.5 "
           "answers from each method's top 5, Claude Fable 5.2 judges each required fact by meaning, three runs "
           "(`make answers-run`, `make answers-report`). Tables are read from `data/eval/scores/`."),
        code(SETUP + "from IPython.display import Markdown\nfrom pathlib import Path\n"
             "Markdown(Path('../data/eval/scores/latest.md').read_text())"),
        code("Markdown(Path('../data/eval/scores/answers.md').read_text())"),
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
