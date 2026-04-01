from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, OrderStatusLog
from .whatsapp import send_whatsapp_notification


class OrderItemInline(admin.TabularInline):
    model  = OrderItem
    extra  = 0
    fields = ['product_name', 'product_price', 'quantity']
    readonly_fields = ['product_name', 'product_price', 'quantity']


class OrderStatusLogInline(admin.TabularInline):
    model  = OrderStatusLog
    extra  = 0
    readonly_fields = ['old_status', 'new_status', 'note', 'changed_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display    = ['order_id', 'full_name', 'phone', 'city',
                       'payment_method', 'colored_status', 'total',
                       'whatsapp_sent', 'created_at']
    list_filter     = ['status', 'payment_method', 'city', 'created_at']
    search_fields   = ['order_id', 'full_name', 'phone', 'email']
    readonly_fields = ['order_id', 'subtotal', 'total', 'created_at', 'updated_at']
    inlines         = [OrderItemInline, OrderStatusLogInline]
    actions         = ['mark_confirmed', 'mark_packed', 'mark_shipped',
                       'mark_delivered', 'resend_whatsapp']

    fieldsets = (
        ('Order Info', {
            'fields': ('order_id', 'status', 'created_at', 'updated_at')
        }),
        ('Customer', {
            'fields': ('full_name', 'phone', 'email', 'address', 'city', 'province', 'notes')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_status', 'transaction_id')
        }),
        ('Financials', {
            'fields': ('subtotal', 'shipping_cost', 'discount', 'total')
        }),
        ('Tracking', {
            'fields': ('tracking_code', 'whatsapp_sent')
        }),
    )

    def colored_status(self, obj):
        colors = {
            'pending':   '#f59e0b',
            'confirmed': '#3b82f6',
            'packed':    '#8b5cf6',
            'shipped':   '#06b6d4',
            'delivered': '#22c55e',
            'cancelled': '#ef4444',
            'returned':  '#6b7280',
        }
        color = colors.get(obj.status, '#888')
        return format_html(
            '<span style="color:{};font-weight:700">{}</span>',
            color, obj.get_status_display()
        )
    colored_status.short_description = 'Status'

    def _change_status(self, request, queryset, new_status):
        for order in queryset:
            log_entry = OrderStatusLog(
                order=order, old_status=order.status, new_status=new_status
            )
            order.status = new_status
            order.save()
            log_entry.save()
        self.message_user(request, f"{queryset.count()} order(s) updated.")

    def mark_confirmed(self, request, queryset):
        self._change_status(request, queryset, 'confirmed')
    mark_confirmed.short_description = "✅ Mark as Confirmed"

    def mark_packed(self, request, queryset):
        self._change_status(request, queryset, 'packed')
    mark_packed.short_description = "📦 Mark as Packed"

    def mark_shipped(self, request, queryset):
        self._change_status(request, queryset, 'shipped')
    mark_shipped.short_description = "🚚 Mark as Shipped"

    def mark_delivered(self, request, queryset):
        self._change_status(request, queryset, 'delivered')
    mark_delivered.short_description = "🎉 Mark as Delivered"

    def resend_whatsapp(self, request, queryset):
        for order in queryset:
            send_whatsapp_notification(order)
        self.message_user(request, "WhatsApp notifications sent.")
    resend_whatsapp.short_description = "📱 Resend WhatsApp Notification"
