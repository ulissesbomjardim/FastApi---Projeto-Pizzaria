"""
Configuração dos testes para a API da Pizzaria
"""
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adicionar o diretório backend ao sys.path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.config.database import get_db
from src.config.security import hash_password
from src.main import app
from src.models import Item, Order, User
from src.models.base import Base


# Configuração do banco de teste em memória
@pytest.fixture(scope='session')
def test_engine():
    """Criar engine de teste usando SQLite em memória"""
    # Usar arquivo temporário para persistir durante a sessão de teste
    test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    test_db.close()

    engine = create_engine(f'sqlite:///{test_db.name}', connect_args={'check_same_thread': False})

    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)

    yield engine

    # Limpeza após os testes
    engine.dispose()
    os.unlink(test_db.name)


@pytest.fixture(scope='function')
def test_db(test_engine):
    """Criar sessão de banco de dados para cada teste"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Limpar todas as tabelas após cada teste
        with test_engine.connect() as connection:
            transaction = connection.begin()
            for table in reversed(Base.metadata.sorted_tables):
                connection.execute(table.delete())
            transaction.commit()


@pytest.fixture(scope='function')
def client(test_db):
    """Cliente de teste do FastAPI com banco de dados isolado"""

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Dados de exemplo para criação de usuário"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPass123!',  # Senha com maiúscula, minúscula, número e especial
    }


@pytest.fixture
def sample_admin_data():
    """Dados de exemplo para criação de administrador"""
    return {
        'username': 'admin',
        'email': 'admin@example.com',
        'password': 'AdminPass123!',  # Senha com maiúscula, minúscula, número e especial
    }


@pytest.fixture
def sample_item_data():
    """Dados de exemplo para criação de item"""
    return {
        'name': 'Pizza Margherita',
        'description': 'Pizza tradicional com molho de tomate, mozzarella e manjericão',
        'price': 25.90,
        'category': 'pizza',
        'size': 'media',
        'is_available': True,
    }


@pytest.fixture
def sample_order_data():
    """Dados de exemplo para criação de pedido"""
    return {
        'customer_name': 'João Silva',
        'customer_phone': '11999999999',
        'customer_address': 'Rua das Flores, 123',
        'items': [{'item_id': 1, 'quantity': 2}, {'item_id': 2, 'quantity': 1}],
    }


@pytest.fixture
def create_test_user(test_db):
    """Criar usuário de teste no banco"""

    def _create_user(user_data=None, is_admin=False):
        if user_data is None:
            user_data = {'username': 'testuser', 'email': 'test@example.com', 'password': 'TestPass123!'}

        hashed_password = hash_password(user_data['password'])
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            hashed_password=hashed_password,
            is_admin=is_admin,
            is_active=True,
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        return user

    return _create_user


@pytest.fixture
def create_test_item(test_db):
    """Criar item de teste no banco"""

    def _create_item(item_data=None):
        from src.models.item import CategoryType, SizeType

        if item_data is None:
            item_data = {
                'name': 'Pizza Margherita',
                'description': 'Pizza tradicional',
                'price': 25.90,
                'category': CategoryType.PIZZA,
                'size': SizeType.MEDIA,
                'is_available': True,
            }

        # Converter string para enum se necessário
        category = item_data['category']
        if isinstance(category, str):
            # Mapear strings para enums
            category_map = {
                'pizza': CategoryType.PIZZA,
                'bebida': CategoryType.BEBIDA,
                'entrada': CategoryType.ENTRADA,
                'sobremesa': CategoryType.SOBREMESA,
                'promocao': CategoryType.PROMOCAO,
                'massa': CategoryType.ENTRADA  # Fallback para testes que usam 'massa'
            }
            category = category_map.get(category, CategoryType.PIZZA)
        
        size = item_data.get('size', SizeType.MEDIA)
        if isinstance(size, str):
            # Mapear strings para enums
            size_map = {
                'pequena': SizeType.PEQUENA,
                'media': SizeType.MEDIA,
                'grande': SizeType.GRANDE,
                'familia': SizeType.FAMILIA,
                'unico': SizeType.UNICO,
                '350ml': SizeType.ML_350,
                '500ml': SizeType.ML_500,
                '1l': SizeType.L_1,
                '2l': SizeType.L_2
            }
            size = size_map.get(size, SizeType.MEDIA)

        item = Item(
            name=item_data['name'],
            description=item_data.get('description'),
            price=item_data['price'],
            category=category,
            size=size,
            is_available=item_data.get('is_available', True),
        )
        test_db.add(item)
        test_db.commit()
        test_db.refresh(item)
        return item

    return _create_item


@pytest.fixture
def auth_headers(client, create_test_user):
    """Headers de autenticação para testes"""
    
    def _get_headers(is_admin=False):
        import uuid
        # Criar usuário único para cada teste
        unique_id = str(uuid.uuid4())[:8]
        
        user_data = {
            'username': f'testuser_{unique_id}' if not is_admin else f'admin_{unique_id}',
            'email': f'test_{unique_id}@example.com' if not is_admin else f'admin_{unique_id}@example.com',
            'password': 'TestPass123!' if not is_admin else 'AdminPass123!',
        }
        user = create_test_user(user_data, is_admin=is_admin)

        # Fazer login
        login_response = client.post(
            '/auth/login', json={'email_or_username': user_data['email'], 'password': user_data['password']}
        )

        assert login_response.status_code == 200
        token_data = login_response.json()

        return {'Authorization': f"Bearer {token_data['access_token']}", 'Content-Type': 'application/json'}

    return _get_headers


@pytest.fixture
def admin_headers(auth_headers):
    """Headers de autenticação para administrador"""
    return auth_headers(is_admin=True)


@pytest.fixture
def user_headers(auth_headers):
    """Headers de autenticação para usuário comum"""
    return auth_headers(is_admin=False)


@pytest.fixture
def sample_order_data():
    """Dados de exemplo para criação de pedido"""
    return {
        'customer_name': 'João Silva',
        'customer_phone': '(11) 99999-9999',  # Formato correto
        'payment_method': 'pix',  # Método de pagamento obrigatório
        'is_delivery': False,  # Retirada, sem endereço
        'observations': 'Pedido de teste',
        'items': []  # Será preenchido pelos testes
    }


# Marcadores personalizados para pytest
def pytest_configure(config):
    """Configurar marcadores personalizados"""
    config.addinivalue_line('markers', 'unit: marca testes unitários')
    config.addinivalue_line('markers', 'integration: marca testes de integração')
    config.addinivalue_line('markers', 'auth: marca testes de autenticação')
    config.addinivalue_line('markers', 'orders: marca testes de pedidos')
    config.addinivalue_line('markers', 'items: marca testes de itens')
    config.addinivalue_line('markers', 'users: marca testes de usuários')


# Fixtures para testes de gerenciamento de itens em pedidos
@pytest.fixture
def setup_order_with_items(client, auth_headers, create_test_item):
    """Criar pedido com itens para testes"""
    def _create_order(user_headers=None):
        item = create_test_item()
        if user_headers is None:
            user_headers = auth_headers()

        order_data = {
            'customer_name': 'João Silva',
            'customer_phone': '(11) 99999-9999',
            'is_delivery': True,
            'payment_method': 'pix',
            'delivery_address': {
                'street': 'Rua das Flores, 123',
                'neighborhood': 'Centro',
                'city': 'São Paulo',
                'state': 'SP',
                'zip_code': '01234-567'
            },
            'items': [{'item_id': item.id, 'quantity': 2}],
        }

        response = client.post('/orders/create-order', headers=user_headers, json=order_data)
        if response.status_code == 201:
            return response.json()
        else:
            pytest.fail(f'Falha ao criar pedido: {response.json()}')
    
    return _create_order


@pytest.fixture
def setup_delivered_order(client, auth_headers, create_test_item):
    """Criar pedido com status 'entregue' para testes"""
    def _create_delivered_order(user_headers=None):
        # Criar pedido básico
        item = create_test_item()
        if user_headers is None:
            user_headers = auth_headers()

        order_data = {
            'customer_name': 'João Silva',
            'customer_phone': '(11) 99999-9999',
            'is_delivery': False,
            'payment_method': 'pix',
            'items': [{'item_id': item.id, 'quantity': 1}],
        }

        response = client.post('/orders/create-order', headers=user_headers, json=order_data)
        if response.status_code != 201:
            pytest.fail(f'Falha ao criar pedido: {response.json()}')
        
        order = response.json()
        
        # Atualizar status para entregue (como admin)
        admin_headers = auth_headers(is_admin=True)
        status_response = client.patch(
            f"/orders/{order['id']}/status",
            headers=admin_headers,
            params={"new_status": "entregue"}
        )
        
        if status_response.status_code == 200:
            order['status'] = 'entregue'
        
        return order
    
    return _create_delivered_order


@pytest.fixture
def setup_single_item_order(client, auth_headers, create_test_item):
    """Criar pedido com apenas um item para testes"""
    def _create_single_item_order(user_headers=None):
        item = create_test_item()
        if user_headers is None:
            user_headers = auth_headers()

        order_data = {
            'customer_name': 'João Silva',
            'customer_phone': '(11) 99999-9999',
            'is_delivery': False,
            'payment_method': 'pix',
            'items': [{'item_id': item.id, 'quantity': 1}],
        }

        response = client.post('/orders/create-order', headers=user_headers, json=order_data)
        
        if response.status_code == 201:
            return response.json()
        else:
            pytest.fail(f'Falha ao criar pedido: {response.json()}')
    
    return _create_single_item_order


# Configuração para executar testes assíncronos
@pytest.fixture(scope='session')
def event_loop():
    """Criar event loop para testes assíncronos"""
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
