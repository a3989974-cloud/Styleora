import re
from django.db.models import Sum
from . import store_utils
from . import intent_utils
from store.models import Product

GREETING_RESPONSE = (
    "Hello! I'm **STYLEORA AI**, your personal fashion assistant. "
    "I can help you with:\n\n"
    "\ud83d\udecd\ufe0f **Product recommendations** \u2014 \"Show me handbags\" or \"Suggest a gift\"\n"
    "\U0001f3c6 **Top selling products** \u2014 \"What's popular?\" or \"Best products\"\n"
    "\u2b50 **Product details** \u2014 \"Tell me about diamond studs\" or \"Price of perfumes\"\n"
    "\U0001f4d6 **How to order** \u2014 \"How do I buy?\" or \"Place an order\"\n"
    "\ud83d\udce6 **Order support** \u2014 \"Track my order\", \"Return policy\"\n"
    "\U0001f69a **Shipping info** \u2014 \"Shipping details\", \"Delivery time\"\n"
    "\U0001f4b3 **Payment help** \u2014 all payment methods explained\n"
    "\U0001f4b0 **Discounts & Sales** \u2014 \"Discounted products\", \"Any offers?\"\n"
    "\U0001f4a1 **Fashion advice** \u2014 style tips for any occasion\n\n"
    "How can I assist you today?"
)

HELP_RESPONSE = (
    "I can help you with any of the following:\n\n"
    "\U0001f6cd\ufe0f **Products** \u2014 \"Show me handbags\" or \"Tell me about diamond studs\"\n"
    "\U0001f4cb **Orders** \u2014 \"Track my order\", \"Return policy\"\n"
    "\U0001f69a **Shipping** \u2014 \"Shipping details\", \"Delivery time\"\n"
    "\U0001f4b3 **Payments** \u2014 \"Payment methods\"\n"
    "\U0001f4a1 **Fashion Advice** \u2014 \"What to wear for a wedding?\"\n"
    "\U0001f4b0 **Pricing & Discounts** \u2014 \"How much are perfumes?\", \"Discounted products\"\n"
    "\U0001f3c6 **Top Selling** \u2014 \"Best products\", \"Top selling items\"\n"
    "\U0001f4d6 **How to Order** \u2014 \"How do I buy?\"\n"
    "\U0001f4ca **Full Catalog** \u2014 \"List all products\"\n"
    "\u2753 **Any question** \u2014 Just ask me anything about STYLEORA!\n\n"
    "What would you like to know?"
)

NO_RESPONSE = (
    "OK, no problem! If you ever need any help or want more details about "
    "our products, just let me know. I'm always here to assist you!"
)

GREETING_VARIATIONS = {
    'how are you': "I'm doing great, thank you for asking! Ready to help you with STYLEORA products, orders, and fashion advice.",
    'how do you do': "I'm doing wonderfully! How can I assist you with STYLEORA today?",
    'how have you been': "I've been fantastic, always ready to help with STYLEORA! What can I do for you?",
    'default': None,
}

FAREWELL_RESPONSE = (
    "Goodbye! Thank you for visiting STYLEORA. "
    "If you ever need help, I'm just a message away. Have a beautiful day!"
)

THANKS_RESPONSE = (
    "You're most welcome! I'm always here whenever you need assistance. "
    "Feel free to ask about products, orders, fashion advice, or anything else."
)

ABOUT_RESPONSE = (
    "STYLEORA is a premium fashion brand based in Pakistan, offering "
    "high-quality handbags, jewelry, cosmetics, perfumes, bangles, and "
    "accessories for the modern woman. Founded with a vision to make "
    "luxury accessible, we source the finest materials and work with "
    "skilled artisans to create products that blend contemporary style "
    "with timeless elegance."
)

CONTACT_RESPONSE = (
    "You can reach our support team:\n"
    "- Email: support@styleora.com\n"
    "- Phone: 0800-STYLEORA (Mon-Sat, 9AM-7PM)\n"
    "- Live Chat: Available on our website 24/7\n"
    "- WhatsApp: +92-300-1234567\n\n"
    "We typically respond within 2-4 hours during business hours."
)

