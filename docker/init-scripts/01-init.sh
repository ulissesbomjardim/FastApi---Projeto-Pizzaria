#!/bin/bash
set -e

# Criar banco se não existir
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Configurações de desempenho
    ALTER DATABASE $POSTGRES_DB SET timezone TO 'America/Sao_Paulo';
    
    -- Criar extensões úteis
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    -- Log de inicialização
    SELECT 'Banco de dados pizzaria_db inicializado com sucesso!' as status;
EOSQL