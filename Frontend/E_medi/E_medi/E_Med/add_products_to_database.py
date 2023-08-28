#add_products_to_database.py

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_medi.settings')
django.setup()

from E_Med.models import Product, Category


def add_products():
    product_list = [
        {
            'name': 'OMEPRAZOLE',
            'description': 'Description for OMEPRAZOLE',
            'price': 10.99,
            'stock': 100,
            'category': 'Medicine',  # Change this to the appropriate category name
        },
        {
            'name': 'TAB - ALLEGRA',
            'description': 'Description for TAB - ALLEGRA',
            'price': 15.99,
            'stock': 50,
            'category': 'Medicine',  # Change this to the appropriate category name
        },
        {
            'name': 'CAP - ZIFFY',
            'description': 'Description for CAP - ZIFFY',
            'price': 8.99,
            'stock': 75,
            'category': 'Medicine',  # Change this to the appropriate category name
        },
        {
            'name': 'TAB - SECNIL FORTE',
            'description': 'Description for TAB - SECNIL FORTE',
            'price': 12.99,
            'stock': 60,
            'category': 'Medicine',  # Change this to the appropriate category name
        },
    ]

    for item in product_list:
        category_name = item.pop('category')
        category, _ = Category.objects.get_or_create(name=category_name)
        product, _ = Product.objects.update_or_create(category=category, **item)
        print(f"Added/Updated product: {product.name}")

if __name__ == "__main__":
    add_products()
