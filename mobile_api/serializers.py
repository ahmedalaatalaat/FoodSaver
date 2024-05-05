from django.contrib.humanize.templatetags.humanize import naturaltime
from rest_framework import serializers
from .models import *


class RegistrationSerializer(serializers.Serializer):
    gender_types = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    
    email = serializers.EmailField()
    username = serializers.CharField(max_length=320)
    name = serializers.CharField(max_length=160)
    phone_number = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=20, min_length=8)
    gender = serializers.ChoiceField(gender_types)
    birthday = serializers.DateField()


class ProfileUpdateSerializer(serializers.Serializer):
    gender_types = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    
    email = serializers.EmailField()
    name = serializers.CharField(max_length=160)
    phone_number = serializers.CharField(max_length=20)
    gender = serializers.ChoiceField(gender_types)
    birthday = serializers.DateField()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=320)
    password = serializers.CharField(max_length=20, min_length=8)


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    name = serializers.CharField(source='user.first_name')
    email = serializers.EmailField(source='user.email')
    
    class Meta:
        model = ClientUser
        fields = ['id', 'name', 'username', 'email', 'phone_number', 'gender', 'birthday', 'image']


class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'image']


class ProductSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name')
    shop_address = serializers.CharField(source='shop.address')
    expire_time_humified = serializers.SerializerMethodField()
    
    def get_expire_time_humified(self, obj):
        return naturaltime(obj.expire_time)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'expire_time', 'image', 'shop_name', 'shop_address', 'expire_time_humified']


class ClientWishListSerializer(serializers.ModelSerializer):
    product_id = serializers.CharField(source='product.id')
    product_name = serializers.CharField(source='product.name')
    product_price = serializers.FloatField(source='product.price')
    product_description = serializers.CharField(source='product.description')
    product_expire_time = serializers.DateTimeField(source='product.expire_time')
    product_image = serializers.SerializerMethodField(source='product.id')
    product_shop_name = serializers.CharField(source='product.shop.name')
    product_shop_address = serializers.CharField(source='product.shop.name')
    product_expire_time_humified = serializers.SerializerMethodField()
    
    
    def get_product_expire_time_humified(self, obj):
        return naturaltime(obj.product.expire_time)
    
    def get_product_image(self, obj):
        return obj.product.image.url
    
    class Meta:
        model = ClientWishList
        fields = ['product_id', 'product_name', 'product_price', 'product_description', 'product_expire_time', 'product_image', 'product_shop_name', 'product_shop_address', 'product_expire_time_humified']


class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.CharField(source='product.id')
    product_name = serializers.CharField(source='product.name')
    product_price = serializers.FloatField(source='product.price')
    product_description = serializers.CharField(source='product.description')
    product_expire_time = serializers.DateTimeField(source='product.expire_time')
    product_image = serializers.SerializerMethodField(source='product.id')
    product_shop_name = serializers.CharField(source='product.shop.name')
    product_shop_address = serializers.CharField(source='product.shop.name')
    product_expire_time_humified = serializers.SerializerMethodField()
    
    
    def get_product_expire_time_humified(self, obj):
        return naturaltime(obj.product.expire_time)
    
    def get_product_image(self, obj):
        return obj.product.image.url
    
    class Meta:
        model = CartItem
        fields = ['product_id', 'product_name', 'product_price', 'product_description', 'product_expire_time', 'product_image', 'product_shop_name', 'product_shop_address', 'product_expire_time_humified', 'quantity', 'order_data']