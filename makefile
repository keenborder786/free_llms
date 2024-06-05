PYTHON_FILES=./src
lint:
	poetry run ruff $(PYTHON_FILES)
	poetry run mypy $(PYTHON_FILES)

format:
	poetry run ruff format $(PYTHON_FILES)
	poetry run ruff --select I --fix $(PYTHON_FILES)
