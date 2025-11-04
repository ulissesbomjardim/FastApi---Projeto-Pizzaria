import enum
from decimal import Decimal

from sqlalchemy import Boolean, Column, Enum, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel


class CategoryType(enum.Enum):
    PIZZA = 'pizza'
    BEBIDA = 'bebida'
    ENTRADA = 'entrada'
    SOBREMESA = 'sobremesa'
    PROMOCAO = 'promocao'


class SizeType(enum.Enum):
    PEQUENA = 'pequena'
    MEDIA = 'media'
    GRANDE = 'grande'
    FAMILIA = 'familia'
    # Para bebidas e outros itens
    UNICO = 'unico'
    ML_350 = '350ml'
    ML_500 = '500ml'
    L_1 = '1l'
    L_2 = '2l'


class Item(BaseModel):
    __tablename__ = 'items'

    # Informações básicas do item
    name = Column('name', String(100), nullable=False)
    description = Column('description', Text, nullable=True)
    category = Column('category', Enum(CategoryType), nullable=False)

    # Preço e tamanhos
    size = Column('size', Enum(SizeType), nullable=False)
    price = Column('price', Float, nullable=False)

    # Status de disponibilidade
    is_available = Column('is_available', Boolean, nullable=False, default=True)

    # Informações nutricionais (opcional)
    calories = Column('calories', Integer, nullable=True)
    preparation_time = Column('preparation_time', Integer, nullable=True)  # em minutos

    # Imagem do produto (URL ou path)
    image_url = Column('image_url', String(255), nullable=True)

    # Ingredientes especiais ou observações
    ingredients = Column('ingredients', Text, nullable=True)
    allergens = Column('allergens', String(255), nullable=True)

    # Relacionamento com itens de pedido
    order_items = relationship('OrderItem', back_populates='item')

    def __init__(
        self,
        name: str,
        category: CategoryType,
        size: SizeType,
        price: float,
        description: str = None,
        is_available: bool = True,
        calories: int = None,
        preparation_time: int = None,
        image_url: str = None,
        ingredients: str = None,
        allergens: str = None,
    ):
        self.name = name
        self.description = description
        self.category = category
        self.size = size
        self.price = float(price)
        self.is_available = is_available
        self.calories = calories
        self.preparation_time = preparation_time
        self.image_url = image_url
        self.ingredients = ingredients
        self.allergens = allergens

    def __str__(self):
        return f'{self.name} ({self.size.value}) - R$ {self.price:.2f}'

    @property
    def formatted_price(self):
        return f'R$ {self.price:.2f}'

    @property
    def is_pizza(self):
        return self.category == CategoryType.PIZZA

    @property
    def is_beverage(self):
        return self.category == CategoryType.BEBIDA
