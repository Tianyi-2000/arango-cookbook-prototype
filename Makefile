PY := .venv/bin/python

.PHONY: up down venv verify check test-checks
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
