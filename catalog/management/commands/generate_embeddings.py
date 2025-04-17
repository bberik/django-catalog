from django.core.management.base import BaseCommand
from django.db import transaction
from catalog.models import Product
from tqdm import tqdm

class Command(BaseCommand):
    help = 'Generate embeddings for all products that do not have them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of products to process in each batch'
        )

    def handle(self, *args, **options):
        # Get all products without embeddings
        products = Product.objects.filter(embedding__isnull=True)
        total_products = products.count()
        
        if total_products == 0:
            self.stdout.write(self.style.SUCCESS('No products found without embeddings'))
            return

        self.stdout.write(f'Found {total_products} products without embeddings')
        
        # Process products in batches
        batch_size = options['batch_size']
        processed = 0
        
        with tqdm(total=total_products, desc="Generating embeddings") as pbar:
            for i in range(0, total_products, batch_size):
                batch = products[i:i + batch_size]
                
                with transaction.atomic():
                    for product in batch:
                        product.embedding = product.generate_embedding()
                        product.save(update_fields=['embedding'])
                        processed += 1
                        pbar.update(1)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Processed {processed}/{total_products} products'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated embeddings for {processed} products'
            )
        ) 