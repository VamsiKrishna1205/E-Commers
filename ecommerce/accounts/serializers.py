from rest_framework import serializers
from .models import User,Product, Category,User, CartItem, Order, CartItem
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'is_customer', 'is_admin')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        is_admin = validated_data.pop('is_admin', False)
        is_customer = validated_data.pop('is_customer', True)
        
        # Create the user
        user = User.objects.create_user(**validated_data)

        # Set flags manually
        user.is_admin = is_admin
        user.is_customer = is_customer
        
        if is_admin:
            user.is_staff = True 

        user.save()
        return user


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'image_url']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name'] 

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['product', 'quantity', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    product_list = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'shipping_address', 'total_cost', 'status', 'created_at', 'product_list']

    def get_product_list(self, obj):
        return obj.product_details()  # List of product names and their details in the order