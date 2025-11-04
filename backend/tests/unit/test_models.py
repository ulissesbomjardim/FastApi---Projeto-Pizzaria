"""
Testes unitários para os modelos do banco de dados
"""
from datetime import datetime
from decimal import Decimal

import pytest
from src.models import Item, Order, OrderItem, User
from src.models.item import CategoryType, SizeType


class TestUserModel:
    """Testes para o modelo User"""

    @pytest.mark.unit
    @pytest.mark.users
    def test_create_user(self, test_db):
        """Testar criação de usuário"""
        user = User(
            username='testuser',
            email='test@example.com',
            hashed_password='hashed_password',
            is_admin=False,
            is_active=True,
        )

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Verificar se o usuário foi criado corretamente
        assert user.id is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.hashed_password == 'hashed_password'
        assert user.is_admin is False
        assert user.is_active is True
        assert user.created_at is not None
        assert user.updated_at is not None

    @pytest.mark.unit
    @pytest.mark.users
    def test_user_defaults(self, test_db):
        """Testar valores padrão do usuário"""
        user = User(username='testuser2', email='test2@example.com', hashed_password='hashed_password')

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Verificar valores padrão
        assert user.is_admin is False
        assert user.is_active is True

    @pytest.mark.unit
    @pytest.mark.users
    def test_user_string_representation(self, test_db):
        """Testar representação string do usuário"""
        user = User(username='testuser3', email='test3@example.com', hashed_password='hashed_password')

        # O modelo não tem __str__ definido, então só verifica se o objeto existe
        str_repr = str(user)
        assert str_repr is not None
        assert 'User' in str_repr


class TestItemModel:
    """Testes para o modelo Item"""

    @pytest.mark.unit
    @pytest.mark.items
    def test_create_item(self, test_db):
        """Testar criação de item"""
        item = Item(
            name='Pizza Margherita',
            description='Pizza tradicional com molho de tomate, mozzarella e manjericão',
            price=25.90,
            category=CategoryType.PIZZA,
            size=SizeType.MEDIA,
            is_available=True,
        )

        test_db.add(item)
        test_db.commit()
        test_db.refresh(item)

        # Verificar se o item foi criado corretamente
        assert item.id is not None
        assert item.name == 'Pizza Margherita'
        assert item.description == 'Pizza tradicional com molho de tomate, mozzarella e manjericão'
        assert item.price == 25.90
        assert item.category == CategoryType.PIZZA
        assert item.size == SizeType.MEDIA
        assert item.is_available is True
        assert item.created_at is not None
        assert item.updated_at is not None

    @pytest.mark.unit
    @pytest.mark.items
    def test_item_defaults(self, test_db):
        """Testar valores padrão do item"""
        item = Item(name='Pizza Pepperoni', price=28.50, category=CategoryType.PIZZA, size=SizeType.GRANDE)

        test_db.add(item)
        test_db.commit()
        test_db.refresh(item)

        # Verificar valores padrão
        assert item.is_available is True
        assert item.description is None  # Valor padrão

    @pytest.mark.unit
    @pytest.mark.items
    def test_item_price_precision(self, test_db):
        """Testar precisão do preço"""
        item = Item(name='Refrigerante', price=5.99, category=CategoryType.BEBIDA, size=SizeType.ML_350)

        test_db.add(item)
        test_db.commit()
        test_db.refresh(item)

        # Verificar precisão do preço
        assert item.price == 5.99

    @pytest.mark.unit
    @pytest.mark.items
    def test_item_string_representation(self, test_db):
        """Testar representação string do item"""
        item = Item(name='Pizza Quatro Queijos', price=32.00, category=CategoryType.PIZZA, size=SizeType.GRANDE)

        str_repr = str(item)
        assert 'Pizza Quatro Queijos' in str_repr


