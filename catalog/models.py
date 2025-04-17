from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from sentence_transformers import SentenceTransformer
from pgvector.django import VectorField, IvfflatIndex

# Initialize the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(db_index=True)
    embedding = VectorField(
        dimensions=384,  # Size of the embedding vector from all-MiniLM-L6-v2
        null=True,
        blank=True
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.FloatField(default=0)
    rating = models.FloatField(default=0)
    stock = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True)
    brand = models.CharField(max_length=100)
    sku = models.CharField(max_length=100)
    weight = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    depth = models.FloatField()
    warranty_information = models.CharField(max_length=255)
    shipping_information = models.CharField(max_length=255)
    availability_status = models.CharField(max_length=50)
    return_policy = models.CharField(max_length=255)
    minimum_order_quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    thumbnail = models.URLField()
    images = models.JSONField()  # Stores list of image URLs

    def __str__(self):
        return self.title

    def generate_embedding(self):
        """Generate embedding from title and description"""
        text = f"{self.title} {self.description}"
        return model.encode(text).tolist()
    
    

    class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['description']),
            IvfflatIndex(
                name='product_embedding_idx',
                fields=['embedding'],
                opclasses=['vector_l2_ops']
            ),
        ]

@receiver(pre_save, sender=Product)
def generate_product_embedding(sender, instance, **kwargs):
    """Generate embedding before saving the product"""
    if not instance.embedding:
        instance.embedding = instance.generate_embedding()

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    comment = models.TextField()
    date = models.DateTimeField()
    reviewer_name = models.CharField(max_length=100)
    reviewer_email = models.EmailField()

    def __str__(self):
        return f"{self.reviewer_name} - {self.product.title}"