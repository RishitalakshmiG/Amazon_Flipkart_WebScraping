"""
Main application module for Price Comparison
"""
import logging
import os
from database import Database
from amazon_scraper import AmazonScraper
from flipkart_scraper import FlipkartScraper
from excel_reporter import ExcelReporter
from product_matcher import filter_products
from utils import setup_logging, compare_products, extract_product_details, find_matching_product_list, detect_product_category

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

def normalize_product_name(name):
    """
    Normalize product name for comparison
    Args:
        name: Product name to normalize
    Returns:
        str: Normalized name (lowercase, trimmed)
    """
    return name.strip().lower()

def extract_numeric_value(value_str):
    """
    Extract numeric value from a string like '45 g', '45g', '45gm', '1.5 oz'
    Args:
        value_str: String containing number and unit
    Returns:
        tuple: (numeric_value, unit) or (None, None)
    """
    if not value_str:
        return None, None
    
    import re
    # Extract number and unit
    match = re.search(r'(\d+\.?\d*)\s*([a-z]+)', value_str.lower().strip())
    if match:
        numeric = float(match.group(1))
        unit = match.group(2)
        # Normalize units
        unit_map = {'g': 'g', 'gm': 'g', 'gram': 'g', 'oz': 'oz', 'ounce': 'oz', 'ml': 'ml', 'cc': 'ml'}
        normalized_unit = unit_map.get(unit, unit)
        return numeric, normalized_unit
    return None, None

def weights_match(weight1, weight2):
    """
    Check if two weight values match (numerically)
    Args:
        weight1: First weight string (e.g., '45 g')
        weight2: Second weight string (e.g., '45g')
    Returns:
        bool: True if weights match, False otherwise
    """
    if not weight1 or not weight2:
        return False
    
    num1, unit1 = extract_numeric_value(weight1)
    num2, unit2 = extract_numeric_value(weight2)
    
    if num1 is None or num2 is None:
        # Fallback to string comparison if parsing fails
        return weight1.lower() == weight2.lower()
    
    # Units must match
    if unit1 != unit2:
        return False
    
    # Numeric values must match (with tiny tolerance for floating point)
    return abs(num1 - num2) < 0.01