class TestOrderModel:
    """Testes para o modelo Order"""

    @pytest.mark.unit
    @pytest.mark.orders
    def test_create_order(self, test_db, create_test_user):
        """Testar criação de pedido"""
        # Criar usuário primeiro
        user = create_test_user()

        order = Order(
            order_number='PED001',
            customer_name='João Silva',
            customer_phone='11999999999',
            delivery_address='Rua das Flores, 123',
            payment_method='pix',
            subtotal=51.80,
            total_amount=51.80,
            user_id=user.id,
        )

        test_db.add(order)
        test_db.commit()
        test_db.refresh(order)

        # Verificar se o pedido foi criado corretamente
        assert order.id is not None
        assert order.order_number == 'PED001'
        assert order.customer_name == 'João Silva'
        assert order.customer_phone == '11999999999'
        assert order.delivery_address == 'Rua das Flores, 123'
        assert order.payment_method == 'pix'
        assert order.subtotal == 51.80
        assert order.total_amount == 51.80
        assert order.status == 'pendente'  # Status padrão
        assert order.user_id == user.id

    @pytest.mark.unit
    @pytest.mark.orders
    def test_order_defaults(self, test_db, create_test_user):
        """Testar valores padrão do pedido"""
        user = create_test_user()

        order = Order(
            order_number='PED002',
            customer_name='Maria Silva',
            customer_phone='11888888888',
            payment_method='dinheiro',
            subtotal=30.00,
            total_amount=35.00,
            user_id=user.id,
        )

        test_db.add(order)
        test_db.commit()
        test_db.refresh(order)

        # Verificar valores padrão
        assert order.status == 'pendente'
        assert order.is_delivery is True
        assert order.delivery_fee == 0.0

    @pytest.mark.unit
    @pytest.mark.orders
    def test_order_number_generation(self, test_db, create_test_user):
        """Testar geração automática do número do pedido"""
        user = create_test_user()

        order1 = Order(
            order_number='PED003',
            customer_name='João Silva',
            customer_phone='11999999999',
            payment_method='pix',
            subtotal=51.80,
            total_amount=51.80,
            user_id=user.id,
        )

        order2 = Order(
            order_number='PED004',
            customer_name='Maria Silva',
            customer_phone='11888888888',
            payment_method='dinheiro',
            subtotal=30.00,
            total_amount=35.00,
            user_id=user.id,
        )

        test_db.add_all([order1, order2])
        test_db.commit()

        # Verificar que os números são únicos
        assert order1.order_number != order2.order_number
        assert order1.order_number == 'PED003'
        assert order2.order_number == 'PED004'

    @pytest.mark.unit
    @pytest.mark.orders
    def test_order_user_relationship(self, test_db, create_test_user):
        """Testar relacionamento entre pedido e usuário"""
        user = create_test_user()

        order = Order(
            order_number='PED005',
            customer_name='João Silva',
            customer_phone='11999999999',
            payment_method='pix',
            subtotal=51.80,
            total_amount=51.80,
            user_id=user.id,
        )

        test_db.add(order)
        test_db.commit()
        test_db.refresh(order)

        # Verificar relacionamento
        assert order.user is not None
        assert order.user.id == user.id
        assert order.user.username == user.username

    @pytest.mark.unit
    @pytest.mark.orders
    def test_order_string_representation(self, test_db, create_test_user):
        """Testar representação string do pedido"""
        user = create_test_user()

        order = Order(
            order_number='PED006',
            customer_name='João Silva',
            customer_phone='11999999999',
            payment_method='pix',
            subtotal=51.80,
            total_amount=51.80,
            user_id=user.id,
        )

        str_repr = str(order)
        assert str_repr is not None
        assert 'Order' in str_repr


class TestOrderItemModel:
    """Testes para o modelo OrderItem"""

    @pytest.mark.unit
    @pytest.mark.orders
    def test_create_order_item(self, test_db, create_test_user, create_test_item):
        """Testar criação de item do pedido"""
        # Criar dependências
        user = create_test_user()
        item = create_test_item()

        order = Order(
            order_number='PED007',
            customer_name='João Silva',
            customer_phone='11999999999',
            payment_method='pix',
            subtotal=51.80,
            total_amount=51.80,
            user_id=user.id,
        )

        test_db.add(order)
        test_db.commit()
        test_db.refresh(order)

        order_item = OrderItem(
            order_id=order.id, item_id=item.id, quantity=2, unit_price=item.price, notes='Sem cebola'
        )

        test_db.add(order_item)
        test_db.commit()
        test_db.refresh(order_item)

        # Verificar se o item do pedido foi criado corretamente
        assert order_item.id is not None
        assert order_item.order_id == order.id
        assert order_item.item_id == item.id
        assert order_item.quantity == 2
        assert order_item.unit_price == item.price
        assert order_item.notes == 'Sem cebola'
        assert order_item.created_at is not None
        assert order_item.updated_at is not None

    @pytest.mark.unit
    @pytest.mark.orders
    def test_order_item_relationships(self, test_db, create_test_user, create_test_item):
        """Testar relacionamentos do OrderItem"""
        # Criar dependências
        user = create_test_user()
        item = create_test_item()

        order = Order(
            order_number='PED008',
            customer_name='Maria Silva',
            customer_phone='11888888888',
            payment_method='dinheiro',
            subtotal=30.00,
            total_amount=35.00,
            user_id=user.id,
        )

        test_db.add(order)
        test_db.commit()
        test_db.refresh(order)

        order_item = OrderItem(order_id=order.id, item_id=item.id, quantity=1, unit_price=item.price)

        test_db.add(order_item)
        test_db.commit()
        test_db.refresh(order_item)

        # Verificar relacionamentos
        assert order_item.order is not None
        assert order_item.order.id == order.id
        assert order_item.order.order_number == 'PED008'

        assert order_item.item is not None
        assert order_item.item.id == item.id
        assert order_item.item.name == item.name

    @pytest.mark.unit
    @pytest.mark.orders
    def test_order_item_string_representation(self, test_db, create_test_user, create_test_item):
        """Testar representação string do OrderItem"""
        user = create_test_user()
        item = create_test_item()

        order = Order(
            order_number='PED009',
            customer_name='Ana Silva',
            customer_phone='11777777777',
            payment_method='cartao_credito',
            subtotal=40.00,
            total_amount=45.00,
            user_id=user.id,
        )

        test_db.add(order)
        test_db.commit()
        test_db.refresh(order)

        order_item = OrderItem(order_id=order.id, item_id=item.id, quantity=3, unit_price=item.price)

        str_repr = str(order_item)
        assert str(order_item.quantity) in str_repr or item.name in str_repr
