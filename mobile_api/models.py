from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to="category_images/")
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class ClientUser(models.Model):
    GenderTypes = (
        ("M", "Male"),
        ("F", "Female"),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_user')
    phone_number = models.CharField(max_length=20)
    gender = models.CharField(max_length=1, choices=GenderTypes)
    birthday = models.DateField()
    image = models.ImageField(upload_to="client_images/", null=True, blank=True)

    class Meta:
        verbose_name = "Client User"
        verbose_name_plural = "Client Users"

    def __str__(self):
        return self.user.username


class Shop(models.Model):
    name = models.CharField(max_length=60)
    address = models.TextField()
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="shop_user")
    
    class Meta:
        verbose_name = "Shop"
        verbose_name_plural = "Shops"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=60)
    price = models.FloatField()
    description = models.TextField()
    expire_time = models.DateTimeField()
    image = models.ImageField(upload_to='product_images/')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='product_shop')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product_category')
    
    
    class Meta:
        ordering = ['expire_time']
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name


class ClientWishList(models.Model):
    client = models.ForeignKey(ClientUser, on_delete=models.CASCADE, related_name='wishlist_client')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_product')

    class Meta:
        unique_together = ['client', 'product']
        verbose_name = "Client Wish List"
        verbose_name_plural = "Client Wish Lists"

    def __str__(self):
        return str(self.id)


class Cart(models.Model):
    OrderStatues = (
        ('1', "Ordering"),
        ('2', "Processing"),
        ('3', 'Done'),
    )
    cart_ID = models.CharField(unique=True, max_length=20)
    start_cart = models.DateTimeField(auto_now_add=True)
    order_data = models.DateTimeField(null=True, blank=True)
    client = models.ForeignKey(ClientUser, on_delete=models.CASCADE, related_name='cart_client')
    status = models.CharField(max_length=1, choices=OrderStatues)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return self.cart_ID


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_products')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.IntegerField(default=1)
    order_data = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"

    def __str__(self):
        return str(self.id)


@receiver(post_save, sender=User)
def create_auth_token(sender, instance, created=False, *args, **kwargs):
    if created:
        Token.objects.create(user=instance)

