from django.db import models
from django.utils import timezone
from accounts.models import Customer
from products.models import Product
import uuid


PAKISTAN_CITIES = [
    ('karachi','Karachi'), ('lahore','Lahore'), ('islamabad','Islamabad'),
    ('rawalpindi','Rawalpindi'), ('faisalabad','Faisalabad'), ('multan','Multan'),
    ('peshawar','Peshawar'), ('quetta','Quetta'), ('sialkot','Sialkot'),
    ('gujranwala','Gujranwala'), ('hyderabad','Hyderabad'), ('bahawalpur','Bahawalpur'),
    ('sargodha','Sargodha'), ('sukkur','Sukkur'), ('larkana','Larkana'),
    ('sahiwal','Sahiwal'), ('gujrat','Gujrat'), ('sheikhupura','Sheikhupura'),
    ('jhang','Jhang'), ('rahim_yar_khan','Rahim Yar Khan'),
    ('abbottabad','Abbottabad'), ('mardan','Mardan'), ('mingora','Mingora'),
    ('dera_ghazi','Dera Ghazi Khan'), ('nawabshah','Nawabshah'),
    ('mirpur','Mirpur (AJK)'), ('muzaffarabad','Muzaffarabad'),
    ('other','Other'),
]


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',    '⏳ Pending'),
        ('confirmed',  '✅ Confirmed'),
        ('packed',     '📦 Packed'),
        ('shipped',    '🚚 Shipped'),
        ('delivered',  '🎉 Delivered'),
        ('cancelled',  '❌ Cancelled'),
        ('returned',   '↩️ Returned'),
    ]

    PAYMENT_CHOICES = [
        ('cod',       'Cash on Delivery'),
        ('jazzcash',  'JazzCash'),
        ('easypaisa', 'EasyPaisa'),
    ]

    PAYMENT_STATUS = [
        ('pending',  'Pending'),
        ('paid',     'Paid'),
        ('failed',   'Failed'),
        ('refunded', 'Refunded'),
    ]

    # Unique order ID shown to customer
    order_id       = models.CharField(max_length=20, unique=True, blank=True)

    # Customer — optional (guest or logged in)
    customer       = models.ForeignKey(Customer, on_delete=models.SET_NULL,
                                       null=True, blank=True, related_name='orders')

    # Guest / Shipping Info
    full_name      = models.CharField(max_length=200)
    phone          = models.CharField(max_length=20)
    email          = models.EmailField(blank=True)
    address        = models.TextField()
    city           = models.CharField(max_length=100, choices=PAKISTAN_CITIES)
    province       = models.CharField(max_length=100, blank=True)
    notes          = models.TextField(blank=True)

    # Financials
    subtotal       = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost  = models.DecimalField(max_digits=10, decimal_places=2, default=200)
    discount       = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total          = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Payment
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES,
                                      default='cod')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS,
                                      default='pending')
    transaction_id = models.CharField(max_length=200, blank=True)

    # Status & Tracking
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                      default='pending')
    tracking_code  = models.CharField(max_length=100, blank=True)

    # WhatsApp notification sent?
    whatsapp_sent  = models.BooleanField(default=False)

    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = self._generate_order_id()
        self.total = self.subtotal + self.shipping_cost - self.discount
        super().save(*args, **kwargs)

    def _generate_order_id(self):
        import random, string
        prefix = 'DD'
        suffix = ''.join(random.choices(string.digits, k=6))
        return f"{prefix}{suffix}"

    @property
    def status_steps(self):
        """Returns ordered steps for tracking timeline"""
        steps = ['pending', 'confirmed', 'packed', 'shipped', 'delivered']
        current_idx = steps.index(self.status) if self.status in steps else 0
        return [
            {'key': s, 'label': dict(self.STATUS_CHOICES)[s], 'done': i <= current_idx}
            for i, s in enumerate(steps)
        ]

    def __str__(self):
        return f"Order #{self.order_id} — {self.full_name}"


class OrderItem(models.Model):
    order          = models.ForeignKey(Order, on_delete=models.CASCADE,
                                       related_name='items')
    product        = models.ForeignKey(Product, on_delete=models.SET_NULL,
                                       null=True)
    product_name   = models.CharField(max_length=255)   # snapshot
    product_price  = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot
    quantity       = models.PositiveIntegerField(default=1)

    @property
    def line_total(self):
        return self.product_price * self.quantity

    def __str__(self):
        return f"{self.quantity}× {self.product_name}"


class OrderStatusLog(models.Model):
    """Tracks every status change for admin history"""
    order      = models.ForeignKey(Order, on_delete=models.CASCADE,
                                   related_name='status_logs')
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    note       = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"#{self.order.order_id}: {self.old_status} → {self.new_status}"
