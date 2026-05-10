from django.db.models import Q, Count, Sum
from store.models import Product, Category, Order, OrderItem, Coupon, ProductReview


def search_products(query=None, category_slug=None, min_price=None, max_price=None, brand=None, limit=10):
    qs = Product.objects.filter(is_available=True)
    if query:
        words = query.split()
        name_q = Q()
        desc_q = Q()
        brand_q = Q()
        for w in words:
            name_q |= Q(name__icontains=w)
            desc_q |= Q(description__icontains=w)
            brand_q |= Q(brand__icontains=w)
        qs = qs.filter(name_q | desc_q | brand_q)
    if category_slug:
        qs = qs.filter(category__slug=category_slug)
    if min_price is not None:
        qs = qs.filter(price__gte=min_price)
    if max_price is not None:
        qs = qs.filter(price__lte=max_price)
    if brand:
        qs = qs.filter(brand__iexact=brand)
    return qs.order_by('-is_featured', '-is_trending', 'name')[:limit]


def get_categories():
    return Category.objects.all().order_by('name')


def get_product_by_name(name):
    return Product.objects.filter(
        Q(name__icontains=name) | Q(slug__icontains=name)
    ).first()


def format_product_brief(product):
    price = product.discount_price if product.discount_price else product.price
    parts = [f"{product.name} — ${price}"]
    if product.discount_price:
        parts.append(f"(was ${product.price}, save {product.get_discount_percent()}%)")
    if product.brand:
        parts.append(f"by {product.brand}")
    parts.append(f"[Stock: {product.stock}]")
    return ' '.join(parts)


def format_product_detail(product):
    price = product.discount_price if product.discount_price else product.price
    lines = [
        f"**{product.name}**",
        f"Price: **${price}**",
    ]
    if product.discount_price:
        lines.append(f"Original: ~~${product.price}~~ (Save {product.get_discount_percent()}%)")
    if product.brand:
        lines.append(f"Brand: {product.brand}")
    if product.description:
        lines.append(f"Description: {product.description[:300]}")
    lines.append(f"Category: {product.category.name if product.category else 'N/A'}")
    lines.append(f"Stock: {product.stock} units")
    if product.is_featured:
        lines.append("\u2b50 Featured Product")
    if product.is_trending:
        lines.append("\U0001f525 Trending Now")
    return '\n'.join(lines)


def get_products_by_category(category_name=None):
    if category_name:
        cats = Category.objects.filter(Q(name__icontains=category_name) | Q(slug__icontains=category_name))
    else:
        cats = Category.objects.all()
    result = {}
    for cat in cats:
        products = Product.objects.filter(category=cat, is_available=True)[:5]
        if products:
            result[cat.name] = [format_product_brief(p) for p in products]
    return result


def search_orders(query):
    try:
        return Order.objects.filter(
            Q(order_number__icontains=query) |
            Q(phone__icontains=query)
        )[:5]
    except Exception:
        return []


def get_order_by_number(order_number):
    try:
        return Order.objects.filter(order_number__iexact=order_number.strip()).first()
    except Exception:
        return None


def format_order(order):
    items_info = ''
    try:
        items = order.items.all()
        if items:
            items_info = '\nItems: ' + ', '.join(f"{i.product.name} x{i.quantity}" for i in items[:3])
    except Exception:
        pass
    return (
        f"**Order #{order.order_number}**\n"
        f"Status: {order.status.title()}\n"
        f"Payment: {order.payment_method.upper()} \u2014 {order.payment_status.title()}\n"
        f"Total: ${order.total_amount}"
        f"{items_info}\n"
        f"Date: {order.created_at.strftime('%b %d, %Y')}"
    )


def search_products_by_brand(brand_name):
    return Product.objects.filter(brand__iexact=brand_name, is_available=True)[:10]


def get_all_brands():
    return [b for b in Product.objects.values_list('brand', flat=True).distinct() if b]


def get_reviews_for_product(product_name):
    product = get_product_by_name(product_name)
    if not product:
        return []
    return list(ProductReview.objects.filter(product=product).select_related('user')[:10])


def format_review(review):
    stars = '\u2b50' * review.rating
    return (
        f"{stars} by {review.user.username}\n"
        f"{review.comment[:200]}"
    )


def get_active_coupons():
    from django.utils import timezone
    today = timezone.now().date()
    return list(Coupon.objects.filter(is_active=True, valid_from__lte=today, valid_until__gte=today)[:10])


def format_coupon(coupon):
    return (
        f"**{coupon.code}** \u2014 {coupon.discount_percent}% off "
        f"(min order: ${coupon.min_order_amount}) "
        f"Valid until {coupon.valid_until.strftime('%b %d, %Y')}"
    )


def get_new_arrivals(days=30):
    from django.utils import timezone
    cutoff = timezone.now() - timezone.timedelta(days=days)
    return Product.objects.filter(created_at__gte=cutoff, is_available=True)[:10]


