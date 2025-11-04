import json
from decimal import Decimal

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from .config.database import engine
from .models import Base
from .routers.auth_routes import auth_router
from .routers.item_routes import item_router
from .routers.order_routes import order_router
from .routers.user_routes import user_router
from .utils.init_db import init_database


def decimal_default(obj):
    """Conversor JSON customizado para Decimal"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def safe_float_to_decimal(value):
    """Converte float para decimal seguro com 2 casas decimais"""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        # Arredondar para 2 casas decimais para evitar problemas de precisão
        return round(float(value), 2)
    return value


def convert_model_floats(obj):
    """Converte campos float de modelos para valores seguros"""
    if hasattr(obj, '__dict__'):
        # É um modelo SQLAlchemy
        model_dict = {}
        for key, value in obj.__dict__.items():
            if not key.startswith('_'):
                if isinstance(value, float):
                    model_dict[key] = safe_float_to_decimal(value)
                elif isinstance(value, list):
                    model_dict[key] = [convert_model_floats(item) for item in value]
                elif hasattr(value, '__dict__'):
                    model_dict[key] = convert_model_floats(value)
                else:
                    model_dict[key] = value
        return model_dict
    elif isinstance(obj, list):
        return [convert_model_floats(item) for item in obj]
    else:
        return obj

# Criar as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Inicializar dados padrão (usuário admin)
init_database()

app = FastAPI(
    title='Pizzaria API', 
    description='API para sistema de pizzaria', 
    version='1.0.0',
    # Configurar encoder customizado para Decimal
    json_encoders={
        Decimal: lambda v: float(v) if v is not None else None
    }
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost",
        "http://127.0.0.1"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Incluir os roteadores
app.include_router(auth_router)
app.include_router(order_router)
app.include_router(item_router)
app.include_router(user_router)


@app.get('/')
async def root():
    return {'message': 'Pizzaria API - Sistema de Pedidos'}
