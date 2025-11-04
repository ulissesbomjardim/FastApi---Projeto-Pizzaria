"""
Utilitários para cálculos de pedidos
"""
from decimal import Decimal
from typing import List
from sqlalchemy.orm import Session
from ..models.order import Order
from ..models.order_item import OrderItem
from ..models.item import Item


def recalculate_order_totals(order: Order, db: Session) -> dict:
    """
    Recalcula todos os totais de um pedido baseado nos itens atuais
    
    Args:
        order: Instância do pedido a ser recalculado
        db: Sessão do banco de dados
        
    Returns:
        dict: Dicionário com os novos valores calculados
    """
    # Buscar todos os itens do pedido
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    
    if not order_items:
        # Se não há itens, zerar totais
        order.subtotal = 0.0
        order.total_amount = 0.0
        order.estimated_delivery_time = None
        
        return {
            'subtotal': 0.0,
            'delivery_fee': order.delivery_fee or 0.0,
            'total_amount': 0.0,
            'estimated_delivery_time': None,
            'items_count': 0
        }
    
    # Calcular subtotal
    subtotal = sum(Decimal(str(oi.total_price)) for oi in order_items)
    
    # Taxa de entrega
    delivery_fee = Decimal(str(order.delivery_fee)) if order.delivery_fee else Decimal('0.00')
    
    # Total final
    total_amount = subtotal + delivery_fee
    
    # Recalcular tempo de preparo
    item_ids = [oi.item_id for oi in order_items]
    items_prep_times = db.query(Item.preparation_time).filter(Item.id.in_(item_ids)).all()
    max_prep_time = max([pt[0] or 20 for pt in items_prep_times]) if items_prep_times else 20
    delivery_time = 30 if order.is_delivery else 0
    estimated_delivery_time = max_prep_time + delivery_time
    
    # Atualizar o pedido
    order.subtotal = float(subtotal)
    order.total_amount = float(total_amount)
    order.estimated_delivery_time = estimated_delivery_time
    
    return {
        'subtotal': float(subtotal),
        'delivery_fee': float(delivery_fee),
        'total_amount': float(total_amount),
        'estimated_delivery_time': estimated_delivery_time,
        'items_count': len(order_items)
    }


def calculate_item_subtotal(unit_price: float, quantity: int) -> float:
    """
    Calcula o subtotal de um item específico
    
    Args:
        unit_price: Preço unitário do item
        quantity: Quantidade do item
        
    Returns:
        float: Subtotal calculado
    """
    return float(Decimal(str(unit_price)) * Decimal(str(quantity)))


def validate_order_modification(order: Order) -> bool:
    """
    Valida se um pedido pode ser modificado baseado no seu status
    
    Args:
        order: Instância do pedido
        
    Returns:
        bool: True se pode ser modificado, False caso contrário
    """
    forbidden_statuses = ['entregue', 'cancelado', 'saiu_entrega']
    return order.status not in forbidden_statuses