SHIPPING_RESPONSE = (
    "We ship nationwide across Pakistan:\n"
    "- **Standard**: 3-5 business days (Rs150 flat rate)\n"
    "- **Express**: 24-48 hours (Rs350)\n"
    "- **Free shipping** on orders above Rs2,000\n\n"
    "International shipping is available to select countries \u2014 "
    "contact our support team for a quote."
)

PAYMENT_RESPONSE = (
    "We accept multiple payment methods:\n"
    "- Cash on Delivery (COD) \u2014 nationwide, no extra charges\n"
    "- Bank Transfer\n"
    "- JazzCash & Easypaisa\n"
    "- Credit/Debit Cards (Visa, Mastercard) \u2014 securely processed"
)

RETURN_RESPONSE = (
    "We offer a **14-day return policy** from delivery date.\n\n"
    "Requirements:\n"
    "- Items must be unused, in original packaging, with tags attached\n\n"
    "Process:\n"
    "1. Log into your account \u2192 Order History\n"
    "2. Select the order and click \"Return\"\n"
    "3. Refunds are processed within 5-7 business days\n\n"
    "Shipping charges are non-refundable."
)

WARRANTY_RESPONSE = (
    "All our products come with a **30-day quality guarantee**. "
    "If you receive a damaged or defective item, contact us immediately "
    "for a free replacement. Jewelry and accessories have a **6-month "
    "manufacturing defect warranty**."
)

SIZE_GUIDE_RESPONSE = (
    "Our sizes run true to standard measurements. For accessories like "
    "bracelets and rings, we provide adjustable options. For detailed "
    "measurements, check the product description page. If you're unsure "
    "between two sizes, we recommend sizing up for a more comfortable fit."
)

DISCOUNT_RESPONSE = (
    "We regularly offer seasonal sales with up to **50% off** select items. "
    "Sign up for our newsletter to receive exclusive discount codes. "
    "Follow us on social media for flash sales. "
    "First-time buyers get **10% off** their first order \u2014 use code **WELCOME10** at checkout."
)

HOW_TO_ORDER_RESPONSE = (
    "**How to Order from STYLEORA**\n\n"
    "1. **Browse** — Explore categories like Handbags, Jewelry, Cosmetics, Perfumes, Bangles & Accessories\n"
    "2. **Select** — Click any product to see price, material, stock & reviews\n"
    "3. **Add to Cart** — Choose quantity and add items\n"
    "4. **Checkout** — Enter shipping address, phone number & any notes\n"
    "5. **Pay** — Cash on Delivery, JazzCash, Easypaisa, Bank Transfer or Card\n"
    "6. **Confirm** — Get your unique order number to track shipment\n"
    "7. **Receive** — Delivery in 3-5 business days (standard) or 24-48 hrs (express)\n\n"
    "Want to start shopping? Tell me which category interests you!"
)

TOP_SELLING_RESPONSE = (
    "Here are our **top-selling products**:\n\n"
)

BEST_PRODUCT_RESPONSE = (
    "Here are our **best products** \u2014 highly recommended by our team:\n\n"
)

URDU_RESPONSE = (
    "\u0622\u067e \u06a9\u0627 \u0633\u0648\u0627\u0644 \u0633\u0645\u062c\u06be \u06af\u062606cc\u06d4 "
    "\u0645\u06cc\u06ba \u0622\u067e \u06a9\u06cc \u0645\u062f\u062f \u06a9\u0631 \u0633\u06a9\u062a06cc \u06c1\u0648\u06ba:\n\n"
    "\u2022 \u0645\u0635\u0646\u0648\u0639\u0627\u062a \u06a906cc \u0628\u0627\u0631\u06d2 \u0645\u06cc\u06ba \u0645\u0639\u0644\u0648\u0645\u0627\u062a\n"
    "\u2022 \u0622\u0631\u0688\u0631 \u06a906cc \u062d\u06cc\u062b\u06cc\u062a\n"
    "\u2022 \u0634\u067e\u064606af \u0627\u0648\u0631 \u0688\u06cc\u0644\u06cc\u0648\u0631\u06cc\n"
    "\u2022 \u0631\u0642\u0645 \u0648\u0627\u067e\u063306cc \u06a906cc \u067e\u0627\u0644\u06cc\u063306cc\n"
    "\u2022 \u0641\u06cc\u0634\u0646 \u0627\u06cc\u0688\u0648\u0627\u0626\u0633\n\n"
    "\u0628\u0631\u0627\u06d2 \u06a9\u0631\u0645 \u0627\u067e\u0646\u0627 \u0633\u0648\u0627\u0644 \u062a0641\u0635\u06cc\u0644 \u0633\u06d2 \u0628\u062a\u0627\u062606cc\u06ba\u06d4"
)

