from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Category, Product, Order, OrderItem, Wishlist, Coupon
from django.db.models import Avg
import random

def home(request):
    categories = Category.objects.all()[:6]
    featured_products = Product.objects.filter(is_featured=True, is_available=True)[:8]
    trending_products = Product.objects.filter(is_trending=True, is_available=True)[:8]
    new_arrivals = Product.objects.order_by('-created_at')[:8]
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
        'trending_products': trending_products,
        'new_arrivals': new_arrivals,
    }
    return render(request, 'store/home.html', context)

def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True)
    
    category_slug = request.GET.get('category')
    brand = request.GET.get('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort', '-created_at')
    search = request.GET.get('search')
    
    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)
    if brand:
        products = products.filter(brand__icontains=brand)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if search:
        products = products.filter(name__icontains=search)
    
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')
    
    brands = Product.objects.values_list('brand', flat=True).distinct()
    
    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'current_category': current_category,
    }
    
    # Category background images
    bg_images = {
        'handbags': 'https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?w=1920',
        'jewelry': 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=1920',
        'cosmetics': 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=1920',
        'perfumes': 'https://images.unsplash.com/photo-1587017539504-67cfbddac569?w=1920',
        'bangles': 'https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=1920',
        'accessories': 'https://images.unsplash.com/photo-1606760227091-3dd870d97f1d?w=1920',
    }
    bg_url = bg_images.get(category_slug, 'https://images.unsplash.com/photo-1483985988355-763728e1935b?w=1920')
    context['bg_url'] = bg_url
    
    return render(request, 'store/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    reviews = product.reviews.all()[:5]
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'average_rating': average_rating,
        'in_wishlist': in_wishlist,
    }
    return render(request, 'store/product_detail.html', context)

@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    context = {'wishlist_items': wishlist_items}
    return render(request, 'store/wishlist.html', context)

@require_POST
@login_required
def add_to_wishlist(request):
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    messages.success(request, 'Added to wishlist!')
    return redirect('product_detail', slug=product.slug)

@require_POST
@login_required
def remove_from_wishlist(request, product_id):
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    messages.success(request, 'Removed from wishlist!')
    return redirect('wishlist')

def cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.discount_price or product.price
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'price': item_total,
                'total': item_total * item['quantity'],
            })
            total += item_total * item['quantity']
        except Product.DoesNotExist:
            continue
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'store/cart.html', context)

@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    product = get_object_or_404(Product, id=product_id)
    
    cart = request.session.get('cart', {})
    
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += quantity
    else:
        cart[str(product_id)] = {'quantity': quantity}
    
    request.session['cart'] = cart
    messages.success(request, f'{product.name} added to cart!')
    return redirect('cart')

@require_POST
def update_cart(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    
    cart = request.session.get('cart', {})
    
    if str(product_id) in cart:
        if quantity > 0:
            cart[str(product_id)]['quantity'] = quantity
        else:
            del cart[str(product_id)]
    
    request.session['cart'] = cart
    return redirect('cart')

@require_POST
def remove_from_cart(request):
    product_id = request.POST.get('product_id')
    
    cart = request.session.get('cart', {})
    
    if str(product_id) in cart:
        del cart[str(product_id)]
    
    request.session['cart'] = cart
    return redirect('cart')

def checkout(request):
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.error(request, 'Your cart is empty!')
        return redirect('cart')
    
    cart_items = []
    total = 0
    
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            price = product.discount_price or product.price
            item_total = price * item['quantity']
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'price': price,
                'total': item_total,
            })
            total += item_total
        except Product.DoesNotExist:
            continue
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email')
        shipping_address = request.POST.get('shipping_address')
        phone = request.POST.get('phone')
        payment_method = request.POST.get('payment_method', 'cod')
        coupon_code = request.POST.get('coupon_code', '')
        notes = request.POST.get('notes', '')
        
        # Handle User (Guest Checkout)
        current_user = request.user
        if not current_user.is_authenticated:
            if email:
                try:
                    current_user = User.objects.get(email=email)
                except User.DoesNotExist:
                    current_user = User.objects.create_user(
                        username=email, 
                        email=email, 
                        password='guest_password'
                    )
                    current_user.first_name = first_name
                    current_user.last_name = last_name
                    current_user.save()
            else:
                messages.error(request, 'Email is required for guest checkout.')
                return redirect('checkout')
        
        discount = 0
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                today = __import__('datetime').datetime.now().date()
                if coupon.valid_from <= today <= coupon.valid_until and total >= coupon.min_order_amount:
                    discount = total * coupon.discount_percent / 100
            except Coupon.DoesNotExist:
                pass
        
        final_total = total - discount
        
        order_number = 'ORD' + ''.join(str(random.randint(0, 9)) for _ in range(8))
        
        order = Order.objects.create(
            user=current_user,
            order_number=order_number,
            shipping_address=shipping_address,
            phone=phone,
            payment_method=payment_method,
            notes=notes,
            total_amount=final_total,
        )
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price']
            )
            item['product'].stock -= item['quantity']
            item['product'].save()
        
        request.session['cart'] = {}
        messages.success(request, f'Order placed successfully! Order #{order_number}')
        return redirect('order_success', order_number=order_number)
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'store/checkout.html', context)

def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    context = {'order': order}
    return render(request, 'store/order_success.html', context)

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {'orders': orders}
    return render(request, 'store/order_history.html', context)

@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    context = {'order': order}
    return render(request, 'store/order_detail.html', context)