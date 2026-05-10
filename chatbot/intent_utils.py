import re
from .store_utils import get_categories, get_all_brands

CATEGORY_NAMES = set()
BRAND_NAMES = set()

INTENT_PATTERNS = {
    'greeting': [
        r'\bhi\b', r'\bhello\b', r'\bhey\b', r'\bhi\s+there\b', r'\bhello\s+there\b',
        r'\bgood\s+morning\b', r'\bgood\s+evening\b', r'\bgood\s+afternoon\b',
        r'\bassalam-o-alaikum\b', r'\bhi\s+styleora\b', r'\bhello\s+styleora\b',
        r'\bhey\s+styleora\b', r'\bhowdy\b', r'\bgreetings\b',
        r'\bhow\s+are\s+you\b', r'\bhow\s+do\s+you\s+do\b', r'\bhow\s+have\s+you\s+been\b',
        r'\bwasup\b', r'\bwhats\s+up\b', r'\bsup\b', r'\bhow\s+are\s+things?\b',
        r'\bhow\s+goes\s+it\b',
    ],
    'farewell': [
        r'\bbye\b', r'\bgoodbye\b', r'\bsee\s+you\b', r'\btake\s+care\b',
        r'\bkhuda\s+hafiz\b',
    ],
    'thanks': [
        r'\bthank\w*\b', r'\bthx\b', r'\bthanks\s+a\s+lot\b', r'\bmuch\s+appreciated\b',
    ],
    'product_search': [
        r'\bshow\b', r'\bfind\b', r'\blooking\s+for\b', r'\bi\s+want\b',
        r'\brecommend\b', r'\bsuggest\b', r'\bgot\s+any\b',
        r'\bdisplay\b', r'\blist\b', r'\bbrowse\b', r'\bproducts?\b',
        r'\bgifts?\b', r'\bfor\s+(her|him|wife|husband|friend|mom|dad)\b',
        r'\bwhat\s+products?\b', r'\bwhat\s+items?\b', r'\bwhat\s+categories?\b',
    ],
    'product_detail': [
        r'\btell\s+me\s+about\b', r'\bdetails?\b', r'\binfo\b', r'\binformation\b',
        r'\bdescribe\b', r'\bwhat\s+is\b', r'\bwhat\s+are\b',
        r'\bmore\s+about\b', r'\babout\s+the\b',
    ],
    'order_status': [
        r'\btrack\b', r'\border\s+status\b', r'\bwhere\s+is\s+my\b',
        r'\bmy\s+order\b', r'\border\s+#?\d', r'\bstatus\s+of\s+order\b',
        r'\bcheck\s+(my\s+)?order\b',
    ],
    'order_number': [
        r'\border\s+#?\d+', r'\b#?\d{4,}\b',
    ],
    'fashion_advice': [
        r'\bwhat\s+(should|do)\s+i\s+wear\b', r'\bfashion\b', r'\bstyle\b',
        r'\boutfit\b', r'\boccasion\b', r'\bdress\b', r'\bstyling\b',
        r'\bwhat\s+goes\b', r'\bmatch(es|ing)?\b',
        r'\bwhat\s+to\s+wear\b', r'\blook\s+good\b',
    ],
    'price_inquiry': [
        r'\bhow\s+much\b', r'\bprices?\b', r'\bcost\b', r'\bwhats?.?\s+the\s+(price|cost)\b',
        r'\brate\b', r'\bexpensive\b', r'\bcheap\b', r'\baffordable\b', r'\bbudget\b',
        r'\bhow\s+many\s+(rupees|dollars)\b', r'\bunder\s+\d+\b',
        r'\brange\b', r'\bstarting\s+from\b', r'\bpricing\b',
    ],
    'return_policy': [
        r'\breturn\b', r'\brefund\b', r'\bexchange\b', r'\breplace\b',
        r'\breturn\s+policy\b', r'\bmoney\s+back\b',
    ],
    'shipping': [
        r'\bshipping\b', r'\bdelivery\b', r'\bdeliver\b', r'\bcourier\b',
        r'\bship\b', r'\bhow\s+long\b', r'\bwhen\s+will\b',
    ],
    'payment': [
        r'\bpayment\b', r'\bpay\b', r'\bcod\b', r'\bjazzcash\b',
        r'\beasypaisa\b', r'\bcredit\s+card\b', r'\bdebit\s+card\b',
    ],
    'discount': [
        r'\bdiscount\w*\b', r'\bcoupons?\b', r'\bpromo\b', r'\boffers?\b',
        r'\bsale\b', r'\bcodes?\b', r'\bvouchers?\b',
        r'\bany\s+discount\w*\b', r'\bany\s+coupons?\b', r'\bany\s+offers?\b',
        r'\bdiscount\s+codes?\b', r'\bpromo\s+codes?\b',
        r'\bon\s+sale\b', r'\bspecial\s+price\b', r'\block\s+prices?\b', r'\bdeals?\b',
    ],
    'warranty': [
        r'\bwarranty\b', r'\bguarantee\b', r'\bdefect\b', r'\bdamaged\b',
        r'\bbroken\b', r'\bfaulty\b',
    ],
    'contact': [
        r'\bcontact\b', r'\bsupport\b', r'\bphone\b', r'\bemail\b',
        r'\bcall\b', r'\bhelpline\b', r'\breach\b', r'\bcustomer\s+service\b',
    ],
    'about': [
        r'\babout\b', r'\bcompany\b', r'\bbrand\b', r'\bwho\s+are\s+you\b',
        r'\btell\s+me\s+about\s+(yourself|styleora|the\s+company)\b',
    ],
    'size_guide': [
        r'\bsize\b', r'\bfit\b', r'\bmeasurement\b', r'\bsizing\b',
        r'\bwhat\s+size\b', r'\bhow\s+to\s+measure\b',
    ],
    'help': [
        r'\bhelp\b', r'\bwhat\s+can\s+you\s+do\b', r'\bcapabilities?\b',
        r'\bhow\s+(can\s+)?(you\s+)?help\b', r'\bfeatures?\b',
        r'\bwhat\s+can\s+i\s+ask\b', r'\bcommands?\b', r'\bguide\b',
        r'\bi\s+need\s+help\b', r'\bcan\s+you\s+help\b',
    ],
    'negative': [
        r'\bno\b', r'\bnope\b', r'\bnah\b', r'\bnot\s+really\b',
        r'\bno\s+thanks?\b', r'\bno\s+thank\s+you\b', r'\bnothing\b',
        r'\bnot\s+now\b', r'\bnever\s+mind\b', r'\bleave\s+it\b',
        r'\bthats?\s+all\b', r'\bi\s+am\s+done\b', r'\bi\s+am\s+fine\b', r'\bi\s+am\s+ok\b',
    ],
    'brand_search': [
        r'\bfrom\s+\w+', r'\bby\s+\w+', r'\bbrand\b',
    ],
    'stock_check': [
        r'\bin\s+stock\b', r'\bavailable\b', r'\bstock\b',
        r'\bhow\s+many\b', r'\bquantity\b',
    ],
    'reviews': [
        r'\breviews?\b', r'\brating\b', r'\bratings\b', r'\bstars?\b',
        r'\bwhat\s+do\s+customers\s+say\b', r'\bfeedback\b',
        r'\btestimonial', r'\breviewed\b',
    ],
    'new_arrivals': [
        r'\bnew\b', r'\barrivals?\b', r'\bjust\s+in\b', r'\blatest\b',
        r'\brecently\s+added\b', r'\bwhats?\s+new\b',
    ],
    'compare': [
        r'\bcompare\b', r'\bvs\b', r'\bversus\b', r'\bdifference\b',
        r'\bwhich\s+is\s+(better|cheaper|best)\b',
        r'\bwould\s+you\s+recommend\b',
    ],
    'how_to_order': [
        r'\bhow\s+to\s+order\b', r'\bplace\s+an?\s+order\b', r'\border\s+(now|here)\b',
        r'\bbuy\s+(products?|items?|now)\b', r'\bpurchase\b', r'\bshopping\s+process\b',
        r'\bhow\s+can\s+i\s+buy\b', r'\bhow\s+do\s+i\s+order\b',
        r'\bshopping\s+guide\b', r'\bhow\s+to\s+buy\b', r'\bmake\s+an?\s+order\b',
        r'\bshopping\s+steps?\b', r'\bstep\w*\s+to\s+order\b',
    ],
    'top_selling': [
        r'\btop\s+sell\w+\b', r'\bbest\s+sell\w+\b', r'\bmost\s+popular\b',
        r'\bpopular\s+products?\b', r'\bmost\s+bought\b', r'\bmost\s+sold\b',
        r'\bcustomer\s+favou?rite\b', r'\bpeople\s+buy\b', r'\bwhats?\s+hot\b',
    ],
    'best_product': [
        r'\bbest\s+(product|item|pick|choice)\b', r'\btop\s+(rated?|quality)\b',
        r'\bwhat\s+should\s+i\s+buy\b', r'\brecommend\w*\s+(me\s+)?a\b',
        r'\bwhich\s+(product|item|one)\s+is\s+best\b', r'\bmust\s+have\b',
        r'\bworth\s+buying\b', r'\bwhats?\s+the\s+best\b',
        r'\btop\s+\d\b', r'\bgood\s+quality\b', r'\bhighly\s+recommend\b',
    ],
    'shipment_detail': [
        r'\bship\w+\s+(detail|info|time|cost|fee|charge|method)\b',
        r'\bdelivery\s+(detail|time|info|cost|fee|charge|method|process)\b',
        r'\btracking\b', r'\bhow\s+long\s+(does\s+)?(delivery|shipping)\b',
        r'\bwhen\s+will\s+(i\s+)?(get|receive)\b', r'\bshipping\s+to\b',
        r'\bwhere\s+do\s+you\s+ship\b', r'\bdo\s+you\s+ship\b',
    ],
}


