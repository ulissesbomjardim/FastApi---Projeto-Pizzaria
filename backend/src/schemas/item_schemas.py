"""
Schemas para itens do cardápio da pizzaria
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, validator

# Importar os Enums do modelo
from ..models.item import CategoryType, SizeType


class ItemBase(BaseModel):
    """Schema base para itens do cardápio"""

    name: str = Field(..., min_length=2, max_length=100, description='Nome do item')
    description: Optional[str] = Field(None, max_length=500, description='Descrição do item')
    category: CategoryType = Field(..., description='Categoria do item')
    size: SizeType = Field(..., description='Tamanho do item')
    price: float = Field(..., gt=0, description='Preço do item')
    is_available: bool = Field(default=True, description='Se o item está disponível')
    calories: Optional[int] = Field(None, gt=0, description='Calorias do item')
    preparation_time: Optional[int] = Field(None, gt=0, description='Tempo de preparo em minutos')
    image_url: Optional[str] = Field(None, description='URL da imagem do item')
    ingredients: Optional[str] = Field(None, max_length=1000, description='Ingredientes do item')
    allergens: Optional[str] = Field(None, max_length=255, description='Alérgenos do item')

    @validator('price')
    def validate_price(cls, v):
        """Validar preço positivo com máximo 2 casas decimais"""
        if v <= 0:
            raise ValueError('Preço deve ser maior que zero')
        # Arredondar para 2 casas decimais
        return round(v, 2)

    @validator('name')
    def validate_name(cls, v):
        """Validar nome do item"""
        if not v or not v.strip():
            raise ValueError('Nome do item não pode estar vazio')
        return v.strip()


class ItemCreate(ItemBase):
    """Schema para criação de item"""

    pass


class ItemUpdate(BaseModel):
    """Schema para atualização de item"""

    name: Optional[str] = Field(None, min_length=2, max_length=100, description='Nome do item')
    description: Optional[str] = Field(None, max_length=500, description='Descrição do item')
    category: Optional[CategoryType] = Field(None, description='Categoria do item')
    size: Optional[SizeType] = Field(None, description='Tamanho do item')
    price: Optional[float] = Field(None, gt=0, description='Preço do item')
    is_available: Optional[bool] = Field(None, description='Se o item está disponível')
    calories: Optional[int] = Field(None, gt=0, description='Calorias do item')
    preparation_time: Optional[int] = Field(None, gt=0, description='Tempo de preparo em minutos')
    image_url: Optional[str] = Field(None, description='URL da imagem do item')
    ingredients: Optional[str] = Field(None, max_length=1000, description='Ingredientes do item')
    allergens: Optional[str] = Field(None, max_length=255, description='Alérgenos do item')

    @validator('price')
    def validate_price(cls, v):
        """Validar preço se fornecido"""
        if v is not None:
            if v <= 0:
                raise ValueError('Preço deve ser maior que zero')
            return round(v, 2)
        return v

    @validator('name')
    def validate_name(cls, v):
        """Validar nome se fornecido"""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Nome do item não pode estar vazio')
            return v.strip()
        return v


class ItemResponse(ItemBase):
    """Schema para resposta de item"""

    id: int = Field(..., description='ID único do item')
    created_at: datetime = Field(..., description='Data de criação')
    updated_at: datetime = Field(..., description='Data da última atualização')

    class Config:
        from_attributes = True


class ItemSummary(BaseModel):
    """Schema resumido para listagem de itens"""

    id: int = Field(..., description='ID do item')
    name: str = Field(..., description='Nome do item')
    category: CategoryType = Field(..., description='Categoria do item')
    size: SizeType = Field(..., description='Tamanho do item')
    price: float = Field(..., description='Preço do item')
    is_available: bool = Field(..., description='Disponibilidade do item')
    preparation_time: Optional[int] = Field(None, description='Tempo de preparo em minutos')

    class Config:
        from_attributes = True


# Schema para filtros de busca
class ItemFilters(BaseModel):
    """Schema para filtros de busca de itens"""

    category: Optional[CategoryType] = Field(None, description='Filtrar por categoria')
    size: Optional[SizeType] = Field(None, description='Filtrar por tamanho')
    min_price: Optional[float] = Field(None, gt=0, description='Preço mínimo')
    max_price: Optional[float] = Field(None, gt=0, description='Preço máximo')
    available_only: bool = Field(default=True, description='Apenas itens disponíveis')
    has_ingredients: Optional[bool] = Field(None, description='Filtrar itens com ingredientes informados')

    @validator('max_price')
    def validate_price_range(cls, v, values):
        """Validar que preço máximo é maior que mínimo"""
        if v is not None and 'min_price' in values and values['min_price'] is not None:
            if v <= values['min_price']:
                raise ValueError('Preço máximo deve ser maior que preço mínimo')
        return v
