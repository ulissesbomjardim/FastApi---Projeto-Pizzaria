from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..config.database import get_db
from ..config.security import get_current_user, verify_admin_access
from ..models.user import User
from ..schemas.auth_schemas import UserResponse, UserUpdate

user_router = APIRouter(prefix='/users', tags=['users'])


@user_router.get('/me', response_model=UserResponse)
async def get_current_user_info(current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Obter informações do usuário atual
    """
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuário não encontrado')
    return user


@user_router.put('/me', response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate, current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Atualizar informações do usuário atual
    """
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuário não encontrado')

    # Atualizar apenas os campos fornecidos
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@user_router.get('/list', response_model=List[UserResponse])
async def list_users(
    skip: int = 0, limit: int = 50, current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Listar usuários (apenas administradores)
    """
    # Verificar se o usuário é admin
    verify_admin_access(current_user_id, db)

    users = db.query(User).offset(skip).limit(limit).all()
    return users


@user_router.get('/{user_id}', response_model=UserResponse)
async def get_user_by_id(user_id: int, current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Obter usuário por ID (apenas administradores)
    """
    # Verificar se o usuário é admin
    verify_admin_access(current_user_id, db)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuário não encontrado')
    return user


@user_router.patch('/{user_id}/admin')
async def toggle_admin_status(
    user_id: int, is_admin: bool, current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Alterar status de administrador (apenas administradores)
    """
    # Verificar se o usuário é admin
    verify_admin_access(current_user_id, db)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuário não encontrado')

    # Não permitir que o usuário remova seu próprio status de admin
    if user_id == current_user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Não é possível remover seu próprio status de administrador'
        )

    user.is_admin = is_admin
    db.commit()
    db.refresh(user)

    action = 'promovido a' if is_admin else 'removido de'
    return {'message': f'Usuário {user.username} {action} administrador com sucesso', 'user': user}


@user_router.patch('/{user_id}/active')
async def toggle_user_active_status(
    user_id: int, is_active: bool, current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Ativar/desativar usuário (apenas administradores)
    """
    # Verificar se o usuário é admin
    verify_admin_access(current_user_id, db)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuário não encontrado')

    # Não permitir que o usuário desative a própria conta
    if user_id == current_user_id and not is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Não é possível desativar sua própria conta'
        )

    user.is_active = is_active
    db.commit()
    db.refresh(user)

    action = 'ativado' if is_active else 'desativado'
    return {'message': f'Usuário {user.username} {action} com sucesso', 'user': user}


@user_router.get('/admin/stats')
async def get_user_statistics(current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Obter estatísticas de usuários (apenas administradores)
    """
    # Verificar se o usuário é admin
    verify_admin_access(current_user_id, db)

    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    admin_users = db.query(User).filter(User.is_admin == True).count()
    inactive_users = total_users - active_users

    return {
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'admin_users': admin_users,
        'regular_users': total_users - admin_users,
    }
