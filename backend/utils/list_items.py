"""
Script para listar itens do cardápio
"""
import sys
sys.path.append('/app')
sys.path.append('/app/backend')

from backend.src.config.database import SessionLocal
from backend.src.models.item import Item

def list_items():
    db = SessionLocal()
    
    try:
        items = db.query(Item).all()
        print(f'Total de itens: {len(items)}')
        
        if items:
            print("\nItens do cardápio:")
            print("-" * 80)
            for item in items:
                available = "✅" if item.is_available else "❌"
                print(f'{available} ID: {item.id:2d} | {item.name:25s} | R$ {item.price:6.2f} | {item.category}')
        else:
            print("Nenhum item encontrado no cardápio!")
            
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_items()