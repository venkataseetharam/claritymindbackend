# Makefile for deploying and managing Flask app on Heroku

# Default target - display help message
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  deploy       Deploy the Flask app to Heroku"
	@echo "  scale        Scale the number of web dynos"
	@echo "  logs         View logs for the application"
	@echo "  restart      Restart the application"

# Deploy the Flask app to Heroku
.PHONY: deploy
deploy:
	heroku create  # Create a new Heroku app
	git push heroku master  # Push code to Heroku
	heroku run python manage.py migrate  # Run migrations (if applicable)
	heroku ps:scale web=1  # Scale the number of web dynos

# Scale the number of web dynos
.PHONY: scale
scale:
	heroku ps:scale web=1

# View logs for the application
.PHONY: logs
logs:
	heroku logs --tail

# Restart the application
.PHONY: restart
restart:
	heroku restart
