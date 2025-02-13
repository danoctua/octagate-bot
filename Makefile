_configure_redis_password:
	docker compose run --rm redis redis-cli -a $(REDIS_PASSWORD) CONFIG SET requirepass $(REDIS_PASSWORD)

build:
	docker compose build

down:
	docker compose down

restart: stop run

run:
	docker compose up -d

setup:
	./scripts/setup.sh

stop:
	docker compose stop

generate-migration:
	docker compose run --rm telegram-bot alembic revision --autogenerate -m "$(m)"

create-empty-migration:
	docker compose run --rm telegram-bot alembic revision -m "$(m)"

migrate:
	docker compose run --rm telegram-bot alembic upgrade head

setup-venv:
	pip3 install -r core/requirements.txt
	pip3 install -r bot_ui/requirements.txt
	pip3 install -r wallet_indexer/requirements.txt
	pip3 install -r api/requirements.txt


include core/config/.env