def compare_products(name_a, name_b):
    pa = get_product_by_name(name_a)
    pb = get_product_by_name(name_b)
    if not pa or not pb:
        return None
    def price(p):
        return p.discount_price if p.discount_price else p.price
    lines = [
        f"**Comparison: {pa.name} vs {pb.name}**\n",
        f"| Feature | {pa.name} | {pb.name} |",
        f"|---|--:|--:|",
        f"| Price | ${price(pa)} | ${price(pb)} |",
        f"| Brand | {pa.brand or 'N/A'} | {pb.brand or 'N/A'} |",
        f"| Stock | {pa.stock} | {pb.stock} |",
        f"| Category | {pa.category.name if pa.category else 'N/A'} | {pb.category.name if pb.category else 'N/A'} |",
    ]
    if pa.is_featured or pb.is_featured:
        lines.append(f"| Featured | {'Yes' if pa.is_featured else 'No'} | {'Yes' if pb.is_featured else 'No'} |")
    if pa.is_trending or pb.is_trending:
        lines.append(f"| Trending | {'Yes' if pa.is_trending else 'No'} | {'Yes' if pb.is_trending else 'No'} |")
    return '\n'.join(lines)


def get_top_selling_products(limit=5):
    return Product.objects.filter(
        is_available=True, orderitem__isnull=False
    ).annotate(
        total_sold=Sum('orderitem__quantity')
    ).order_by('-total_sold')[:limit]


def get_discounted_products():
    return Product.objects.filter(is_available=True, discount_price__isnull=False)[:10]


def format_discounted_product(product):
    save = product.get_discount_percent()
    return (
        f"{product.name} — ~~${product.price}~~ **${product.discount_price}** "
        f"(Save {save}%) [Stock: {product.stock}]"
    )


def get_best_products(limit=4):
    return Product.objects.filter(
        is_available=True, is_featured=True
    ).order_by('-is_trending', '-created_at')[:limit]


def format_how_to_order():
    return (
        "**How to Order from STYLEORA**\n\n"
        "### 1. Browse Products\n"
        "Explore our collections by category: Handbags, Jewelry, Cosmetics, "
        "Perfumes, Bangles, and Accessories. Use the search bar to find specific items.\n\n"
        "### 2. Select Your Item\n"
        "Click on any product to view full details — price, description, material, "
        "brand, stock availability, and customer reviews.\n\n"
        "### 3. Add to Cart\n"
        "Choose the quantity and click **Add to Cart**. Your cart will show a summary "
        "of all items with the total price.\n\n"
        "### 4. Review Cart\n"
        "Go to your cart to review items, adjust quantities, or remove products. "
        "Apply any discount coupon codes here.\n\n"
        "### 5. Checkout\n"
        "Click **Proceed to Checkout** and provide:\n"
        "- Your shipping address\n"
        "- Phone number for delivery updates\n"
        "- Any special instructions\n\n"
        "### 6. Choose Payment Method\n"
        "Select from:\n"
        "- **Cash on Delivery (COD)** — pay when you receive\n"
        "- **Online Payment** — JazzCash, Easypaisa, Bank Transfer, or Credit/Debit Card\n\n"
        "### 7. Confirm Order\n"
        "Review your order summary and click **Place Order**. "
        "You'll receive an order confirmation with a unique **Order Number** "
        "to track your shipment.\n\n"
        "### 8. Receive & Enjoy\n"
        "Your order will be delivered within 3-5 business days (standard shipping). "
        "Enjoy your STYLEORA products!"
    )


def format_shipment_details():
    return (
        "**Shipment & Delivery Information**\n\n"
        "### Shipping Methods\n"
        "- **Standard Shipping**: 3-5 business days — Rs150 flat rate\n"
        "- **Express Shipping**: 24-48 hours — Rs350\n"
        "- **Free Shipping**: On orders above Rs2,000\n\n"
        "### Coverage\n"
        "We ship nationwide across Pakistan. International shipping is available "
        "to select countries — contact support for a quote.\n\n"
        "### Tracking\n"
        "Once your order is shipped, you'll receive a tracking link via SMS and email. "
        "You can also track your order through your account's **Order History** page.\n\n"
        "### Delivery Timeline\n"
        "| Step | Timeframe |\n"
        "|---|---|\n"
        "| Order Confirmation | Immediately |\n"
        "| Processing | 24 hours |\n"
        "| Dispatch | 1-2 business days |\n"
        "| In Transit | 1-3 business days (standard) |\n"
        "| Delivered | As per selected method |\n\n"
        "### Important Notes\n"
        "- Delivery only on business days (Mon-Sat, excluding public holidays)\n"
        "- A signature may be required upon delivery\n"
        "- If you're not home, the courier will attempt redelivery"
    )


def get_all_products_by_category():
    result = {}
    for cat in Category.objects.all().order_by('name'):
        products = Product.objects.filter(category=cat, is_available=True).order_by('name')
        if products:
            result[cat.name] = [format_product_brief(p) for p in products]
    return result


def get_products_by_price_range(min_price, max_price):
    return Product.objects.filter(
        is_available=True,
        price__gte=min_price,
        price__lte=max_price
    ).order_by('price')[:10]
