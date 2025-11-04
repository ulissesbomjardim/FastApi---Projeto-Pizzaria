import json
from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..config.database import get_db
from ..config.security import get_current_user, verify_admin_access
from ..models.item import Item
from ..models.order import Order
from ..models.order_item import OrderItem
from ..models.user import User
from ..schemas.order_schemas import OrderCreate, OrderResponse, OrderSummary, OrderItemAdd, OrderItemRemove

order_router = APIRouter(prefix='/orders', tags=['orders'])


def safe_float(value, decimal_places=2):
    """Converte Decimal/float para float garantindo casas decimais corretas"""
    if isinstance(value, Decimal):
        return float(round(value, decimal_places))
    elif isinstance(value, (int, float)):
        return float(round(Decimal(str(value)), decimal_places))
    return float(value)


@order_router.get('/')
async def home():
    """
    Rota padrão de pedidos
    """
    return {'message': 'rota de pedidos'}


@order_router.post('/debug-order')
async def debug_order(request_data: dict, current_user_id: int = Depends(get_current_user)):
    """
    Endpoint temporário para debug de dados de pedido
    """
    print(f"DEBUG - Raw order data: {request_data}")
    print(f"DEBUG - User ID: {current_user_id}")
    return {"received": request_data, "user_id": current_user_id}


