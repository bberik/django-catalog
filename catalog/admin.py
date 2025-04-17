from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django import forms
from .models import Product, Category, Tag

class TagAdmin(admin.ModelAdmin):
    search_fields = ['name']
    ordering = ['name']

class ImageURLForm(forms.ModelForm):
    image_urls = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter one image URL per line\nExample:\nhttps://example.com/image1.png\nhttps://example.com/image2.png'}),
        help_text='Enter one image URL per line. All URLs must be valid and point to image files.',
        required=False
    )

    class Meta:
        model = Product
        exclude = ('images',)

    def clean_image_urls(self):
        urls = self.cleaned_data.get('image_urls', '').strip().split('\n')
        urls = [url.strip() for url in urls if url.strip()]
        
        url_validator = URLValidator()
        for url in urls:
            try:
                url_validator(url)
            except ValidationError:
                raise ValidationError(f'Invalid URL: {url}')
        
        return urls

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.images = self.cleaned_data.get('image_urls', [])
        if commit:
            instance.save()
        return instance

class ProductAdmin(admin.ModelAdmin):
    form = ImageURLForm
    list_display = ('title', 'category', 'price', 'stock', 'created_at')
    list_filter = ('category', 'tags', 'brand')
    search_fields = ('title', 'description', 'brand')
    exclude = ('embedding', 'created_at', 'updated_at')
    autocomplete_fields = ['tags']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'tags'),
            'description': 'Enter the basic product information. Title and description should be clear and informative.'
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'discount_percentage', 'stock', 'minimum_order_quantity'),
            'description': 'Set the product price, any applicable discounts, and stock information.'
        }),
        ('Product Details', {
            'fields': ('brand', 'sku', 'weight', 'width', 'height', 'depth'),
            'description': 'Enter the physical specifications and identification details of the product.'
        }),
        ('Shipping & Policies', {
            'fields': ('warranty_information', 'shipping_information', 'availability_status', 'return_policy'),
            'description': 'Specify warranty, shipping, and return policy information.'
        }),
        ('Images', {
            'fields': ('thumbnail', 'image_urls'),
            'description': 'Add product images. Thumbnail is the main product image. Enter additional image URLs below, one per line.',
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.images:
            form.base_fields['image_urls'].initial = '\n'.join(obj.images)
        return form

admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(Tag, TagAdmin)
