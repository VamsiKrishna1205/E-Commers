from django.urls import path
from .views import RegisterView,ProductListView, ProductDetailView, ProductCreateView, ProductUpdateView, ProductDeleteView, CategoryListCreateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    #products
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/<int:id>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('products/<int:id>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:id>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    
    #category
    path('categories/', CategoryListCreateAPIView.as_view(), name='category-list-create'),
    
    # cart
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    
    # Customer: View orders
    path('orders/', views.view_orders, name='view_orders'),

    # Admin: Manage orders (view and update status)
    path('orders/manage/<int:order_id>/', views.manage_order, name='manage_order'),
]
