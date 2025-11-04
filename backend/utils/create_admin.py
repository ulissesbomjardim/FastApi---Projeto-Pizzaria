"""
Script para criar usuário admin
"""
import sys
import os
sys.path.append('/app')
sys.path.append('/app/backend')

from backend.src.config.database import SessionLocal
from backend.src.models.user import User
from backend.src.config.security import hash_password

def create_admin_user():
    """Criar usuário admin para teste"""
    db = SessionLocal()
    
    try:
        # Verificar se usuário admin já existe com esse email
        existing_user = db.query(User).filter(User.email == "admin@pizzaria.com").first()
        if existing_user:
            print("✅ Usuário admin já existe")
            print(f"   Email: {existing_user.email}")
            print(f"   Username: {existing_user.username}")
            print("   Resetando senha para: Admin123!@#")
            
            # Resetar senha para coincidir com .env
            existing_user.hashed_password = hash_password("Admin123!@#")
            existing_user.is_admin = True
            db.commit()
            print("✅ Senha resetada com sucesso!")
            return
        
        # Criar novo usuário admin
        hashed_password = hash_password("Admin123!@#")
        
        admin_user = User(
            username="admin",
            email="admin@pizzaria.com",
            hashed_password=hashed_password,
            is_active=True,
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Usuário admin criado com sucesso!")
        print(f"   Email: {admin_user.email}")
        print(f"   Username: {admin_user.username}")
        print("   Senha: Admin123!@#")
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()