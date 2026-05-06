from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime
import random
import string
from .models import Category, Product, ProductReview, Order, OrderItem, Wishlist, Coupon
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ProductReviewSerializer, OrderSerializer, WishlistSerializer, CouponSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        category = self.request.query_params.get('category')
        brand = self.request.query_params.get('brand')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        is_available = self.request.query_params.get('is_available')
        is_trending = self.request.query_params.get('is_trending')
        is_featured = self.request.query_params.get('is_featured')
        search = self.request.query_params.get('search')

        if category:
            queryset = queryset.filter(category__slug=category)
        if brand:
            queryset = queryset.filter(brand__icontains=brand)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if is_available:
            queryset = queryset.filter(is_available=is_available.lower() == 'true')
        if is_trending:
            queryset = queryset.filter(is_trending=True)
        if is_featured:
            queryset = queryset.filter(is_featured=True)
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset

    @action(detail=False, methods=['get'])
    def featured(self, request):
        products = Product.objects.filter(is_featured=True)[:8]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def trending(self, request):
        products = Product.objects.filter(is_trending=True)[:8]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def new_arrivals(self, request):
        products = Product.objects.order_by('-created_at')[:8]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

class ProductReviewViewSet(viewsets.ModelViewSet):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def create(self, request):
        data = request.data
        user = request.user
        order_number = 'ORD' + ''.join(random.choices(string.digits, k=8))
        
        order = Order.objects.create(
            user=user,
            order_number=order_number,
            shipping_address=data.get('shipping_address', ''),
            phone=data.get('phone', ''),
            notes=data.get('notes', ''),
            payment_method=data.get('payment_method', 'cod'),
            total_amount=data.get('total_amount', 0),
        )

        items_data = data.get('items', [])
        for item in items_data:
            product = get_object_or_404(Product, id=item['product_id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                price=item['price']
            )
            product.stock -= item['quantity']
            product.save()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def history(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def create(self, request):
        product_id = request.data.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        wishlist, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        return Response({'status': 'added to wishlist'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'], url_path='remove/(?P<product_id>[^/.]+)')
    def remove_from_wishlist(self, request, product_id=None):
        Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
        return Response({'status': 'removed from wishlist'})

class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def validate(self, request):
        code = request.data.get('code')
        total_amount = float(request.data.get('total_amount', 0))
        
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
            today = timezone.now().date()
            
            if coupon.valid_from <= today <= coupon.valid_until:
                if total_amount >= coupon.min_order_amount:
                    return Response({
                        'valid': True,
                        'discount_percent': coupon.discount_percent
                    })
            return Response({'valid': False, 'message': 'Coupon not valid'})
        except Coupon.DoesNotExist:
            return Response({'valid': False, 'message': 'Invalid coupon code'})