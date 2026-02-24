"""
Utility functions for the Price Comparison Application
"""
import logging
import re
from datetime import datetime
from config import LOG_FILE, LOG_LEVEL

# Setup logging
def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)

def clean_price(price_string):
    """
    Extract price from string and convert to float
    Args:
        price_string: Price string (e.g., "₹1,299.99" or "$1,299.99")
    Returns:
        float: Cleaned price value
    """
    try:
        price_str = str(price_string).strip()
        
        # Handle concatenated prices like "64900₹64900" - take first occurrence
        # Split by currency symbols to get individual price parts
        parts = re.split(r'[₹$€£]', price_str)
        
        # Get the first non-empty part that looks like a price
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Remove commas and spaces
            cleaned = part.replace(',', '').replace(' ', '')
            
            # Check if it's a valid number
            if cleaned and cleaned.replace('.', '').isdigit():
                price = float(cleaned)
                
                # Validate price is reasonable (between ₹100 and ₹100,000,000)
                if 100 <= price <= 100000000:
                    return price
        
        # If no valid price found, try more aggressive cleaning
        cleaned = re.sub(r'[₹$€£\s,]', '', price_str)
        if cleaned:
            price = float(cleaned)
            if 100 <= price <= 100000000:
                return price
                
        return None
    except (ValueError, AttributeError) as e:
        logger.warning(f"Could not parse price: {price_string}")
        return None

def clean_rating(rating_string):
    """
    Extract rating from string and convert to float
    Args:
        rating_string: Rating string (e.g., "4.5 out of 5" or "4.5★")
    Returns:
        float: Cleaned rating value
    """
    try:
        # Extract first number found
        match = re.search(r'\d+\.?\d*', str(rating_string).strip())
        if match:
            return float(match.group())
        return None
    except (ValueError, AttributeError):
        logger.warning(f"Could not parse rating: {rating_string}")
        return None

def clean_reviews(review_string):
    """
    Extract number of reviews from string
    Args:
        review_string: Review count string (e.g., "1,245 reviews" or "1.2K")
    Returns:
        int: Number of reviews
    """
    try:
        # Remove text and commas
        cleaned = re.sub(r'[^\d.K]', '', str(review_string).strip().upper())
        
        if 'K' in cleaned:
            return int(float(cleaned.replace('K', '')) * 1000)
        return int(float(cleaned))
    except (ValueError, AttributeError):
        logger.warning(f"Could not parse reviews: {review_string}")
        return 0

