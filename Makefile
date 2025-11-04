# Makefile para Projeto Pizzaria Docker

.PHONY: help build up down logs shell-backend shell-frontend shell-db clean restart status

# Exibir ajuda
help:
	@echo "Comandos disponíveis:"
	@echo "  make build     - Construir todas as imagens Docker"
	@echo "  make up        - Subir todos os serviços"
	@echo "  make down      - Parar todos os serviços"
	@echo "  make logs      - Ver logs de todos os serviços"
	@echo "  make restart   - Reiniciar todos os serviços"
	@echo "  make clean     - Limpar containers, volumes e imagens"
	@echo "  make status    - Ver status dos serviços"
	@echo "  make shell-backend   - Acessar shell do backend"
	@echo "  make shell-frontend  - Acessar shell do frontend"
	@echo "  make shell-db        - Acessar shell do PostgreSQL"
	@echo "  make populate        - Popular banco com dados de teste"

# Construir imagens
build:
	docker-compose --env-file docker/.env build --no-cache

# Subir serviços
up:
	docker-compose --env-file docker/.env up -d

# Subir serviços com logs
up-logs:
	docker-compose --env-file docker/.env up

# Parar serviços
down:
	docker-compose --env-file docker/.env down

# Ver logs
logs:
	docker-compose --env-file docker/.env logs -f

# Ver logs de um serviço específico
logs-backend:
	docker-compose --env-file docker/.env logs -f backend

logs-frontend:
	docker-compose --env-file docker/.env logs -f frontend

logs-db:
	docker-compose --env-file docker/.env logs -f postgres

# Reiniciar serviços
restart:
	docker-compose --env-file docker/.env restart

# Shell do backend
shell-backend:
	docker-compose --env-file docker/.env exec backend /bin/bash

# Shell do frontend
shell-frontend:
	docker-compose --env-file docker/.env exec frontend /bin/sh

# Shell do PostgreSQL
shell-db:
	docker-compose --env-file docker/.env exec postgres psql -U pizzaria_user -d pizzaria_db

# Status dos serviços
status:
	docker-compose --env-file docker/.env ps

# Limpar tudo
clean:
	docker-compose --env-file docker/.env down -v --rmi all --remove-orphans
	docker system prune -f

# Popular banco com dados
populate:
	docker-compose --env-file docker/.env exec backend python backend/utils/populate_menu.py

# Executar migrações
migrate:
	docker-compose --env-file docker/.env exec backend alembic upgrade head

# Criar migration
migrate-create:
	docker-compose --env-file docker/.env exec backend alembic revision --autogenerate -m "$(msg)"

# Executar testes
test:
	docker-compose --env-file docker/.env exec backend python -m pytest

# Build e up em uma linha
quick-start: build up

# URLs úteis
urls:
	@echo "🌐 URLs dos serviços:"
	@echo "  Frontend:  http://localhost:3000"
	@echo "  Backend:   http://localhost:8000"
	@echo "  API Docs:  http://localhost:8000/docs"
	@echo "  PgAdmin:   http://localhost:5050"
	@echo "  PostgreSQL: localhost:5432"