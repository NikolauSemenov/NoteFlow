SERVICE_DIR := src

setup:
	@poetry install --sync

lint:
	@printf "${TXT_BOLD}${TXT_MAGENTA}=========================== MYPY ==============================${TXT_RESET}\n"
	@poetry run mypy $(SERVICE_DIR)/
	@printf "${TXT_BOLD}${TXT_MAGENTA}=========================== RUFF ==============================${TXT_RESET}\n"
	@poetry run ruff check --fix --show-fixes --exit-non-zero-on-fix $(SERVICE_DIR)

format:
	@poetry run ruff format $(SERVICE_DIR)/

migration:
	@poetry run alembic revision --autogenerate

migrate:
	@poetry run alembic upgrade head

start_docker:
	docker compose up -d
