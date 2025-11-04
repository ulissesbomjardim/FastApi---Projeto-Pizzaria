"""
Script para popular o banco de dados com itens completos do cardápio
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config.database import SessionLocal
from src.models.item import CategoryType, Item, SizeType


def create_complete_menu():
    """Criar cardápio completo da pizzaria"""
    db = SessionLocal()

    try:
        # Verificar quantos itens já existem
        existing_count = db.query(Item).count()
        print(f'Itens existentes no banco: {existing_count}')

        # Lista completa de itens para criar
        items_to_create = [
            # === PIZZAS ===
            # Pizzas Pequenas
            Item(
                name='Pizza Margherita Pequena',
                description='Pizza clássica com molho de tomate, mussarela e manjericão fresco',
                category=CategoryType.PIZZA,
                size=SizeType.PEQUENA,
                price=18.90,
                is_available=True,
                preparation_time=20,
                ingredients='Molho de tomate, mussarela, manjericão, massa tradicional',
                allergens='Glúten, Laticínios',
            ),
            Item(
                name='Pizza Pepperoni Pequena',
                description='Pizza com pepperoni italiano e mussarela',
                category=CategoryType.PIZZA,
                size=SizeType.PEQUENA,
                price=22.90,
                is_available=True,
                preparation_time=20,
                ingredients='Molho de tomate, mussarela, pepperoni, massa tradicional',
                allergens='Glúten, Laticínios',
            ),
            # Pizzas Médias
            Item(
                name='Pizza Margherita Média',
                description='Pizza clássica com molho de tomate, mussarela e manjericão fresco',
                category=CategoryType.PIZZA,
                size=SizeType.MEDIA,
                price=28.90,
                is_available=True,
                preparation_time=25,
                ingredients='Molho de tomate, mussarela, manjericão, massa tradicional',
                allergens='Glúten, Laticínios',
            ),
            Item(
                name='Pizza Pepperoni Média',
                description='Pizza com pepperoni italiano e mussarela',
                category=CategoryType.PIZZA,
                size=SizeType.MEDIA,
                price=34.90,
                is_available=True,
                preparation_time=25,
                ingredients='Molho de tomate, mussarela, pepperoni, massa tradicional',
                allergens='Glúten, Laticínios',
            ),
            Item(
                name='Pizza Calabresa Média',
                description='Pizza com calabresa, cebola e mussarela',
                category=CategoryType.PIZZA,
                size=SizeType.MEDIA,
                price=32.90,
                is_available=True,
                preparation_time=25,
                ingredients='Molho de tomate, mussarela, calabresa, cebola, massa tradicional',
                allergens='Glúten, Laticínios',
            ),
            # Pizzas Grandes
            Item(
                name='Pizza Margherita Grande',
                description='Pizza clássica com molho de tomate, mussarela e manjericão fresco',
                category=CategoryType.PIZZA,
                size=SizeType.GRANDE,
                price=42.90,
                is_available=True,
                preparation_time=30,
                ingredients='Molho de tomate, mussarela, manjericão, massa tradicional',
                allergens='Glúten, Laticínios',
            ),
            Item(
                name='Pizza Pepperoni Grande',
                description='Pizza com pepperoni italiano e mussarela',
                category=CategoryType.PIZZA,
                size=SizeType.GRANDE,
                price=48.90,
                is_available=True,
                preparation_time=30,
                ingredients='Molho de tomate, mussarela, pepperoni, massa tradicional',
                allergens='Glúten, Laticínios',
            ),
            Item(
                name='Pizza Portuguesa Grande',
                description='Pizza com presunto, ovos, cebola, azeitona e mussarela',
                category=CategoryType.PIZZA,
                size=SizeType.GRANDE,
                price=46.90,
                is_available=True,
                preparation_time=30,
                ingredients='Molho de tomate, mussarela, presunto, ovos, cebola, azeitona, massa tradicional',
                allergens='Glúten, Laticínios, Ovos',
            ),
            # Pizza Família
            Item(
                name='Pizza Família Especial',
                description='Pizza gigante para a família com 4 sabores: Margherita, Calabresa, Portuguesa e Pepperoni',
                category=CategoryType.PIZZA,
                size=SizeType.FAMILIA,
                price=65.90,
                is_available=True,
                preparation_time=35,
                ingredients='Molho de tomate, mussarela, diversos recheios, massa tradicional',
                allergens='Glúten, Laticínios, Ovos',
            ),
            # === BEBIDAS ===
            # Refrigerantes 350ml
            Item(
                name='Coca-Cola 350ml',
                description='Refrigerante Coca-Cola gelado',
                category=CategoryType.BEBIDA,
                size=SizeType.ML_350,
                price=4.50,
                is_available=True,
                preparation_time=1,
            ),
            Item(
                name='Guaraná Antarctica 350ml',
                description='Refrigerante Guaraná Antarctica gelado',
                category=CategoryType.BEBIDA,
                size=SizeType.ML_350,
                price=4.50,
                is_available=True,
                preparation_time=1,
            ),
            # Refrigerantes 500ml
            Item(
                name='Coca-Cola 500ml',
                description='Refrigerante Coca-Cola gelado',
                category=CategoryType.BEBIDA,
                size=SizeType.ML_500,
                price=6.50,
                is_available=True,
                preparation_time=1,
            ),
            Item(
                name='Fanta Laranja 500ml',
                description='Refrigerante Fanta Laranja gelado',
                category=CategoryType.BEBIDA,
                size=SizeType.ML_500,
                price=6.50,
                is_available=True,
                preparation_time=1,
            ),
            # Refrigerantes 1L
            Item(
                name='Coca-Cola 1L',
                description='Refrigerante Coca-Cola gelado - garrafa 1 litro',
                category=CategoryType.BEBIDA,
                size=SizeType.L_1,
                price=8.90,
                is_available=True,
                preparation_time=1,
            ),
            # Refrigerantes 2L
            Item(
                name='Coca-Cola 2L',
                description='Refrigerante Coca-Cola gelado - garrafa 2 litros',
                category=CategoryType.BEBIDA,
                size=SizeType.L_2,
                price=12.90,
                is_available=True,
                preparation_time=1,
            ),
            # === ENTRADAS ===
            Item(
                name='Pão de Alho',
                description='Delicioso pão de alho da casa com queijo',
                category=CategoryType.ENTRADA,
                size=SizeType.UNICO,
                price=15.90,
                is_available=True,
                preparation_time=10,
                ingredients='Pão, alho, manteiga, queijo, orégano',
                allergens='Glúten, Laticínios',
            ),
            Item(
                name='Bruschetta Italiana',
                description='Bruschetta com tomate, manjericão e azeite',
                category=CategoryType.ENTRADA,
                size=SizeType.UNICO,
                price=18.90,
                is_available=True,
                preparation_time=8,
                ingredients='Pão italiano, tomate, manjericão, alho, azeite',
                allergens='Glúten',
            ),
            Item(
                name='Bolinha de Queijo',
                description='Porção de 10 bolinhas de queijo empanadas',
                category=CategoryType.ENTRADA,
                size=SizeType.UNICO,
                price=22.90,
                is_available=True,
                preparation_time=15,
                ingredients='Queijo, farinha de trigo, ovos, farinha de rosca',
                allergens='Glúten, Laticínios, Ovos',
            ),
            # === SOBREMESAS ===
            Item(
                name='Petit Gateau',
                description='Petit gateau de chocolate com sorvete de baunilha',
                category=CategoryType.SOBREMESA,
                size=SizeType.UNICO,
                price=16.90,
                is_available=True,
                preparation_time=12,
                ingredients='Chocolate, farinha, ovos, açúcar, sorvete',
                allergens='Glúten, Laticínios, Ovos',
            ),
            Item(
                name='Tiramisu da Casa',
                description='Tradicional tiramisu italiano com café',
                category=CategoryType.SOBREMESA,
                size=SizeType.UNICO,
                price=14.90,
                is_available=True,
                preparation_time=5,
                ingredients='Mascarpone, biscoitos, café, cacau, ovos',
                allergens='Glúten, Laticínios, Ovos',
            ),
            Item(
                name='Pudim de Leite',
                description='Pudim de leite condensado com calda de caramelo',
                category=CategoryType.SOBREMESA,
                size=SizeType.UNICO,
                price=12.90,
                is_available=True,
                preparation_time=3,
                ingredients='Leite condensado, ovos, açúcar, leite',
                allergens='Laticínios, Ovos',
            ),
            # === PROMOÇÕES ===
            Item(
                name='Combo Pizza + Refri',
                description='Pizza Média + Refrigerante 500ml por um preço especial',
                category=CategoryType.PROMOCAO,
                size=SizeType.UNICO,
                price=35.90,
                is_available=True,
                preparation_time=25,
                ingredients='Pizza à sua escolha + refrigerante',
                allergens='Glúten, Laticínios (varia conforme pizza)',
            ),
            Item(
                name='Combo Família Completo',
                description='Pizza Família + 2 Refrigerantes 1L + Entrada',
                category=CategoryType.PROMOCAO,
                size=SizeType.UNICO,
                price=89.90,
                is_available=True,
                preparation_time=40,
                ingredients='Pizza família + bebidas + entrada',
                allergens='Glúten, Laticínios (varia conforme itens)',
            ),
        ]

        # Verificar quais itens já existem
        existing_names = [item.name for item in db.query(Item).all()]
        new_items = []

        for item in items_to_create:
            if item.name not in existing_names:
                new_items.append(item)

        if new_items:
            print(f'Adicionando {len(new_items)} novos itens...')
            db.add_all(new_items)
            db.commit()

            print('✅ Cardápio completo criado com sucesso!')

            # Mostrar resumo por categoria
            categories = db.query(Item.category).distinct().all()
            for (category,) in categories:
                count = db.query(Item).filter(Item.category == category).count()
                print(f'  📦 {category.value.title()}: {count} itens')
        else:
            print('ℹ️  Todos os itens já existem no banco de dados')

        # Mostrar total
        total_items = db.query(Item).count()
        print(f'\n🍕 Total de itens no cardápio: {total_items}')

    except Exception as e:
        db.rollback()
        print(f'❌ Erro ao criar cardápio: {e}')

    finally:
        db.close()


if __name__ == '__main__':
    create_complete_menu()