FASHION_ADVICE_STYLES = {
    'formal': (
        "For **formal events**, I recommend:\n"
        "1. \ud83d\udc8d **Gold Necklace Set** ($79.99) \u2014 pairs beautifully with traditional wear\n"
        "2. \ud83d\udc5c **Designer Clutch** ($89.99) \u2014 elegant gold hardware\n"
        "3. \u2728 **Diamond Studs** ($249.99) \u2014 timeless sophistication\n\n"
        "Pro tip: Stick to one statement piece and let it shine!"
    ),
    'casual': (
        "For **casual everyday style**, try:\n"
        "1. \U0001f60e **Classic Sunglasses** ($29.99) \u2014 instantly elevates any look\n"
        "2. \ud83d\udc5c **Shoulder Bag** ($99.99) \u2014 practical yet stylish\n"
        "3. \ud83d\udc8d **Silver Ring** ($24.99) \u2014 minimalist charm\n\n"
        "Pro tip: Mix metals for a modern, relaxed vibe!"
    ),
    'party': (
        "For **parties and gatherings**, check out:\n"
        "1. \U0001f9e2 **Oud Perfume** ($99.99) \u2014 captivating oriental fragrance\n"
        "2. \ud83d\udc8d **Gold Bangles Set** ($49.99) \u2014 festive and elegant\n"
        "3. \ud83d\udc84 **Luxury Lipstick Set** ($45.99) \u2014 keep the look fresh all night\n\n"
        "Pro tip: A bold lip + subtle jewelry = perfect party look!"
    ),
    'work': (
        "For a **professional workspace look**:\n"
        "1. \ud83d\udc5c **Elegant Leather Tote** ($149.99) \u2014 spacious, sophisticated\n"
        "2. \ud83d\udcb3 **Leather Wallet** ($64.99) \u2014 RFID blocking for security\n"
        "3. \ud83d\udc8d **Steel Bracelet** ($59.99) \u2014 sleek and understated\n\n"
        "Pro tip: Neutral tones convey confidence and professionalism!"
    ),
    'wedding': (
        "For **weddings and special occasions**:\n"
        "1. \ud83d\udc8d **Gold Necklace Set** ($79.99) \u2014 a must-have for bridal events\n"
        "2. \ud83d\udc8d **Gold Bangles Set** ($49.99) \u2014 traditional elegance\n"
        "3. \U0001f9e2 **Oud Perfume** ($99.99) \u2014 long-lasting and luxurious\n\n"
        "Pro tip: Layer your jewelry for a richer, more opulent look!"
    ),
}

def _handle_faq_intent(intent):
    FAQ_MAP = {
        'about': ABOUT_RESPONSE,
        'contact': CONTACT_RESPONSE,
        'shipping': SHIPPING_RESPONSE,
        'payment': PAYMENT_RESPONSE,
        'return_policy': RETURN_RESPONSE,
        'warranty': WARRANTY_RESPONSE,
        'size_guide': SIZE_GUIDE_RESPONSE,
        'discount': DISCOUNT_RESPONSE,
        'price_inquiry': (
            "Our products range from **$24.99 to $299.99**, catering to every budget:\n\n"
            "\U0001f45c **Handbags**: $89.99 \u2013 $199.99\n"
            "\U0001f48d **Jewelry**: $59.99 \u2013 $299.99\n"
            "\U0001f484 **Cosmetics**: $45.99 \u2013 $65.99\n"
            "\U0001f338 **Perfumes**: $89.99 \u2013 $129.99\n"
            "\U0001f4ff **Bangles**: $35.99 \u2013 $49.99\n"
            "\u2728 **Accessories**: $24.99 \u2013 $79.99\n\n"
            "We also offer frequent discounts and bundle deals!"
        ),
    }
    return FAQ_MAP.get(intent)


