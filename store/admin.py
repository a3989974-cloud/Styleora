from django.contrib import admin, messages
from django.utils.html import format_html, mark_safe
from django.urls import reverse
from .models import Category, Product, ProductReview, Order, OrderItem, Wishlist, Coupon


@admin.action(description='Mark selected as featured')
def make_featured(modeladmin, request, queryset):
    queryset.update(is_featured=True)
    messages.success(request, f'{queryset.count()} products marked as featured.')


@admin.action(description='Remove featured from selected')
def unmake_featured(modeladmin, request, queryset):
    queryset.update(is_featured=False)
    messages.success(request, f'Featured removed from {queryset.count()} products.')


@admin.action(description='Mark selected as trending')
def make_trending(modeladmin, request, queryset):
    queryset.update(is_trending=True)
    messages.success(request, f'{queryset.count()} products marked as trending.')


@admin.action(description='Mark selected as available')
def make_available(modeladmin, request, queryset):
    queryset.update(is_available=True)
    messages.success(request, f'{queryset.count()} products marked as available.')


@admin.action(description='Mark selected as unavailable')
def make_unavailable(modeladmin, request, queryset):
    queryset.update(is_available=False)
    messages.success(request, f'{queryset.count()} products marked as unavailable.')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_per_page = 20
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['image_tag', 'name', 'category', 'display_price', 'stock', 'status_badges', 'is_featured', 'is_trending']
    list_filter = ['category', 'is_available', 'is_featured', 'is_trending', 'created_at']
    search_fields = ['name', 'brand', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['stock', 'is_featured', 'is_trending']
    list_per_page = 25
    date_hierarchy = 'created_at'
    show_full_result_count = True
    autocomplete_fields = ['category']
    save_on_top = True
    actions = [make_featured, unmake_featured, make_trending, make_available, make_unavailable]
    
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price')
        }),
        ('Inventory', {
            'fields': ('stock', 'is_available')
        }),
        ('Promotion', {
            'fields': ('is_featured', 'is_trending')
        }),
        ('Media & Brand', {
            'fields': ('image', 'images', 'brand')
        }),
    )
    
    def display_price(self, obj):
        if obj.discount_price:
            return format_html('${} <span style="text-decoration:line-through;color:#999;">${}</span>', obj.discount_price, obj.price)
        return f'${obj.price}'
    display_price.short_description = 'Price'
    
    def status_badges(self, obj):
        badges = ''
        if not obj.is_available:
            badges += '<span style="background:#dc2626;color:white;padding:3px 8px;border-radius:4px;font-size:11px;font-weight:600;">OUT OF STOCK</span> '
        if obj.is_trending:
            badges += '<span style="background:#2563eb;color:white;padding:3px 8px;border-radius:4px;font-size:11px;font-weight:600;">TRENDING</span> '
        if obj.is_featured:
            badges += '<span style="background:#c9a962;color:#0f0f0f;padding:3px 8px;border-radius:4px;font-size:11px;font-weight:600;">FEATURED</span> '
        return mark_safe(badges.strip()) or '-'
    status_badges.short_description = 'Status'
    
    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:50px;height:50px;object-fit:cover;border-radius:6px;" />', obj.image.url)
        return '-'
    image_tag.short_description = 'Image'

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating_stars', 'comment_preview', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['product__name', 'user__username', 'comment']
    list_per_page = 20
    autocomplete_fields = ['product', 'user']
    radio_fields = {'rating': admin.HORIZONTAL}
    
    def rating_stars(self, obj):
        stars = ''
        for i in range(5):
            if i < obj.rating:
                stars += '<span style="color:#c9a962;">★</span>'
            else:
                stars += '<span style="color:#444;">★</span>'
        return format_html(stars)
    rating_stars.short_description = 'Rating'
    
    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = 'Comment'


@admin.action(description='Mark selected orders as confirmed')
def confirm_orders(modeladmin, request, queryset):
    queryset.update(status='confirmed')
    messages.success(request, f'{queryset.count()} orders confirmed.')


@admin.action(description='Mark selected orders as delivered')
def deliver_orders(modeladmin, request, queryset):
    queryset.update(status='delivered')
    messages.success(request, f'{queryset.count()} orders marked as delivered.')


@admin.action(description='Mark selected orders as cancelled')
def cancel_orders(modeladmin, request, queryset):
    queryset.update(status='cancelled')
    messages.success(request, f'{queryset.count()} orders cancelled.')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'status_badge', 'payment_badge', 'total_amount', 'order_date']
    list_filter = ['status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email', 'phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    show_full_result_count = True
    save_on_top = True
    actions = [confirm_orders, deliver_orders, cancel_orders]
    autocomplete_fields = ['user']
    radio_fields = {'status': admin.HORIZONTAL, 'payment_status': admin.HORIZONTAL}
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_status')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'total_amount')
        }),
        ('Shipping', {
            'fields': ('shipping_address', 'phone', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def customer(self, obj):
        return obj.user.username if obj.user else 'Guest'
    customer.short_description = 'Customer'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#f59e0b',
            'confirmed': '#3b82f6',
            'shipped': '#8b5cf6',
            'delivered': '#10b981',
            'cancelled': '#dc2626',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html('<span style="background:{};color:white;padding:4px 12px;border-radius:20px;font-size:11px;font-weight:600;">{}</span>', color, obj.get_status_display())
    status_badge.short_description = 'Status'
    
    def payment_badge(self, obj):
        colors = {
            'pending': '#f59e0b',
            'paid': '#10b981',
            'failed': '#dc2626',
        }
        color = colors.get(obj.payment_status, '#6b7280')
        return format_html('<span style="background:{};color:white;padding:4px 12px;border-radius:20px;font-size:11px;font-weight:600;">{}</span>', color, obj.get_payment_status_display())
    payment_badge.short_description = 'Payment'
    
    def order_date(self, obj):
        return obj.created_at.strftime('%b %d, %Y %I:%M %p')
    order_date.short_description = 'Date'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'product', 'quantity', 'price', 'total']
    search_fields = ['order__order_number', 'product__name']
    list_per_page = 25
    autocomplete_fields = ['order', 'product']
    readonly_fields = ['price']
    
    def order_number(self, obj):
        return obj.order.order_number
    order_number.short_description = 'Order #'
    
    def total(self, obj):
        return f'${obj.price * obj.quantity}'
    total.short_description = 'Total'

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    search_fields = ['user__username', 'product__name']
    list_per_page = 20
    autocomplete_fields = ['user', 'product']
    show_full_result_count = True

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percent', 'min_order_amount', 'valid_period', 'is_active_badge', 'is_active']
    list_filter = ['is_active', 'valid_from', 'valid_until']
    search_fields = ['code']
    list_editable = ['is_active']
    list_per_page = 20
    show_full_result_count = True
    fieldsets = (
        ('Coupon Details', {
            'fields': ('code', 'discount_percent', 'min_order_amount')
        }),
        ('Validity', {
            'fields': ('is_active', 'valid_from', 'valid_until')
        }),
    )
    
    def valid_period(self, obj):
        return f'{obj.valid_from.strftime("%b %d")} - {obj.valid_until.strftime("%b %d, %Y")}'
    valid_period.short_description = 'Valid Period'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="background:#10b981;color:white;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;">ACTIVE</span>')
        return format_html('<span style="background:#6b7280;color:white;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;">INACTIVE</span>')
    is_active_badge.short_description = 'Status'