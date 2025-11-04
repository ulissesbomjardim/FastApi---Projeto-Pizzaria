#!/usr/bin/env python3

import sys
import os
sys.path.append('/app')

from sqlalchemy.orm import Session
from src.config.database import SessionLocal
from src.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user():
    db: Session = SessionLocal()
    try:
        # Verificar se o usuário admin já existe
        existing_admin = db.query(User).filter(User.email == "admin@pizzaria.com").first()
        
        if existing_admin:
            print(f"Usuário admin já existe: {existing_admin.email} (is_admin: {existing_admin.is_admin})")
            if not existing_admin.is_admin:
                existing_admin.is_admin = True
                db.commit()
                print("Usuário promovido para admin!")
        else:
            # Criar novo usuário admin
            hashed_password = pwd_context.hash("Admin123!@#")
            
            admin_user = User(
                username="admin",
                email="admin@pizzaria.com",
                full_name="Administrador",
                hashed_password=hashed_password,
                is_admin=True,
                is_active=True
            )
            
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            print(f"Usuário admin criado: {admin_user.email} (is_admin: {admin_user.is_admin})")
            
        # Verificar também o usuário teste
        existing_test = db.query(User).filter(User.email == "teste1@example.com").first()
        
        if not existing_test:
            hashed_password = pwd_context.hash("Minh@Senha1")
            
            test_user = User(
                username="teste1",
                email="teste1@example.com",
                full_name="Usuário Teste",
                hashed_password=hashed_password,
                is_admin=False,
                is_active=True
            )
            
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            print(f"Usuário teste criado: {test_user.email} (is_admin: {test_user.is_admin})")
        else:
            print(f"Usuário teste já existe: {existing_test.email} (is_admin: {existing_test.is_admin})")
            
    except Exception as e:
        print(f"Erro ao criar usuários: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()