def calculate_name_similarity(name1, name2):
    """
    Calculate similarity between two product names using semantic matching
    Args:
        name1: First product name
        name2: Second product name
    Returns:
        tuple: (is_identical, similarity_score)
    """
    norm1 = normalize_product_name(name1)
    norm2 = normalize_product_name(name2)
    
    # First check: Are they exactly the same?
    if norm1 == norm2:
        logger.debug(f"  [EXACT MATCH] '{norm1}'")
        return True, 100
    
    # Split into meaningful words (exclude short words and common articles)
    common_words = {'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'from', '-', '–'}
    
    words1 = [w for w in norm1.split() if len(w) > 2 and w.lower() not in common_words]
    words2 = [w for w in norm2.split() if len(w) > 2 and w.lower() not in common_words]
    
    if not words1 or not words2:
        logger.debug(f"  [NO MATCH] Empty word list: {words1} vs {words2}")
        return False, 0
    
    # LENIENT HANDLING FOR INCOMPLETE PRODUCT NAMES
    # If one name has only 1-2 words (likely incomplete extraction), be more lenient
    short_name_threshold = 2
    if len(words1) <= short_name_threshold or len(words2) <= short_name_threshold:
        # If all keywords from short name are in long name, consider it a match
        shorter_words = words1 if len(words1) <= len(words2) else words2
        longer_words = words2 if len(words1) <= len(words2) else words1
        
        # Check if all words from shorter name exist in longer name
        overlap = sum(1 for word in shorter_words if word in longer_words)
        overlap_percentage = (overlap / len(shorter_words)) * 100 if shorter_words else 0
        
        if overlap_percentage >= 100:  # All words from short name must be in long name
            logger.debug(f"  [LENIENT MATCH] Short name match: {overlap_percentage:.0f}%")
            return False, 75  # Not identical, but good match
        else:
            logger.debug(f"  [LENIENT MISMATCH] Short name only {overlap_percentage:.0f}% overlap")
            return False, overlap_percentage
    
    # Both lists should have similar length (within 30% for better compatibility)
    length_diff = abs(len(words1) - len(words2))
    max_len = max(len(words1), len(words2))
    
    # Calculate overlap
    overlap = sum(1 for word in words1 if word in words2)
    overlap_percentage = (overlap / max_len) * 100 if max_len > 0 else 0
    
    # More lenient: require 70%+ overlap instead of 95%
    if overlap_percentage >= 70:
        logger.debug(f"  [SIMILARITY MATCH {overlap_percentage:.0f}%]")
        return False, overlap_percentage
    
    # Default: not a match
    logger.debug(f"  [SIMILARITY MISMATCH] Only {overlap_percentage:.0f}% overlap")
    return False, overlap_percentage

def rank_products_by_similarity(products, search_query):
    """
    Rank products by similarity to search query
    Args:
        products: List of products with 'product_name' key
        search_query: Search query string
    Returns:
        list: Products ranked by similarity score (highest first)
    """
    search_keywords = set(search_query.lower().split())
    ranked = []
    
    for prod in products:
        name = prod['product_name'].lower()
        prod_keywords = set(name.split())
        
        # Calculate similarity: how many search keywords are in product name
        matching_keywords = len(search_keywords & prod_keywords)
        similarity_score = (matching_keywords / len(search_keywords)) * 100 if search_keywords else 0
        
        ranked.append({
            'product': prod,
            'similarity_score': similarity_score,
            'matching_keywords': matching_keywords
        })
    
    # Sort by similarity score (highest first)
    ranked.sort(key=lambda x: x['similarity_score'], reverse=True)
    return ranked

def display_top_products(amazon_ranked, flipkart_ranked, search_query):
    """
    Display top 10 products from each site and allow user to select
    Args:
        amazon_ranked: Ranked Amazon products
        flipkart_ranked: Ranked Flipkart products
        search_query: Original search query
    Returns:
        None
    """
    print("\n" + "="*100)
    print(f"TOP MATCHING PRODUCTS FOR: '{search_query}'")
    print("="*100)
    
    print("\nAMAZON (Top 10):")
    print("-" * 100)
    for i, item in enumerate(amazon_ranked[:10], 1):
        prod = item['product']
        score = item['similarity_score']
        print(f"{i}. [{score:.0f}%] {prod['product_name'][:85]}")
        print(f"   Price: ₹{prod.get('price', 'N/A')}")
    
    print("\nFLIPKART (Top 10):")
    print("-" * 100)
    for i, item in enumerate(flipkart_ranked[:10], 1):
        prod = item['product']
        score = item['similarity_score']
        print(f"{i}. [{score:.0f}%] {prod['product_name'][:85]}")
        print(f"   Price: ₹{prod.get('price', 'N/A')}")
    
    print("\n" + "="*100)
    print("WARNING - The search is VAGUE - please select matching products:")
    print("  - Example: 'portronics earphones' matches 5+ different models")
    print("  - Try: 'portronics conch theta' for specific model")
    print("="*100 + "\n")

def find_best_matching_pair(amazon_results, flipkart_results, search_query=None):
    """
    Find the best matching product pair by semantic similarity
    
    MATCHING CRITERIA (in order of importance):
    1. Category must match (e.g., phone vs phone)
    2. Brand must match exactly
    3. Base model/name must be >= 70% similar
    4. STORAGE CAPACITY MUST MATCH EXACTLY (if present in both)
    5. COLOR MUST MATCH EXACTLY (if present in both)
    6. Size/Weight/Dimensions should match if specified
    
    This ensures we compare "iPhone 17 Pro 256GB Cosmic Orange" with 
    "Apple iPhone 17 Pro (Cosmic Orange, 256GB)" and NOT with 
    "Apple iPhone 17 Pro (Deep Blue, 256GB)"
    
    Args:
        amazon_results: List of Amazon products
        flipkart_results: List of Flipkart products
        search_query: Original search query (for ranking)
    Returns:
        tuple: (amazon_product, flipkart_product, match_quality)
    """
    if not amazon_results or not flipkart_results:
        return None, None, "no_results"
    
    # Rank products by similarity to search query
    if search_query:
        amazon_ranked = rank_products_by_similarity(amazon_results, search_query)
        flipkart_ranked = rank_products_by_similarity(flipkart_results, search_query)
    else:
        amazon_ranked = [{'product': p, 'similarity_score': 100} for p in amazon_results]
        flipkart_ranked = [{'product': p, 'similarity_score': 100} for p in flipkart_results]
    
    best_match = None
    best_score = 0
    best_name_similarity = 0
    best_spec_match_details = {}
    match_quality = "no_match"
    
    logger.info(f"\n{'='*70}")
    logger.info(f"SEMANTIC PRODUCT MATCHING")
    logger.info(f"{'='*70}")
    logger.info(f"Matching {len(amazon_results)} Amazon vs {len(flipkart_results)} Flipkart products")
    logger.info(f"Search Query: {search_query}")
    logger.info(f"{'='*70}\n")
    
    # Try to find matches
    for amazon_item in amazon_ranked:
        amazon_prod = amazon_item['product']
        amazon_base, amazon_color, amazon_storage, amazon_size, amazon_weight, amazon_dims, amazon_brand = extract_product_details(amazon_prod['product_name'])
        amazon_category = detect_product_category(amazon_prod['product_name'])
        
        # DEBUG: Log extracted details
        logger.debug(f"\nAmazon product analysis:")
        logger.debug(f"  Name: {amazon_prod['product_name'][:80]}")
        logger.debug(f"  Extracted - Brand: {amazon_brand}, Color: '{amazon_color}', Storage: {amazon_storage}GB, Category: {amazon_category}")
        
        for flipkart_item in flipkart_ranked:
            flipkart_prod = flipkart_item['product']
            flipkart_base, flipkart_color, flipkart_storage, flipkart_size, flipkart_weight, flipkart_dims, flipkart_brand = extract_product_details(flipkart_prod['product_name'])
            flipkart_category = detect_product_category(flipkart_prod['product_name'])
            
            # DEBUG: Log extracted details
            logger.debug(f"  Flipkart product analysis:")
            logger.debug(f"    Name: {flipkart_prod['product_name'][:80]}")
            logger.debug(f"    Extracted - Brand: {flipkart_brand}, Color: '{flipkart_color}', Storage: {flipkart_storage}GB, Category: {flipkart_category}")
            
            match_score = 0
            rejection_reason = None
            match_details = {
                'category_match': False,
                'brand_match': False,
                'name_similarity': 0,
                'storage_match': False,
                'color_match': False,
                'size_match': False,
                'weight_match': False,
            }
            
            # ===== STEP 0: PRODUCT CATEGORY MUST BE COMPATIBLE =====
            if amazon_category != flipkart_category:
                if amazon_category != 'general' and flipkart_category != 'general':
                    rejection_reason = f"Category mismatch: {amazon_category} vs {flipkart_category}"
                    continue
            match_details['category_match'] = True
            match_score += 5
            
            # ===== STEP 1: BRAND MUST MATCH =====
            if amazon_brand.lower() != flipkart_brand.lower():
                rejection_reason = f"Brand mismatch: {amazon_brand} vs {flipkart_brand}"
                continue
            match_details['brand_match'] = True
            match_score += 20
            logger.debug(f"✓ Brand match: {amazon_brand}")
            
            # ===== STEP 2: BASE NAME SIMILARITY (must be >= 70%) =====
            is_identical, similarity = calculate_name_similarity(amazon_base, flipkart_base)
            match_details['name_similarity'] = similarity
            
            # Accept match if similarity is 70% or higher (lenient for incomplete product names)
            if similarity < 70:
                rejection_reason = f"Name similarity too low: {similarity:.0f}% (required: 70%)"
                continue
            
            match_score += (similarity / 5)  # Max 20 points
            logger.debug(f"✓ Name similarity: {similarity:.0f}%")
            
            # ===== STEP 2.5: PRODUCT VARIANT CHECK - Ensure same product variants =====
            # Key variant descriptors that distinguish different product models
            variant_keywords = {
                'matte_type': ['matte lock', 'very matte', 'ultra matte', 'matte finish', 'semi-matte'],
                'phone_size': ['pro', 'max', 'mini', 'plus', 'ultra'],
                'material': ['titanium', 'stainless', 'aluminum', 'ceramic'],
            }
            
            # Extract variants from both product names
            amazon_lower = amazon_base.lower()
            flipkart_lower = flipkart_base.lower()
            
            variant_mismatch = False
            for category, keywords in variant_keywords.items():
                # Find which variant (if any) each product has
                amazon_variant = [kw for kw in keywords if kw in amazon_lower]
                flipkart_variant = [kw for kw in keywords if kw in flipkart_lower]
                
                # If both have variants, they must match
                if amazon_variant and flipkart_variant:
                    if amazon_variant != flipkart_variant:
                        # Different variants in same category - likely different products
                        rejection_reason = f"Product variant mismatch ({category}): {amazon_variant} vs {flipkart_variant}"
                        logger.debug(f"  [VARIANT MISMATCH] {rejection_reason}")
                        variant_mismatch = True
                        break
                # If one has a variant and the other doesn't (for key categories), also reject
                elif (amazon_variant or flipkart_variant) and category in ['phone_size', 'material']:
                    # One has variant, other doesn't - different products
                    rejection_reason = f"Product variant missing ({category}): {amazon_variant if amazon_variant else 'none'} vs {flipkart_variant if flipkart_variant else 'none'}"
                    logger.debug(f"  [VARIANT MISMATCH] {rejection_reason}")
                    variant_mismatch = True
                    break
            
            if variant_mismatch:
                continue
            
            # ===== STEP 3: STORAGE - MUST MATCH EXACTLY (IF BOTH HAVE IT) =====
            # Only enforce storage matching if BOTH products have storage extracted from their names
            # If only one has storage info in the name, that's OK - products may not include it in the title
            if amazon_storage and flipkart_storage:
                # Both have storage extracted - must match exactly
                if amazon_storage != flipkart_storage:
                    rejection_reason = f"Storage capacity mismatch: {amazon_storage}GB vs {flipkart_storage}GB"
                    continue
                
                match_details['storage_match'] = True
                match_score += 25  # High priority
                logger.debug(f"✓ Storage match: {amazon_storage}GB")
            elif amazon_storage or flipkart_storage:
                # Only one has storage in the name - this is not a rejection, just note it
                logger.debug(f"⚠ Only one product has storage in name (A:{amazon_storage}, F:{flipkart_storage})")
            
            # ===== STEP 4: COLOR - MUST MATCH EXACTLY (CRITICAL) =====
            if amazon_color or flipkart_color:
                # Normalize color comparison
                amazon_color_norm = amazon_color.strip().lower() if amazon_color else ""
                flipkart_color_norm = flipkart_color.strip().lower() if flipkart_color else ""
                
                # If one has color, both should have color for proper matching
                if amazon_color_norm and flipkart_color_norm:
                    # Both have colors - must match exactly
                    if amazon_color_norm != flipkart_color_norm:
                        rejection_reason = f"Color mismatch: '{amazon_color}' vs '{flipkart_color}'"
                        continue
                    match_details['color_match'] = True
                    match_score += 20  # High priority
                    logger.debug(f"✓ Color match: {amazon_color}")
                elif amazon_color_norm or flipkart_color_norm:
                    # Only one has color extracted - this is a mismatch
                    rejection_reason = f"Color availability mismatch: A has '{amazon_color}', F has '{flipkart_color}'"
                    continue
            
            # ===== STEP 5: SIZE - SHOULD MATCH (for cosmetics/packages) =====
            if amazon_size or flipkart_size:
                if amazon_size and flipkart_size:
                    try:
                        if float(amazon_size) == float(flipkart_size):
                            match_details['size_match'] = True
                            match_score += 10
                            logger.debug(f"✓ Size match: {amazon_size}")
                        else:
                            logger.debug(f"⚠ Size mismatch: {amazon_size} vs {flipkart_size} (not critical for this match)")
                    except (ValueError, TypeError):
                        logger.debug(f"⚠ Could not compare sizes: {amazon_size} vs {flipkart_size}")
            
            # ===== STEP 6: WEIGHT - SHOULD MATCH (for cosmetics) =====
            if amazon_weight or flipkart_weight:
                if amazon_weight and flipkart_weight:
                    if weights_match(amazon_weight, flipkart_weight):
                        match_details['weight_match'] = True
                        match_score += 10
                        logger.debug(f"✓ Weight match: {amazon_weight}")
            
            # ===== EXCELLENT MATCH FOUND =====
            if match_score > best_score:
                best_score = match_score
                best_name_similarity = similarity
                best_match = (amazon_prod, flipkart_prod)
                best_spec_match_details = match_details
                
                logger.info(f"\n[BEST MATCH CANDIDATE] Score: {best_score:.1f}")
                logger.info(f"  Amazon:  {amazon_prod['product_name']}")
                logger.info(f"  Flipkart: {flipkart_prod['product_name']}")
                logger.info(f"  Details: {match_details}")
    
    logger.info(f"\n{'='*70}")
    if best_match:
        # Determine match quality based on criteria met
        criteria_met = sum([
            best_spec_match_details.get('brand_match', False),
            best_spec_match_details.get('storage_match', False),
            best_spec_match_details.get('color_match', False),
            best_spec_match_details.get('size_match', False),
        ])
        
        if (best_spec_match_details.get('storage_match') and 
            best_spec_match_details.get('color_match')):
            match_quality = "perfect"
        elif criteria_met >= 3 and best_name_similarity >= 80:
            match_quality = "excellent"
        elif criteria_met >= 2 and best_name_similarity >= 70:
            match_quality = "good"
        elif criteria_met >= 1 and best_name_similarity >= 60:
            match_quality = "partial"
        else:
            match_quality = "weak"
        
        logger.info(f"[FINAL RESULT] Match Quality: {match_quality.upper()} (Score: {best_score:.1f})")
        logger.info(f"  Amazon:  {best_match[0]['product_name']}")
        logger.info(f"  Flipkart: {best_match[1]['product_name']}")
        logger.info(f"{'='*70}\n")
        
        if best_name_similarity >= 50:
            return best_match[0], best_match[1], match_quality
    
    # No acceptable match found
    logger.warning(f"\n{'='*70}")
    logger.warning(f"NO PERFECT MATCH FOUND")
    logger.warning(f"Attempting intelligent fallback matching...")
    logger.warning(f"{'='*70}\n")
    
    if search_query:
        display_top_products(amazon_ranked, flipkart_ranked, search_query)
    
    # FALLBACK PRIORITY 1: COLOR + STORAGE match (most important)
    # Even if brand name extraction differs (iPhone vs Apple), match on these specs
    best_by_color_storage = None
    best_flipkart_by_color_storage = None
    
    for amazon_item in amazon_ranked:
        amazon_prod = amazon_item['product']
        amazon_base, amazon_color, amazon_storage, _, _, _, amazon_brand = extract_product_details(amazon_prod['product_name'])
        
        for flipkart_item in flipkart_ranked:
            flipkart_prod = flipkart_item['product']
            flipkart_base, flipkart_color, flipkart_storage, _, _, _, flipkart_brand = extract_product_details(flipkart_prod['product_name'])
            
            # Match by COLOR + STORAGE (ignoring brand extraction issues)
            base_name_match = calculate_name_similarity(amazon_base, flipkart_base)[1] >= 70
            
            amazon_color_norm = amazon_color.strip().lower() if amazon_color else ""
            flipkart_color_norm = flipkart_color.strip().lower() if flipkart_color else ""
            color_match = (amazon_color_norm and flipkart_color_norm and amazon_color_norm == flipkart_color_norm)
            
            storage_match = amazon_storage and flipkart_storage and amazon_storage == flipkart_storage
            
            # CRITICAL: Color + Storage match on same model
            if color_match and storage_match and base_name_match:
                best_by_color_storage = amazon_prod
                best_flipkart_by_color_storage = flipkart_prod
                
                logger.warning(f"\n✓ FALLBACK LEVEL 1: Color + Storage match found!")
                logger.warning(f"  Color: {amazon_color} | Storage: {amazon_storage}GB")
                logger.warning(f"  Amazon:  {best_by_color_storage['product_name'][:70]}")
                logger.warning(f"  Flipkart: {best_flipkart_by_color_storage['product_name'][:70]}\n")
                break
        
        if best_by_color_storage:
            break
    
    if best_by_color_storage and best_flipkart_by_color_storage:
        logger.warning(f"Using FALLBACK LEVEL 1 (color + storage match):")
        logger.warning(f"  Amazon: {best_by_color_storage['product_name'][:70]}")
        logger.warning(f"  Flipkart: {best_flipkart_by_color_storage['product_name'][:70]}")
        return best_by_color_storage, best_flipkart_by_color_storage, "color_storage_match"
    
    # SECOND FALLBACK: Try to find at least COLOR match (if storage doesn't match perfectly)
    # This is more intelligent - we check if products are the same MODEL, then match COLOR
    best_by_color_only = None
    best_by_color_only_flipkart = None
    
    for amazon_item in amazon_ranked:
        amazon_prod = amazon_item['product']
        amazon_base, amazon_color, amazon_storage, _, _, _, amazon_brand = extract_product_details(amazon_prod['product_name'])
        
        for flipkart_item in flipkart_ranked:
            flipkart_prod = flipkart_item['product']
            flipkart_base, flipkart_color, flipkart_storage, _, _, _, flipkart_brand = extract_product_details(flipkart_prod['product_name'])
            
            # SMART MATCHING: Check if base names are similar (model match) FIRST
            # This handles "iPhone 17 Pro" vs "Apple iPhone 17 Pro" 
            # Use 60% threshold here since we're just checking base model, not full product name
            base_name_match = calculate_name_similarity(amazon_base, flipkart_base)[1] >= 60
            
            # Then check for COLOR match
            amazon_color_norm = amazon_color.strip().lower() if amazon_color else ""
            flipkart_color_norm = flipkart_color.strip().lower() if flipkart_color else ""
            color_match = (amazon_color_norm and flipkart_color_norm and amazon_color_norm == flipkart_color_norm)
            
            # Key improvement: Match on base name + color, NOT requiring brand to match
            # because brand extraction is inconsistent between Amazon and Flipkart
            if base_name_match and color_match:
                best_by_color_only = amazon_prod
                best_by_color_only_flipkart = flipkart_prod
                
                logger.warning(f"\n⚠ SECOND LEVEL FALLBACK (Color match found):")
                logger.warning(f"  Amazon Color: '{amazon_color}' | Storage: {amazon_storage}GB")
                logger.warning(f"  Flipkart Color: '{flipkart_color}' | Storage: {flipkart_storage}GB")
                logger.warning(f"  Amazon:  {best_by_color_only['product_name'][:70]}")
                logger.warning(f"  Flipkart: {best_by_color_only_flipkart['product_name'][:70]}\n")
                break
        
        if best_by_color_only:
            break
    
    if best_by_color_only and best_by_color_only_flipkart:
        logger.warning(f"Using second-level fallback (color match only):")
        logger.warning(f"  Amazon: {best_by_color_only['product_name'][:70]}")
        logger.warning(f"  Flipkart: {best_by_color_only_flipkart['product_name'][:70]}")
        logger.warning(f"⚠️  WARNING: Storage capacity differs - prices may not be comparable\n")
        return best_by_color_only, best_by_color_only_flipkart, "color_match_only"
    
    # Last resort: Return top-ranked products with STRONG warning
    if amazon_ranked and flipkart_ranked:
        top_amazon = amazon_ranked[0]['product']
        top_flipkart = flipkart_ranked[0]['product']
        a_base, a_color, a_storage, _, _, _, _ = extract_product_details(top_amazon['product_name'])
        f_base, f_color, f_storage, _, _, _, _ = extract_product_details(top_flipkart['product_name'])
        
        logger.warning(f"\n⛔ LAST RESORT FALLBACK - NO ACCEPTABLE MATCH FOUND:")
        logger.warning(f"  Amazon: {top_amazon['product_name'][:70]}")
        logger.warning(f"    Color: '{a_color}' | Storage: {a_storage}GB")
        logger.warning(f"  Flipkart: {top_flipkart['product_name'][:70]}")
        logger.warning(f"    Color: '{f_color}' | Storage: {f_storage}GB")
        logger.warning(f"\n⛔ CRITICAL WARNING:")
        logger.warning(f"   - Colors DO NOT MATCH ({a_color} vs {f_color})")
        logger.warning(f"   - Storage capacity may differ ({a_storage}GB vs {f_storage}GB)")
        logger.warning(f"   - This comparison may not be valid!")
        logger.warning(f"   - Please try a more specific search query\n")
        return top_amazon, top_flipkart, "partial_match_with_mismatches"
    
    return None, None, "no_match"


class PriceComparator:
    """Main application class for price comparison"""
    
    def __init__(self):
        """Initialize the application"""
        self.db = Database()
        self.amazon_scraper = AmazonScraper()
        self.flipkart_scraper = FlipkartScraper()
        self.excel_reporter = ExcelReporter()
        logger.info("Price Comparator initialized")
    
    def search_and_compare(self, product_name):
        """
        Search for product in database or scrape if not found
        Args:
            product_name: Product to search
        Returns:
            dict: Comparison results
        """
        logger.info(f"Starting search for: {product_name}")
        
        # Search in database
        db_result = self.db.search_product(product_name)
        
        amazon_data = None
        flipkart_data = None
        from_database = True
        
        # Check if both products are in database
        if db_result and db_result['amazon'] and db_result['flipkart']:
            logger.info("Products found in database")
            amazon_data = db_result['amazon']
            flipkart_data = db_result['flipkart']
        else:
            # Need to scrape
            logger.info("Products not in database, scraping...")
            from_database = False
            
            # Scrape Amazon
            amazon_raw = self.amazon_scraper.search(product_name)
            amazon_results = filter_products(product_name, amazon_raw, similarity_threshold=0.65)
            # Scrape Flipkart
            flipkart_raw = self.flipkart_scraper.search(product_name)
            flipkart_results = filter_products(product_name, flipkart_raw, similarity_threshold=0.65)
            
            logger.info(f"Amazon returned {len(amazon_results)} results")
            for i, p in enumerate(amazon_results[:3]):
                logger.info(f"  Amazon {i+1}: {p['product_name'][:70]}")
            
            logger.info(f"Flipkart returned {len(flipkart_results)} results")
            for i, p in enumerate(flipkart_results[:3]):
                logger.info(f"  Flipkart {i+1}: {p['product_name'][:70]}")
            
            if amazon_results and flipkart_results:
                # Find best matching pair by size, color, and other attributes
                amazon_product, flipkart_product, match_quality = find_best_matching_pair(amazon_results, flipkart_results, product_name)
                
                # Store in database
                if amazon_product:
                    self.db.insert_amazon_product(
                        amazon_product['product_name'],
                        amazon_product['price'],
                        amazon_product['rating'],
                        amazon_product['review_count'],
                        amazon_product['url'],
                        amazon_product['description']
                    )
                    amazon_data = amazon_product
                
                if flipkart_product:
                    self.db.insert_flipkart_product(
                        flipkart_product['product_name'],
                        flipkart_product['price'],
                        flipkart_product['rating'],
                        flipkart_product['review_count'],
                        flipkart_product['url'],
                        flipkart_product['description']
                    )
                    flipkart_data = flipkart_product
            elif amazon_results:
                # Only Amazon has results
                amazon_product = amazon_results[0]
                self.db.insert_amazon_product(
                    amazon_product['product_name'],
                    amazon_product['price'],
                    amazon_product['rating'],
                    amazon_product['review_count'],
                    amazon_product['url'],
                    amazon_product['description']
                )
                amazon_data = amazon_product
                logger.warning("Only Amazon products found, comparison limited to one platform")
            elif flipkart_results:
                # Only Flipkart has results
                flipkart_product = flipkart_results[0]
                self.db.insert_flipkart_product(
                    flipkart_product['product_name'],
                    flipkart_product['price'],
                    flipkart_product['rating'],
                    flipkart_product['review_count'],
                    flipkart_product['url'],
                    flipkart_product['description']
                )
                flipkart_data = flipkart_product
                logger.warning("Only Flipkart products found, comparison limited to one platform")
        
        # Compare products
        if amazon_data and flipkart_data:
            comparison = compare_products(amazon_data, flipkart_data)
            
            # Add to Excel
            self.excel_reporter.add_product_comparison(
                {'amazon': amazon_data, 'flipkart': flipkart_data},
                comparison
            )
            
            result = {
                'status': 'success',
                'from_database': from_database,
                'amazon': amazon_data,
                'flipkart': flipkart_data,
                'comparison': comparison
            }
        elif amazon_data or flipkart_data:
            # Only one platform has data - return partial results
            result = {
                'status': 'partial',
                'message': 'Found on only one platform',
                'from_database': from_database,
                'amazon': amazon_data,
                'flipkart': flipkart_data,
                'comparison': None
            }
        else:
            result = {
                'status': 'error',
                'message': 'Could not find products on both platforms',
                'amazon': amazon_data,
                'flipkart': flipkart_data
            }
        
        return result
    
    def display_comparison(self, result):
        """
        Display comparison results to user
        Args:
            result: Comparison result dictionary
        """
        print("\n" + "="*80)
        
        status = result.get('status')
        
        if status == 'error':
            print(f"Error: {result.get('message', 'Unknown error')}")
            return
        
        if status == 'partial':
            print("WARNING: Product found on only one platform")
            print(f"Message: {result.get('message', '')}")
            print("="*80)
        else:
            print(f"PRODUCT COMPARISON RESULTS")
            print(f"Source: {'Database' if result['from_database'] else 'Web Scraping'}")
            print("="*80)
        
        amazon = result.get('amazon', {})
        flipkart = result.get('flipkart', {})
        comparison = result.get('comparison', {})
        
        # Amazon Details
        if amazon:
            print(f"\nAMAZON:")
            print(f"  Product:      {amazon.get('product_name', 'N/A')}")
            print(f"  Price:        {amazon.get('price', 'N/A')}")
            print(f"  Rating:       {amazon.get('rating', 'N/A')} stars")
            print(f"  Reviews:      {amazon.get('review_count', 0)}")
            print(f"  URL:          {amazon.get('url', 'N/A')}")
        else:
            print("\nAMAZON: Not found")
        
        # Flipkart Details
        if flipkart:
            print(f"\nFLIPKART:")
            print(f"  Product:      {flipkart.get('product_name', 'N/A')}")
            print(f"  Price:        {flipkart.get('price', 'N/A')}")
            print(f"  Rating:       {flipkart.get('rating', 'N/A')} stars")
            print(f"  Reviews:      {flipkart.get('review_count', 0)}")
            print(f"  URL:          {flipkart.get('url', 'N/A')}")
        else:
            print(f"\nFLIPKART: Not found")
        
        # Comparison (only if both products exist)
        if comparison and amazon and flipkart:
            print(f"\nCOMPARISON & RECOMMENDATION:")
            print(f"  Cheaper Deal: {comparison.get('cheaper_platform', 'N/A')}")
            print(f"  Cheaper By:   {comparison.get('cheaper_by_percentage', 0)}%")
            print(f"  Better Rating:{comparison.get('better_rating_platform', 'N/A')}")
            print(f"  More Reviews: {comparison.get('better_reviews_platform', 'N/A')}")
            print(f"\n  RECOMMENDATION: Buy from {comparison.get('recommendation', 'N/A')}")
        
        print("\n" + "="*80)
        if amazon and flipkart:
            print(f"Excel report updated: {self.excel_reporter.get_file_path()}")
        print("="*80 + "\n")
    
    def show_all_products(self):
        """Display all products in database"""
        products = self.db.get_all_products()
        
        if not products:
            print("No products in database")
            return
        
        print("\n" + "="*80)
        print("ALL PRODUCTS IN DATABASE")
        print("="*80)
        
        print(f"\nAMAZON PRODUCTS ({len(products['amazon'])} items):")
        for idx, product in enumerate(products['amazon'], 1):
            print(f"{idx}. {product['product_name']} - ₹{product['price']}")
        
        print(f"\nFLIPKART PRODUCTS ({len(products['flipkart'])} items):")
        for idx, product in enumerate(products['flipkart'], 1):
            print(f"{idx}. {product['product_name']} - ₹{product['price']}")
        
        print("="*80 + "\n")
    
    def clear_database(self):
        """Clear all data from database"""
        self.db.clear_table('amazon_products')
        self.db.clear_table('flipkart_products')
        logger.info("Database cleared")
        print("Database cleared successfully!")

def main():
    """Main function to run the application"""
    print("\n" + "="*80)
    print("PRICE COMPARISON SYSTEM - AMAZON vs FLIPKART")
    print("="*80 + "\n")
    
    comparator = PriceComparator()
    
    while True:
        print("\nMENU:")
        print("1. Search & Compare Product")
        print("2. View All Products in Database")
        print("3. Clear Database")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            product = input("\nEnter product name to search: ").strip()
            if product:
                result = comparator.search_and_compare(product)
                comparator.display_comparison(result)
            else:
                print("Please enter a valid product name!")
        
        elif choice == '2':
            comparator.show_all_products()
        
        elif choice == '3':
            confirm = input("Are you sure? This will delete all data. (yes/no): ").strip().lower()
            if confirm == 'yes':
                comparator.clear_database()
        
        elif choice == '4':
            print("\nThank you for using Price Comparison System!")
            break
        
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main()
