build:
	docker compose build

down:
	docker compose down

down_prod:
	docker compose -f docker-compose.prod.yml down

restart: stop run

restart_prod: stop_prod run_prod

run:
	docker compose up -d

run_prod:
	docker compose -f docker-compose.prod.yml up -d

setup:
	./scripts/setup.sh

stop:
	docker compose stop

stop_prod:
	docker compose -f docker-compose.prod.yml stop
