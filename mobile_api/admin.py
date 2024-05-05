from django.contrib.admin import TabularInline
from django.contrib import admin
from .models import *


class ClientWishList_admin(admin.ModelAdmin):
    list_select_related = (
        'client',
        'product',
        'client__user',
        'product__category',
        'product__shop',
    )
    list_display = ['client_name', 'client_username', 'product_name', 'product_shop', 'product_category']
    list_filter = ['product__category', 'product__shop']
    search_fields = ['product__shop__name', 'client__user__email']
    
    
    def client_name(self, obj):
        return obj.client.user.first_name
    
    def client_username(self, obj):
        return obj.client.user.username
    
    def product_shop(self, obj):
        return obj.product.shop.name
    
    def product_category(self, obj):
        return obj.product.category.name
    
    def product_name(self, obj):
        return obj.product.name


class ClientUser_admin(admin.ModelAdmin):
    list_select_related = (
        'user',
    )
    list_display = ['client_name', 'client_username', 'client_email', 'phone_number', 'gender', 'birthday']
    list_filter = ['birthday', 'gender']
    search_fields = ['user__first_name', 'user__email', 'user__username']
    
    
    def client_name(self, obj):
        return obj.user.first_name
    
    def client_username(self, obj):
        return obj.user.username
    
    def client_email(self, obj):
        return obj.user.email


class Category_admin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['id', 'name']


class Product_admin(admin.ModelAdmin):
    list_select_related = (
        'shop',
        'category',
    )
    list_display = ['name', 'price', 'expire_time', 'shop_name', 'category_name']
    list_filter = ['shop', 'category', 'expire_time']
    search_fields = ['name',]
    
    
    def shop_name(self, obj):
        return obj.shop.name
    
    def category_name(self, obj):
        return obj.category.name


class InlineCartItem(TabularInline):
    model = CartItem
    extra = 1
    fk_name = 'cart'


class Cart_admin(admin.ModelAdmin):
    inlines = [InlineCartItem]
    list_select_related = (
        'client',
    )
    list_display = ['cart_ID', 'client_email', 'client_name', 'client_phone', 'start_cart', 'status']
    list_filter = ['status', 'start_cart']
    search_fields = ['client__user__username', 'client__user__first_name', 'client__user__email', 'client__phone_number']
    
    def client_email(self, obj):
        return obj.client.user.email
    
    def client_name(self, obj):
        return obj.client.user.first_name
    
    def client_phone(self, obj):
        return obj.client.phone_number

class Shop_admin(admin.ModelAdmin):
    list_display = ['id', 'name', 'address']
    search_fields = ['id', 'name', 'address']


admin.site.register(ClientWishList, ClientWishList_admin)
admin.site.register(ClientUser, ClientUser_admin)
admin.site.register(Category, Category_admin)
admin.site.register(Product, Product_admin)
admin.site.register(Cart, Cart_admin)
admin.site.register(Shop, Shop_admin)
# admin.site.register(CartItem)


admin.site.site_header = 'Food Saver Cpanel' #Modify Site Header
admin.site.site_title = 'Food Saver' #Modify Site Title
admin.site.index_title = 'Food Saver Administration' #Modify Site Index Title

