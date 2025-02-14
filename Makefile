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

generate-local-certs:
	# Wait for confirmation from user to generate new certificates
	@echo "This will generate new local certificates, are you sure you want to continue? [y/N] "; \
	read REPLY; \
	if [ "$$REPLY" != "y" ] && [ "$$REPLY" != "Y" ]; then \
		exit 1; \
	fi
	# Remove existing certificates or ignore if they don't exist
	rm -r certs || true

	mkdir certs
	mkcert -cert-file certs/local-cert.pem -key-file certs/local-key.pem "localhost"


include core/config/.env
