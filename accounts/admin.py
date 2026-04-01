from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Customer, Address


class AddressInline(admin.TabularInline):
    model  = Address
    extra  = 0
    fields = ['full_name', 'phone', 'city', 'address', 'is_default']


@admin.register(Customer)
class CustomerAdmin(UserAdmin):
    list_display   = ['email', 'first_name', 'last_name', 'phone', 'is_active', 'date_joined']
    search_fields  = ['email', 'first_name', 'last_name', 'phone']
    ordering       = ['-date_joined']
    inlines        = [AddressInline]

    fieldsets = (
        (None,           {'fields': ('email', 'password')}),
        ('Personal Info',{'fields': ('first_name', 'last_name', 'phone')}),
        ('Permissions',  {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates',        {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':  ('email', 'password1', 'password2'),
        }),
    )
    readonly_fields = ['date_joined', 'last_login']
