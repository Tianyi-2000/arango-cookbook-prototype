PY := .venv/bin/python

.PHONY: up down venv verify check test-checks review tickets-plan tickets-one tickets load test-retrieve freeze eval eval-reserve fresh answers answers-run answers-report extract check-semantic nb
up:      ## start ArangoDB on localhost:8535
	docker compose up -d
down:
	docker compose down
venv:    ## create .venv and install pinned requirements
	python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt
verify:  ## check the running ArangoDB supports vector index, filtered vector search, BM25
	$(PY) scripts/verify_env.py
check:   ## data consistency: KB, gold set, tickets (see eval.md)
	$(PY) scripts/check_data.py
test-checks:  ## inject known faults into a copy of data/ and confirm make check catches each one
	$(PY) scripts/test_check_data.py
review:  ## render data/eval/gold_review.md from gold.json for human review
	$(PY) scripts/render_gold_review.py
tickets-plan:  ## dry run: ticket plan, cost estimate, one example prompt (no API calls)
	$(PY) scripts/generate_tickets.py
tickets-one:   ## generate one ticket to test the API path (needs ANTHROPIC_API_KEY in .env)
	$(PY) scripts/generate_tickets.py --one
tickets:       ## generate all missing tickets (needs ANTHROPIC_API_KEY in .env)
	$(PY) scripts/generate_tickets.py --all
load:    ## rebuild database northwind_kb from data/: documents, parsed edges, graph, BM25 view, vector index
	$(PY) -m cookbook.build
test-retrieve:  ## run M1-M4 on the reserve questions: index use, no stale or wrong-state hits (needs make load)
	$(PY) scripts/test_retrieve.py
freeze:  ## freeze the gold set: write data/eval/FROZEN (sha256 of gold.json)
	$(PY) scripts/freeze_gold.py
eval:    ## retrieval eval on the frozen gold set -> data/eval/scores/latest.{json,md} (needs make load)
	$(PY) scripts/run_eval.py
eval-reserve:  ## the same eval on the reserve questions, for debugging (writes nothing)
	$(PY) scripts/run_eval.py --reserve
fresh:   ## freshness demo in northwind_kb_demo: change a policy, ask again -> data/eval/fresh_demo.md
	$(PY) scripts/fresh_demo.py
answers:  ## dry run of the answer eval: cost estimate and one prompt, no API calls
	$(PY) scripts/run_answers.py
answers-run:  ## answer eval: M1-M6 x 30 x 3 runs, Opus 5.5 answers, Fable 5.2 judge; stops at the $50 ledger cap
	$(PY) scripts/run_answers.py --run
answers-report:  ## answer eval tables from the cached answers -> data/eval/scores/answers.md
	$(PY) scripts/run_answers.py --report
extract:  ## dry run of the semantic extraction (Claude); --one / --run via scripts/extract_semantic.py
	$(PY) scripts/extract_semantic.py
check-semantic:  ## score extracted concepts against the hand-written list for 10 versions
	$(PY) scripts/check_semantic.py
nb:      ## write the five chapter notebooks and run them in place (outputs saved; needs make up)
	$(PY) scripts/make_notebooks.py
	cd notebooks && JUPYTER_PATH="$(CURDIR)/.venv/share/jupyter" ../.venv/bin/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=600 01_setup.ipynb 02_data_model.ipynb 03_freshness.ipynb 04_retrieval.ipynb 05_evaluation.ipynb
