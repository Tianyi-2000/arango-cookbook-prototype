PY := .venv/bin/python

.PHONY: up down venv verify
up:      ## start ArangoDB on localhost:8535
	docker compose up -d
down:
	docker compose down
venv:    ## create .venv and install pinned requirements
	python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt
verify:  ## check the running ArangoDB supports vector index, filtered vector search, BM25
	$(PY) scripts/verify_env.py
