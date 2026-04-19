PYTHONPATH=src
UVICORN=$(shell python3 -m uvicorn --version > /dev/null 2>&1 && echo "python3 -m uvicorn" || echo "uvicorn")

dev:
	PYTHONPATH=$(PYTHONPATH) python3 -m uvicorn api.main:app --reload

test:
	PYTHONPATH=$(PYTHONPATH) python3 -m pytest

lint:
	PYTHONPATH=$(PYTHONPATH) python3 -m ruff check src/

.PHONY: dev test lint
