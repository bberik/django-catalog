import json
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from catalog.models import Category, Tag, Product, Review

class Command(BaseCommand):
    help = 'Import product data from JSON file into the database'

    def handle(self, *args, **options):
        # Get the path to the JSON file
        json_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'dummy_data.json')
        
        # Load the JSON data
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        
        # Process each product
        for product_data in data.get('products', []):
            # Get or create category
            category_name = product_data.get('category', 'Uncategorized')
            category, _ = Category.objects.get_or_create(name=category_name)
            
            # Create product
            product = Product(
                title=product_data.get('title', ''),
                description=product_data.get('description', ''),
                category=category,
                price=product_data.get('price', 0.0),
                discount_percentage=product_data.get('discountPercentage', 0.0),
                rating=product_data.get('rating', 0.0),
                stock=product_data.get('stock', 0),
                brand=product_data.get('brand', ''),
                sku=product_data.get('sku', ''),
                weight=product_data.get('weight', 0.0),
                width=product_data.get('dimensions', {}).get('width', 0.0),
                height=product_data.get('dimensions', {}).get('height', 0.0),
                depth=product_data.get('dimensions', {}).get('depth', 0.0),
                warranty_information=product_data.get('warrantyInformation', ''),
                shipping_information=product_data.get('shippingInformation', ''),
                availability_status=product_data.get('availabilityStatus', ''),
                return_policy=product_data.get('returnPolicy', ''),
                minimum_order_quantity=product_data.get('minimumOrderQuantity', 1),
                thumbnail=product_data.get('thumbnail', ''),
                images=product_data.get('images', [])
            )
            product.save()
            
            # Add tags
            for tag_name in product_data.get('tags', []):
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                product.tags.add(tag)
            
            # Add reviews
            for review_data in product_data.get('reviews', []):
                Review.objects.create(
                    product=product,
                    rating=review_data.get('rating', 0),
                    comment=review_data.get('comment', ''),
                    date=parse_datetime(review_data.get('date')) or parse_datetime('2024-01-01T00:00:00Z'),
                    reviewer_name=review_data.get('reviewerName', 'Anonymous'),
                    reviewer_email=review_data.get('reviewerEmail', 'anonymous@example.com')
                )
            
            self.stdout.write(self.style.SUCCESS(f'Successfully imported product: {product.title}')) 