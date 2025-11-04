"""
Script para criar um usuário de teste
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config.database import SessionLocal
from src.models.user import User
from src.config.security import hash_password

def create_test_user():
    """Criar usuário de teste"""
    db = SessionLocal()
    
    try:
        # Verificar se usuário já existe
        existing_user = db.query(User).filter(User.email == "teste1@example.com").first()
        if existing_user:
            print("✅ Usuário de teste já existe: teste1@example.com")
            return
        
        # Criar usuário de teste
        hashed_password = hash_password("Minh@Senha1")
        
        test_user = User(
            username="teste1",
            email="teste1@example.com",
            hashed_password=hashed_password,
            is_active=True,
            is_admin=False
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print("✅ Usuário de teste criado com sucesso!")
        print(f"   Email: {test_user.email}")
        print(f"   Username: {test_user.username}")
        print("   Senha: Minh@Senha1")
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário de teste: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()