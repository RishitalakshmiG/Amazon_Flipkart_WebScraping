"""
Simple debug test to see what's happening with matching
"""
import sys
sys.path.insert(0, 'c:\\Users\\grish\\Downloads\\amazon_flipkart')

from main import extract_product_details, calculate_name_similarity

# Test the extraction and matching directly
amazon_name = "RENEE Very Matte Lipstick - Rouge"
flipkart_name = "Renee Very Matte Lipstick- Rouge 6 g"

print("="*70)
print("DEBUG: Direct matching test")
print("="*70)

print(f"\nAmazon: {amazon_name}")
amazon_base, amazon_color, amazon_size, amazon_weight, amazon_storage, amazon_dims, amazon_brand = extract_product_details(amazon_name)
print(f"  Base: '{amazon_base}'")
print(f"  Brand: '{amazon_brand}'")

print(f"\nFlipkart: {flipkart_name}")
fk_base, fk_color, fk_size, fk_weight, fk_storage, fk_dims, fk_brand = extract_product_details(flipkart_name)
print(f"  Base: '{fk_base}'")
print(f"  Brand: '{fk_brand}'")

# Test brand match
print(f"\n[STEP 1] Brand Match:")
print(f"  '{amazon_brand}' == '{fk_brand}' ? {amazon_brand.lower() == fk_brand.lower()}")

# Test name similarity
print(f"\n[STEP 2] Name Similarity:")
is_identical, similarity = calculate_name_similarity(amazon_base, fk_base)
print(f"  '{amazon_base}' vs '{fk_base}'")
print(f"  Similarity: {similarity:.0f}%")
print(f"  Pass (>= 70%)? {similarity >= 70}")

# Test variant check
print(f"\n[STEP 2.5] Variant Check:")
variant_keywords = {
    'matte_type': ['matte lock', 'very matte', 'ultra matte', 'matte finish', 'semi-matte'],
    'phone_size': ['pro', 'max', 'mini', 'plus', 'ultra'],
    'material': ['titanium', 'stainless', 'aluminum', 'ceramic'],
}

amazon_lower = amazon_base.lower()
flipkart_lower = fk_base.lower()

for category, keywords in variant_keywords.items():
    amazon_variant = [kw for kw in keywords if kw in amazon_lower]
    flipkart_variant = [kw for kw in keywords if kw in flipkart_lower]
    
    if amazon_variant or flipkart_variant:
        print(f"  {category}: Amazon={amazon_variant}, Flipkart={flipkart_variant}")
        if amazon_variant and flipkart_variant:
            if amazon_variant != flipkart_variant:
                print(f"    -> MISMATCH!")
            else:
                print(f"    -> OK (both have same)")
        elif amazon_variant or flipkart_variant:
            if category in ['phone_size', 'material']:
                print(f"    -> MISMATCH (only one has variant, category is strict)")
