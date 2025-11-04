import os

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

# Carregar variáveis de ambiente
load_dotenv()

# Chave secreta para JWT
SECRET_KEY = os.getenv('SECRET_KEY', 'secret')

# Algoritmo para JWT
ALGORITHM = 'HS256'

# Tempo de expiração do token (30 minutos)
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Usar bcrypt diretamente em vez de passlib
import bcrypt

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")


def hash_password(password: str) -> str:
    """
    Hash da senha usando bcrypt diretamente com truncamento seguro
    """
    # Truncar a senha para 72 bytes para compatibilidade com bcrypt
    password_bytes = password.encode('utf-8')[:72]
    
    # Gerar salt e fazer hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Retornar como string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar senha usando bcrypt diretamente com truncamento seguro
    """
    try:
        # Truncar a senha para 72 bytes para compatibilidade com bcrypt
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        
        # Verificar usando bcrypt diretamente
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        # Em caso de erro, retornar False (senha inválida)
        return False


def verify_token(token: str = Depends(oauth2_schema)):
    """
    Função para verificar e decodificar o access token JWT
    """
    try:
        # Decodificar o token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Verificar se é um access token (ou token antigo sem tipo)
        token_type = payload.get('type')
        if token_type is not None and token_type != 'access':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token inválido - tipo incorreto. Use access token para autenticação.',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        user_id_str = payload.get('sub')

        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token inválido - sub não encontrado',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        # Converter para int se necessário
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token inválido - user_id inválido',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        return user_id

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Access token inválido ou expirado',
            headers={'WWW-Authenticate': 'Bearer'},
        )


def get_current_user(user_id: int = Depends(verify_token)):
    """
    Função para obter o usuário atual baseado no token
    Nota: Deve ser usada junto com Depends(get_db) no endpoint
    """
    return user_id


def get_current_user_optional():
    """
    Função para obter o usuário atual baseado no token (opcional - não gera erro se token inválido)
    """
    from fastapi import Request

    def _get_optional_user(request: Request):
        try:
            # Tentar extrair o token do header Authorization
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return None

            token = auth_header.split(' ')[1]

            # Decodificar o token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # Verificar se é um access token (ou token antigo sem tipo)
            token_type = payload.get('type')
            if token_type is not None and token_type != 'access':
                return None

            user_id_str = payload.get('sub')
            if user_id_str is None:
                return None

            # Converter para int se necessário
            try:
                user_id = int(user_id_str)
                return user_id
            except (ValueError, TypeError):
                return None

        except (JWTError, Exception):
            return None

    return _get_optional_user


def verify_refresh_token(refresh_token: str):
    """
    Função para verificar e decodificar o refresh token JWT
    """
    try:
        # Decodificar o token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        # Verificar se é um refresh token
        token_type = payload.get('type')
        if token_type != 'refresh':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token inválido - tipo incorreto. Use refresh token.',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        user_id_str = payload.get('sub')

        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token inválido - sub não encontrado',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        # Converter para int se necessário
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token inválido - user_id inválido',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        return user_id

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Refresh token inválido ou expirado',
            headers={'WWW-Authenticate': 'Bearer'},
        )


def verify_admin_access(current_user_id: int, db: Session):
    """
    Função para verificar se o usuário atual é administrador
    """
    from ..models.user import User

    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuário não encontrado')
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Acesso negado. Apenas administradores podem realizar esta ação.',
        )
    return user
