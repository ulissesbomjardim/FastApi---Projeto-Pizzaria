"""
Testes de integração para gerenciamento de itens em pedidos
"""
import json
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestOrderItemManagement:
    """Testes para adicionar e remover itens de pedidos"""
    
    def test_add_item_to_order_success(self, auth_headers, setup_order_with_items):
        """Testar adicionar item a um pedido existente com sucesso"""
        user_headers = auth_headers()
        order = setup_order_with_items(user_headers)
        
        # Dados para adicionar um novo item
        add_item_data = {
            "item_id": 1,  # Item que deve existir no cardápio
            "quantity": 2,
            "observations": "Sem cebola"
        }
        
        response = client.post(
            f"/orders/{order['id']}/add-item",
            headers=user_headers,
            json=add_item_data
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data['message'] == 'Item adicionado ao pedido com sucesso'
        assert data['order_id'] == order['id']
        assert 'item_added' in data
        assert data['item_added']['item_id'] == add_item_data['item_id']
        # Se for o mesmo item, soma as quantidades. Se for item diferente, usa a quantidade nova
        assert data['item_added']['quantity'] >= add_item_data['quantity']
        assert data['item_added']['observations'] == add_item_data['observations']
        assert 'new_totals' in data
        assert data['new_totals']['total_amount'] > order['total_amount']

    def test_add_item_to_nonexistent_order_fails(self, auth_headers):
        """Testar adicionar item a pedido inexistente"""
        user_headers = auth_headers()
        
        add_item_data = {
            "item_id": 1,
            "quantity": 1
        }
        
        response = client.post(
            "/orders/99999/add-item",
            headers=user_headers,
            json=add_item_data
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'Pedido não encontrado' in response.json()['detail']

    def test_add_nonexistent_item_to_order_fails(self, auth_headers, setup_order_with_items):
        """Testar adicionar item inexistente a um pedido"""
        user_headers = auth_headers()
        order = setup_order_with_items(user_headers)
        
        add_item_data = {
            "item_id": 99999,  # Item que não existe
            "quantity": 1
        }
        
        response = client.post(
            f"/orders/{order['id']}/add-item",
            headers=user_headers,
            json=add_item_data
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'Item não encontrado no cardápio' in response.json()['detail']

    def test_add_item_to_other_user_order_fails(self, auth_headers, setup_order_with_items):
        """Testar adicionar item ao pedido de outro usuário"""
        user_headers = auth_headers(); order = setup_order_with_items(user_headers)
        other_user_headers = auth_headers(is_admin=False)  # Outro usuário
        
        add_item_data = {
            "item_id": 1,
            "quantity": 1
        }
        
        response = client.post(
            f"/orders/{order['id']}/add-item",
            headers=other_user_headers,
            json=add_item_data
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'Você só pode modificar seus próprios pedidos' in response.json()['detail']

    def test_add_item_invalid_quantity_fails(self, auth_headers, setup_order_with_items):
        """Testar adicionar item com quantidade inválida"""
        user_headers = auth_headers(); order = setup_order_with_items(user_headers)
        
        # Testar quantidade zero
        add_item_data = {
            "item_id": 1,
            "quantity": 0
        }
        
        response = client.post(
            f"/orders/{order['id']}/add-item",
            headers=user_headers,
            json=add_item_data
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Testar quantidade muito alta
        add_item_data = {
            "item_id": 1,
            "quantity": 100
        }
        
        response = client.post(
            f"/orders/{order['id']}/add-item",
            headers=user_headers,
            json=add_item_data
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_remove_item_from_order_success(self, auth_headers, setup_order_with_items):
        """Testar remover item de um pedido com sucesso"""
        user_headers = auth_headers(); order = setup_order_with_items(user_headers)
        
        # Assumindo que o pedido tem pelo menos um item
        assert len(order['items']) > 0
        first_item = order['items'][0]
        
        response = client.delete(
            f"/orders/{order['id']}/remove-item?order_item_id={first_item['id']}",
            headers=user_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert 'Item removido do pedido' in data['message']
        assert data['order_id'] == order['id']
        assert 'item_removed' in data
        assert data['item_removed']['id'] == first_item['id']

    def test_remove_nonexistent_order_item_fails(self, auth_headers, setup_order_with_items):
        """Testar remover item inexistente de um pedido"""
        user_headers = auth_headers(); order = setup_order_with_items(user_headers)
        
        response = client.delete(
            f"/orders/{order['id']}/remove-item?order_item_id=99999",
            headers=user_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'Item não encontrado neste pedido' in response.json()['detail']

    def test_remove_item_from_other_user_order_fails(self, auth_headers, setup_order_with_items):
        """Testar remover item do pedido de outro usuário"""
        user_headers = auth_headers(); order = setup_order_with_items(user_headers)
        other_user_headers = auth_headers(is_admin=False)  # Outro usuário
        
        first_item = order['items'][0]
        
        response = client.delete(
            f"/orders/{order['id']}/remove-item?order_item_id={first_item['id']}",
            headers=other_user_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'Você só pode modificar seus próprios pedidos' in response.json()['detail']

    def test_add_item_to_delivered_order_fails(self, auth_headers, setup_delivered_order):
        """Testar adicionar item a pedido já entregue"""
        user_headers = auth_headers(); order = setup_delivered_order(user_headers)
        
        add_item_data = {
            "item_id": 1,
            "quantity": 1
        }
        
        response = client.post(
            f"/orders/{order['id']}/add-item",
            headers=user_headers,
            json=add_item_data
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Não é possível modificar pedido com status' in response.json()['detail']

    def test_remove_item_from_delivered_order_fails(self, auth_headers, setup_delivered_order):
        """Testar remover item de pedido já entregue"""
        user_headers = auth_headers(); order = setup_delivered_order(user_headers)
        
        first_item = order['items'][0]
        
        response = client.delete(
            f"/orders/{order['id']}/remove-item?order_item_id={first_item['id']}",
            headers=user_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Não é possível modificar pedido com status' in response.json()['detail']

    def test_remove_last_item_cancels_order(self, auth_headers, setup_single_item_order):
        """Testar que remover o último item cancela o pedido"""
        user_headers = auth_headers(); order = setup_single_item_order(user_headers)
        
        # Deve ter apenas um item
        assert len(order['items']) == 1
        only_item = order['items'][0]
        
        response = client.delete(
            f"/orders/{order['id']}/remove-item?order_item_id={only_item['id']}",
            headers=user_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert 'Pedido cancelado pois não há mais itens' in data['message']
        assert data['order_status'] == 'cancelado'

    def test_add_existing_item_increases_quantity(self, auth_headers, setup_order_with_items):
        """Testar que adicionar item já existente aumenta a quantidade"""
        user_headers = auth_headers(); order = setup_order_with_items(user_headers)
        
        # Pegar um item que já existe no pedido
        existing_item = order['items'][0]
        original_quantity = existing_item['quantity']
        
        add_item_data = {
            "item_id": existing_item['item_id'],
            "quantity": 2,
            "observations": "Observação adicional"
        }
        
        response = client.post(
            f"/orders/{order['id']}/add-item",
            headers=user_headers,
            json=add_item_data
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data['item_added']['quantity'] == original_quantity + 2
        assert 'Observação adicional' in data['item_added']['observations']

    def test_unauthenticated_add_item_fails(self, setup_order_with_items):
        """Testar adicionar item sem autenticação"""
        order = setup_order_with_items()
        
        add_item_data = {
            "item_id": 1,
            "quantity": 1
        }
        
        response = client.post(
            f"/orders/{order['id']}/add-item",
            json=add_item_data
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_remove_item_fails(self, setup_order_with_items):
        """Testar remover item sem autenticação"""
        order = setup_order_with_items()
        
        first_item = order['items'][0]
        
        response = client.delete(
            f"/orders/{order['id']}/remove-item?order_item_id={first_item['id']}"
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