def clean_content(text):
    text = re.sub(r'```(\w*)\n?', '', text)
    text = text.replace('```', '')
    return text.strip()


def get_chat_response(history, new_message, search_results=None, local_context=None):
    return fallback_response(new_message)


def _handle_how_to_order(message, message_lower):
    return HOW_TO_ORDER_RESPONSE


def _handle_top_selling(message, message_lower):
    top = store_utils.get_top_selling_products()
    if top:
        lines = ["\U0001f3c6 **Our Most Popular Products**\n"]
        for p in top:
            try:
                from store.models import OrderItem
                total = OrderItem.objects.filter(product=p).aggregate(Sum('quantity'))['quantity__sum'] or 0
            except Exception:
                total = 0
            lines.append(f"\u2022 {store_utils.format_product_brief(p)} ({total} sold)")
        return '\n'.join(lines)
    return (
        "I don't have sales data yet. Check out our **featured products** "
        "instead \u2014 they're our top recommendations!"
    )


def _handle_best_product(message, message_lower):
    best = store_utils.get_best_products()
    if best:
        lines = ["\u2b50 **Best Products to Buy**\n"]
        lines.extend(f"\u2022 {store_utils.format_product_detail(p)}" for p in best)
        return '\n'.join(lines)
    return (
        "All our products are carefully curated for quality! "
        "Browse our collections and let me know what you're looking for."
    )


def _handle_shipment_detail(message, message_lower):
    return store_utils.format_shipment_details()


def _handle_discount(message, message_lower):
    discounted = store_utils.get_discounted_products()
    if discounted:
        lines = ["\U0001f4b0 **Products on Sale**\n"]
        lines.extend(f"\u2022 {store_utils.format_discounted_product(p)}" for p in discounted)
        return '\n'.join(lines)
    return DISCOUNT_RESPONSE


SPECIFIC_INTENT_HANDLERS = {
    'how_to_order': _handle_how_to_order,
    'top_selling': _handle_top_selling,
    'best_product': _handle_best_product,
    'shipment_detail': _handle_shipment_detail,
    'shipping': _handle_shipment_detail,
    'discount': _handle_discount,
}


