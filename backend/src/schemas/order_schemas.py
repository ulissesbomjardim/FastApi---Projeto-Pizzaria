"""
Schemas para sistema de pedidos e itens da pizzaria
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class ItemCategory(str, Enum):
    """Categorias de itens do cardápio"""

    PIZZA = 'pizza'
    BEBIDA = 'bebida'
    SOBREMESA = 'sobremesa'
    ENTRADA = 'entrada'
    COMBO = 'combo'


class ItemSize(str, Enum):
    """Tamanhos disponíveis"""

    PEQUENA = 'pequena'
    MEDIA = 'media'
    GRANDE = 'grande'
    FAMILIA = 'familia'
    UNICO = 'unico'
    ML_350 = '350ml'
    ML_500 = '500ml'
    L_1 = '1l'
    L_2 = '2l'


class OrderStatus(str, Enum):
    """Status do pedido"""

    PENDENTE = 'pendente'
    CONFIRMADO = 'confirmado'
    PREPARANDO = 'preparando'
    PRONTO = 'pronto'
    SAIU_ENTREGA = 'saiu_entrega'
    ENTREGUE = 'entregue'
    CANCELADO = 'cancelado'


class PaymentMethod(str, Enum):
    """Métodos de pagamento"""

    DINHEIRO = 'dinheiro'
    CARTAO_CREDITO = 'cartao_credito'
    CARTAO_DEBITO = 'cartao_debito'
    PIX = 'pix'
    VALE_REFEICAO = 'vale_refeicao'


class OrderItemAdd(BaseModel):
    """Schema para adicionar item a um pedido"""
    
    item_id: int = Field(..., description='ID do item do cardápio')
    quantity: int = Field(..., ge=1, le=50, description='Quantidade do item (1-50)')
    observations: Optional[str] = Field(None, max_length=500, description='Observações especiais do item')

    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantidade deve ser maior que zero')
        if v > 50:
            raise ValueError('Quantidade máxima é 50 unidades por item')
        return v


class OrderItemRemove(BaseModel):
    """Schema para remover item de um pedido"""
    
    order_item_id: int = Field(..., description='ID do item no pedido (order_item.id)')
    
    class Config:
        schema_extra = {
            "example": {
                "order_item_id": 123
            }
        }


# === SCHEMAS DE ITENS ===


class ItemBase(BaseModel):
    """Schema base para itens do cardápio"""

    name: str = Field(..., min_length=2, max_length=100, description='Nome do item')
    description: Optional[str] = Field(None, max_length=500, description='Descrição do item')
    category: ItemCategory = Field(..., description='Categoria do item')
    price: Decimal = Field(..., gt=0, description='Preço do item')
    size: Optional[ItemSize] = Field(None, description='Tamanho do item')
    is_available: bool = Field(default=True, description='Se o item está disponível')
    preparation_time: Optional[int] = Field(None, gt=0, description='Tempo de preparo em minutos')
    ingredients: Optional[List[str]] = Field(None, description='Lista de ingredientes')
    image_url: Optional[str] = Field(None, description='URL da imagem do item')

    @validator('price')
    def validate_price(cls, v):
        """Validar preço com 2 casas decimais"""
        if v.as_tuple().exponent < -2:
            raise ValueError('Preço deve ter no máximo 2 casas decimais')
        return v


class ItemCreate(ItemBase):
    """Schema para criação de item"""

    pass


class ItemUpdate(BaseModel):
    """Schema para atualização de item"""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[ItemCategory] = None
    price: Optional[Decimal] = Field(None, gt=0)
    size: Optional[ItemSize] = None
    is_available: Optional[bool] = None
    preparation_time: Optional[int] = Field(None, gt=0)
    ingredients: Optional[List[str]] = None
    image_url: Optional[str] = None


class ItemResponse(ItemBase):
    """Schema para resposta de item"""

    id: int = Field(..., description='ID único do item')
    created_at: datetime = Field(..., description='Data de criação')
    updated_at: datetime = Field(..., description='Data da última atualização')

    @validator('ingredients', pre=True)
    def parse_ingredients(cls, v):
        """Converter string de ingredientes em lista"""
        if isinstance(v, str):
            # Se for string, dividir por vírgula e limpar espaços
            return [ingredient.strip() for ingredient in v.split(',') if ingredient.strip()]
        elif isinstance(v, list):
            return v
        return None

    class Config:
        from_attributes = True


# === SCHEMAS DE PEDIDOS ===


class OrderItemBase(BaseModel):
    """Schema base para item do pedido"""

    item_id: int = Field(..., description='ID do item do cardápio')
    quantity: int = Field(..., gt=0, description='Quantidade do item')
    unit_price: Decimal = Field(..., gt=0, description='Preço unitário do item')
    observations: Optional[str] = Field(None, max_length=200, description='Observações do item')

    @validator('unit_price')
    def validate_unit_price(cls, v):
        """Validar preço unitário com 2 casas decimais"""
        if v.as_tuple().exponent < -2:
            raise ValueError('Preço unitário deve ter no máximo 2 casas decimais')
        return v


class OrderItemCreate(BaseModel):
    """Schema para criação de item do pedido"""

    item_id: int = Field(..., description='ID do item do cardápio')
    quantity: int = Field(..., gt=0, le=10, description='Quantidade do item (máx. 10)')
    observations: Optional[str] = Field(None, max_length=200, description='Observações do item')


class OrderItemResponse(OrderItemBase):
    """Schema para resposta de item do pedido"""

    id: int = Field(..., description='ID único do item do pedido')
    subtotal: Decimal = Field(..., description='Subtotal do item (quantidade x preço)')
    item: ItemResponse = Field(..., description='Dados completos do item')

    class Config:
        from_attributes = True


class AddressBase(BaseModel):
    """Schema base para endereço de entrega"""

    street: str = Field(..., min_length=5, max_length=200, description='Rua e número')
    neighborhood: str = Field(..., min_length=2, max_length=100, description='Bairro')
    city: str = Field(..., min_length=2, max_length=100, description='Cidade')
    state: str = Field(..., min_length=2, max_length=2, description='Estado (UF)')
    zip_code: str = Field(..., pattern=r'^\d{5}-?\d{3}$', description='CEP')
    complement: Optional[str] = Field(None, max_length=100, description='Complemento')
    reference: Optional[str] = Field(None, max_length=200, description='Ponto de referência')

    @validator('state')
    def validate_state(cls, v):
        """Validar UF"""
        return v.upper()

    @validator('zip_code')
    def validate_zip_code(cls, v):
        """Formatar CEP"""
        # Remove traços e espaços
        v = v.replace('-', '').replace(' ', '')
        if len(v) != 8:
            raise ValueError('CEP deve ter 8 dígitos')
        # Adiciona traço no formato correto
        return f'{v[:5]}-{v[5:]}'


class OrderBase(BaseModel):
    """Schema base para pedido"""

    customer_name: Optional[str] = Field(
        None, min_length=2, max_length=100, description='Nome do cliente (opcional, usa username se não informado)'
    )
    customer_phone: str = Field(..., pattern=r'^\(\d{2}\)\s\d{4,5}-\d{4}$', description='Telefone do cliente')
    delivery_address: Optional[AddressBase] = Field(None, description='Endereço de entrega')
    is_delivery: bool = Field(default=True, description='Se é entrega ou retirada')
    payment_method: PaymentMethod = Field(..., description='Método de pagamento')
    observations: Optional[str] = Field(None, max_length=500, description='Observações gerais do pedido')

    @validator('customer_phone')
    def validate_phone(cls, v):
        """Validar formato do telefone"""
        import re

        # Remove caracteres especiais para validação
        phone_digits = re.sub(r'[^\d]', '', v)
        if len(phone_digits) not in [10, 11]:
            raise ValueError('Telefone deve ter 10 ou 11 dígitos')
        return v


class OrderCreate(OrderBase):
    """Schema para criação de pedido"""

    items: List[OrderItemCreate] = Field(..., min_items=1, description='Lista de itens do pedido')

    @validator('items')
    def validate_items(cls, v):
        """Validar se há pelo menos um item"""
        if not v:
            raise ValueError('Pedido deve ter pelo menos um item')
        return v


class OrderUpdate(BaseModel):
    """Schema para atualização de pedido"""

    status: Optional[OrderStatus] = Field(None, description='Novo status do pedido')
    observations: Optional[str] = Field(None, max_length=500, description='Novas observações')
    delivery_time_estimate: Optional[int] = Field(None, gt=0, description='Estimativa de entrega em minutos')


class OrderResponse(OrderBase):
    """Schema para resposta de pedido"""

    id: int = Field(..., description='ID único do pedido')
    order_number: str = Field(..., description='Número do pedido')
    user_id: int = Field(..., description='ID do usuário que fez o pedido')
    status: OrderStatus = Field(..., description='Status atual do pedido')
    items: List[OrderItemResponse] = Field(..., description='Lista de itens do pedido')
    subtotal: Decimal = Field(..., description='Subtotal dos itens')
    delivery_fee: Decimal = Field(default=0, description='Taxa de entrega')
    total_amount: Decimal = Field(..., description='Valor total do pedido')
    estimated_delivery_time: Optional[int] = Field(None, description='Tempo estimado de entrega/preparo em minutos')
    created_at: datetime = Field(..., description='Data de criação do pedido')
    updated_at: datetime = Field(..., description='Data da última atualização')

    class Config:
        from_attributes = True


class OrderSummary(BaseModel):
    """Schema para resumo de pedido (lista)"""

    id: int = Field(..., description='ID do pedido')
    order_number: str = Field(..., description='Número do pedido')
    customer_name: str = Field(..., description='Nome do cliente')
    status: OrderStatus = Field(..., description='Status do pedido')
    total_amount: Decimal = Field(..., description='Valor total')
    created_at: datetime = Field(..., description='Data de criação')
    items_count: int = Field(..., description='Quantidade de itens diferentes')

    class Config:
        from_attributes = True


# === SCHEMAS DE RELATÓRIOS ===


class SalesReport(BaseModel):
    """Schema para relatório de vendas"""

    period: str = Field(..., description='Período do relatório')
    total_orders: int = Field(..., description='Total de pedidos')
    total_revenue: Decimal = Field(..., description='Receita total')
    average_ticket: Decimal = Field(..., description='Ticket médio')
    most_sold_items: List[dict] = Field(..., description='Itens mais vendidos')

    class Config:
        from_attributes = True
