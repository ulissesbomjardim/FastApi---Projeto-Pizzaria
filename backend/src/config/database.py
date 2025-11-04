import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuração do banco de dados
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./backend/database/database.db')

# Configuração específica baseada no tipo de banco
if DATABASE_URL.startswith('postgresql'):
    # PostgreSQL (Docker/Produção)
    engine = create_engine(DATABASE_URL, echo=False)
elif DATABASE_URL.startswith('sqlite'):
    # SQLite (Desenvolvimento local)
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    DATABASE_DIR = BASE_DIR / 'database'
    DATABASE_DIR.mkdir(exist_ok=True)
    
    if not DATABASE_URL.startswith('sqlite:///./'):
        DATABASE_URL = f'sqlite:///{DATABASE_DIR}/database.db'
    
    engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
else:
    raise ValueError(f"Tipo de banco não suportado: {DATABASE_URL}")

# SessionLocal para criar sessões do banco
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

# Dependency para obter a sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
