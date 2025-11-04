from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..config.database import get_db
from ..config.security import get_current_user, verify_admin_access
from ..models.item import CategoryType, Item, SizeType
from ..models.user import User
from ..schemas.item_schemas import ItemCreate, ItemResponse, ItemUpdate

item_router = APIRouter(prefix='/items', tags=['items'])


@item_router.get('/')
async def home():
    """
    Rota padrão de itens
    """
    return {'message': 'rota de itens do cardápio'}


@item_router.post('/create-item', response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: ItemCreate, current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Rota para criação de um novo item do cardápio (apenas administradores)
    """
    # Verificar se o usuário é admin
    verify_admin_access(current_user_id, db)
    try:
        # Verificar se o usuário existe e está ativo
        current_user = db.query(User).filter(User.id == current_user_id).first()
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Usuário não encontrado')

        # Verificar se item com mesmo nome já existe
        existing_item = db.query(Item).filter(Item.name == item_data.name).first()
        if existing_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Item com nome '{item_data.name}' já existe"
            )

        # Criar o novo item
        new_item = Item(
            name=item_data.name,
            description=item_data.description,
            category=item_data.category,
            size=item_data.size,
            price=item_data.price,
            is_available=item_data.is_available,
            calories=item_data.calories,
            preparation_time=item_data.preparation_time,
            image_url=item_data.image_url,
            ingredients=item_data.ingredients,
            allergens=item_data.allergens,
        )

        db.add(new_item)
        db.commit()
        db.refresh(new_item)

        return new_item

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Erro interno do servidor: {str(e)}'
        )


@item_router.get('/list-items', response_model=List[ItemResponse])
async def list_items(
    skip: int = 0,
    limit: int = 100,
    category: Optional[CategoryType] = None,
    available_only: bool = True,
    db: Session = Depends(get_db),
):
    """
    Listar itens do cardápio com filtros opcionais
    """
    try:
        query = db.query(Item)

        # Filtrar por categoria se especificado
        if category:
            query = query.filter(Item.category == category)

        # Filtrar apenas itens disponíveis se solicitado
        if available_only:
            query = query.filter(Item.is_available == True)

        # Ordenar por categoria e nome
        query = query.order_by(Item.category, Item.name)

        # Aplicar paginação
        items = query.offset(skip).limit(limit).all()

        return items

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Erro ao listar itens: {str(e)}')


@item_router.get('/get-item/{item_id}', response_model=ItemResponse)
async def get_item(item_id: int, db: Session = Depends(get_db)):
    """
    Obter detalhes de um item específico pelo ID
    """
    item = db.query(Item).filter(Item.id == item_id).first()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Item com ID {item_id} não encontrado')

    return item


@item_router.put('/edit-item/{item_id}', response_model=ItemResponse)
async def edit_item(
    item_id: int, item_data: ItemUpdate, current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Editar um item do cardápio (apenas administradores)
    """
    try:
        # Verificar se o usuário é admin
        verify_admin_access(current_user_id, db)

        # Buscar o item
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Item com ID {item_id} não encontrado')

        # Verificar se novo nome já existe (se foi alterado)
        if item_data.name and item_data.name != item.name:
            existing_item = db.query(Item).filter(Item.name == item_data.name).first()
            if existing_item:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=f"Item com nome '{item_data.name}' já existe"
                )

        # Atualizar campos fornecidos
        update_data = item_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)

        db.commit()
        db.refresh(item)

        return item

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Erro ao editar item: {str(e)}')


@item_router.delete('/delete-item/{item_id}')
async def delete_item(item_id: int, current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Deletar um item do cardápio (apenas administradores)
    """
    try:
        # Verificar se o usuário é admin
        verify_admin_access(current_user_id, db)

        # Buscar o item
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Item com ID {item_id} não encontrado')

        # Verificar se item está sendo usado em pedidos
        from ..models.order_item import OrderItem

        item_in_orders = db.query(OrderItem).filter(OrderItem.item_id == item_id).first()

        if item_in_orders:
            # Ao invés de deletar, desativar o item
            item.is_available = False
            db.commit()
            return {
                'message': f"Item '{item.name}' foi desativado pois está sendo usado em pedidos",
                'action': 'deactivated',
            }
        else:
            # Deletar permanentemente se não estiver em uso
            db.delete(item)
            db.commit()
            return {'message': f"Item '{item.name}' deletado com sucesso", 'action': 'deleted'}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Erro ao deletar item: {str(e)}')


@item_router.put('/toggle-availability/{item_id}', response_model=ItemResponse)
async def toggle_item_availability(
    item_id: int, current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Alternar disponibilidade de um item (apenas administradores)
    """
    try:
        # Verificar se o usuário é admin
        verify_admin_access(current_user_id, db)

        # Buscar o item
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Item com ID {item_id} não encontrado')

        # Alternar disponibilidade
        item.is_available = not item.is_available
        db.commit()
        db.refresh(item)

        status_text = 'ativado' if item.is_available else 'desativado'
        return item

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Erro ao alterar disponibilidade: {str(e)}'
        )


# Endpoints públicos (sem autenticação)


@item_router.get('/menu', response_model=List[ItemResponse])
async def get_public_menu(
    category: CategoryType = None,
    available_only: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Obter cardápio público (sem autenticação)
    """
    query = db.query(Item)

    if category:
        query = query.filter(Item.category == category)

    if available_only:
        query = query.filter(Item.is_available == True)

    items = query.offset(skip).limit(limit).all()
    return items


@item_router.get('/categories')
async def get_categories():
    """
    Obter todas as categorias disponíveis
    """
    return [{'value': category.value, 'label': category.value.title()} for category in CategoryType]


@item_router.get('/search')
async def search_items(
    q: str,
    category: CategoryType = None,
    available_only: bool = True,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """
    Buscar itens por nome ou descrição
    """
    query = db.query(Item).filter(Item.name.ilike(f'%{q}%') | Item.description.ilike(f'%{q}%'))

    if category:
        query = query.filter(Item.category == category)

    if available_only:
        query = query.filter(Item.is_available == True)

    items = query.offset(skip).limit(limit).all()
    return items


@item_router.get('/{item_id}/public', response_model=ItemResponse)
async def get_item_public(item_id: int, db: Session = Depends(get_db)):
    """
    Obter detalhes de um item específico (público)
    """
    item = db.query(Item).filter(Item.id == item_id, Item.is_available == True).first()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item não encontrado ou não disponível')

    return item
