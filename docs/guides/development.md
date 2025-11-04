# 📋 Guia de Desenvolvimento - Hashtag Pizzaria

## 🎯 Configurações Padrão (NUNCA MUDAR)

### 🐧 Sistema Operacional
- **SEMPRE usar**: WSL Ubuntu para Docker
- **Comando padrão**: `wsl -e bash -c 'comando'`
- **Diretório WSL**: `/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria`

### 🐍 Gerenciador de Dependências Python
- **SEMPRE usar**: Poetry (não pip, não conda)
- **Instalação**: `curl -sSL https://install.python-poetry.org | python3 -` ou `pip install poetry`
- **Adicionar dependência**: `poetry add nome_da_biblioteca`
- **Remover dependência**: `poetry remove nome_da_biblioteca`
- **Ativar ambiente**: `poetry shell`
- **Instalar deps**: `poetry install`

### 🐳 Docker
- **SEMPRE usar**: Docker Compose via WSL
- **Subir containers**: `wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && docker compose up -d'`
- **Parar containers**: `wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && docker compose down'`
- **Logs**: `wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && docker compose logs -f'`

### 🌐 URLs dos Serviços
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **PgAdmin**: http://localhost:5050
- **PostgreSQL**: localhost:5432

### 🔧 Estrutura do Projeto
```
├── backend/
│   ├── src/
│   │   ├── main.py
│   │   ├── config/
│   │   ├── models/
│   │   ├── routers/
│   │   └── schemas/
│   └── tests/
├── frontend/
│   ├── assets/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── index.html
├── docker/
└── docs/
```

### 💾 Banco de Dados
- **Sistema**: PostgreSQL 15
- **ORM**: SQLAlchemy com Alembic
- **Migrations**: `alembic revision --autogenerate -m "descrição"`
- **Aplicar**: `alembic upgrade head`

### 🎨 Frontend
- **Framework**: Vanilla JavaScript (ES6+)
- **CSS**: Custom CSS com variáveis
- **Versionamento**: Sempre usar ?v=X nos arquivos para cache busting

### 🔒 Variáveis de Ambiente (.env)
```env
SECRET_KEY=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
POSTGRES_DB=pizzaria_db
POSTGRES_USER=pizzaria_user
POSTGRES_PASSWORD=pizzaria_password123
DATABASE_URL=postgresql://pizzaria_user:pizzaria_password123@postgres:5432/pizzaria_db
ADMIN_EMAIL=admin@pizzaria.com
ADMIN_PASSWORD=Admin123!@#
```

## 🚀 Comandos Essenciais

### Docker (Sempre via WSL)
```bash
# Subir todos os serviços
wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && docker compose up -d'

# Parar todos os serviços
wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && docker compose down'

# Limpar cache e rebuildar
wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && docker compose down && docker system prune -f && docker compose up -d'

# Ver logs em tempo real
wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && docker compose logs -f'

# Executar comando no backend
wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && docker exec pizzaria_backend COMANDO'
```

### Poetry (Backend Python)
```bash
# Instalar dependências
cd backend && poetry install

# Adicionar nova dependência
cd backend && poetry add fastapi sqlalchemy alembic

# Adicionar dependência de desenvolvimento
cd backend && poetry add --group dev pytest black

# Ativar ambiente virtual
cd backend && poetry shell

# Rodar testes
cd backend && poetry run pytest
```

### Desenvolvimento Frontend
```bash
# Sempre versionar arquivos após mudanças
# HTML: ?v=X
# CSS: ?v=X  
# JS: ?v=X

# Exemplo:
<link rel="stylesheet" href="assets/css/style.css?v=8">
<script src="assets/js/menu.js?v=9"></script>
```

## 🔍 Debug e Troubleshooting

### Verificar Status dos Containers
```bash
docker ps
docker compose ps
```

### Acessar Logs Específicos
```bash
# Backend
docker logs pizzaria_backend

# Frontend (Nginx)
docker logs pizzaria_frontend

# PostgreSQL
docker logs pizzaria_postgres
```

### Testar APIs
```bash
# Menu
curl http://localhost:8000/items/menu

# Health check
curl http://localhost:8000/

# Frontend
curl http://localhost:3000
```

### Acessar Banco de Dados
- **PgAdmin**: http://localhost:5050
- **Email**: admin@admin.com
- **Senha**: admin
- **Server**: postgres
- **Database**: pizzaria_db
- **User**: pizzaria_user
- **Password**: pizzaria_password123

## ⚠️ Regras Importantes

1. **NUNCA** usar pip direto - sempre Poetry
2. **NUNCA** rodar Docker no Windows - sempre WSL
3. **SEMPRE** versionar arquivos frontend após mudanças
4. **SEMPRE** usar paths absolutos em comandos Docker
5. **NUNCA** commitar .env com senhas reais
6. **SEMPRE** testar localmente antes de fazer push

## 📱 Categorias do Sistema
- **pizza**: 9 itens
- **bebida**: 6 itens  
- **sobremesa**: 3 itens
- **entrada**: 3 itens
- **promocao**: 2 itens

## 🎨 Assets
- **Imagens SVG**: /frontend/assets/images/
- **CSS**: /frontend/assets/css/
- **JavaScript**: /frontend/assets/js/

Total: 23 itens no menu