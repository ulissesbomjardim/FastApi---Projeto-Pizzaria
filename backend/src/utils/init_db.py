"""
Utilitários para inicialização do banco de dados
"""
import os
from sqlalchemy.orm import Session
from ..config.database import SessionLocal
from ..models.user import User
from ..config.security import hash_password


def create_default_users():
    """
    Cria os usuários padrão (admin e teste) se não existirem
    """
    db: Session = SessionLocal()
    
    try:
        # 1. Criar usuário admin
        admin_email = os.getenv("ADMIN_EMAIL", "admin@pizzaria.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "Admin123!@#")
        
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        
        if not existing_admin:
            # Criar usuário admin
            hashed_password = hash_password(admin_password)
            
            admin_user = User(
                username="admin",
                email=admin_email,
                hashed_password=hashed_password,
                is_admin=True,
                is_active=True
            )
            
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            print(f"✅ Usuário admin criado: {admin_email}")
            print(f"🔑 Senha: {admin_password}")
            
        else:
            print(f"ℹ️  Usuário admin já existe: {admin_email}")
            # Garantir que tem permissões corretas
            existing_admin.is_admin = True
            existing_admin.is_active = True
            existing_admin.hashed_password = hash_password(admin_password)
            db.commit()
            print("🔄 Permissões e senha do admin atualizadas")
        
        # 2. Criar usuário de teste
        test_email = os.getenv("EMAIL", "teste1@example.com")
        test_password = os.getenv("PASSWORD", "Minh@Senha1")
        
        existing_test = db.query(User).filter(User.email == test_email).first()
        
        if not existing_test:
            # Criar usuário de teste
            hashed_password = hash_password(test_password)
            
            test_user = User(
                username="teste1",
                email=test_email,
                hashed_password=hashed_password,
                is_admin=False,
                is_active=True
            )
            
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            print(f"✅ Usuário de teste criado: {test_email}")
            print(f"🔑 Senha: {test_password}")
            
        else:
            print(f"ℹ️  Usuário de teste já existe: {test_email}")
            # Garantir que tem senha correta
            existing_test.hashed_password = hash_password(test_password)
            existing_test.is_active = True
            db.commit()
            print("🔄 Senha do usuário de teste atualizada")
            
    except Exception as e:
        print(f"❌ Erro ao criar usuários padrão: {e}")
        db.rollback()
    finally:
        db.close()


def create_default_admin():
    """
    Mantida para compatibilidade - chama create_default_users
    """
    create_default_users()


def init_database():
    """
    Inicializa o banco de dados com dados padrão
    """
    print("🚀 Inicializando banco de dados...")
    create_default_users()
    print("✅ Inicialização concluída!")
    print("\n📝 Credenciais para login:")
    print("   👨‍💼 Admin: admin@pizzaria.com / Admin123!@#")
    print("   👤 Teste: teste1@example.com / Minh@Senha1")