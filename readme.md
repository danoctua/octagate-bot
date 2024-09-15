[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
# 8club guard bot
## Installation
To install and run the Telegram Bot, follow these steps:
1. Make sure you have Docker installed on your machine.
2. Clone this repository.
3. Run `make setup` to install all required dependencies.
4. Run `make build` to build the docker container.
5. Run `make run` to start the bot.
## Usage
Once the bot is up and running, users can interact with it on Telegram. The bot will provide instructions on how to play the game and match users with each other to play the prisoner dilemma game.
## Makefile Commands
- `make build`: Build the Docker container.
- `make compile-translations`: Compile translations after changes were introduced.
- `make down`: Stop and remove the Docker containers.
- `make restart`: Restart the Docker containers to apply changes in the code.
- `make run`: Start the Docker containers.
- `make setup`: Set up bot dependencies.
- `make stop`: Stop the Docker containers.
