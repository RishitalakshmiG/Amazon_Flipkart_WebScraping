"""
Debug test to see what's being extracted for Renee lipsticks
"""
import sys
sys.path.insert(0, 'c:\\Users\\grish\\Downloads\\amazon_flipkart')

from utils import extract_product_details

products = [
    "RENEE Very Matte Lipstick- Weight less 0.8 g",
    "Renee Matte Lock Lipstick, Ultra Matte Finish, Moisturizing, Long Lasting & Weightless 5 g",
    "Renee Stay With Me Matte Lip Color - Play Of Clay, 5ml"
]

print("="*70)
print("PRODUCT EXTRACTION DEBUG")
print("="*70)

for prod in products:
    base, color, size, weight, storage, dims, brand = extract_product_details(prod)
    print(f"\nProduct: {prod}")
    print(f"  Base Name: '{base}'")
    print(f"  Color: '{color}'")
    print(f"  Weight: '{weight}'")
    print(f"  Brand: '{brand}'")
    print(f"  Are 'Very Matte' and 'Matte Lock' similar? Let's check...")

# Now let's test name similarity
from main import calculate_name_similarity

name1 = "Renee Very Matte Lipstick"
name2 = "Renee Matte Lock Lipstick"
name3 = "Renee Stay With Me Matte Lip Color"

print("\n" + "="*70)
print("NAME SIMILARITY TESTS")
print("="*70)

pairs = [
    (name1, name2),
    (name1, name3),
    (name2, name3),
]

for n1, n2 in pairs:
    is_identical, similarity = calculate_name_similarity(n1, n2)
    print(f"\n'{n1}'")
    print(f"vs '{n2}'")
    print(f"Similarity: {similarity:.0f}% - {'MATCH' if similarity >= 70 else 'REJECTED'}")