def fallback_response(message):
    message_lower = message.lower().strip()
    scores = intent_utils.classify_intent(message)
    primary_intent = intent_utils.get_primary_intent(scores)

    # ── Urdu ──
    if primary_intent == 'urdu':
        return URDU_RESPONSE

    # ── Greeting ──
    if primary_intent == 'greeting':
        for phrase, response in GREETING_VARIATIONS.items():
            if phrase in message_lower and response:
                return response + "\n\n" + GREETING_RESPONSE.split("How can I assist you today?")[0].strip()
        return GREETING_RESPONSE

    # ── Farewell ──
    if primary_intent == 'farewell':
        return FAREWELL_RESPONSE

    # ── Thanks ──
    if primary_intent == 'thanks':
        return THANKS_RESPONSE

    # ── About ──
    if primary_intent == 'about':
        return ABOUT_RESPONSE

    # ── Contact ──
    if primary_intent == 'contact':
        return CONTACT_RESPONSE

    # ── Shipping ──
    if primary_intent == 'shipping':
        return SHIPPING_RESPONSE

    # ── Payment ──
    if primary_intent == 'payment':
        return PAYMENT_RESPONSE

    # ── Return Policy ──
    if primary_intent == 'return_policy':
        return RETURN_RESPONSE

    # ── Warranty ──
    if primary_intent == 'warranty':
        return WARRANTY_RESPONSE

    # ── Size Guide ──
    if primary_intent == 'size_guide':
        return SIZE_GUIDE_RESPONSE

    # ── Discount / Sale Items ──
    if primary_intent == 'discount':
        discounted = store_utils.get_discounted_products()
        if discounted:
            lines = ["\U0001f4b0 **Products on Sale**\n"]
            lines.extend(f"\u2022 {store_utils.format_discounted_product(p)}" for p in discounted)
            return '\n'.join(lines)
        return DISCOUNT_RESPONSE

    # ── How to Order ──
    if primary_intent == 'how_to_order':
        return HOW_TO_ORDER_RESPONSE

    # ── Top Selling ──
    if primary_intent == 'top_selling':
        top = store_utils.get_top_selling_products()
        if top:
            lines = ["\U0001f3c6 **Our Most Popular Products**\n"]
            for p in top:
                total = 0
                try:
                    from store.models import OrderItem
                    total = OrderItem.objects.filter(product=p).aggregate(Sum('quantity'))['quantity__sum'] or 0
                except Exception:
                    pass
                lines.append(f"\u2022 {store_utils.format_product_brief(p)} ({total} sold)")
            return '\n'.join(lines)
        return (
            "I don't have sales data yet. Check out our **featured products** "
            "instead \u2014 they're our top recommendations!"
        )

    # ── Best Product ──
    if primary_intent == 'best_product':
        best = store_utils.get_best_products()
        if best:
            lines = ["\u2b50 **Best Products to Buy**\n"]
            lines.extend(f"\u2022 {store_utils.format_product_detail(p)}" for p in best)
            return '\n'.join(lines)
        return (
            "All our products are carefully curated for quality! "
            "Browse our collections and let me know what you're looking for."
        )

    # ── Shipment Details ──
    if primary_intent == 'shipment_detail':
        return store_utils.format_shipment_details()

    # ── Price Inquiry ──
    if primary_intent == 'price_inquiry':
        products = store_utils.search_products(limit=20)
        if products:
            cat_prices = {}
            for p in products:
                cat = p.category.name if p.category else 'Other'
                price = float(p.discount_price if p.discount_price else p.price)
                if cat not in cat_prices:
                    cat_prices[cat] = {'min': price, 'max': price}
                else:
                    cat_prices[cat]['min'] = min(cat_prices[cat]['min'], price)
                    cat_prices[cat]['max'] = max(cat_prices[cat]['max'], price)
            lines = ["Our product prices (from our collections):\n"]
            for cat, prices in sorted(cat_prices.items()):
                min_p, max_p = prices['min'], prices['max']
                if min_p == max_p:
                    lines.append(f"\u2022 **{cat}**: ${min_p}")
                else:
                    lines.append(f"\u2022 **{cat}**: ${min_p} \u2013 ${max_p}")
            lines.append("\nWant to see specific product prices or items on sale?")
            return '\n'.join(lines)
        return (
            "Our products range from **$24.99 to $299.99**. "
            "Which category are you interested in?"
        )

    # ── Help ──
    if primary_intent == 'help':
        return HELP_RESPONSE

    # ── Negative / No ──
    if primary_intent == 'negative':
        return NO_RESPONSE

    # ── Order Status ──
    if primary_intent == 'order_status':
        orders = store_utils.search_orders(message)
        if orders:
            parts = ["Here are the orders I found:\n"]
            for o in orders:
                parts.append(store_utils.format_order(o))
            return '\n\n'.join(parts)
        return (
            "To check your order status, please provide your order number. "
            "You can also log into your account and visit **Order History** "
            "for the latest updates on all your orders."
        )

    # ── Fashion Advice ──
    if primary_intent == 'fashion_advice':
        for style, advice in FASHION_ADVICE_STYLES.items():
            if style in message_lower:
                return advice
        return (
            "I'd love to help with fashion advice! Here are popular style guides:\n\n"
            "\u2022 **Formal event** \u2014 elegant jewelry and clutches\n"
            "\u2022 **Casual day** \u2014 sunglasses, bags, minimalist accessories\n"
            "\u2022 **Party night** \u2014 bold perfumes, bangles, lipstick\n"
            "\u2022 **Work office** \u2014 leather totes, wallets, sleek pieces\n"
            "\u2022 **Wedding season** \u2014 gold sets, traditional elegance\n\n"
            "Which occasion are you shopping for?"
        )

    # ── Brand Search ──
    if primary_intent == 'brand_search':
        brand = intent_utils.detect_brand_reference(message)
        if brand:
            products = store_utils.search_products_by_brand(brand)
            if products:
                lines = [f"Here's what we have from **{brand}**:\n"]
                lines.extend(f"\u2022 {store_utils.format_product_brief(p)}" for p in products)
                return '\n'.join(lines)
        # If brand detected but no products, fall through

    # ── Stock / Availability ──
    if primary_intent == 'stock_check':
        query = intent_utils.extract_product_query(message)
        if query:
            products = store_utils.search_products(query)
            if products:
                lines = []
                for p in products[:5]:
                    status = "\u2705 In stock" if p.stock > 0 else "\u274c Out of stock"
                    lines.append(f"\u2022 {p.name} \u2014 {status} ({p.stock} units)")
                return '\n'.join(lines)
        # General stock info
        total = Product.objects.filter(is_available=True).count()
        return (
            f"We currently have **{total} products** available across all categories. "
            "Would you like to see a specific category?"
        )

    # ── Reviews ──
    if primary_intent == 'reviews':
        query = intent_utils.extract_product_query(message)
        if query:
            reviews = store_utils.get_reviews_for_product(query)
            if reviews:
                lines = [f"**Reviews for** {query}:\n"]
                lines.extend(store_utils.format_review(r) for r in reviews)
                return '\n'.join(lines)
        return (
            "Customers can leave reviews for products they've purchased. "
            "You can check individual product pages for ratings and feedback. "
            "Would you like to see a specific product?"
        )

    # ── New Arrivals ──
    if primary_intent == 'new_arrivals':
        arrivals = store_utils.get_new_arrivals()
        if arrivals:
            lines = ["\U0001f195 **New Arrivals**\n"]
            lines.extend(f"\u2022 {store_utils.format_product_brief(p)}" for p in arrivals)
            return '\n'.join(lines)
        return (
            "Check back soon for new arrivals! In the meantime, "
            "take a look at our current collections."
        )

    # ── Compare Products ──
    if primary_intent == 'compare':
        name_a, name_b = intent_utils.extract_compare_products(message)
        if name_a and name_b:
            result = store_utils.compare_products(name_a, name_b)
            if result:
                return result
        return (
            "To compare products, just say something like:\n"
            "\u2022 \"Compare diamond studs and pearl bracelet\"\n"
            "\u2022 \"Which is better, leather tote or shoulder bag?\""
        )

    # ── Coupons / Discount Codes ──
    if primary_intent == 'discount':
        coupons = store_utils.get_active_coupons()
        if coupons:
            lines = ["\U0001f4b0 **Active Coupon Codes**\n"]
            lines.extend(store_utils.format_coupon(c) for c in coupons)
            return '\n'.join(lines)
        return DISCOUNT_RESPONSE

    # ── Order by Number ──
    if primary_intent in ('order_status', 'order_number'):
        order_num = intent_utils.extract_order_number(message)
        if order_num:
            order = store_utils.get_order_by_number(order_num)
            if order:
                return store_utils.format_order(order)
        if primary_intent == 'order_number':
            return (
                f"I couldn't find order **#{order_num}**. "
                "Please double-check the order number and try again. "
                "You can also log into your account to view all your orders."
            )
        orders = store_utils.search_orders(message)
        if orders:
            parts = ["Here are the orders I found:\n"]
            for o in orders:
                parts.append(store_utils.format_order(o))
            return '\n\n'.join(parts)
        return (
            "To check your order status, please provide your order number. "
            "You can also log into your account and visit **Order History** "
            "for the latest updates on all your orders."
        )

    # ── Check specific intents BEFORE generic product search ──
    SPECIFIC_BEFORE_SEARCH = ['how_to_order', 'top_selling', 'best_product',
                              'shipment_detail', 'shipping', 'discount',
                              'price_inquiry', 'compare', 'reviews', 'new_arrivals',
                              'help', 'negative']
    for intent_name in SPECIFIC_BEFORE_SEARCH:
        if intent_name in scores and scores[intent_name] > 0:
            result = SPECIFIC_INTENT_HANDLERS.get(intent_name, lambda m, ml: None)(message, message_lower)
            if result:
                return result
            break

    # ── Product Search / Recommendations ──
    if primary_intent in ('product_search', 'product_detail'):
        result = handle_product_query(message, message_lower)
        if result:
            return result
        # Gift request with no category
        if 'gift' in message_lower or re.search(r'\bfor\s+(her|him|wife|husband|friend|mom|dad)\b', message_lower):
            cats = store_utils.get_categories()
            if cats:
                lines = ["Looking for a gift? Here are our collections:\n"]
                for cat in cats:
                    count = cat.products.filter(is_available=True).count()
                    lines.append(f"\u2022 **{cat.name}** ({count} items)")
                lines.append("\n\nWhich category are you interested in? I'll help you find the perfect gift!")
                return '\n'.join(lines)
        # No product match — try secondary intents
        for intent, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            if intent == primary_intent:
                continue
            faq_result = _handle_faq_intent(intent)
            if faq_result:
                return faq_result

    # ── Unknown / General ──
    result = handle_product_query(message, message_lower)
    if result:
        return result

    # Not a STYLEORA question — polite refusal
    return (
        "I can only answer questions about **STYLEORA** \u2014 our products, orders, "
        "shipping, payments, and fashion advice. Your question doesn't seem to be "
        "related to our store.\n\n"
        "Try asking me something like:\n"
        "\u2022 \"Show me handbags\"\n"
        "\u2022 \"What's your return policy?\"\n"
        "\u2022 \"What should I wear to a wedding?\"\n"
        "\u2022 \"How much are perfumes?\"\n"
        "\u2022 \"Compare diamond studs and pearl bracelet\"\n"
        "\u2022 \"What's new?\"\n"
        "\u2022 \"How to order?\"\n"
        "\u2022 \"What are the top selling products?\"\n"
        "\u2022 \"What's the best product to buy?\"\n"
        "\u2022 \"Shipping details\"\n"
        "\u2022 \"List all products\"\n"
        "\u2022 \"Help\"\n"
        "\u2022 \"How are you?\""
    )

    # Default — only STYLEORA questions
    return (
        "I can only answer questions about **STYLEORA** \u2014 our products, orders, "
        "shipping, payments, and fashion advice. Here's what I can help with:\n\n"
        "\U0001f6cd\ufe0f **Products** \u2014 \"Show me handbags\" or \"Tell me about diamond studs\"\n"
        "\U0001f4cb **Orders** \u2014 \"Track my order\", \"Return policy\"\n"
        "\U0001f69a **Shipping** \u2014 \"Shipping details\", \"Delivery time\"\n"
        "\U0001f4b3 **Payments** \u2014 \"Payment methods\"\n"
        "\U0001f4a1 **Fashion Advice** \u2014 \"What to wear for a wedding?\"\n"
        "\U0001f4b0 **Pricing & Discounts** \u2014 \"How much are perfumes?\", \"Discounted products\"\n"
        "\U0001f3c6 **Top Selling** \u2014 \"Best products\", \"Top selling items\"\n"
        "\U0001f4d6 **How to Order** \u2014 \"How do I buy?\"\n"
        "\U0001f4ca **Full Catalog** \u2014 \"List all products\"\n\n"
        "If your question isn't about STYLEORA, I won't be able to answer it."
    )