def classify_intent(message):
    message_lower = message.lower().strip()
    scores = {}
    for intent, patterns in INTENT_PATTERNS.items():
        score = 0
        for p in patterns:
            if re.search(p, message_lower):
                score += 1
        if score > 0:
            scores[intent] = score

    urdu_chars = re.findall(r'[\u0600-\u06FF]', message)
    if len(urdu_chars) > 2:
        scores['urdu'] = scores.get('urdu', 0) + 3

    return scores


def get_primary_intent(scores):
    if not scores:
        return 'unknown'
    return max(scores, key=scores.get)


def extract_product_query(message):
    words = message.lower().split()
    stop_words = {'show', 'me', 'find', 'i', 'want', 'a', 'an', 'the', 'some',
                  'looking', 'for', 'tell', 'about', 'need', 'got', 'any',
                  'do', 'you', 'have', 'display', 'list', 'browse', 'search',
                  'recommend', 'suggest', 'please', 'can', 'could', 'would',
                  'buy', 'get', 'is', 'are', 'was', 'were', 'in', 'of', 'to',
                  'what', 'which', 'where', 'when', 'who', 'how', 'much',
                  'many', 'does', 'did', 'with', 'and', 'or', 'from', 'by',
                  'on', 'at', 'for', 'my', 'your', 'our', 'their', 'its',
                  'this', 'that', 'these', 'those', 'compare'}
    meaningful = [w for w in words if w not in stop_words and len(w) > 1]
    return ' '.join(meaningful)


