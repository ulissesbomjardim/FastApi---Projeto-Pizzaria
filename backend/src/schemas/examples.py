"""
Exemplo de uso dos schemas Pydantic criados
Este arquivo demonstra como usar os schemas em suas rotas
"""

# Exemplo de como usar os schemas nas rotas do FastAPI

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Importar dependências
from backend.src.config.database import get_db
from backend.src.config.security import bcrypt_context

# Importar os schemas
from backend.src.schemas import (
    ErrorResponse,
    MessageResponse,
    PaginatedResponse,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
)

# Exemplo de router usando os schemas
example_router = APIRouter(prefix='/examples', tags=['examples'])

# === EXEMPLO 1: Criação de usuário com validação completa ===
@example_router.post('/users', response_model=UserResponse)
async def create_user_example(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Exemplo de criação de usuário usando schema com validações:
    - Email válido
    - Username apenas letras, números e underscore
    - Senha forte (maiúscula, minúscula, número, especial)
    - Confirmação de senha
    """
    # O Pydantic já validou todos os dados aqui!
    # user_data.password já foi validado como senha forte
    # user_data.email já foi validado como email válido
    # user_data.confirm_password já foi verificado se bate com password

    try:
        # Hash da senha
        from ..config.security import hash_password
        hashed_password = hash_password(user_data.password)

        # Criar usuário no banco (exemplo)
        # new_user = User(
        #     username=user_data.username,
        #     email=user_data.email,
        #     hashed_password=hashed_password
        # )
        # db.add(new_user)
        # db.commit()
        # db.refresh(new_user)

        # Exemplo de resposta usando schema
        return {
            'id': 1,
            'username': user_data.username,
            'email': user_data.email,
            'is_active': True,
            'is_admin': False,
            'created_at': '2025-11-02T10:00:00',
            'updated_at': '2025-11-02T10:00:00',
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Erro ao criar usuário')


# === EXEMPLO 2: Login com schema de resposta estruturada ===
@example_router.post('/login', response_model=Token)
async def login_example(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Exemplo de login retornando token estruturado
    """
    # O campo email_or_username permite login com email ou username
    # Pydantic já validou que os campos não estão vazios

    try:
        # Buscar usuário e validar senha (exemplo)
        # user = get_user_by_email_or_username(login_data.email_or_username, db)
        # if not user or not bcrypt_context.verify(login_data.password, user.hashed_password):
        #     raise HTTPException(status_code=401, detail="Credenciais inválidas")

        # Gerar token JWT (exemplo)
        # access_token = create_access_token(data={"sub": user.username})

        return {
            'access_token': 'exemplo.jwt.token',
            'token_type': 'bearer',
            'expires_in': 1800,  # 30 minutos
            'user': {
                'id': 1,
                'username': 'exemplo_user',
                'email': 'exemplo@email.com',
                'is_active': True,
                'is_admin': False,
                'created_at': '2025-11-02T10:00:00',
                'updated_at': '2025-11-02T10:00:00',
            },
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Credenciais inválidas')


# === EXEMPLO 3: Resposta de erro padronizada ===
@example_router.get('/error-example')
async def error_example():
    """
    Exemplo de como retornar erro padronizado
    """
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            'error': 'not_found',
            'message': 'Recurso não encontrado',
            'details': {'resource': 'user', 'id': 999},
            'timestamp': '2025-11-02T10:00:00Z',
            'success': False,
        },
    )


# === EXEMPLO 4: Resposta de sucesso simples ===
@example_router.delete('/users/{user_id}', response_model=MessageResponse)
async def delete_user_example(user_id: int):
    """
    Exemplo de resposta simples de sucesso
    """
    # Lógica de exclusão aqui...

    return {'message': f'Usuário {user_id} excluído com sucesso', 'success': True, 'timestamp': '2025-11-02T10:00:00Z'}


# === EXEMPLO 5: Lista paginada com metadados ===
@example_router.get('/users', response_model=PaginatedResponse)
async def list_users_example(page: int = 1, per_page: int = 20):
    """
    Exemplo de lista paginada com metadados
    """
    # Simular dados de usuários
    users_data = [
        {
            'id': i,
            'username': f'user_{i}',
            'email': f'user{i}@example.com',
            'is_active': True,
            'is_admin': False,
            'created_at': '2025-11-02T10:00:00',
            'updated_at': '2025-11-02T10:00:00',
        }
        for i in range(1, 6)  # 5 usuários exemplo
    ]

    return {
        'data': users_data,
        'meta': {
            'current_page': page,
            'per_page': per_page,
            'total_items': 100,  # Total simulado
            'total_pages': 5,
            'has_next': page < 5,
            'has_previous': page > 1,
        },
        'success': True,
        'timestamp': '2025-11-02T10:00:00Z',
    }


# === VALIDAÇÕES AUTOMÁTICAS DOS SCHEMAS ===
"""
Exemplos de validações que acontecem automaticamente:

1. UserCreate:
   - Email deve ser válido (user@domain.com)
   - Username: mín 3, máx 50 chars, só letras/números/underscore
   - Password: mín 8 chars, deve ter maiúscula + minúscula + número + especial
   - Confirm_password deve ser igual ao password

2. UserLogin:
   - email_or_username não pode estar vazio
   - password não pode estar vazio

3. OrderCreate:
   - customer_name: mín 2, máx 100 chars
   - customer_phone: formato (XX) XXXX-XXXX ou (XX) XXXXX-XXXX  
   - items: deve ter pelo menos 1 item
   - payment_method: deve ser um dos valores do enum

4. OrderItemCreate:
   - quantity: deve ser > 0 e <= 10
   - item_id: deve ser um inteiro válido
   - observations: máx 200 chars

5. AddressBase:
   - zip_code: formato XXXXX-XXX (CEP brasileiro)
   - state: apenas 2 letras (UF)
   - street: mín 5, máx 200 chars

Todas essas validações acontecem ANTES da função da rota ser executada!
Se alguma validação falhar, FastAPI retorna automaticamente erro 422.
"""
