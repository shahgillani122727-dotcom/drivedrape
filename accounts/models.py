from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomerManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class Customer(AbstractBaseUser, PermissionsMixin):
    email       = models.EmailField(unique=True)
    first_name  = models.CharField(max_length=100, blank=True)
    last_name   = models.CharField(max_length=100, blank=True)
    phone       = models.CharField(max_length=20, blank=True)
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomerManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.email


class Address(models.Model):
    PROVINCE_CHOICES = [
        ('punjab',   'Punjab'),
        ('sindh',    'Sindh'),
        ('kpk',      'Khyber Pakhtunkhwa'),
        ('baloch',   'Balochistan'),
        ('gilgit',   'Gilgit-Baltistan'),
        ('azad_k',   'Azad Kashmir'),
        ('islamabad','Islamabad (ICT)'),
    ]
    customer   = models.ForeignKey(Customer, on_delete=models.CASCADE,
                                   related_name='addresses')
    full_name  = models.CharField(max_length=200)
    phone      = models.CharField(max_length=20)
    address    = models.TextField()
    city       = models.CharField(max_length=100)
    province   = models.CharField(max_length=20, choices=PROVINCE_CHOICES)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name}, {self.city}"