def detect_category_reference(message):
    global CATEGORY_NAMES
    if not CATEGORY_NAMES:
        try:
            CATEGORY_NAMES.update(cat.name.lower() for cat in get_categories())
        except Exception:
            pass
    message_lower = message.lower()
    for cat_name in sorted(CATEGORY_NAMES, key=len, reverse=True):
        if cat_name in message_lower:
            return cat_name.title()
    singular_map = {
        'handbag': 'Handbags', 'hand bag': 'Handbags',
        'bangle': 'Bangles', 'perfume': 'Perfumes',
        'accessory': 'Accessories',
        'cosmetic': 'Cosmetics', 'nail paint': 'Nail Paints',
        'nail paints': 'Nail Paints',
        'jewel': 'Jewelry', 'jewellery': 'Jewelry',
        'lipstick': 'Cosmetics', 'foundation': 'Cosmetics',
        'sunglass': 'Accessories', 'wallet': 'Accessories',
        'necklace': 'Jewelry', 'earring': 'Jewelry',
        'bracelet': 'Accessories', 'ring': 'Accessories',
        'tote': 'Handbags', 'clutch': 'Handbags',
    }
    for word, cat_name in singular_map.items():
        if word in message_lower:
            return cat_name
    return None


def detect_brand_reference(message):
    global BRAND_NAMES
    if not BRAND_NAMES:
        try:
            BRAND_NAMES.update(b.lower() for b in get_all_brands())
        except Exception:
            pass
    message_lower = message.lower()
    for brand in BRAND_NAMES:
        if brand.lower() in message_lower:
            return brand.title()
    return None


def extract_compare_products(message):
    # Direct regex extraction
    match = re.search(r'compare\s+(.+?)\s+(?:vs|versus|and|or)\s+(.+)', message, re.IGNORECASE)
    if match:
        a = match.group(1).strip()
        b = match.group(2).strip()
        # Clean leading/trailing noise
        a = re.sub(r'^(?:compare|to|the|a|an)\s+', '', a, flags=re.IGNORECASE).strip()
        b = re.sub(r'^(?:compare|to|the|a|an)\s+', '', b, flags=re.IGNORECASE).strip()
        return a, b
    # Fallback: split on vs/and/or
    parts = re.split(r'\b(vs|versus|and|or)\b', message, flags=re.IGNORECASE)
    if len(parts) >= 3:
        a = extract_product_query(parts[0])
        b = extract_product_query(parts[2])
        if a and b:
            return a, b
    return None, None


def extract_order_number(message):
    match = re.search(r'#?(\d{4,})', message)
    if match:
        return match.group(1)
    return None
