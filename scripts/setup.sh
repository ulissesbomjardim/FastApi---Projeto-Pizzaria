#!/bin/bash
# 🚀 Script de Setup Completo do Projeto Hashtag Pizzaria
# Uso: ./scripts/setup.sh

set -e  # Para na primeira falha

PROJECT_PATH="/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria"
echo "🍕 Iniciando setup do projeto Hashtag Pizzaria..."

# Navegar para o diretório do projeto
cd "$PROJECT_PATH"

echo "📋 Verificando dependências..."

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado! Instale o Docker primeiro."
    exit 1
fi

# Verificar se Docker Compose está disponível
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose não encontrado!"
    exit 1
fi

# Verificar se Poetry está instalado
if ! command -v poetry &> /dev/null; then
    echo "⚠️  Poetry não encontrado. Instalando..."
    curl -sSL https://install.python-poetry.org | python3 - || pip install poetry
fi

echo "✅ Dependências verificadas!"

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker compose down 2>/dev/null || true

# Limpar sistema Docker (opcional)
echo "🧹 Limpando cache do Docker..."
docker system prune -f

# Verificar se arquivo .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado. Criando..."
    cat > .env << 'EOL'
# Chave secreta para JWT
SECRET_KEY=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

# Configurações do PostgreSQL
POSTGRES_DB=pizzaria_db
POSTGRES_USER=pizzaria_user
POSTGRES_PASSWORD=pizzaria_password123

# Configurações do banco de dados
DATABASE_URL=postgresql://pizzaria_user:pizzaria_password123@postgres:5432/pizzaria_db

# Configurações da aplicação
DEBUG=True
ENVIRONMENT=development

# Configurações do usuário admin padrão
ADMIN_EMAIL=admin@pizzaria.com
ADMIN_PASSWORD=Admin123!@#
EOL
    echo "✅ Arquivo .env criado!"
fi

# Setup do backend com Poetry
echo "🐍 Configurando backend com Poetry..."
cd backend
poetry install
cd ..

# Construir e subir containers
echo "🐳 Construindo e subindo containers Docker..."
docker compose up -d --build

# Aguardar containers ficarem saudáveis
echo "⏳ Aguardando containers ficarem prontos..."
sleep 30

# Verificar se containers estão rodando
echo "🔍 Verificando status dos containers..."
docker compose ps

# Testar conectividade
echo "🌐 Testando conectividade..."
for i in {1..10}; do
    if curl -s http://localhost:3000 > /dev/null; then
        echo "✅ Frontend funcionando!"
        break
    fi
    echo "⏳ Aguardando frontend... (tentativa $i/10)"
    sleep 5
done

for i in {1..10}; do
    if curl -s http://localhost:8000 > /dev/null; then
        echo "✅ Backend funcionando!"
        break
    fi
    echo "⏳ Aguardando backend... (tentativa $i/10)"
    sleep 5
done

# Verificar dados no banco
echo "📊 Verificando dados do banco..."
docker exec pizzaria_backend python -c "
from backend.src.config.database import get_db
from backend.src.models.item import Item
try:
    db = next(get_db())
    count = db.query(Item).count()
    print(f'✅ Banco funcionando! {count} itens encontrados.')
except Exception as e:
    print(f'❌ Erro no banco: {e}')
"

echo ""
echo "🎉 Setup concluído com sucesso!"
echo "📋 URLs disponíveis:"
echo "   🌐 Frontend: http://localhost:3000"
echo "   🔧 Backend:  http://localhost:8000"
echo "   📊 PgAdmin:  http://localhost:5050"
echo ""
echo "👥 Credenciais padrão:"
echo "   📧 Admin: admin@pizzaria.com"
echo "   🔒 Senha: Admin123!@#"
echo ""
echo "💡 Para ver logs: docker compose logs -f"
echo "💡 Para parar: docker compose down"