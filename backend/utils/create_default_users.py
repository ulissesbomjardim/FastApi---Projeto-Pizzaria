"""
Script para criar usuários padrão (admin e teste)
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config.database import SessionLocal
from src.models.user import User
from src.config.security import hash_password

def create_default_users():
    """Criar usuários padrão do sistema"""
    db = SessionLocal()
    
    try:
        print("🔧 Criando usuários padrão...")
        
        # 1. Criar usuário admin
        admin_email = "admin@pizzaria.com"
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        
        if existing_admin:
            print("✅ Usuário admin já existe")
            # Garantir que tem permissão de admin e senha correta
            existing_admin.hashed_password = hash_password("Admin123!@#")
            existing_admin.is_admin = True
            existing_admin.is_active = True
            db.commit()
            print(f"   Email: {existing_admin.email}")
            print(f"   Username: {existing_admin.username}")
            print("   Senha atualizada: Admin123!@#")
        else:
            # Criar novo usuário admin
            hashed_password = hash_password("Admin123!@#")
            
            admin_user = User(
                username="admin",
                email=admin_email,
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
        
        # 2. Criar usuário de teste
        test_email = "teste1@example.com"
        existing_test = db.query(User).filter(User.email == test_email).first()
        
        if existing_test:
            print("✅ Usuário de teste já existe")
            # Garantir que tem a senha correta
            existing_test.hashed_password = hash_password("Minh@Senha1")
            existing_test.is_admin = False
            existing_test.is_active = True
            db.commit()
            print(f"   Email: {existing_test.email}")
            print(f"   Username: {existing_test.username}")
            print("   Senha atualizada: Minh@Senha1")
        else:
            # Criar novo usuário de teste
            hashed_password = hash_password("Minh@Senha1")
            
            test_user = User(
                username="teste1",
                email=test_email,
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
        
        print("\n🎉 Usuários padrão configurados com sucesso!")
        print("\n📝 Credenciais para login:")
        print("   👨‍💼 Admin: admin@pizzaria.com / Admin123!@#")
        print("   👤 Teste: teste1@example.com / Minh@Senha1")
        
    except Exception as e:
        print(f"❌ Erro ao criar usuários padrão: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_default_users()