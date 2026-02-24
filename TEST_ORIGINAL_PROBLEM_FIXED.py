"""
Final comprehensive test: Original problem scenario
Tests that Cosmic Orange is selected instead of Deep Blue
"""
import sys
sys.path.insert(0, 'c:\\Users\\grish\\Downloads\\amazon_flipkart')

from main import find_best_matching_pair

print("="*70)
print("FINAL TEST: Original Problem - Cosmic Orange vs Deep Blue")
print("="*70)

# Scenario: User searches for iPhone 17 Pro in Cosmic Orange
# Amazon has it, Flipkart has both Cosmic Orange and Deep Blue

amazon_products = [
    {
        'product_name': 'Apple iPhone 17 Pro - Cosmic Orange',
        'price': 999,
        'rating': 4.5,
        'category': 'electronics'
    }
]

flipkart_products = [
    {
        'product_name': 'Apple iPhone 17 Pro (Deep Blue, 256 GB)',
        'price': 950,
        'rating': 4.4,
        'category': 'electronics'
    },
    {
        'product_name': 'Apple iPhone 17 Pro (Cosmic Orange, 256 GB)',
        'price': 990,
        'rating': 4.6,
        'category': 'electronics'
    }
]

print("\nScenario:")
print(f"  Amazon: {amazon_products[0]['product_name']}")
print(f"  Flipkart Option 1: {flipkart_products[0]['product_name']}")
print(f"  Flipkart Option 2: {flipkart_products[1]['product_name']}")

print("\nExpected Result:")
print("  Algorithm should select Flipkart Option 2 (Cosmic Orange) because colors match")

print("\nRunning find_best_matching_pair()...")
amazon_matched, flipkart_matched, match_quality = find_best_matching_pair(
    amazon_products,
    flipkart_products,
    search_query="iPhone 17 Pro"
)

print("\n" + "="*70)
print("ACTUAL RESULT")
print("="*70)

print(f"\nAmazon: {amazon_matched['product_name']}")
print(f"Flipkart: {flipkart_matched['product_name']}")
print(f"Match Quality: {match_quality}")

# Verify
expected_flipkart = "Apple iPhone 17 Pro (Cosmic Orange, 256 GB)"
if flipkart_matched['product_name'] == expected_flipkart:
    print("\n" + "="*70)
    print("[SUCCESS] PROBLEM FIXED!")
    print("="*70)
    print("Cosmic Orange is correctly selected instead of Deep Blue")
else:
    print("\n" + "="*70)
    print("[FAILED] Problem still exists!")
    print("="*70)
    print(f"Expected: {expected_flipkart}")
    print(f"Got: {flipkart_matched['product_name']}")
