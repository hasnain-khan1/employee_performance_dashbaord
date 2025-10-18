# EPMS Docker Compose Management
# Usage: make <command>

.PHONY: help dev prod build up down logs clean seed test

# Default target
help:
	@echo "Available commands:"
	@echo "  dev          - Start development environment"
	@echo "  prod         - Start production environment"
	@echo "  build        - Build all images"
	@echo "  up           - Start all services"
	@echo "  down         - Stop all services"
	@echo "  logs         - Show logs for all services"
	@echo "  clean        - Clean up containers, volumes, and images"
	@echo "  seed         - Run database seeding"
	@echo "  test         - Run tests"
	@echo "  shell-backend - Open shell in backend container"
	@echo "  shell-db     - Open shell in database container"

# Development environment
dev:
	@echo "Starting development environment..."
	docker-compose --env-file env.development up -d
	@echo "Development environment started!"
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:5173"
	@echo "Database: localhost:5432"
	@echo "Redis: localhost:6379"

# Production environment
prod:
	@echo "Starting production environment..."
	docker-compose --env-file env.production --profile production up -d
	@echo "Production environment started!"
	@echo "Application: http://localhost"

# Build all images
build:
	@echo "Building all images..."
	docker-compose build --no-cache
	@echo "Build completed!"

# Start all services
up:
	@echo "Starting all services..."
	docker-compose up -d
	@echo "All services started!"

# Stop all services
down:
	@echo "Stopping all services..."
	docker-compose down
	@echo "All services stopped!"

# Show logs
logs:
	docker-compose logs -f

# Clean up everything
clean:
	@echo "Cleaning up containers, volumes, and images..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	docker volume prune -f
	@echo "Cleanup completed!"

# Run database seeding
seed:
	@echo "Running database seeding..."
	docker-compose --profile development run --rm seed
	@echo "Database seeding completed!"

# Run tests
test:
	@echo "Running tests..."
	docker-compose exec backend python manage.py test
	docker-compose exec frontend npm run test
	@echo "Tests completed!"

# Open shell in backend container
shell-backend:
	docker-compose exec backend bash

# Open shell in database container
shell-db:
	docker-compose exec db psql -U postgres -d epms_db

# Show service status
status:
	docker-compose ps

# Restart specific service
restart-%:
	docker-compose restart $*

# View logs for specific service
logs-%:
	docker-compose logs -f $*
