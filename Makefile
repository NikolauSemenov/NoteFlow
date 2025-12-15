SERVICE_DIR := src
PROJECT := notes-flow

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

build_docker:
	docker compose -p ${PROJECT} build

start_docker:
	docker compose -p ${PROJECT} up -d

stop_docker:
	docker compose -p ${PROJECT} down

logging_docker:
	docker compose -p ${PROJECT} logs -f --tail=50 app

ps_docker:
	docker compose -p ${PROJECT} ps

restart_docker:
	docker compose restart ${PROJECT}

revision_docker:
	docker compose -p ${PROJECT} run --rm --no-deps app \
		alembic revision --autogenerate -m "$(MESSAGE)"

migrate_docker:
	docker compose -p ${PROJECT} run --rm app \
		alembic upgrade head

downgrade_docker:
	docker compose -p ${PROJECT} run --rm app \
		alembic downgrade -1
