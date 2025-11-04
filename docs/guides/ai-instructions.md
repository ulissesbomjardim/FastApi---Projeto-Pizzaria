# 🤖 Instruções para IA - Hashtag Pizzaria

Este documento contém instruções específicas para manter consistência no desenvolvimento do projeto Hashtag Pizzaria.

## 🎯 REGRAS OBRIGATÓRIAS (NUNCA IGNORAR)

### 1. Sistema Operacional e Ferramentas
- **SEMPRE** usar WSL Ubuntu para comandos Docker
- **NUNCA** executar Docker diretamente no Windows PowerShell
- **Comando padrão**: `wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && COMANDO'`

### 2. Gerenciamento de Dependências Python
- **SEMPRE** usar Poetry, nunca pip ou conda diretamente
- **Adicionar dependência**: `poetry add biblioteca`
- **Ambiente virtual**: Poetry gerencia automaticamente
- **Instalação**: `poetry install`

### 3. Docker e Containers
```bash
# Padrão para todos os comandos Docker:
wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && docker compose COMANDO'

# Exemplos obrigatórios:
# Subir: docker compose up -d
# Parar: docker compose down  
# Logs: docker compose logs -f
# Status: docker compose ps
```

### 4. Estrutura de Arquivos (IMUTÁVEL)
```
backend/
├── src/
│   ├── main.py
│   ├── config/
│   │   ├── database.py
│   │   └── security.py
│   ├── models/
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── item.py
│   │   └── order.py
│   ├── routers/
│   │   ├── auth_routes.py
│   │   ├── item_routes.py
│   │   ├── order_routes.py
│   │   └── user_routes.py
│   └── schemas/
├── tests/
└── utils/

frontend/
├── assets/
│   ├── css/
│   │   ├── style.css
│   │   ├── components.css
│   │   └── responsive.css
│   ├── js/
│   │   ├── main.js
│   │   ├── api.js
│   │   ├── auth.js
│   │   ├── cart.js
│   │   └── menu.js
│   └── images/
└── index.html
```

### 5. URLs e Portas (FIXAS)
- Frontend: http://localhost:3000
- Backend: http://localhost:8000  
- PgAdmin: http://localhost:5050
- PostgreSQL: localhost:5432

### 6. Cache Busting Frontend
- **SEMPRE** versionar arquivos após mudanças: `?v=X`
- **HTML**: `<link rel="stylesheet" href="assets/css/style.css?v=8">`
- **CSS**: Incrementar número após modificações
- **JS**: Incrementar número após modificações

## 🗄️ BANCO DE DADOS

### Configuração PostgreSQL
```env
POSTGRES_DB=pizzaria_db
POSTGRES_USER=pizzaria_user  
POSTGRES_PASSWORD=pizzaria_password123
DATABASE_URL=postgresql://pizzaria_user:pizzaria_password123@postgres:5432/pizzaria_db
```

### Estrutura de Dados
- **23 itens total** no menu
- **Categorias**: pizza (9), bebida (6), sobremesa (3), entrada (3), promocao (2)
- **Models**: User, Item, Order, OrderItem
- **Migrations**: Alembic com `alembic revision --autogenerate`

### Credenciais Admin
```env
ADMIN_EMAIL=admin@pizzaria.com
ADMIN_PASSWORD=Admin123!@#
```

## 🎨 FRONTEND

### CSS Framework
- **Vanilla CSS** com custom properties (--var)
- **Três arquivos**: style.css, components.css, responsive.css
- **Theme**: Dark com gradientes vermelhos
- **Botões**: Sempre seguir padrão .btn-primary

### JavaScript
- **ES6+** modular
- **Cinco módulos**: main.js, api.js, auth.js, cart.js, menu.js
- **API calls**: Sempre usar fetch com headers corretos
- **Cache**: localStorage para carrinho e auth

### Imagens SVG
- **Categorias**: pizza.svg, bebida.svg, sobremesa.svg, entrada.svg, promocao.svg, todos.svg
- **Fallback**: Sempre usar imagem da categoria se item não tem imagem
- **Styling**: .category-image com background gradient

## 🔧 COMANDOS ESSENCIAIS

### Setup Inicial
```bash
# Via script automatizado
wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && ./scripts/setup.sh'
```

### Desenvolvimento Diário
```bash
# Iniciar projeto
wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && ./scripts/dev-commands.sh start'

# Ver logs
wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && ./scripts/dev-commands.sh logs'

# Status
wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && ./scripts/dev-commands.sh status'
```

### Debug Banco
```bash
# Query rápida
wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && docker exec pizzaria_backend python -c "
from backend.src.config.database import get_db
from backend.src.models.item import Item
db = next(get_db())
print(f\"Total itens: {db.query(Item).count()}\")
"'
```

## 🚨 TROUBLESHOOTING PADRÃO

### Container não sobe
1. `docker compose down`
2. `docker system prune -f`  
3. `docker compose up -d --build`

### Frontend não carrega
1. Verificar versioning: incrementar ?v=X
2. Ctrl+Shift+R para limpar cache
3. Verificar se Nginx está rodando: `docker logs pizzaria_frontend`

### Backend não conecta
1. Verificar .env
2. `docker logs pizzaria_backend`
3. Testar: `curl http://localhost:8000`

### Banco não conecta
1. Verificar container: `docker logs pizzaria_postgres`
2. Aguardar 30s após docker up
3. Verificar credenciais no PgAdmin

## 📋 CHECKLIST PRÉ-DEPLOY

- [ ] Todos os containers rodando: `docker compose ps`
- [ ] Frontend carregando: `curl http://localhost:3000`
- [ ] Backend respondendo: `curl http://localhost:8000`
- [ ] 23 itens no banco: query de verificação
- [ ] Imagens SVG funcionando: verificar todas as categorias
- [ ] Filtros funcionando: testar todos os botões
- [ ] Cache limpo: versões atualizadas

## 🎯 PADRÕES DE CÓDIGO

### Python (Backend)
- Black para formatação
- FastAPI com type hints
- SQLAlchemy models com relacionamentos
- Pydantic schemas para validação
- Pytest para testes

### JavaScript (Frontend)  
- ES6+ com modules
- Async/await para API calls
- Classes para componentes
- LocalStorage para persistência
- Vanilla DOM manipulation

### CSS
- Custom properties para temas
- BEM naming quando aplicável
- Mobile-first responsive
- Gradientes e sombras consistentes
- Animações suaves (0.2s-0.5s)

---

**🤖 PARA IA: Use este documento como referência absoluta. Sempre consulte antes de sugerir mudanças na estrutura ou comandos.**