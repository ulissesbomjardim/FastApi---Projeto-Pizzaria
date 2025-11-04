# 🚀 Instalação Rápida - GitHub

## ⚡ Setup em 3 Passos

### 1️⃣ **Clone e Configure**
```bash
git clone https://github.com/ulissesbomjardim/FastApi---Projeto-Pizzaria.git
cd "FastApi - Projeto Pizzaria"
cp .env.example .env
```

### 2️⃣ **Edite o .env**
Abra o arquivo `.env` e ajuste:
- `SECRET_KEY` - Gere uma chave segura
- `POSTGRES_PASSWORD` - Defina senha do banco
- Outras configurações conforme necessário

### 3️⃣ **Execute com Docker**
```bash
docker-compose up -d
```

## 🌐 **Acessos**
- **Frontend:** http://localhost:3000
- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs

## 👤 **Login Padrão**
- **Email:** admin@pizzaria.com  
- **Senha:** Admin123!@#

---

**📖 Documentação completa:** Veja o [README.md](README.md) principal para detalhes técnicos completos.