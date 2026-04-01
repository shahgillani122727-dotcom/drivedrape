from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import Customer


class Category(models.Model):
    name        = models.CharField(max_length=100)
    slug        = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image       = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active   = models.BooleanField(default=True)
    order       = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                    null=True, related_name='products')
    name        = models.CharField(max_length=255)
    slug        = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price  = models.DecimalField(max_digits=10, decimal_places=2,
                                       blank=True, null=True)
    stock       = models.PositiveIntegerField(default=0)
    is_active   = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def current_price(self):
        return self.sale_price if self.sale_price else self.price

    @property
    def is_on_sale(self):
        return bool(self.sale_price and self.sale_price < self.price)

    @property
    def discount_percent(self):
        if self.is_on_sale:
            return int(((self.price - self.sale_price) / self.price) * 100)
        return 0

    @property
    def avg_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    @property
    def review_count(self):
        return self.reviews.filter(is_approved=True).count()

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def main_image(self):
        img = self.images.filter(is_main=True).first()
        return img if img else self.images.first()

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='images')
    image   = models.ImageField(upload_to='products/')
    alt     = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)
    order   = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name} — image {self.order}"


class Review(models.Model):
    product     = models.ForeignKey(Product, on_delete=models.CASCADE,
                                    related_name='reviews')
    customer    = models.ForeignKey(Customer, on_delete=models.SET_NULL,
                                    null=True, blank=True)
    guest_name  = models.CharField(max_length=100, blank=True)
    guest_email = models.EmailField(blank=True)
    rating      = models.PositiveSmallIntegerField(
                    validators=[MinValueValidator(1), MaxValueValidator(5)])
    title       = models.CharField(max_length=200, blank=True)
    comment     = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def reviewer_name(self):
        if self.customer:
            return self.customer.get_full_name() or self.customer.email
        return self.guest_name or 'Anonymous'

    def __str__(self):
        return f"{self.product.name} — {self.rating}★ by {self.reviewer_name}"
