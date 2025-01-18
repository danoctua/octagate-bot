_configure_redis_password:
	docker compose run --rm redis redis-cli -a $(REDIS_PASSWORD) CONFIG SET requirepass $(REDIS_PASSWORD)


build:
	docker compose build

down:
	docker compose down

restart:
	docker compose stop telegram-bot && docker compose up -d telegram-bot

run:
	docker compose up -d

setup:
	./scripts/setup.sh

stop:
	docker compose stop


include .env
