from django.urls import path
from . import views


app_name = "mobile_api"


urlpatterns = [
    path('login/', views.LoginView.as_view(), name="login"),
    path('register/', views.RegisterView.as_view(), name="register"),
    path('profile/', views.ClientUserView.as_view(), name="profile"),
    path('home_screen/', views.HomeScreenView.as_view(), name="home_screen"),
    path('products/', views.ProductView.as_view(), name="products"),
    path('wishlist/', views.WishListView.as_view(), name="wishlist"),
    path('cart/', views.CartView.as_view(), name="cart"),
    path('modify_cart/', views.CartModificationView.as_view(), name="modify_cart"),
    path('make_order/', views.OrderView.as_view(), name="make_order"),
]