def get_timestamp():
    """Get current timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def extract_product_variant(product_name):
    """
    Extract color/variant from product name
    Args:
        product_name: Full product name
    Returns:
        tuple: (base_name, color/variant)
    """
    # Pattern 1: Amazon format "Product - Color" (after dash)
    dash_match = re.search(r'\s*-\s*([A-Za-z\s]+)$', product_name)
    if dash_match:
        color = dash_match.group(1).strip()
        if color and len(color) > 1:  # Avoid single letters
            return (product_name[:dash_match.start()].strip(), color)
    
    # Pattern 2: Flipkart format "Product (Color, GB)"
    paren_match = re.search(r'\(([A-Za-z]+)(?:,|\))', product_name)
    if paren_match:
        color = paren_match.group(1).strip()
        # Check if this is actually a color, not "GB" or other specs
        if color.lower() not in ['gb', 'mb', 'ram', 'storage']:
            base_name = product_name[:paren_match.start()].strip()
            return (base_name, color)
    
    return (product_name, "")

def extract_product_details(product_name):
    """
    Extract comprehensive product details from product name
    Args:
        product_name: Full product name
    Returns:
        tuple: (base_name, color, storage, size, weight, dimensions, brand)
    """
    color = ""
    storage = ""
    size = ""
    weight = ""
    dimensions = ""
    brand = ""
    base_name = product_name
    original_name = product_name
    
    # Extract brand (first significant word)
    words = [w for w in product_name.split() if len(w) > 2]
    if words:
        brand = words[0]
    
    # Try to extract a "core product name" - usually the first 1-4 words that make sense
    # E.g., "Apple iPhone 17 Pro" or "iPhone 17 Pro" - but NOT the full description
    # Strategy: Look for the first colon or detailed specification info
    core_product_end = len(product_name)
    
    # Look for patterns that indicate detailed specs starting:
    # "Product Name 256 GB: Description" -> take "Product Name 256 GB" as base
    # But for Flipkart format "Product (Color, Storage)" we want everything before the first paren
    
    # First, check for Flipkart-style parenthetical info (has priority)
    paren_idx = product_name.find('(')
    colon_idx = product_name.find(': ')
    semicolon_idx = product_name.find('; ')
    
    # Take the earliest "end marker"
    potential_ends = [idx for idx in [paren_idx, colon_idx, semicolon_idx] if idx > 15]  # Need at least 15 chars
    if potential_ends:
        core_product_end = min(potential_ends)
    
    potential_base = product_name[:core_product_end].strip()
    # Make sure the base name is reasonable (not too short, not too long)
    if 10 < len(potential_base) < len(product_name) * 0.4:
        base_name = potential_base
    else:
        # Fallback: just take first few words with the storage info
        words_to_take = min(6, len(words))
        base_name = ' '.join(words[:words_to_take])
    
    # Extract storage FIRST (e.g., "256 GB", "128GB")
    storage_match = re.search(r'(\d+)\s*GB', product_name, re.IGNORECASE)
    if storage_match:
        storage = storage_match.group(1)
    
    # Define comprehensive color name list - single and multi-word colors
    COLOR_WORDS = [
        # Multi-word colors (check these first)
        r'Cosmic Orange', r'Deep Blue', r'Space Black', r'Midnight Black', r'Sierra Blue',
        r'Desert Titanium', r'Natural Titanium', r'Blue Titanium', r'Black Titanium',
        r'White Titanium', r'Pacific Blue', r'Alpine Green', r'Gold Titanium',
        r'Silver Titanium', r'Dark Purple', r'Light Purple', r'Forest Green',
        r'Ocean Blue', r'Sky Blue', r'Phantom Black', r'Phantom White',
        r'Phantom Silver', r'Midnight Green', r'Product Red', r'Starlight Blue',
        r'Starlight Green', r'Starlight Black', r'Starlight White', r'Glacier White',
        r'Pearl White', r'Pearl Black', r'Marble White', r'Marble Black',
        r'Space Gray', r'Space Grey',
        # Single-word colors
        r'Black', r'White', r'Silver', r'Gold', r'Red', r'Blue', r'Green',
        r'Purple', r'Pink', r'Orange', r'Yellow', r'Brown', r'Grey', r'Gray',
        r'Titanium', r'Rose', r'Pearl', r'Phantom', r'Midnight', r'Starlight',
        r'Glacier', r'Alpine', r'Pacific', r'Desert', r'Cosmic', r'Space',
        r'Sierra', r'Green', r'Ebony', r'Ivory', r'Marble', r'Onyx',
    ]
    
    # Pattern 1: Amazon format "Product - Color Words" (after dash)
    # Captures everything after dash as potential color
    dash_match = re.search(r'\s*-\s*([A-Za-z\s0-9]+)$', product_name)
    if dash_match:
        potential_color = dash_match.group(1).strip()
        # Only accept if it doesn't look like specs (GB, MP, etc)
        if not re.search(r'^\d+\s*(?:GB|MP|RAM)', potential_color, re.IGNORECASE):
            color = potential_color
            base_name = product_name[:dash_match.start()].strip()
    
    # Pattern 2: Flipkart format "Product (Color Words, GB)" or "Product (Color Words)"
    # This pattern extracts the first parenthetical content as color
    if not color:  # Only if we haven't found color yet
        paren_match = re.search(r'\(([A-Za-z\s0-9]+)(?:,|\))', product_name)
        if paren_match:
            potential_color = paren_match.group(1).strip()
            # Filter out technical specs that aren't colors
            non_color_specs = ['gb', 'mb', 'ram', 'storage', 'rom', 'processor', 'chip', 'inches']
            is_spec = any(spec in potential_color.lower() for spec in non_color_specs)
            
            if not is_spec and potential_color and len(potential_color) > 1:
                color = potential_color
                base_name = product_name[:paren_match.start()].strip()
    
    # Pattern 3: Look for color in text like "iPhone 17 Pro Cosmic Orange 256GB"
    # Check for known color names in the product name
    if not color:
        # Build regex pattern from all known colors (longest first to match multi-word colors first)
        sorted_colors = sorted(COLOR_WORDS, key=len, reverse=True)
        color_pattern = '|'.join(sorted_colors)
        color_match = re.search(color_pattern, product_name, re.IGNORECASE)
        if color_match:
            color = color_match.group(0).strip()
            # Normalize capitalization
            color = ' '.join(word.capitalize() for word in color.split())
            # IMPORTANT: Update base_name to remove the color from it
            base_name = (product_name[:color_match.start()] + ' ' + product_name[color_match.end():]).strip()
            # Clean up any double spaces or semicolons at boundaries
            base_name = re.sub(r'\s+', ' ', base_name.replace(';', ' ')).strip()
    
    # Extract weight (e.g., "50g", "1.5 oz", "100ml")
    weight_patterns = [
        r'(\d+\.?\d*)\s*(?:g|gm|gram)',
        r'(\d+\.?\d*)\s*(?:oz|ounce)',
        r'(\d+\.?\d*)\s*(?:ml|litre|liter)',
    ]
    for pattern in weight_patterns:
        weight_match = re.search(pattern, product_name, re.IGNORECASE)
        if weight_match:
            weight = weight_match.group(0).strip()
            break
    
    # Extract package size
    size_patterns = [
        r'(\d+\.?\d*)\s*(?:oz|ounces)',
        r'(\d+\.?\d*)\s*(?:g|ml)',
    ]
    for pattern in size_patterns:
        size_match = re.search(pattern, product_name, re.IGNORECASE)
        if size_match:
            size = size_match.group(1)
            break
    
    # Extract dimensions (e.g., "10x20x5 cm")
    dimensions_match = re.search(r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*(?:cm|mm|in|inch)', product_name, re.IGNORECASE)
    if dimensions_match:
        dimensions = f"{dimensions_match.group(1)}x{dimensions_match.group(2)}x{dimensions_match.group(3)}"
    
    return (base_name, color, storage, size, weight, dimensions, brand)

def detect_product_category(product_name):
    """
    Detect product category to avoid mismatches (e.g., phone vs phone cover)
    Args:
        product_name: Product name to analyze
    Returns:
        str: Category type (phone, cover, case, screen_protector, etc.)
    """
    name_lower = product_name.lower()
    
    # Phone accessories (should NOT match with phones)
    if any(word in name_lower for word in ['cover', 'case', 'flip case', 'back cover', 'protective case', 'bumper']):
        return 'phone_case'
    
    if any(word in name_lower for word in ['tempered glass', 'screen protector', 'glass protector']):
        return 'screen_protector'
    
    if any(word in name_lower for word in ['charger', 'charging cable', 'usb cable', 'adapter']):
        return 'accessory'
    
    # Phones/Devices
    if any(word in name_lower for word in ['smartphone', 'mobile phone', 'mobile', 'phone', 'android']):
        # Check if it's a phone vs phone case/cover
        if any(word in name_lower for word in ['cover', 'case', 'flip', 'back']):
            return 'phone_case'
        return 'phone'
    
    # Cosmetics/Skincare
    if any(word in name_lower for word in ['ointment', 'cream', 'lotion', 'serum', 'moisturizer', 'sunscreen']):
        return 'skincare'
    
    # Electronics/Tablets
    if any(word in name_lower for word in ['tablet', 'ipad', 'laptop', 'monitor', 'tv']):
        return 'electronics'
    
    return 'general'

def find_matching_product_list(product_list, target_base_name, target_color, target_storage="", target_size=""):
    """
    Find best matching product from list by storage, color, and size
    Args:
        product_list: List of product dictionaries
        target_base_name: Target product base name
        target_color: Target color
        target_storage: Target storage (optional but REQUIRED for phones/laptops)
        target_size: Target package size (optional)
    Returns:
        dict: Best matching product or None if no acceptable match found
    """
    if not product_list:
        return None
    
    # Strategy 1: For products with storage (phones, laptops), REQUIRE exact storage match
    if target_storage:
        storage_matches = []
        for product in product_list:
            base_name, color, storage, size = extract_product_details(product['product_name'])
            # MUST have matching storage
            if storage and storage == target_storage:
                # Also check color if available
                if target_color and color.lower() == target_color.lower():
                    return product  # Perfect match: storage + color
                storage_matches.append(product)
        
        # If we found storage matches but no color match, still prefer them
        if storage_matches:
            return storage_matches[0]
    
    # Strategy 2: Try exact color and storage match (fallback if no storage specified)
    for product in product_list:
        base_name, color, storage, size = extract_product_details(product['product_name'])
        if color.lower() == target_color.lower():
            if target_storage and storage == target_storage:
                return product
            elif not target_storage:
                return product
    
    # Strategy 3: Try color match only (only if no storage mismatches)
    for product in product_list:
        base_name, color, storage, size = extract_product_details(product['product_name'])
        if color.lower() == target_color.lower():
            # Don't return if storage differs significantly
            if target_storage and storage and storage != target_storage:
                continue
            return product
    
    # Strategy 4: If no match found and target_storage specified, return None (don't match wrong storage)
    if target_storage:
        return None
    
    # Strategy 5: Try matching by size if available (for products like moisturizers)
    if target_size:
        for product in product_list:
            base_name, color, storage, size = extract_product_details(product['product_name'])
            if size and abs(float(size) - float(target_size)) < 0.5:
                return product
    
    # No acceptable match found
    return None

def compare_products(amazon_data, flipkart_data):
    """
    Compare products from both platforms
    Args:
        amazon_data: Product data from Amazon
        flipkart_data: Product data from Flipkart
    Returns:
        dict: Comparison results and recommendation
    """
    recommendation = {
        'cheaper_platform': None,
        'cheaper_by_percentage': 0,
        'better_rating_platform': None,
        'better_reviews_platform': None,
        'recommendation': None,
        'reason': []
    }
    
    # Compare prices
    if amazon_data['price'] and flipkart_data['price']:
        if amazon_data['price'] < flipkart_data['price']:
            diff = flipkart_data['price'] - amazon_data['price']
            percentage = (diff / flipkart_data['price']) * 100
            recommendation['cheaper_platform'] = 'Amazon'
            recommendation['cheaper_by_percentage'] = round(percentage, 2)
        elif flipkart_data['price'] < amazon_data['price']:
            diff = amazon_data['price'] - flipkart_data['price']
            percentage = (diff / amazon_data['price']) * 100
            recommendation['cheaper_platform'] = 'Flipkart'
            recommendation['cheaper_by_percentage'] = round(percentage, 2)
    
    # Compare ratings
    amazon_rating = amazon_data['rating'] or 0
    flipkart_rating = flipkart_data['rating'] or 0
    
    if amazon_rating > flipkart_rating:
        recommendation['better_rating_platform'] = 'Amazon'
    elif flipkart_rating > amazon_rating:
        recommendation['better_rating_platform'] = 'Flipkart'
    
    # Compare reviews
    amazon_reviews = amazon_data['review_count'] or 0
    flipkart_reviews = flipkart_data['review_count'] or 0
    
    if amazon_reviews > flipkart_reviews:
        recommendation['better_reviews_platform'] = 'Amazon'
    elif flipkart_reviews > amazon_reviews:
        recommendation['better_reviews_platform'] = 'Flipkart'
    
    # Generate recommendation
    score_amazon = 0
    score_flipkart = 0
    
    if recommendation['cheaper_platform'] == 'Amazon':
        score_amazon += 2
    elif recommendation['cheaper_platform'] == 'Flipkart':
        score_flipkart += 2
    
    if recommendation['better_rating_platform'] == 'Amazon':
        score_amazon += 1
    elif recommendation['better_rating_platform'] == 'Flipkart':
        score_flipkart += 1
    
    if recommendation['better_reviews_platform'] == 'Amazon':
        score_amazon += 1
    elif recommendation['better_reviews_platform'] == 'Flipkart':
        score_flipkart += 1
    
    if score_amazon > score_flipkart:
        recommendation['recommendation'] = 'Amazon'
    elif score_flipkart > score_amazon:
        recommendation['recommendation'] = 'Flipkart'
    else:
        recommendation['recommendation'] = 'Both (Similar Quality)'
    
    return recommendation
