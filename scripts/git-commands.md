# 📝 Comandos Git para o Projeto

## Inicialização do Repositório
```bash
# Inicializar Git (já feito se clonou)
git init

# Adicionar origin (URL do projeto)
git remote add origin https://github.com/ulissesbomjardim/FastApi---Projeto-Pizzaria.git

# Primeiro commit
git add .
git commit -m "🎉 Projeto Hashtag Pizzaria - Sistema completo finalizado

✅ Backend FastAPI com JWT
✅ Frontend responsivo  
✅ Painel administrativo
✅ Sistema de pedidos
✅ Docker containerizado
✅ Documentação completa
✅ 123+ testes passando

Projeto pronto para produção!"

# Push inicial
git push -u origin main
```

## Commits Recomendados para Organização
```bash
# Se quiser organizar em commits separados:

# 1. Backend
git add backend/ alembic/ pyproject.toml requirements.txt
git commit -m "🔧 Backend: FastAPI + PostgreSQL + JWT + Testes"

# 2. Frontend  
git add frontend/
git commit -m "🎨 Frontend: Interface responsiva + Admin panel + AuthManager"

# 3. DevOps
git add docker/ docker-compose.yml Dockerfile.* nginx.conf
git commit -m "🐳 Docker: Containerização completa com PostgreSQL"

# 4. Documentação
git add docs/ README.md *.md
git commit -m "📚 Docs: Documentação completa + troubleshooting + setup"

# 5. Configuração
git add .env.example .gitignore Makefile scripts/
git commit -m "⚙️ Config: Ambiente + scripts + configurações"
```

## Comandos Úteis
```bash
# Verificar status
git status

# Ver diferenças
git diff

# Histórico
git log --oneline

# Branches
git branch
git checkout -b feature/nova-funcionalidade

# Sincronizar
git pull origin main
git push origin main
```

## Estrutura de Branches Sugerida
```
main          - Código de produção
develop       - Desenvolvimento principal  
feature/*     - Novas funcionalidades
hotfix/*      - Correções urgentes
release/*     - Preparação de releases
```

## Tags para Releases
```bash
# Criar tag de versão
git tag -a v1.0.0 -m "🚀 Release v1.0.0 - Sistema completo"
git push origin v1.0.0

# Listar tags
git tag
```