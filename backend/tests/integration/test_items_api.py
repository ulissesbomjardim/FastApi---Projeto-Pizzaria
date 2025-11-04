"""
Testes de integração para endpoints de itens do cardápio
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
@pytest.mark.items
class TestPublicItemEndpoints:
    """Testes para endpoints públicos de itens (sem autenticação)"""

    def test_get_public_menu_success(self, client, create_test_item):
        """Testar obtenção do cardápio público"""
        # Criar alguns itens
        item1_data = {
            'name': 'Pizza Margherita',
            'description': 'Pizza tradicional',
            'price': 25.90,
            'category': 'pizza',
            'is_available': True,
        }
        item2_data = {
            'name': 'Refrigerante',
            'description': 'Coca-Cola 350ml',
            'price': 5.50,
            'category': 'bebida',
            'is_available': True,
        }
        create_test_item(item1_data)
        create_test_item(item2_data)

        response = client.get('/items/menu')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]['name'] in ['Pizza Margherita', 'Refrigerante']
        assert data[1]['name'] in ['Pizza Margherita', 'Refrigerante']

    def test_get_public_menu_available_only(self, client, create_test_item):
        """Testar filtro de itens disponíveis no cardápio público"""
        # Criar item disponível
        available_item = {
            'name': 'Pizza Disponível',
            'description': 'Pizza disponível',
            'price': 25.90,
            'category': 'pizza',
            'is_available': True,
        }
        # Criar item indisponível
        unavailable_item = {
            'name': 'Pizza Indisponível',
            'description': 'Pizza não disponível',
            'price': 30.90,
            'category': 'pizza',
            'is_available': False,
        }
        create_test_item(available_item)
        create_test_item(unavailable_item)

        # Buscar apenas disponíveis (padrão)
        response = client.get('/items/menu?available_only=true')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]['name'] == 'Pizza Disponível'
        assert data[0]['is_available'] is True

    def test_get_public_menu_all_items(self, client, create_test_item):
        """Testar obtenção de todos os itens (incluindo indisponíveis)"""
        # Criar itens
        available_item = {
            'name': 'Pizza Disponível',
            'description': 'Pizza disponível',
            'price': 25.90,
            'category': 'pizza',
            'is_available': True,
        }
        unavailable_item = {
            'name': 'Pizza Indisponível',
            'description': 'Pizza não disponível',
            'price': 30.90,
            'category': 'pizza',
            'is_available': False,
        }
        create_test_item(available_item)
        create_test_item(unavailable_item)

        # Buscar todos os itens
        response = client.get('/items/menu?available_only=false')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_get_public_menu_filter_by_category(self, client, create_test_item):
        """Testar filtro por categoria no cardápio público"""
        # Criar itens de categorias diferentes
        pizza_item = {
            'name': 'Pizza Margherita',
            'description': 'Pizza tradicional',
            'price': 25.90,
            'category': 'pizza',
            'is_available': True,
        }
        bebida_item = {
            'name': 'Refrigerante',
            'description': 'Coca-Cola',
            'price': 5.50,
            'category': 'bebida',
            'is_available': True,
        }
        create_test_item(pizza_item)
        create_test_item(bebida_item)

        # Filtrar apenas pizzas
        response = client.get('/items/menu?category=pizza')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]['category'] == 'pizza'
        assert data[0]['name'] == 'Pizza Margherita'

    def test_get_categories_success(self, client):
        """Testar obtenção de categorias disponíveis"""
        response = client.get('/items/categories')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Verificar estrutura das categorias
        for category in data:
            assert 'value' in category
            assert 'label' in category

    def test_search_items_by_name(self, client, create_test_item):
        """Testar busca de itens por nome"""
        # Criar itens
        pizza_item = {
            'name': 'Pizza Margherita',
            'description': 'Pizza tradicional com manjericão',
            'price': 25.90,
            'category': 'pizza',
            'is_available': True,
        }
        pasta_item = {
            'name': 'Lasanha Bolonhesa',
            'description': 'Lasanha com molho bolonhesa',
            'price': 22.50,
            'category': 'massa',
            'is_available': True,
        }
        create_test_item(pizza_item)
        create_test_item(pasta_item)

        # Buscar por "pizza"
        response = client.get('/items/search?q=pizza')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert 'Pizza' in data[0]['name']

    def test_search_items_by_description(self, client, create_test_item):
        """Testar busca de itens por descrição"""
        # Criar item
        pizza_item = {
            'name': 'Pizza Especial',
            'description': 'Pizza com ingredientes selecionados e manjericão fresco',
            'price': 28.90,
            'category': 'pizza',
            'is_available': True,
        }
        create_test_item(pizza_item)

        # Buscar por palavra na descrição
        response = client.get('/items/search?q=manjericão')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert 'manjericão' in data[0]['description']

    def test_get_item_public_success(self, client, create_test_item):
        """Testar obtenção de item específico público"""
        # Criar item
        item = create_test_item()

        response = client.get(f'/items/{item.id}/public')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['id'] == item.id
        assert data['name'] == item.name
        assert data['is_available'] is True

    def test_get_item_public_unavailable_fails(self, client, create_test_item):
        """Testar que item indisponível não é retornado no endpoint público"""
        # Criar item indisponível
        item_data = {
            'name': 'Pizza Indisponível',
            'description': 'Pizza não disponível',
            'price': 25.90,
            'category': 'pizza',
            'is_available': False,
        }
        item = create_test_item(item_data)

        response = client.get(f'/items/{item.id}/public')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert 'não encontrado ou não disponível' in data['detail']

    def test_get_item_public_nonexistent_fails(self, client):
        """Testar obtenção de item inexistente"""
        response = client.get('/items/999/public')

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
@pytest.mark.items
class TestAuthenticatedItemEndpoints:
    """Testes para endpoints de itens que requerem autenticação"""

    def test_list_items_authenticated_success(self, client, user_headers, create_test_item):
        """Testar listagem de itens para usuário autenticado"""
        # Criar alguns itens
        create_test_item()
        create_test_item(
            {
                'name': 'Pizza Calabresa',
                'description': 'Pizza com calabresa',
                'price': 27.90,
                'category': 'pizza',
                'is_available': True,
            }
        )

        response = client.get('/items/list-items', headers=user_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 2

    def test_get_item_authenticated_success(self, client, user_headers, create_test_item):
        """Testar obtenção de item específico para usuário autenticado"""
        item = create_test_item()

        response = client.get(f'/items/get-item/{item.id}', headers=user_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['id'] == item.id
        assert data['name'] == item.name


@pytest.mark.integration
@pytest.mark.items
class TestAdminItemEndpoints:
    """Testes para endpoints de itens que requerem permissões de admin"""

    def test_create_item_admin_success(self, client, admin_headers, sample_item_data):
        """Testar criação de item por administrador"""
        response = client.post('/items/create-item', headers=admin_headers, json=sample_item_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['name'] == sample_item_data['name']
        assert data['price'] == sample_item_data['price']
        assert data['category'] == sample_item_data['category']
        assert data['is_available'] is True

    def test_create_item_regular_user_fails(self, client, user_headers, sample_item_data):
        """Testar que usuário comum não pode criar item"""
        response = client.post('/items/create-item', headers=user_headers, json=sample_item_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert 'Apenas administradores' in data['detail']

    def test_edit_item_admin_success(self, client, admin_headers, create_test_item):
        """Testar edição de item por administrador"""
        item = create_test_item()

        update_data = {
            'name': 'Pizza Margherita Especial',
            'description': 'Pizza Margherita com ingredientes premium',
            'price': 29.90,
            'category': 'pizza',
            'is_available': True,
        }

        response = client.put(f'/items/edit-item/{item.id}', headers=admin_headers, json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['name'] == update_data['name']
        assert data['price'] == update_data['price']

    def test_edit_item_regular_user_fails(self, client, user_headers, create_test_item):
        """Testar que usuário comum não pode editar item"""
        item = create_test_item()

        update_data = {
            'name': 'Pizza Atualizada',
            'description': 'Descrição atualizada',
            'price': 30.00,
            'category': 'pizza',
            'is_available': True,
        }

        response = client.put(f'/items/edit-item/{item.id}', headers=user_headers, json=update_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_item_admin_success(self, client, admin_headers, create_test_item):
        """Testar deleção de item por administrador"""
        item = create_test_item()

        response = client.delete(f'/items/delete-item/{item.id}', headers=admin_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'deletado com sucesso' in data['message']

    def test_delete_item_regular_user_fails(self, client, user_headers, create_test_item):
        """Testar que usuário comum não pode deletar item"""
        item = create_test_item()

        response = client.delete(f'/items/delete-item/{item.id}', headers=user_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_toggle_availability_admin_success(self, client, admin_headers, create_test_item):
        """Testar alternar disponibilidade por administrador"""
        item = create_test_item()
        original_availability = item.is_available

        response = client.put(f'/items/toggle-availability/{item.id}', headers=admin_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['is_available'] != original_availability

    def test_toggle_availability_regular_user_fails(self, client, user_headers, create_test_item):
        """Testar que usuário comum não pode alterar disponibilidade"""
        item = create_test_item()

        response = client.put(f'/items/toggle-availability/{item.id}', headers=user_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.integration
@pytest.mark.items
class TestItemValidation:
    """Testes para validação de dados de itens"""

    def test_create_item_invalid_data_fails(self, client, admin_headers):
        """Testar criação de item com dados inválidos"""
        invalid_data = {
            'name': '',  # Nome vazio
            'description': 'Descrição válida',
            'price': -10.0,  # Preço negativo
            'category': 'invalid_category',  # Categoria inválida
            'is_available': 'not_boolean',  # Tipo inválido
        }

        response = client.post('/items/create-item', headers=admin_headers, json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_item_missing_required_fields_fails(self, client, admin_headers):
        """Testar criação de item com campos obrigatórios ausentes"""
        incomplete_data = {
            'name': 'Pizza Teste'
            # Faltam outros campos obrigatórios
        }

        response = client.post('/items/create-item', headers=admin_headers, json=incomplete_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_edit_nonexistent_item_fails(self, client, admin_headers, sample_item_data):
        """Testar edição de item inexistente"""
        response = client.put('/items/edit-item/999', headers=admin_headers, json=sample_item_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert 'não encontrado' in data['detail']