@order_router.post('/create-order', status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate, current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Rota para criação de um novo pedido (usuário deve estar autenticado)
    """
    try:
        # Debug: Imprimir dados recebidos
        print(f"DEBUG - Order data received: {order_data}")
        print(f"DEBUG - User ID: {current_user_id}")
        # Buscar dados do usuário autenticado
        current_user = db.query(User).filter(User.id == current_user_id).first()
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Usuário não encontrado')
        # Validar se todos os itens existem e estão disponíveis
        item_ids = [item.item_id for item in order_data.items]
        items_db = db.query(Item).filter(Item.id.in_(item_ids)).all()

        if len(items_db) != len(item_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Um ou mais itens não foram encontrados'
            )

        # Verificar se todos os itens estão disponíveis
        unavailable_items = [item for item in items_db if not item.is_available]
        if unavailable_items:
            unavailable_names = [item.name for item in unavailable_items]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Itens indisponíveis: {', '.join(unavailable_names)}"
            )

        # Criar mapeamento de itens por ID
        items_map = {item.id: item for item in items_db}

        # Calcular valores
        subtotal = Decimal('0.00')
        order_items_data = []

        for order_item in order_data.items:
            item = items_map[order_item.item_id]
            unit_price = Decimal(str(item.price))
            item_subtotal = unit_price * Decimal(str(order_item.quantity))
            subtotal += item_subtotal

            order_items_data.append(
                {
                    'item_id': order_item.item_id,
                    'quantity': order_item.quantity,
                    'unit_price': float(unit_price),
                    'total_price': float(item_subtotal),
                    'notes': order_item.observations,
                }
            )

        # Calcular taxa de entrega
        delivery_fee = Decimal('5.00') if order_data.is_delivery else Decimal('0.00')
        total_amount = subtotal + delivery_fee

        # Gerar número do pedido
        import uuid

        order_number = f'PED-{uuid.uuid4().hex[:8].upper()}'

        # Criar o pedido
        new_order = Order(
            order_number=order_number,
            user_id=current_user.id,  # ID do usuário autenticado
            customer_name=order_data.customer_name or current_user.username,  # Usar nome do usuário se não informado
            customer_phone=order_data.customer_phone,
            is_delivery=order_data.is_delivery,
            delivery_address=json.dumps(order_data.delivery_address.dict()) if order_data.delivery_address else None,
            payment_method=order_data.payment_method.value if order_data.payment_method else None,
            observations=order_data.observations,
            subtotal=float(subtotal),
            delivery_fee=float(delivery_fee),
            total_amount=float(total_amount),
            status='pendente',
        )

        db.add(new_order)
        db.flush()  # Para obter o ID do pedido

        # Criar os itens do pedido
        order_items = []
        for item_data in order_items_data:
            order_item = OrderItem(order_id=new_order.id, **item_data)
            order_items.append(order_item)
            db.add(order_item)

        # Calcular tempo estimado de preparo
        max_prep_time = max([items_map[item.item_id].preparation_time or 20 for item in order_data.items])
        delivery_time = 30 if order_data.is_delivery else 0
        new_order.estimated_delivery_time = max_prep_time + delivery_time

        db.commit()
        db.refresh(new_order)

        # Construir resposta manualmente para compatibilidade com o schema
        response_items = []
        for order_item in order_items:
            db.refresh(order_item)
            # Carregar o item completo
            item = db.query(Item).filter(Item.id == order_item.item_id).first()

            response_items.append(
                {
                    'id': order_item.id,
                    'item_id': order_item.item_id,
                    'quantity': order_item.quantity,
                    'unit_price': order_item.unit_price,
                    'subtotal': order_item.total_price,
                    'observations': order_item.notes,
                    'item': {
                        'id': item.id,
                        'name': item.name,
                        'description': item.description,
                        'category': item.category.value if hasattr(item.category, 'value') else item.category,
                        'size': item.size.value if hasattr(item.size, 'value') else item.size,
                        'price': item.price,
                        'is_available': item.is_available,
                        'preparation_time': item.preparation_time,
                        'ingredients': item.ingredients,
                        'allergens': item.allergens,
                        'image_url': item.image_url,
                        'created_at': item.created_at,
                        'updated_at': item.updated_at,
                    },
                }
            )

        # Construir resposta do pedido
        response_data = {
            'id': new_order.id,
            'order_number': new_order.order_number,
            'user_id': new_order.user_id,
            'customer_name': new_order.customer_name,
            'customer_phone': new_order.customer_phone,
            'is_delivery': new_order.is_delivery,
            'delivery_address': json.loads(new_order.delivery_address) if new_order.delivery_address else None,
            'payment_method': new_order.payment_method,
            'observations': new_order.observations,
            'status': new_order.status,
            'items': response_items,
            'subtotal': new_order.subtotal,
            'delivery_fee': new_order.delivery_fee,
            'total_amount': new_order.total_amount,
            'estimated_delivery_time': new_order.estimated_delivery_time,
            'created_at': new_order.created_at,
            'updated_at': new_order.updated_at,
        }

        return response_data

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Erro interno do servidor: {str(e)}'
        )


@order_router.get('/my-orders', response_model=List[OrderSummary])
async def list_my_orders(
    skip: int = 0,
    limit: int = 20,
    status_filter: str = None,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Listar pedidos do usuário autenticado
    """
    query = db.query(Order).filter(Order.user_id == current_user_id)

    if status_filter:
        query = query.filter(Order.status == status_filter)

    orders = query.offset(skip).limit(limit).all()

    # Converter para OrderSummary
    orders_summary = []
    for order in orders:
        items_count = len(order.items) if hasattr(order, 'items') else 0
        orders_summary.append(
            OrderSummary(
                id=order.id,
                order_number=order.order_number,
                customer_name=order.customer_name,
                status=order.status,
                total_amount=order.total_amount,
                created_at=order.created_at,
                items_count=items_count,
            )
        )

    return orders_summary


@order_router.get('/{order_id}', response_model=OrderResponse)
async def get_order(order_id: int, current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Buscar pedido por ID - usuário só pode ver seus próprios pedidos ou admin pode ver todos
    """
    try:
        order = db.query(Order).filter(Order.id == order_id).first()

        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Pedido não encontrado')

        # Verificar se o usuário tem permissão para ver este pedido
        user = db.query(User).filter(User.id == current_user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Usuário não encontrado')
        
        # Se não for admin e não for o dono do pedido, negar acesso
        if not user.is_admin and order.user_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Acesso negado ao pedido')

        # Construir resposta manualmente para compatibilidade com o schema
        response_items = []
        
        # Verificar se existe a relação order_items
        if hasattr(order, 'order_items') and order.order_items:
            for order_item in order.order_items:
                try:
                    # Carregar o item completo
                    item = db.query(Item).filter(Item.id == order_item.item_id).first()
                    
                    if item:
                        response_items.append(
                            {
                                'id': order_item.id,
                                'item_id': order_item.item_id,
                                'quantity': order_item.quantity,
                                'unit_price': order_item.unit_price,
                                'subtotal': order_item.total_price,
                                'observations': order_item.notes or "",
                                'item': {
                                    'id': item.id,
                                    'name': item.name,
                                    'description': item.description or "",
                                    'category': item.category.value if hasattr(item.category, 'value') else str(item.category),
                                    'size': item.size.value if hasattr(item.size, 'value') else str(item.size),
                                    'price': float(item.price),
                                    'is_available': item.is_available,
                                    'preparation_time': item.preparation_time,
                                    'ingredients': item.ingredients or [],
                                    'allergens': item.allergens,
                                    'image_url': item.image_url,
                                    'created_at': item.created_at,
                                    'updated_at': item.updated_at,
                                },
                            }
                        )
                except Exception as e:
                    # Se houver erro com um item específico, pular e continuar
                    print(f"Erro ao processar item do pedido: {e}")
                    continue

        # Construir resposta do pedido
        response_data = {
            'id': order.id,
            'order_number': order.order_number,
            'user_id': order.user_id,
            'customer_name': order.customer_name,
            'customer_phone': order.customer_phone,
            'is_delivery': order.is_delivery,
            'delivery_address': json.loads(order.delivery_address) if order.delivery_address else None,
            'payment_method': order.payment_method,
            'observations': order.observations or "",
            'status': order.status,
            'items': response_items,
            'subtotal': float(order.subtotal) if order.subtotal else 0.0,
            'delivery_fee': float(order.delivery_fee) if order.delivery_fee else 0.0,
            'total_amount': float(order.total_amount) if order.total_amount else 0.0,
            'estimated_delivery_time': order.estimated_delivery_time,
            'created_at': order.created_at,
            'updated_at': order.updated_at,
        }

        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )


@order_router.patch('/{order_id}/status')
async def update_order_status(
    order_id: int, new_status: str, current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Atualizar status do pedido (apenas administradores)
    """
    # Verificar se o usuário é admin
    verify_admin_access(current_user_id, db)
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Pedido não encontrado')

    # Validar status
    valid_statuses = ['pendente', 'confirmado', 'preparando', 'pronto', 'saiu_entrega', 'entregue', 'cancelado']
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status inválido. Valores válidos: {', '.join(valid_statuses)}",
        )

    order.status = new_status
    db.commit()
    db.refresh(order)

    return {'message': f'Status do pedido {order.order_number} atualizado para {new_status}'}


@order_router.get('/admin/all-orders', response_model=List[OrderSummary])
async def get_all_orders_admin(
    skip: int = 0,
    limit: int = 50,
    status_filter: str = None,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obter todos os pedidos (apenas administradores)
    """
    # Verificar se o usuário é admin
    verify_admin_access(current_user_id, db)

    query = db.query(Order)

    if status_filter:
        query = query.filter(Order.status == status_filter)

    orders = query.offset(skip).limit(limit).all()

    # Converter para OrderSummary
    orders_summary = []
    for order in orders:
        items_count = len(order.order_items) if hasattr(order, 'order_items') else 0
        orders_summary.append(
            OrderSummary(
                id=order.id,
                order_number=order.order_number,
                customer_name=order.customer_name,
                status=order.status,
                total_amount=order.total_amount,
                created_at=order.created_at,
                items_count=items_count,
            )
        )

    return orders_summary


@order_router.delete('/{order_id}/cancel')
async def cancel_order(order_id: int, current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Cancelar pedido (dono do pedido ou administrador)
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Pedido não encontrado')

    # Verificar permissão
    current_user = db.query(User).filter(User.id == current_user_id).first()

    # Verificar se é o dono do pedido ou admin
    if order.user_id != current_user_id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Sem permissão para cancelar este pedido')

    # Verificar se o pedido pode ser cancelado
    if order.status in ['entregue', 'cancelado']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível cancelar pedido com status '{order.status}'",
        )

    order.status = 'cancelado'
    db.commit()
    db.refresh(order)

    return {'message': f'Pedido {order.order_number} cancelado com sucesso'}


@order_router.get('/admin/stats')
async def get_order_statistics(current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Obter estatísticas de pedidos (apenas administradores)
    """
    # Verificar se o usuário é admin
    verify_admin_access(current_user_id, db)

    from sqlalchemy import func

    # Estatísticas gerais
    total_orders = db.query(Order).count()
    orders_by_status = db.query(Order.status, func.count(Order.id).label('count')).group_by(Order.status).all()

    # Receita total (excluindo cancelados)
    total_revenue = db.query(func.sum(Order.total_amount)).filter(Order.status != 'cancelado').scalar() or 0

    # Pedidos de hoje
    from datetime import date, datetime

    today = date.today()
    orders_today = db.query(Order).filter(func.date(Order.created_at) == today).count()

    # Ticket médio
    completed_orders = db.query(Order).filter(Order.status.in_(['entregue'])).count()

    average_ticket = total_revenue / completed_orders if completed_orders > 0 else 0

    return {
        'total_orders': total_orders,
        'orders_today': orders_today,
        'total_revenue': float(total_revenue),
        'average_ticket': float(average_ticket),
        'orders_by_status': [{'status': status.code if hasattr(status, 'code') else str(status), 'count': count} for status, count in orders_by_status],
    }


@order_router.post('/{order_id}/add-item', status_code=status.HTTP_201_CREATED)
async def add_item_to_order(
    order_id: int,
    item_data: OrderItemAdd,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Adicionar item a um pedido existente (apenas o dono do pedido)
    """
    try:
        # Buscar o pedido
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Pedido não encontrado')
        
        # Verificar se o usuário é o dono do pedido
        if order.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail='Você só pode modificar seus próprios pedidos'
            )
        
        # Verificar se o pedido pode ser modificado
        if order.status in ['entregue', 'cancelado', 'saiu_entrega']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Não é possível modificar pedido com status: {order.status}'
            )
        
        # Buscar o item do cardápio
        item = db.query(Item).filter(Item.id == item_data.item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item não encontrado no cardápio')
        
        # Verificar se o item está disponível
        if not item.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f'Item "{item.name}" não está disponível'
            )
        
        # Verificar se o item já existe no pedido
        existing_order_item = db.query(OrderItem).filter(
            OrderItem.order_id == order_id,
            OrderItem.item_id == item_data.item_id
        ).first()
        
        if existing_order_item:
            # Atualizar quantidade do item existente
            existing_order_item.quantity += item_data.quantity
            
            # Recalcular valores
            unit_price = Decimal(str(item.price))
            existing_order_item.total_price = safe_float(unit_price * Decimal(str(existing_order_item.quantity)))
            
            # Atualizar observações se fornecidas
            if item_data.observations:
                if existing_order_item.notes:
                    existing_order_item.notes += f" | {item_data.observations}"
                else:
                    existing_order_item.notes = item_data.observations
            
            db_order_item = existing_order_item
        else:
            # Criar novo item no pedido
            unit_price = Decimal(str(item.price))
            total_price = unit_price * Decimal(str(item_data.quantity))
            
            new_order_item = OrderItem(
                order_id=order_id,
                item_id=item_data.item_id,
                quantity=item_data.quantity,
                unit_price=safe_float(unit_price),
                total_price=safe_float(total_price),
                notes=item_data.observations
            )
            
            db.add(new_order_item)
            db.flush()  # Para obter o ID
            db_order_item = new_order_item
        
        # Recalcular totais do pedido
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        
        subtotal = sum(Decimal(str(oi.total_price)) for oi in order_items)
        delivery_fee = Decimal(str(order.delivery_fee)) if order.delivery_fee else Decimal('0.00')
        total_amount = subtotal + delivery_fee
        
        # Atualizar pedido
        order.subtotal = float(subtotal)
        order.total_amount = float(total_amount)
        
        # Recalcular tempo de preparo
        item_ids = [oi.item_id for oi in order_items]
        items_prep_times = db.query(Item.preparation_time).filter(Item.id.in_(item_ids)).all()
        max_prep_time = max([pt[0] or 20 for pt in items_prep_times])
        delivery_time = 30 if order.is_delivery else 0
        order.estimated_delivery_time = max_prep_time + delivery_time
        
        db.commit()
        db.refresh(db_order_item)
        db.refresh(order)
        
        return {
            'message': 'Item adicionado ao pedido com sucesso',
            'order_id': order.id,
            'order_number': order.order_number,
            'item_added': {
                'id': db_order_item.id,
                'item_id': db_order_item.item_id,
                'item_name': item.name,
                'quantity': db_order_item.quantity,
                'unit_price': db_order_item.unit_price,
                'total_price': db_order_item.total_price,
                'observations': db_order_item.notes
            },
            'new_totals': {
                'subtotal': order.subtotal,
                'delivery_fee': order.delivery_fee,
                'total_amount': order.total_amount,
                'estimated_delivery_time': order.estimated_delivery_time
            }
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Erro interno do servidor: {str(e)}'
        )


@order_router.delete('/{order_id}/remove-item', status_code=status.HTTP_200_OK)
async def remove_item_from_order(
    order_id: int,
    order_item_id: int,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remover item de um pedido existente (apenas o dono do pedido)
    """
    try:
        # Buscar o pedido
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Pedido não encontrado')
        
        # Verificar se o usuário é o dono do pedido
        if order.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail='Você só pode modificar seus próprios pedidos'
            )
        
        # Verificar se o pedido pode ser modificado
        if order.status in ['entregue', 'cancelado', 'saiu_entrega']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Não é possível modificar pedido com status: {order.status}'
            )
        
        # Buscar o item no pedido
        order_item = db.query(OrderItem).filter(
            OrderItem.id == order_item_id,
            OrderItem.order_id == order_id
        ).first()
        
        if not order_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail='Item não encontrado neste pedido'
            )
        
        # Guardar informações do item antes de remover
        removed_item_info = {
            'id': order_item.id,
            'item_id': order_item.item_id,
            'quantity': order_item.quantity,
            'unit_price': order_item.unit_price,
            'total_price': order_item.total_price,
            'observations': order_item.notes
        }
        
        # Buscar nome do item para resposta
        item = db.query(Item).filter(Item.id == order_item.item_id).first()
        item_name = item.name if item else f"Item ID {order_item.item_id}"
        
        # Remover o item do pedido
        db.delete(order_item)
        db.commit()  # Fazer commit da remoção primeiro
        
        # Verificar se ainda há itens no pedido após a remoção
        remaining_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        
        if not remaining_items:
            # Se não há mais itens, cancelar o pedido
            order.status = 'cancelado'
            order.subtotal = 0.0
            order.total_amount = 0.0
            order.estimated_delivery_time = None
            
            db.commit()
            
            return {
                'message': 'Item removido do pedido. Pedido cancelado pois não há mais itens.',
                'order_id': order.id,
                'order_number': order.order_number,
                'order_status': 'cancelado',
                'item_removed': {
                    **removed_item_info,
                    'item_name': item_name
                }
            }
        
        # Recalcular totais do pedido
        subtotal = sum(Decimal(str(oi.total_price)) for oi in remaining_items)
        delivery_fee = Decimal(str(order.delivery_fee)) if order.delivery_fee else Decimal('0.00')
        total_amount = subtotal + delivery_fee
        
        # Atualizar pedido
        order.subtotal = float(subtotal)
        order.total_amount = float(total_amount)
        
        # Recalcular tempo de preparo
        item_ids = [oi.item_id for oi in remaining_items]
        items_prep_times = db.query(Item.preparation_time).filter(Item.id.in_(item_ids)).all()
        max_prep_time = max([pt[0] or 20 for pt in items_prep_times])
        delivery_time = 30 if order.is_delivery else 0
        order.estimated_delivery_time = max_prep_time + delivery_time
        
        db.commit()
        db.refresh(order)
        
        return {
            'message': 'Item removido do pedido com sucesso',
            'order_id': order.id,
            'order_number': order.order_number,
            'order_status': order.status,
            'item_removed': {
                **removed_item_info,
                'item_name': item_name
            },
            'new_totals': {
                'subtotal': order.subtotal,
                'delivery_fee': order.delivery_fee,
                'total_amount': order.total_amount,
                'estimated_delivery_time': order.estimated_delivery_time
            },
            'remaining_items_count': len(remaining_items)
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Erro interno do servidor: {str(e)}'
        )
