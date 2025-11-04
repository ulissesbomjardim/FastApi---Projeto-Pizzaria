#!/bin/bash
# 🔧 Script de Desenvolvimento - Comandos Úteis
# Uso: ./scripts/dev-commands.sh [comando]

PROJECT_PATH="/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria"
cd "$PROJECT_PATH"

case "$1" in
    "start")
        echo "🚀 Iniciando todos os serviços..."
        docker compose up -d
        echo "✅ Serviços iniciados!"
        echo "Frontend: http://localhost:3000"
        echo "Backend: http://localhost:8000"
        echo "PgAdmin: http://localhost:5050"
        ;;
    
    "stop")
        echo "🛑 Parando todos os serviços..."
        docker compose down
        echo "✅ Serviços parados!"
        ;;
    
    "restart")
        echo "🔄 Reiniciando todos os serviços..."
        docker compose down
        docker compose up -d
        echo "✅ Serviços reiniciados!"
        ;;
    
    "clean")
        echo "🧹 Limpeza completa..."
        docker compose down
        docker system prune -f
        docker compose up -d --build
        echo "✅ Limpeza concluída!"
        ;;
    
    "logs")
        echo "📋 Mostrando logs em tempo real..."
        docker compose logs -f
        ;;
    
    "status")
        echo "📊 Status dos containers:"
        docker compose ps
        echo ""
        echo "🌐 Testando conectividade:"
        curl -s -o /dev/null -w "Frontend: %{http_code}\n" http://localhost:3000
        curl -s -o /dev/null -w "Backend: %{http_code}\n" http://localhost:8000
        ;;
    
    "db-query")
        echo "🗄️ Executando consulta no banco..."
        docker exec pizzaria_backend python -c "
from backend.src.config.database import get_db
from backend.src.models.item import Item

db = next(get_db())
items = db.query(Item).all()
categories = {}
for item in items:
    cat = item.category.value if hasattr(item.category, 'value') else str(item.category)
    categories[cat] = categories.get(cat, 0) + 1

print('📊 Itens por categoria:')
for cat, count in categories.items():
    print(f'  {cat}: {count} itens')
print(f'📈 Total: {len(items)} itens')
"
        ;;
    
    "add-dependency")
        if [ -z "$2" ]; then
            echo "❌ Uso: ./scripts/dev-commands.sh add-dependency NOME_DA_BIBLIOTECA"
            exit 1
        fi
        echo "📦 Adicionando dependência: $2"
        cd backend
        poetry add "$2"
        echo "✅ Dependência $2 adicionada!"
        echo "🔄 Rebuilding containers..."
        cd ..
        docker compose up -d --build pizzaria_backend
        ;;
    
    "test")
        echo "🧪 Executando testes..."
        docker exec pizzaria_backend poetry run pytest -v
        ;;
    
    "format")
        echo "🎨 Formatando código Python..."
        docker exec pizzaria_backend poetry run black .
        echo "✅ Código formatado!"
        ;;
    
    "migration")
        if [ -z "$2" ]; then
            echo "❌ Uso: ./scripts/dev-commands.sh migration 'descrição da migration'"
            exit 1
        fi
        echo "🗄️ Criando migration: $2"
        docker exec pizzaria_backend alembic revision --autogenerate -m "$2"
        echo "✅ Migration criada!"
        echo "💡 Para aplicar: ./scripts/dev-commands.sh migrate"
        ;;
    
    "migrate")
        echo "🗄️ Aplicando migrations..."
        docker exec pizzaria_backend alembic upgrade head
        echo "✅ Migrations aplicadas!"
        ;;
    
    "shell-backend")
        echo "🐍 Acessando shell do backend..."
        docker exec -it pizzaria_backend bash
        ;;
    
    "shell-frontend")
        echo "🌐 Acessando shell do frontend..."
        docker exec -it pizzaria_frontend sh
        ;;
    
    "backup-db")
        timestamp=$(date +"%Y%m%d_%H%M%S")
        echo "💾 Fazendo backup do banco de dados..."
        docker exec pizzaria_postgres pg_dump -U pizzaria_user pizzaria_db > "backup_$timestamp.sql"
        echo "✅ Backup salvo em backup_$timestamp.sql"
        ;;
    
    "version-frontend")
        if [ -z "$2" ]; then
            echo "❌ Uso: ./scripts/dev-commands.sh version-frontend NOVA_VERSAO"
            exit 1
        fi
        echo "🔄 Atualizando versão dos arquivos frontend para v=$2..."
        sed -i "s/?v=[0-9]*/?v=$2/g" frontend/index.html
        echo "✅ Versão atualizada para v=$2"
        ;;
    
    "help"|*)
        echo "🍕 Comandos disponíveis para o projeto Hashtag Pizzaria:"
        echo ""
        echo "📋 Serviços:"
        echo "  start          - Iniciar todos os serviços"
        echo "  stop           - Parar todos os serviços"
        echo "  restart        - Reiniciar todos os serviços"
        echo "  clean          - Limpeza completa e rebuild"
        echo "  status         - Ver status dos containers"
        echo "  logs           - Ver logs em tempo real"
        echo ""
        echo "🗄️ Banco de Dados:"
        echo "  db-query       - Consultar itens do banco"
        echo "  migration MSG  - Criar nova migration"
        echo "  migrate        - Aplicar migrations"
        echo "  backup-db      - Fazer backup do banco"
        echo ""
        echo "🐍 Backend:"
        echo "  add-dependency LIB - Adicionar dependência Python"
        echo "  test           - Executar testes"
        echo "  format         - Formatar código"
        echo "  shell-backend  - Acessar shell do backend"
        echo ""
        echo "🌐 Frontend:"
        echo "  version-frontend N - Atualizar versão dos arquivos"
        echo "  shell-frontend - Acessar shell do frontend"
        echo ""
        echo "💡 Exemplo: ./scripts/dev-commands.sh start"
        ;;
esac