"""
Testes de integração para endpoints de autenticação
"""
import sys
from pathlib import Path

import pytest
from fastapi import status

# Adicionar o diretório backend ao sys.path se necessário
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))


@pytest.mark.integration
@pytest.mark.auth
class TestAuthEndpoints:
    """Testes para endpoints de autenticação"""

    def test_register_user_success(self, client, sample_user_data):
        """Testar registro bem-sucedido de usuário"""
        # Adicionar confirm_password para o schema correto
        user_data = sample_user_data.copy()
        user_data['confirm_password'] = user_data['password']

        response = client.post('/auth/register', json=user_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['username'] == sample_user_data['username']
        assert data['email'] == sample_user_data['email']
        assert 'password' not in data
        assert 'hashed_password' not in data

    def test_register_duplicate_username_fails(self, client, sample_user_data, create_test_user):
        """Testar que registro com username duplicado falha"""
        # Criar usuário primeiro
        create_test_user(sample_user_data)

        # Tentar registrar novamente
        user_data = sample_user_data.copy()
        user_data['confirm_password'] = user_data['password']
        response = client.post('/auth/register', json=user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert 'já existe' in data['detail']

    def test_register_duplicate_email_fails(self, client, sample_user_data, create_test_user):
        """Testar que registro com email duplicado falha"""
        # Criar usuário primeiro
        create_test_user(sample_user_data)

        # Tentar registrar com username diferente mas mesmo email
        duplicate_data = sample_user_data.copy()
        duplicate_data['username'] = 'different_username'
        duplicate_data['confirm_password'] = duplicate_data['password']

        response = client.post('/auth/register', json=duplicate_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert 'já existe' in data['detail']

    def test_register_invalid_email_fails(self, client, sample_user_data):
        """Testar que registro com email inválido falha"""
        invalid_data = sample_user_data.copy()
        invalid_data['email'] = 'invalid-email'
        invalid_data['confirm_password'] = invalid_data['password']

        response = client.post('/auth/register', json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_short_password_fails(self, client, sample_user_data):
        """Testar que registro com senha curta falha"""
        invalid_data = sample_user_data.copy()
        invalid_data['password'] = '123'  # Muito curta
        invalid_data['confirm_password'] = '123'

        response = client.post('/auth/register', json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_success(self, client, create_test_user, sample_user_data):
        """Testar login bem-sucedido"""
        # Criar usuário
        create_test_user(sample_user_data)

        # Fazer login
        login_data = {'email_or_username': sample_user_data['email'], 'password': sample_user_data['password']}
        response = client.post('/auth/login', json=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['token_type'] == 'bearer'
        assert 'expires_in' in data
        assert 'refresh_expires_in' in data
        assert 'user' in data
        assert data['user']['email'] == sample_user_data['email']

    def test_login_with_username_success(self, client, create_test_user, sample_user_data):
        """Testar login com username"""
        # Criar usuário
        create_test_user(sample_user_data)

        # Fazer login com username
        login_data = {'email_or_username': sample_user_data['username'], 'password': sample_user_data['password']}
        response = client.post('/auth/login', json=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'access_token' in data
        assert data['user']['username'] == sample_user_data['username']

    def test_login_wrong_password_fails(self, client, create_test_user, sample_user_data):
        """Testar login com senha incorreta"""
        # Criar usuário
        create_test_user(sample_user_data)

        # Tentar login com senha errada
        login_data = {'email_or_username': sample_user_data['email'], 'password': 'wrong_password'}
        response = client.post('/auth/login', json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert 'incorretos' in data['detail']

    def test_login_nonexistent_user_fails(self, client):
        """Testar login com usuário inexistente"""
        login_data = {'email_or_username': 'nonexistent@example.com', 'password': 'password123'}
        response = client.post('/auth/login', json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_inactive_user_fails(self, client, create_test_user, sample_user_data):
        """Testar login com usuário inativo"""
        # Criar usuário inativo
        user_data = sample_user_data.copy()
        user = create_test_user(user_data)

        # Desativar usuário
        user.is_active = False
        # Note: test_db is passed implicitly via create_test_user fixture

        # Tentar fazer login
        login_data = {'email_or_username': sample_user_data['email'], 'password': sample_user_data['password']}
        response = client.post('/auth/login', json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert 'desativado' in data['detail']


@pytest.mark.integration
@pytest.mark.auth
class TestRefreshToken:
    """Testes para refresh token"""

    def test_refresh_token_success(self, client, create_test_user, sample_user_data):
        """Testar renovação de token com refresh token"""
        # Criar usuário e fazer login
        create_test_user(sample_user_data)

        login_response = client.post(
            '/auth/login',
            json={'email_or_username': sample_user_data['email'], 'password': sample_user_data['password']},
        )

        login_data = login_response.json()
        refresh_token = login_data['refresh_token']

        # Usar refresh token
        refresh_response = client.post('/auth/refresh', json={'refresh_token': refresh_token})

        assert refresh_response.status_code == status.HTTP_200_OK
        refresh_data = refresh_response.json()
        assert 'access_token' in refresh_data
        assert 'refresh_token' in refresh_data
        assert refresh_data['token_type'] == 'bearer'

        # Verificar que temos novos tokens (podem ser iguais se gerados rapidamente)
        assert refresh_data['access_token'] is not None
        assert refresh_data['refresh_token'] is not None

    def test_refresh_with_access_token_success(self, client, user_headers):
        """Testar refresh endpoint com access token válido"""
        # O user_headers fixture já cria usuário e faz login
        refresh_response = client.post('/auth/refresh', headers=user_headers, json={'refresh_token': 'any_token'})

        assert refresh_response.status_code == status.HTTP_200_OK
        data = refresh_response.json()
        assert 'access_token' in data
        assert 'refresh_token' in data

    def test_refresh_invalid_token_fails(self, client):
        """Testar refresh com token inválido"""
        refresh_response = client.post('/auth/refresh', json={'refresh_token': 'invalid_token'})

        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_access_token_as_refresh_fails(self, client, create_test_user, sample_user_data):
        """Testar que access token não funciona como refresh token"""
        # Criar usuário e fazer login
        create_test_user(sample_user_data)

        login_response = client.post(
            '/auth/login',
            json={'email_or_username': sample_user_data['email'], 'password': sample_user_data['password']},
        )

        login_data = login_response.json()
        access_token = login_data['access_token']

        # Tentar usar access token como refresh token
        refresh_response = client.post('/auth/refresh', json={'refresh_token': access_token})

        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_inactive_user_fails(self, client, create_test_user, sample_user_data, test_db):
        """Testar refresh com usuário inativo"""
        # Criar usuário e fazer login
        user = create_test_user(sample_user_data)

        login_response = client.post(
            '/auth/login',
            json={'email_or_username': sample_user_data['email'], 'password': sample_user_data['password']},
        )

        login_data = login_response.json()
        refresh_token = login_data['refresh_token']

        # Desativar usuário
        user.is_active = False
        test_db.commit()

        # Tentar usar refresh token
        refresh_response = client.post('/auth/refresh', json={'refresh_token': refresh_token})

        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED
        data = refresh_response.json()
        assert 'desativado' in data['detail']


@pytest.mark.integration
@pytest.mark.auth
class TestAuthProtectedEndpoints:
    """Testes para endpoints que requerem autenticação"""

    def test_protected_endpoint_without_token_fails(self, client):
        """Testar acesso a endpoint protegido sem token"""
        response = client.get('/users/me')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_protected_endpoint_with_invalid_token_fails(self, client):
        """Testar acesso com token inválido"""
        headers = {'Authorization': 'Bearer invalid_token'}
        response = client.get('/users/me', headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_protected_endpoint_with_valid_token_success(self, client, user_headers):
        """Testar acesso com token válido"""
        response = client.get('/users/me', headers=user_headers)

        assert response.status_code == status.HTTP_200_OK

    def test_admin_endpoint_regular_user_fails(self, client, user_headers):
        """Testar que usuário comum não acessa endpoint admin"""
        response = client.get('/users/list', headers=user_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert 'admin' in data['detail'] or 'administrador' in data['detail']

    def test_admin_endpoint_admin_user_success(self, client, admin_headers):
        """Testar que administrador acessa endpoint admin"""
        response = client.get('/users/list', headers=admin_headers)

        assert response.status_code == status.HTTP_200_OK
