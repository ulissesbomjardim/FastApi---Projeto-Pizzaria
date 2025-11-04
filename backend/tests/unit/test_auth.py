"""
Testes unitários para autenticação e segurança
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from fastapi import HTTPException
from jose import JWTError, jwt

# Adicionar o diretório backend ao sys.path se necessário
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.config.security import (
    ALGORITHM,
    SECRET_KEY,
    hash_password,
    verify_admin_access,
    verify_password,
    verify_refresh_token,
    verify_token,
)
from src.models import User


@pytest.mark.unit
@pytest.mark.auth
class TestPasswordHashing:
    """Testes para hash de senhas"""

    def test_password_hashing(self):
        """Testar hash de senha"""
        password = 'testpassword123'
        hashed = hash_password(password)

        assert hashed != password
        assert verify_password(password, hashed)

    def test_password_verification_fails_with_wrong_password(self):
        """Testar que senha incorreta falha na verificação"""
        password = 'testpassword123'
        wrong_password = 'wrongpassword'
        hashed = hash_password(password)

        assert not verify_password(wrong_password, hashed)


@pytest.mark.unit
@pytest.mark.auth
class TestJWTTokens:
    """Testes para tokens JWT"""

    def test_create_and_verify_access_token(self):
        """Testar criação e verificação de access token"""
        user_id = 1
        token_data = {'sub': str(user_id), 'type': 'access', 'exp': datetime.utcnow() + timedelta(minutes=30)}
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        # Decodificar token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        assert payload['sub'] == str(user_id)
        assert payload['type'] == 'access'

    def test_create_and_verify_refresh_token(self):
        """Testar criação e verificação de refresh token"""
        user_id = 1
        token_data = {'sub': str(user_id), 'type': 'refresh', 'exp': datetime.utcnow() + timedelta(days=7)}
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        # Decodificar token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        assert payload['sub'] == str(user_id)
        assert payload['type'] == 'refresh'

    def test_expired_token_raises_error(self):
        """Testar que token expirado gera erro"""
        user_id = 1
        token_data = {
            'sub': str(user_id),
            'type': 'access',
            'exp': datetime.utcnow() - timedelta(minutes=1),  # Token expirado
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        with pytest.raises(JWTError):
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    def test_invalid_token_raises_error(self):
        """Testar que token inválido gera erro"""
        invalid_token = 'invalid.token.here'

        with pytest.raises(JWTError):
            jwt.decode(invalid_token, SECRET_KEY, algorithms=[ALGORITHM])


@pytest.mark.unit
@pytest.mark.auth
class TestTokenVerification:
    """Testes para verificação de tokens"""

    def test_verify_valid_access_token(self):
        """Testar verificação de access token válido"""
        user_id = 1
        token_data = {'sub': str(user_id), 'type': 'access', 'exp': datetime.utcnow() + timedelta(minutes=30)}
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        # Pass the token string directly
        result = verify_token(token)
        assert result == user_id

    def test_verify_refresh_token_as_access_fails(self):
        """Testar que refresh token falha como access token"""
        user_id = 1
        token_data = {
            'sub': str(user_id),
            'type': 'refresh',  # Refresh token usado como access
            'exp': datetime.utcnow() + timedelta(days=7),
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)

        assert exc_info.value.status_code == 401
        assert 'tipo incorreto' in str(exc_info.value.detail)

    def test_verify_valid_refresh_token(self):
        """Testar verificação de refresh token válido"""
        user_id = 1
        token_data = {'sub': str(user_id), 'type': 'refresh', 'exp': datetime.utcnow() + timedelta(days=7)}
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        result = verify_refresh_token(token)
        assert result == user_id

    def test_verify_access_token_as_refresh_fails(self):
        """Testar que access token falha como refresh token"""
        user_id = 1
        token_data = {
            'sub': str(user_id),
            'type': 'access',  # Access token usado como refresh
            'exp': datetime.utcnow() + timedelta(minutes=30),
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        with pytest.raises(HTTPException) as exc_info:
            verify_refresh_token(token)

        assert exc_info.value.status_code == 401


@pytest.mark.unit
@pytest.mark.auth
class TestAdminVerification:
    """Testes para verificação de permissões de admin"""

    def test_verify_admin_access_success(self, test_db, create_test_user):
        """Testar verificação bem-sucedida de admin"""
        # Criar usuário admin
        admin_user = create_test_user(is_admin=True)

        # Verificar acesso admin
        result = verify_admin_access(admin_user.id, test_db)

        assert result.id == admin_user.id
        assert result.is_admin is True

    def test_verify_admin_access_fails_for_regular_user(self, test_db, create_test_user):
        """Testar que usuário comum falha na verificação de admin"""
        # Criar usuário comum
        regular_user = create_test_user(is_admin=False)

        # Verificar que falha
        with pytest.raises(HTTPException) as exc_info:
            verify_admin_access(regular_user.id, test_db)

        assert exc_info.value.status_code == 403
        assert 'Apenas administradores' in str(exc_info.value.detail)

    def test_verify_admin_access_fails_for_nonexistent_user(self, test_db):
        """Testar que usuário inexistente falha na verificação"""
        nonexistent_user_id = 999

        with pytest.raises(HTTPException) as exc_info:
            verify_admin_access(nonexistent_user_id, test_db)

        assert exc_info.value.status_code == 404
        assert 'Usuário não encontrado' in str(exc_info.value.detail)


@pytest.mark.unit
@pytest.mark.auth
class TestTokenEdgeCases:
    """Testes para casos extremos com tokens"""

    def test_token_without_sub_fails(self):
        """Testar token sem campo 'sub'"""
        token_data = {
            'type': 'access',
            'exp': datetime.utcnow() + timedelta(minutes=30)
            # 'sub' ausente
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)

        assert exc_info.value.status_code == 401
        assert 'sub não encontrado' in str(exc_info.value.detail)

    def test_token_with_invalid_user_id_fails(self):
        """Testar token com user_id inválido"""
        token_data = {
            'sub': 'not_a_number',  # ID inválido
            'type': 'access',
            'exp': datetime.utcnow() + timedelta(minutes=30),
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)

        assert exc_info.value.status_code == 401
        assert 'user_id inválido' in str(exc_info.value.detail)

    def test_token_without_type_is_accepted_as_legacy(self):
        """Testar que token sem tipo é aceito como legacy access token"""
        user_id = 1
        token_data = {
            'sub': str(user_id),
            # Sem campo 'type' - token legacy
            'exp': datetime.utcnow() + timedelta(minutes=30),
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        from fastapi.security import HTTPAuthorizationCredentials

        result = verify_token(token)
        assert result == user_id
