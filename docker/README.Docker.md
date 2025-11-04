# 🍕 Pizzaria Docker Setup

Este projeto está configurado para rodar completamente em Docker com PostgreSQL.

## 📋 Pré-requisitos

### Windows (WSL Ubuntu)
```bash
# 1. Instalar Docker
sudo apt update
sudo apt install docker.io docker-compose

# 2. Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# 3. Reiniciar o WSL ou fazer logout/login
wsl --shutdown
# Reabrir WSL
```

### Verificar instalação
```bash
docker --version
docker-compose --version
```

## 🚀 Quick Start

### Método 1: Script Interativo (Recomendado)
```bash
# No WSL Ubuntu, navegar para o projeto:
cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria"

# Tornar o script executável
chmod +x docker/docker-setup.sh

# Executar o script
./docker/docker-setup.sh
```

### Método 2: Comandos Manuais
```bash
# 1. Navegar para o diretório do projeto
cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria"

# 2. Buildar as imagens
sudo docker-compose --env-file docker/.env build

# 3. Subir os serviços
sudo docker-compose --env-file docker/.env up -d

# 4. Ver status
sudo docker-compose --env-file docker/.env ps
```

## 🌐 URLs dos Serviços

| Serviço | URL | Descrição |
|---------|-----|-----------|
| Frontend | http://localhost:3000 | Interface da pizzaria |
| Backend | http://localhost:8000 | API FastAPI |
| API Docs | http://localhost:8000/docs | Documentação Swagger |
| PgAdmin | http://localhost:5050 | Gerenciador do PostgreSQL |
| PostgreSQL | localhost:5432 | Banco de dados |

## 🗄️ Credenciais Padrão

### Admin da Aplicação
- **Email:** admin@pizzaria.com
- **Senha:** Admin123!@#

### PgAdmin
- **Email:** admin@pizzaria.com  
- **Senha:** admin123

### PostgreSQL
- **Host:** localhost
- **Porta:** 5432
- **Banco:** pizzaria_db
- **Usuário:** pizzaria_user
- **Senha:** pizzaria_secret_123

## 📊 Comandos Úteis

```bash
# Ver logs em tempo real
sudo docker-compose --env-file docker/.env logs -f

# Ver logs de um serviço específico
sudo docker-compose --env-file docker/.env logs -f backend
sudo docker-compose --env-file docker/.env logs -f frontend
sudo docker-compose --env-file docker/.env logs -f postgres

# Parar todos os serviços
sudo docker-compose --env-file docker/.env down

# Reiniciar serviços
sudo docker-compose --env-file docker/.env restart

# Acessar shell do backend
sudo docker-compose --env-file docker/.env exec backend /bin/bash

# Acessar PostgreSQL
sudo docker-compose --env-file docker/.env exec postgres psql -U pizzaria_user -d pizzaria_db

# Popular banco com dados de teste
sudo docker-compose --env-file docker/.env exec backend python backend/utils/populate_menu.py

# Executar migrações
sudo docker-compose --env-file docker/.env exec backend alembic upgrade head

# Executar testes
sudo docker-compose --env-file docker/.env exec backend python -m pytest
```

## 🧹 Limpeza

```bash
# Parar e remover containers
sudo docker-compose --env-file docker/.env down

# Remover volumes também (⚠️ apaga dados do banco)
sudo docker-compose --env-file docker/.env down -v

# Limpeza completa (containers, imagens, volumes)
sudo docker-compose --env-file docker/.env down -v --rmi all --remove-orphans
sudo docker system prune -f
```

## 🛠️ Desenvolvimento

### Estrutura dos Containers

- **Frontend (Nginx):** Serve os arquivos estáticos da aplicação web
- **Backend (FastAPI):** API Python com hot-reload habilitado
- **PostgreSQL:** Banco de dados com persistência
- **PgAdmin:** Interface web para gerenciar o PostgreSQL

### Volumes Montados

- `./frontend` → `/usr/share/nginx/html` (Frontend)
- `./backend` → `/app/backend` (Backend - Hot Reload)
- `postgres_data` → `/var/lib/postgresql/data` (Dados do PostgreSQL)

### Variáveis de Ambiente

Todas as configurações estão em `docker/.env`:
- Credenciais do banco
- Configurações da aplicação  
- Chaves secretas

## 🔧 Troubleshooting

### Container não sobe
```bash
# Ver logs detalhados
sudo docker-compose --env-file docker/.env logs [nome_do_servico]

# Verificar se as portas estão livres
sudo netstat -tlnp | grep :3000
sudo netstat -tlnp | grep :8000
sudo netstat -tlnp | grep :5432
```

### Problemas de permissão
```bash
# Verificar se usuário está no grupo docker
groups $USER

# Se não estiver, adicionar:
sudo usermod -aG docker $USER
# Depois reiniciar WSL
```

### Reset completo
```bash
# Parar tudo e limpar
sudo docker-compose --env-file docker/.env down -v --rmi all
sudo docker system prune -af

# Buildar novamente
sudo docker-compose --env-file docker/.env build --no-cache
sudo docker-compose --env-file docker/.env up -d
```

## 📚 Estrutura do Projeto

```
├── docker/
│   ├── .env                 # Variáveis de ambiente
│   ├── nginx.conf           # Configuração do Nginx
│   └── init-scripts/        # Scripts de inicialização do DB
├── docker-compose.yml       # Orquestração dos serviços
├── docker/
│   ├── Dockerfile.backend   # Imagem do Backend
│   ├── Dockerfile.frontend  # Imagem do Frontend
│   └── docker-setup.sh      # Script interativo
└── Makefile                 # Comandos automatizados
```