#!/usr/bin/env python3
"""
Script simples para garantir usuários padrão no sistema
"""
import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/backend')

try:
    from backend.src.config.database import SessionLocal
    from backend.src.models.user import User
    from backend.src.config.security import hash_password
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    sys.exit(1)

def create_users():
    """Criar usuários padrão"""
    print("🔧 Criando usuários padrão...")
    
    db = SessionLocal()
    
    try:
        # Dados dos usuários
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@pizzaria.com',
                'password': 'Admin123!@#',
                'is_admin': True,
                'is_active': True
            },
            {
                'username': 'teste1',
                'email': 'teste1@example.com', 
                'password': 'Minh@Senha1',
                'is_admin': False,
                'is_active': True
            }
        ]
        
        for user_data in users_data:
            # Verificar se usuário já existe
            existing_user = db.query(User).filter(User.email == user_data['email']).first()
            
            if existing_user:
                print(f"✅ Usuário já existe: {user_data['email']}")
                # Atualizar dados
                existing_user.username = user_data['username']
                existing_user.hashed_password = hash_password(user_data['password'])
                existing_user.is_admin = user_data['is_admin']
                existing_user.is_active = user_data['is_active']
                db.commit()
                print(f"   🔄 Dados atualizados para: {user_data['username']}")
            else:
                # Criar novo usuário
                new_user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    hashed_password=hash_password(user_data['password']),
                    is_admin=user_data['is_admin'],
                    is_active=user_data['is_active']
                )
                
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                
                print(f"✅ Usuário criado: {user_data['email']}")
                print(f"   Username: {user_data['username']}")
                print(f"   Admin: {user_data['is_admin']}")
        
        print("\n🎉 Usuários configurados com sucesso!")
        print("\n📝 Credenciais para login:")
        print("   👨‍💼 Admin: admin@pizzaria.com / Admin123!@#")
        print("   👤 Teste: teste1@example.com / Minh@Senha1")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_users()