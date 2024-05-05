from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.contrib.auth.models import User
from main.utils import get_object_or_none
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q
from .serializers import *
from .models import *
from . import utils


class LoginView(APIView):
    
    def get(self, request):
        serializer = LoginSerializer(data=request.query_params)
        if serializer.is_valid():
            user = get_object_or_none(User, username=request.query_params.get('username'))
            if user and user.check_password(request.query_params.get('password')):
                token = Token.objects.get(user=user)
                data = {
                    'token':str(token)
                }
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response({'code':'701', 'error':'wrong username or password'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@parser_classes((MultiPartParser, ))
class RegisterView(APIView):

    def post(self, request):
        user = get_object_or_none(User, username=request.data.get('username').lower() if request.data.get('username') else request.data.get('username'))
        client = get_object_or_none(ClientUser, user=user)
        if user or client:
            # Error 702: user already exists
            return Response({'code':'702', 'error':'user already exists'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            serializer = RegistrationSerializer(data=request.data)
            if serializer.is_valid():
                user = User.objects.create_user(
                    username=request.data.get('username').lower(),
                    email=request.data.get('email').lower(),
                    password=request.data.get('password'),
                )
                client = ClientUser.objects.create(
                    user=user,
                    phone_number=request.data.get('phone_number'),
                    gender=request.data.get('gender'),
                    birthday=request.data.get('birthday'),
                    image=request.FILES.get('image'),
                )
                token = Token.objects.get(user=user)
                data = {
                    "token": str(token),
                }
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@parser_classes((MultiPartParser, ))
class ClientUserView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        client = get_object_or_none(ClientUser.objects.select_related('user'), user=request.user)
        serializer = ProfileSerializer(client, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        serializer = ProfileUpdateSerializer(data=request.data)
        if serializer.is_valid():
            client = get_object_or_none(ClientUser.objects.select_related('user'), user=request.user)
            client.user.email = request.data.get('email')
            client.phone_number = request.data.get('phone_number')
            client.gender = request.data.get('gender')
            client.birthday = request.data.get('birthday')
            
            if request.FILES.get('image'):
                client.image=request.FILES.get('image')
            client.user.save()
            client.save()
            serializer = ProfileSerializer(client, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HomeScreenView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        after_24_hours = datetime.now() + timedelta(hours=24)
        categories = Category.objects.all()
        products = Product.objects.filter(expire_time__gte=datetime.now(), expire_time__lte=after_24_hours).select_related("shop")
        category_serializer = CategorySerializer(categories, many=True)
        product_serializer = ProductSerializer(products, many=True)
        data = {
            "categories": category_serializer.data,
            "running_out": product_serializer.data,
        }
        return Response(data, status=status.HTTP_200_OK)


class ProductView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        if request.query_params.get('category_id'):
            products = Product.objects.filter(expire_time__gte=datetime.now(), category_id=request.query_params.get('category_id')).select_related("shop")
        elif request.query_params.get('search'):
            products = Product.objects.filter(
                Q(expire_time__gte=datetime.now()) &
                (
                    Q(name__icontains=request.query_params.get('search')) |
                    Q(shop__name__icontains=request.query_params.get('search'))
                )).select_related("shop")
        elif request.query_params.get('id'):
            products = Product.objects.filter(id=request.query_params.get('id')).select_related("shop")
        else:
            products = []
        
        product_serializer = ProductSerializer(products, many=True)
        return Response(product_serializer.data, status=status.HTTP_200_OK)


class WishListView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        client_wishlist = ClientWishList.objects.filter(client__user=request.user).select_related("product", "product__shop")
        product_serializer = ClientWishListSerializer(client_wishlist, many=True)
        return Response(product_serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        product = get_object_or_404(Product, id=request.data.get('product_id'))
        try:
            ClientWishList.objects.create(
                client=request.user.client_user,
                product= product,
            )
        except Exception:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def delete(self, request):
        ClientWishList.objects.filter(product_id=request.data.get('product_id')).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        cart = self.get_cart(request)
        cart_serializer = CartItemSerializer(cart.cart_items.all(), many=True)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        product = get_object_or_404(Product, id=request.data.get('product_id'))
        cart = self.get_cart(request)
        order_item = CartItem.objects.filter(product=product, cart=cart).first()
        if not order_item:
            order_item = CartItem.objects.create(
                product=product,
                cart=self.get_cart(request),
            )
        else:
            order_item.quantity += 1
            order_item.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def delete(self, request):
        Cart.objects.filter(client__user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_cart(self, request):
        cart = Cart.objects.filter(client__user=request.user, status="1").prefetch_related('cart_items__product', "cart_items__product__shop").first()
        if not cart:
            cart = Cart.objects.create(
                cart_ID=utils.generate_unique_string(8),
                client=request.user.client_user,
                status='1', # meaning ordering
            )
        return cart


class CartModificationView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def put(self, request):
        product = get_object_or_404(Product, id=request.data.get('product_id'))
        cart = self.get_cart(request)
        order_item = CartItem.objects.filter(product=product, cart=cart).first()
        if not order_item:
            # Error 703: product is not in the cart
            return Response({'code':'703', 'error':'product is not in the cart'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            if request.data.get('operation') == "+":
                order_item.quantity += 1
                order_item.save()
            elif request.data.get('operation') == "-":
                if order_item.quantity == 1:
                    order_item.delete()
                else:
                    order_item.quantity -= 1
                    order_item.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def delete(self, request):
        product = get_object_or_404(Product, id=request.data.get('product_id'))
        cart = self.get_cart(request)
        order_item = CartItem.objects.filter(product=product, cart=cart).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_cart(self, request):
        cart = Cart.objects.filter(client__user=request.user, status="1").prefetch_related('cart_items__product', "cart_items__product__shop").first()
        if not cart:
            cart = Cart.objects.create(
                cart_ID=utils.generate_unique_string(8),
                client=request.user.client_user,
                status='1', # meaning ordering
            )
        return cart


class OrderView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        cart = self.get_cart(request)
        if not cart or len(cart.cart_items.all()) == 0:
            # Error 704: empty cart
            return Response({'code':'704', 'error':'empty cart'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            cart.status = "2"
            cart.order_data = datetime.now()
            cart.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_cart(self, request):
        cart = Cart.objects.filter(client__user=request.user, status="1").prefetch_related('cart_items__product', "cart_items__product__shop").first()
        return cart

