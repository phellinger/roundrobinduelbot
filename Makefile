.PHONY: deploy help format logs

help:
	@echo "Available targets:"
	@echo "  deploy    - Deploy the bot to TARGET_HOST"
	@echo "  format    - Remove trailing whitespaces from source files"
	@echo "  logs      - View remote Docker logs (use 'make logs ARGS=-f' to follow)"
	@echo ""
	@echo "Make sure to create a .env file with:"
	@echo "  TELEGRAM_BOT_TOKEN=your_token"
	@echo "  TARGET_HOST=user@hostname"
	@echo "  TARGET_PATH=/path/to/deployment"

format:
	@echo "Removing trailing whitespaces..."
	@find . -type f \( -name "*.py" -o -name "Makefile" -o -name "*.yml" -o -name "*.yaml" -o -name "*.txt" -o -name "*.md" \) \
		! -path "./.git/*" \
		! -path "./.venv/*" \
		! -path "./venv/*" \
		! -path "./__pycache__/*" \
		-exec sed -i '' 's/[[:space:]]*$$//' {} \;
	@echo "Formatting complete!"

deploy:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Please create it from .env.template"; \
		exit 1; \
	fi
	@export $$(grep -v '^#' .env | xargs) && \
	if [ -z "$$TARGET_HOST" ]; then \
		echo "Error: TARGET_HOST not set in .env file."; \
		exit 1; \
	fi && \
	if [ -z "$$TARGET_PATH" ]; then \
		echo "Error: TARGET_PATH not set in .env file."; \
		exit 1; \
	fi && \
	echo "Deploying to $$TARGET_HOST:$$TARGET_PATH..." && \
	scp bot.py requirements.txt Dockerfile docker-compose.yml .env $$TARGET_HOST:$$TARGET_PATH/ && \
	ssh $$TARGET_HOST "cd $$TARGET_PATH && docker-compose down && docker-compose up -d --build"

logs:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Please create it from .env.template"; \
		exit 1; \
	fi
	@export $$(grep -v '^#' .env | xargs) && \
	if [ -z "$$TARGET_HOST" ]; then \
		echo "Error: TARGET_HOST not set in .env file."; \
		exit 1; \
	fi && \
	if [ -z "$$TARGET_PATH" ]; then \
		echo "Error: TARGET_PATH not set in .env file."; \
		exit 1; \
	fi && \
	ssh $$TARGET_HOST "cd $$TARGET_PATH && docker-compose logs $(ARGS) bot"