def handle_product_query(message, message_lower, silent=False):
    category_ref = intent_utils.detect_category_reference(message)
    query = intent_utils.extract_product_query(message)

    # ── Product detail request ──
    if any(w in message_lower for w in ['detail', 'tell me about', 'about the', 'info on', 'describe']):
        if query:
            product = store_utils.get_product_by_name(query)
            if product:
                return store_utils.format_product_detail(product)

    # ── Search by category ──
    if category_ref:
        products_by_cat = store_utils.get_products_by_category(category_ref)
        if products_by_cat:
            for cat_name, items in products_by_cat.items():
                if cat_name.lower() == category_ref.lower():
                    lines = [f"Here are our available **{cat_name}**:\n"]
                    lines.extend(f"\u2022 {item}" for item in items)
                    lines.append(f"\nBrowse all {cat_name.lower()} at our store. Want details on any specific item?")
                    return '\n'.join(lines)

    # ── Browse all categories (detailed) — check before query search ──
    if any(w in message_lower for w in ['list all', 'every', 'all products', 'full catalog',
                                         'complete', 'full list', 'all items',
                                         'what products', 'what items',
                                         'products are listed', 'items are listed',
                                         'this store']):
        products_by_cat = store_utils.get_all_products_by_category()
        if products_by_cat:
            lines = ["**Complete STYLEORA Catalog**\n"]
            total = 0
            for cat_name, items in products_by_cat.items():
                lines.append(f"\n\u25b6 **{cat_name}** ({len(items)} items)")
                for item in items:
                    lines.append(f"   \u2022 {item}")
                total += len(items)
            lines.append(f"\n**Total: {total} products across {len(products_by_cat)} categories**")
            lines.append("\nWant details on any specific product? Just ask!")
            return '\n'.join(lines)

    # ── Search by query ──
    if query:
        # First check for special filters
        if any(w in message_lower for w in ['trending', 'featured', 'popular', 'hot', 'new']):
            products = store_utils.search_products(limit=6)
            trending = [p for p in products if p.is_trending]
            featured = [p for p in products if p.is_featured]
            if trending or featured:
                lines = []
                if trending:
                    lines.append("\U0001f525 **Trending Now:**")
                    lines.extend(f"\u2022 {store_utils.format_product_brief(p)}" for p in trending[:4])
                if featured:
                    lines.append("\n\u2b50 **Featured Products:**")
                    lines.extend(f"\u2022 {store_utils.format_product_brief(p)}" for p in featured[:4])
                return '\n'.join(lines)

        # Then try normal search
        products = store_utils.search_products(query)
        if products:
            lines = [f"Here's what I found for \"{query}\":\n"]
            for p in products:
                lines.append(f"\u2022 {store_utils.format_product_brief(p)}")
            lines.append("\nWould you like more details on any of these?")
            return '\n'.join(lines)

    # ─️ Trending / Featured (no query) ──
    if any(w in message_lower for w in ['trending', 'featured', 'popular', 'hot', 'new']):
        all_products = Product.objects.filter(is_available=True).order_by('-is_trending', '-is_featured')[:6]
        trending = [p for p in all_products if p.is_trending]
        featured = [p for p in all_products if p.is_featured]
        if trending or featured:
            lines = []
            if trending:
                lines.append("\U0001f525 **Trending Now:**")
                lines.extend(f"\u2022 {store_utils.format_product_brief(p)}" for p in trending[:4])
            if featured:
                lines.append("\n\u2b50 **Featured Products:**")
                lines.extend(f"\u2022 {store_utils.format_product_brief(p)}" for p in featured[:4])
            return '\n'.join(lines)

    # ── Browse all categories ──
    if any(w in message_lower for w in ['show all', 'browse all', 'what do you have', 'what do you sell',
                                         'categories', 'all categories', 'what categories']):
        cats = store_utils.get_categories()
        if cats:
            lines = ["Here are our collections:\n"]
            for cat in cats:
                count = cat.products.filter(is_available=True).count()
                lines.append(f"\u2022 **{cat.name}** ({count} items)")
            lines.append("\nWhich category interests you?")
            return '\n'.join(lines)

    # Don't show all categories by default — return None to let fallback handle it
    return None
