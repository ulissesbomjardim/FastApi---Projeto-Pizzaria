#!/bin/bash

# Script para executar o projeto Pizzaria no Docker via WSL Ubuntu

set -e

echo "🍕 Pizzaria Docker Setup - WSL Ubuntu"
echo "===================================="

# Verificar se está no WSL
if ! grep -qi microsoft /proc/version; then
    echo "❌ Este script deve ser executado no WSL Ubuntu!"
    exit 1
fi

# Verificar se o Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado!"
    echo "💡 Execute: sudo apt update && sudo apt install docker.io docker-compose"
    exit 1
fi

# Verificar se o Docker Compose está disponível
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado!"
    echo "💡 Execute: sudo apt install docker-compose"
    exit 1
fi

# Verificar se o usuário está no grupo docker
if ! groups $USER | grep -q docker; then
    echo "⚠️  Usuário não está no grupo docker"
    echo "💡 Execute: sudo usermod -aG docker $USER"
    echo "💡 Depois faça logout e login novamente"
    exit 1
fi

# Navegar para o diretório do projeto (assumindo que está em /mnt/g/...)
PROJECT_DIR="/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Diretório do projeto não encontrado: $PROJECT_DIR"
    echo "💡 Ajuste o caminho no script se necessário"
    exit 1
fi

cd "$PROJECT_DIR"

echo "📁 Diretório atual: $(pwd)"

# Função para mostrar menu
show_menu() {
    echo ""
    echo "🔧 Escolha uma opção:"
    echo "1) 🚀 Buildar e subir todos os serviços"
    echo "2) 📦 Apenas buildar as imagens"
    echo "3) ⬆️  Subir serviços existentes"
    echo "4) ⬇️  Parar todos os serviços"
    echo "5) 📊 Ver status dos serviços"
    echo "6) 📝 Ver logs em tempo real"
    echo "7) 🗑️  Limpar tudo (containers, volumes, imagens)"
    echo "8) 🌱 Popular banco com dados de teste"
    echo "9) 🌐 Mostrar URLs dos serviços"
    echo "0) 🚪 Sair"
    echo ""
    read -p "Digite sua escolha [0-9]: " choice
}

# Loop do menu
while true; do
    show_menu
    
    case $choice in
        1)
            echo "🚀 Buildando e subindo todos os serviços..."
            sudo docker-compose --env-file docker/.env build --no-cache
            sudo docker-compose --env-file docker/.env up -d
            echo "✅ Serviços iniciados!"
            sudo docker-compose --env-file docker/.env ps
            ;;
        2)
            echo "📦 Buildando imagens..."
            sudo docker-compose --env-file docker/.env build --no-cache
            echo "✅ Build concluído!"
            ;;
        3)
            echo "⬆️  Subindo serviços..."
            sudo docker-compose --env-file docker/.env up -d
            echo "✅ Serviços iniciados!"
            sudo docker-compose --env-file docker/.env ps
            ;;
        4)
            echo "⬇️  Parando serviços..."
            sudo docker-compose --env-file docker/.env down
            echo "✅ Serviços parados!"
            ;;
        5)
            echo "📊 Status dos serviços:"
            sudo docker-compose --env-file docker/.env ps
            ;;
        6)
            echo "📝 Logs em tempo real (Ctrl+C para sair):"
            sudo docker-compose --env-file docker/.env logs -f
            ;;
        7)
            echo "🗑️  Limpando tudo..."
            read -p "⚠️  Tem certeza? Isso removerá todos os containers, volumes e imagens! (y/N): " confirm
            if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
                sudo docker-compose --env-file docker/.env down -v --rmi all --remove-orphans
                sudo docker system prune -f
                echo "✅ Limpeza concluída!"
            else
                echo "❌ Operação cancelada"
            fi
            ;;
        8)
            echo "🌱 Populando banco com dados de teste..."
            sudo docker-compose --env-file docker/.env exec backend python backend/utils/populate_menu.py
            echo "✅ Dados inseridos!"
            ;;
        9)
            echo "🌐 URLs dos serviços:"
            echo "  Frontend:  http://localhost:3000"
            echo "  Backend:   http://localhost:8000"
            echo "  API Docs:  http://localhost:8000/docs"
            echo "  PgAdmin:   http://localhost:5050"
            echo "  PostgreSQL: localhost:5432"
            ;;
        0)
            echo "👋 Saindo..."
            exit 0
            ;;
        *)
            echo "❌ Opção inválida! Tente novamente."
            ;;
    esac
    
    echo ""
    read -p "Pressione Enter para continuar..."
done