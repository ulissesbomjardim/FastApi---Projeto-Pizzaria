from decimal import Decimal

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ChoiceType

from .base import BaseModel


class Order(BaseModel):
    __tablename__ = 'orders'

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmado', 'Confirmado'),
        ('preparando', 'Preparando'),
        ('pronto', 'Pronto'),
        ('saiu_entrega', 'Saiu para Entrega'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]

    PAYMENT_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('vale_refeicao', 'Vale Refeição'),
    ]

    # Informações básicas do pedido
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(ChoiceType(STATUS_CHOICES), default='pendente')

    # Usuário que fez o pedido (opcional para pedidos de não-cadastrados)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Informações do cliente
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(20), nullable=False)

    # Entrega
    is_delivery = Column(Boolean, default=True)
    delivery_address = Column(Text, nullable=True)  # JSON string com endereço

    # Pagamento
    payment_method = Column(ChoiceType(PAYMENT_CHOICES), nullable=False)

    # Valores
    subtotal = Column(Float, nullable=False)
    delivery_fee = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)

    # Observações e tempo
    observations = Column(Text, nullable=True)
    estimated_delivery_time = Column(Integer, nullable=True)  # em minutos

    # Relacionamentos
    user = relationship('User', back_populates='orders')
    order_items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
