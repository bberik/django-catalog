# Generated by Django 5.2 on 2025-04-16 17:36

import django.db.models.deletion
import pgvector.django.indexes
import pgvector.django.vector
from pgvector.django import VectorExtension
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        VectorExtension(),
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(db_index=True, max_length=255)),
                ("description", models.TextField(db_index=True)),
                (
                    "embedding",
                    pgvector.django.vector.VectorField(
                        blank=True, dimensions=384, null=True
                    ),
                ),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("discount_percentage", models.FloatField()),
                ("rating", models.FloatField()),
                ("stock", models.IntegerField()),
                ("brand", models.CharField(max_length=100)),
                ("sku", models.CharField(max_length=100)),
                ("weight", models.FloatField()),
                ("width", models.FloatField()),
                ("height", models.FloatField()),
                ("depth", models.FloatField()),
                ("warranty_information", models.CharField(max_length=255)),
                ("shipping_information", models.CharField(max_length=255)),
                ("availability_status", models.CharField(max_length=50)),
                ("return_policy", models.CharField(max_length=255)),
                ("minimum_order_quantity", models.PositiveIntegerField()),
                ("created_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
                ("barcode", models.CharField(max_length=100)),
                ("qr_code", models.URLField()),
                ("thumbnail", models.URLField()),
                ("images", models.JSONField()),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="catalog.category",
                    ),
                ),
                ("tags", models.ManyToManyField(to="catalog.tag")),
            ],
        ),
        migrations.CreateModel(
            name="Review",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("rating", models.IntegerField()),
                ("comment", models.TextField()),
                ("date", models.DateTimeField()),
                ("reviewer_name", models.CharField(max_length=100)),
                ("reviewer_email", models.EmailField(max_length=254)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="catalog.product",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(fields=["title"], name="catalog_pro_title_c91890_idx"),
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(
                fields=["description"], name="catalog_pro_descrip_7b75a8_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="product",
            index=pgvector.django.indexes.IvfflatIndex(
                fields=["embedding"],
                name="product_embedding_idx",
                opclasses=["vector_l2_ops"],
            ),
        ),
    ]
