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
