from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category, ProductImage, Review


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ['image', 'alt', 'is_main', 'order']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['name', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display    = ['name', 'category', 'price', 'sale_price',
                       'stock', 'is_active', 'is_featured', 'is_bestseller',
                       'product_image']
    list_editable   = ['price', 'sale_price', 'stock', 'is_active',
                       'is_featured', 'is_bestseller']
    list_filter     = ['category', 'is_active', 'is_featured', 'is_bestseller']
    search_fields   = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines         = [ProductImageInline]

    def product_image(self, obj):
        img = obj.main_image
        if img:
            return format_html('<img src="{}" width="50" height="50" '
                               'style="object-fit:cover;border-radius:4px"/>', img.image.url)
        return '—'
    product_image.short_description = 'Image'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display  = ['product', 'reviewer_name', 'rating', 'is_approved', 'created_at']
    list_editable = ['is_approved']
    list_filter   = ['is_approved', 'rating']
    search_fields = ['product__name', 'guest_name', 'comment']
