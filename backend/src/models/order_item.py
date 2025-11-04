from decimal import Decimal

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel


class OrderItem(BaseModel):
    __tablename__ = 'order_items'

    # Relacionamentos
    order_id = Column('order_id', ForeignKey('orders.id'), nullable=False)
    item_id = Column('item_id', ForeignKey('items.id'), nullable=False)

    # Quantidade do item no pedido
    quantity = Column('quantity', Integer, nullable=False, default=1)

    # Preço unitário no momento do pedido (para histórico)
    unit_price = Column('unit_price', Float, nullable=False)

    # Preço total (quantidade * preço unitário)
    total_price = Column('total_price', Float, nullable=False)

    # Observações específicas do item (ex: sem cebola, massa fina, etc.)
    notes = Column('notes', Text, nullable=True)

    # Relacionamentos
    order = relationship('Order', back_populates='order_items')
    item = relationship('Item', back_populates='order_items')

    def __init__(
        self,
        order_id: int,
        item_id: int,
        quantity: int,
        unit_price: float,
        total_price: float = None,
        notes: str = None,
    ):
        self.order_id = order_id
        self.item_id = item_id
        self.quantity = quantity
        self.unit_price = float(unit_price)
        self.total_price = float(total_price) if total_price is not None else float(unit_price) * quantity
        self.notes = notes

    def __str__(self):
        return f"{self.quantity}x {self.item.name if self.item else 'Item'} - R$ {self.total_price:.2f}"

    def update_total_price(self):
        """Recalcula o preço total baseado na quantidade e preço unitário"""
        self.total_price = self.quantity * self.unit_price

    @property
    def formatted_total_price(self):
        return f'R$ {self.total_price:.2f}'

    @property
    def formatted_unit_price(self):
        return f'R$ {self.unit_price:.2f}'
