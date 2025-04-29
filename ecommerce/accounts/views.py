from rest_framework import generics
from .serializers import RegisterSerializer,ProductSerializer, CategorySerializer, CartItemSerializer, OrderSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny,IsAuthenticated, IsAdminUser
from .models import Product, Category, Cart, CartItem, Order, Product
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.exceptions import NotFound

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

# For login, we use built-in TokenObtainPairView from simplejwt



class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering_fields = ['price']
    ordering = ['price']

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]  # Only admins can create products

class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]  # Only admins can update products

class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]  # Only admins can delete products


class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()  
    serializer_class = CategorySerializer  

    def perform_create(self, serializer):
        # If you want to add custom logic when creating a category (e.g., assign user), you can do that here
        serializer.save()
        


# Get or create cart
def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart

# Add item to cart
@api_view(['POST'])
def add_to_cart(request):
    user = request.user
    cart = get_or_create_cart(user)
    
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)
    
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity  # Increase quantity if item already in cart
    cart_item.save()

    return Response({"detail": "Item added to cart."}, status=status.HTTP_200_OK)

# Remove item from cart
@api_view(['DELETE'])
def remove_from_cart(request, item_id):
    user = request.user
    cart = get_or_create_cart(user)
    
    try:
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        cart_item.delete()
        return Response({"detail": "Item removed from cart."}, status=status.HTTP_200_OK)
    except CartItem.DoesNotExist:
        return Response({"detail": "Item not found in cart."}, status=status.HTTP_404_NOT_FOUND)

# View cart
@api_view(['GET'])
def view_cart(request):
    user = request.user
    cart = get_or_create_cart(user)
    
    cart_items = cart.cart_items.all()
    total_cost = cart.total_cost()
    
    cart_items_data = CartItemSerializer(cart_items, many=True).data
    
    return Response({"cart_items": cart_items_data, "total_cost": total_cost})

# Checkout (Place Order)
@api_view(['POST'])
def checkout(request):
    user = request.user
    cart = get_or_create_cart(user)
    shipping_address = request.data.get('shipping_address')
    
    if not shipping_address:
        return Response({"detail": "Shipping address is required."}, status=status.HTTP_400_BAD_REQUEST)

    order = Order.objects.create(
        user=user,
        cart=cart,
        shipping_address=shipping_address,
        total_cost=cart.total_cost(),
    )

    # Optionally, empty the cart after the order is placed
    cart.cart_items.all().delete()

    return Response({"detail": "Order placed successfully.", "order_id": order.id}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_orders(request):
    user = request.user
    orders = Order.objects.filter(user=user)
    if not orders:
        raise NotFound(detail="No orders found for this user.")

    orders_data = OrderSerializer(orders, many=True).data
    return Response(orders_data)

# Admin: View all orders and update order status
@api_view(['GET', 'PUT'])
@permission_classes([IsAdminUser])
def manage_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        raise NotFound(detail="Order not found.")

    # Get the order details if GET request
    if request.method == 'GET':
        order_data = OrderSerializer(order).data
        return Response(order_data)

    # Update order status if PUT request
    if request.method == 'PUT':
        new_status = request.data.get('status')
        if new_status not in ['Pending', 'Processing', 'Shipped', 'Delivered']:
            return Response({"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = new_status
        order.save()

        return Response({"detail": f"Order status updated to {new_status}."}, status=status.HTTP_200_OK)