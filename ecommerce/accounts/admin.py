# admin.py
from django.contrib import admin
from .models import Product, Category, Order, User

# Product Admin
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'image_tag', 'created_at', 'updated_at')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    fields = ('name', 'description', 'price', 'category', 'image')
    
    # Display image in admin list view
    def image_tag(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="100" />'
        return 'No image'
    image_tag.allow_tags = True
    image_tag.short_description = 'Image'
# Category Admin
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Order Admin
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_cost', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'user__email')
    ordering = ('-created_at',)
    fields = ('user', 'shipping_address', 'total_cost', 'status', 'created_at', 'cart')

# User Admin (Extend the default admin for the custom User model)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_customer', 'is_admin', 'is_staff')
    list_filter = ('is_customer', 'is_admin')
    search_fields = ('username', 'email')

# Register models
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(User, UserAdmin)
