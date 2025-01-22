[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
# Octagate Community Guard

## Configuration
1. Clone the current repository.
2. Open the project and clone https://github.com/OpenBuilders/transaction-lookup repository in the root of the current project.
3. Make sure to copy and fill the templates for the following files:
- `core/config/.env.template` to `core/config/.env`
- `bot_ui/config/.env.template` to `bot_ui/config/.env`
- `wallet_indexer/config/.env.template` to `wallet_indexer/config/.env`

## Installation
To install and run the project, follow these steps:
- Docker and Docker Compose must be installed on your machine.
- Python 3 and pip should be installed to set up the virtual environment.
- Run `make setup-venv` to install all required dependencies.
- Run `make build` to build the docker container.
- Run `make run` to start the project.
## Usage

## Makefile Commands

### Docker Commands

- **_configure_redis_password**: Configures the password for the Redis service using the `redis-cli`. Ensure that the environment variable `REDIS_PASSWORD` is set before running this command.

  ```bash
  make _configure_redis_password
  ```

- **build**: Builds the Docker images defined in the `docker-compose.yml` file.

  ```bash
  make build
  ```

- **down**: Stops and removes all containers defined in the `docker-compose.yml` file.

  ```bash
  make down
  ```

- **restart**: Stops the running containers and then starts them again in detached mode.

  ```bash
  make restart
  ```

- **run**: Starts the containers defined in the `docker-compose.yml` file in detached mode.

  ```bash
  make run
  ```

- **stop**: Stops the containers without removing them.

  ```bash
  make stop
  ```

### Database Migration Commands

- **generate-migration**: Automatically generates a new Alembic migration script based on the current state of the database models. You must provide a message for the migration using the `m` variable.

  ```bash
  make generate-migration m="Add new table"
  ```

- **create-empty-migration**: Creates an empty Alembic migration script. You must provide a message for the migration using the `m` variable.

  ```bash
  make create-empty-migration m="Empty migration"
  ```

- **migrate**: Applies all pending Alembic migrations to the database.

  ```bash
  make migrate
  ```

### Setup Commands

- **setup**: Runs the setup script located at `./scripts/setup.sh`. This script is typically used for initializing or configuring the project.

  ```bash
  make setup
  ```

- **setup-venv**: Installs the required Python packages for the project using pip. Requirements are defined in multiple `requirements.txt` files located in the `core`, `bot_ui`, and `wallet_indexer` directories.

  ```bash
  make setup-venv
  ```
