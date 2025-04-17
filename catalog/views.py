from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from .models import Product, Category, Tag
from sentence_transformers import SentenceTransformer
from pgvector.django import L2Distance

# Initialize the sentence transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")


def product_list(request):
    # Get pagination parameters
    page = request.GET.get("page", 1)
    per_page = request.GET.get("per_page", 24)

    # Get filter parameters
    search_query = request.GET.get("q")
    category_id = request.GET.get("category")
    tag_ids = request.GET.getlist("tags")

    # Start with base queryset
    products = Product.objects.select_related("category").prefetch_related("tags")

    # Apply filters in optimal order
    if category_id:
        # Category filtering is fast due to indexed foreign key
        products = products.filter(category_id=category_id)

    if tag_ids:
        # Add index hint for tag filtering
        products = products.filter(tags__id__in=tag_ids).distinct()

    if search_query:
        # Generate embedding for the search query
        query_embedding = model.encode(search_query).tolist()
        products = products.annotate(distance=L2Distance("embedding", query_embedding)).filter(distance__lt=1.3).order_by("distance")
    
    # Cache expensive queries
    categories = cache.get("all_categories")
    if categories is None:
        categories = Category.objects.all()
        cache.set("all_categories", categories, 3600)

    tags = cache.get("all_tags")
    if tags is None:
        tags = Tag.objects.all()
        cache.set("all_tags", tags, 3600)

    # Paginate products
    paginator = Paginator(products, per_page)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        "products": products,
        "categories": categories,
        "tags": tags,
        "selected_category": category_id,
        "selected_tags": list(map(int, tag_ids)),
        "search_query": search_query,
        "per_page": per_page,
    }

    return render(request, "catalog/product_list.html", context)