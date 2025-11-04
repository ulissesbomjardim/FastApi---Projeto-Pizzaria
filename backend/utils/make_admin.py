#!/usr/bin/env python3
"""
Script para tornar um usuário administrador
"""
import os
import sys

sys.path.append('/app')
sys.path.append('/app/backend')

from backend.src.config.database import SessionLocal
from backend.src.models.user import User


def make_user_admin():
    """Tornar o usuário com ID 1 como administrador"""
    db = SessionLocal()

    try:
        print('=== Tornando usuário administrador ===')

        # Buscar usuário com ID 1 (teste1)
        user = db.query(User).filter(User.id == 1).first()

        if not user:
            print('✗ Usuário com ID 1 não encontrado!')
            return

        print(f'Usuário encontrado: {user.username} ({user.email})')
        print(f'Status atual - Admin: {user.is_admin}')

        # Tornar admin se ainda não for
        if not user.is_admin:
            user.is_admin = True
            db.commit()
            print('✓ Usuário agora é administrador!')
        else:
            print('✓ Usuário já é administrador!')

        # Verificar outros usuários
        all_users = db.query(User).all()
        print(f'\n=== Todos os usuários ({len(all_users)}) ===')
        for u in all_users:
            admin_status = 'ADMIN' if u.is_admin else 'USER'
            print(f'ID {u.id}: {u.username} ({u.email}) - {admin_status}')

    except Exception as e:
        print(f'✗ Erro: {e}')
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
    make_user_admin()
