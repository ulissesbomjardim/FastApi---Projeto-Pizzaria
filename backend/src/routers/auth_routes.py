from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from ..config.database import get_db
from ..config.security import ALGORITHM, SECRET_KEY, get_current_user_optional, hash_password, oauth2_schema, verify_password
from ..models import User
from ..schemas import (
    MessageResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
)

auth_router = APIRouter(prefix='/auth', tags=['auth'])


@auth_router.get('/')
async def home():
    """
    Rota padrão de autenticação
    """
    return {'message': 'rota de autenticação', 'autenticado': False}


@auth_router.post('/register', response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Rota para registro público de usuário (sempre cria usuário comum)
    """
    # Verificar se usuário já existe por email
    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail='E-mail já existe')

    # Verificar se username já existe
    existing_username = db.query(User).filter(User.username == user_data.username).first()

    if existing_username:
        raise HTTPException(status_code=400, detail='Nome de usuário já existe')

    # Criar novo usuário (sempre como usuário comum)
    hashed_password = hash_password(user_data.password)

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=False,  # Sempre False para registro público
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@auth_router.post('/create-admin', response_model=UserResponse)
async def create_admin_user(
    user_data: UserCreate, 
    current_user_id: int | None = Depends(get_current_user_optional()),
    db: Session = Depends(get_db)
):
    """
    Rota para criar um novo usuário administrador (apenas admins podem usar)
    """
    # Verificar se há um usuário logado
    if current_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Acesso negado. Apenas administradores podem criar outros administradores.'
        )
    
    # Verificar se o usuário atual é admin
    from ..config.security import verify_admin_access
    try:
        verify_admin_access(current_user_id, db)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Acesso negado. Apenas administradores podem criar outros administradores.'
        )

    # Verificar se usuário já existe por email
    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail='E-mail já existe')

    # Verificar se username já existe
    existing_username = db.query(User).filter(User.username == user_data.username).first()

    if existing_username:
        raise HTTPException(status_code=400, detail='Nome de usuário já existe')

    # Criar novo usuário admin
    hashed_password = hash_password(user_data.password)

    new_admin = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=True,  # Criar como admin
    )

    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return new_admin


def criar_access_token(user_id: int) -> str:
    """
    Função para criar um access token JWT para o usuário autenticado
    user_id: ID do usuário
    Válido por 30 minutos
    """
    expiration = datetime.utcnow() + timedelta(minutes=30)
    token = jwt.encode({'sub': str(user_id), 'exp': expiration, 'type': 'access'}, SECRET_KEY, algorithm=ALGORITHM)
    return token


def criar_refresh_token(user_id: int) -> str:
    """
    Função para criar um refresh token JWT para o usuário autenticado
    user_id: ID do usuário
    Válido por 7 dias
    """
    expiration = datetime.utcnow() + timedelta(days=7)
    token = jwt.encode({'sub': str(user_id), 'exp': expiration, 'type': 'refresh'}, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verificar_refresh_token(refresh_token: str) -> int:
    """
    Função para verificar e decodificar o refresh token JWT
    Retorna o user_id se o token for válido
    """
    try:
        # Decodificar o token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        # Verificar se é um refresh token
        token_type = payload.get('type')
        if token_type != 'refresh':
            raise HTTPException(status_code=401, detail='Token inválido - tipo incorreto')

        # Obter user_id
        user_id_str = payload.get('sub')
        if user_id_str is None:
            raise HTTPException(status_code=401, detail='Token inválido - sub não encontrado')

        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(status_code=401, detail='Token inválido - user_id inválido')

        return user_id

    except JWTError:
        raise HTTPException(status_code=401, detail='Refresh token inválido ou expirado')


@auth_router.post('/login', response_model=Token)
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Rota para autenticação de usuário
    """

    # Buscar usuário por email ou username
    user = (
        db.query(User)
        .filter((User.email == login_data.email_or_username) | (User.username == login_data.email_or_username))
        .first()
    )

    # Verificar se usuário existe e senha está correta
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Email/usuário ou senha incorretos')

    # Verificar se usuário está ativo
    if not user.is_active:
        raise HTTPException(status_code=401, detail='Usuário desativado')

    else:
        access_token = criar_access_token(user.id)
        refresh_token = criar_refresh_token(user.id)

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer',
        'expires_in': 1800,  # 30 minutos para access token
        'refresh_expires_in': 604800,  # 7 dias para refresh token
        'user': user,
    }


@auth_router.post('/login-form', response_model=Token)
async def login_user_form(dados_formulario: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Rota para autenticação de usuário
    """

    # Buscar usuário por email ou username
    user = (
        db.query(User)
        .filter((User.email == dados_formulario.username) | (User.username == dados_formulario.username))
        .first()
    )

    # Verificar se usuário existe e senha está correta
    if not user or not verify_password(dados_formulario.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Email/usuário ou senha incorretos')

    # Verificar se usuário está ativo
    if not user.is_active:
        raise HTTPException(status_code=401, detail='Usuário desativado')

    # Gerar tokens
    access_token = criar_access_token(user.id)
    refresh_token = criar_refresh_token(user.id)

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer',
        'expires_in': 1800,  # 30 minutos para access token
        'refresh_expires_in': 604800,  # 7 dias para refresh token
        'user': user,
    }


@auth_router.post('/refresh', response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
    current_user_id: int | None = Depends(get_current_user_optional()),
):
    """
    Rota para renovar o access token usando o refresh token
    Verifica se há um access token válido primeiro, senão usa o refresh token
    """
    try:
        user_id = None

        # Se houver um access token válido, usar ele
        if current_user_id is not None:
            user_id = current_user_id
        else:
            # Caso contrário, verificar e decodificar o refresh token
            from ..config.security import verify_refresh_token

            user_id = verify_refresh_token(refresh_data.refresh_token)

        # Buscar o usuário no banco de dados
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuário não encontrado')

        # Verificar se o usuário ainda está ativo
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Usuário desativado')

        # Gerar novos tokens
        new_access_token = criar_access_token(user.id)
        new_refresh_token = criar_refresh_token(user.id)

        return {
            'access_token': new_access_token,
            'refresh_token': new_refresh_token,
            'token_type': 'bearer',
            'expires_in': 1800,  # 30 minutos para access token
            'refresh_expires_in': 604800,  # 7 dias para refresh token
        }

    except HTTPException:
        # Re-raise HTTPException para manter o status code correto
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Erro interno do servidor: {str(e)}'
        )
