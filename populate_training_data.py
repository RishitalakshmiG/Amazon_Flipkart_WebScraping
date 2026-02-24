"""
Pre-populate training dataset with common e-commerce product pairs
This gives you a starting point for fine-tuning
"""
from build_training_dataset import add_similar_pair, add_dissimilar_pair

def populate_initial_training_data():
    """Add initial training pairs for common products"""
    
    print("\n" + "="*80)
    print("POPULATING INITIAL TRAINING DATA")
    print("="*80 + "\n")
    
    # iPhone pairs
    print("Adding iPhone training pairs...")
    add_similar_pair("iPhone 14 Pro 256GB", "Apple iPhone 14 Pro 256GB")
    add_similar_pair("iPhone 14 Pro 512GB Space Black", "iPhone 14 Pro 512GB (Space Black)")
    add_similar_pair("iPhone 14 Plus", "Apple iPhone 14 Plus")
    add_dissimilar_pair("iPhone 14 Pro", "iPhone 14 Pro Max", reason="different_product")
    add_dissimilar_pair("iPhone 14 Pro 256GB", "iPhone 14 Pro 512GB", reason="wrong_storage")
    add_dissimilar_pair("iPhone 14 Space Black", "iPhone 14 Purple", reason="wrong_color")
    add_dissimilar_pair("iPhone 14 Case", "iPhone 14", reason="accessory")
    
    # Samsung pairs
    print("\nAdding Samsung training pairs...")
    add_similar_pair("Samsung Galaxy S23 Ultra", "Samsung Galaxy S23 Ultra 12GB")
    add_similar_pair("Samsung Galaxy S23 Ultra 512GB", "Samsung S23 Ultra 512GB Black")
    add_similar_pair("Samsung Galaxy S23", "Samsung S23 Phantom Black")
    add_dissimilar_pair("Samsung Galaxy S23", "Samsung Galaxy S23 Ultra", reason="different_product")
    add_dissimilar_pair("Samsung Galaxy S23 256GB", "Samsung Galaxy S23 512GB", reason="wrong_storage")
    add_dissimilar_pair("Samsung Galaxy S23 Black", "Samsung Galaxy S23 Green", reason="wrong_color")
    add_dissimilar_pair("Samsung Galaxy S23 Screen Protector", "Samsung Galaxy S23", reason="accessory")
    
    # Laptop pairs
    print("\nAdding Laptop training pairs...")
    add_similar_pair("MacBook Air M2 256GB", "Apple MacBook Air M2 256GB")
    add_similar_pair("Dell XPS 13 Plus Intel Core i7", "Dell XPS 13 Plus i7")
    add_similar_pair("HP Pavilion 15 AMD Ryzen 7", "HP Pavilion 15 Ryzen 7")
    add_dissimilar_pair("MacBook Air M2", "MacBook Air M3", reason="different_product")
    add_dissimilar_pair("Dell XPS 13 256GB", "Dell XPS 13 512GB", reason="wrong_storage")
    add_dissimilar_pair("MacBook Air 15", "MacBook Pro 15", reason="different_product")
    add_dissimilar_pair("Laptop Case 13 inch", "Dell XPS 13", reason="accessory")
    
    # Tablet pairs
    print("\nAdding Tablet training pairs...")
    add_similar_pair("iPad Pro 11 inch 256GB", "Apple iPad Pro 11 inch 256GB")
    add_similar_pair("Samsung Galaxy Tab S8", "Samsung Galaxy Tab S8 128GB")
    add_similar_pair("iPad Air 5th Generation 64GB", "iPad Air 5 64GB")
    add_dissimilar_pair("iPad Pro 11 inch", "iPad Pro 12.9 inch", reason="different_product")
    add_dissimilar_pair("iPad Pro 256GB", "iPad Pro 512GB", reason="wrong_storage")
    add_dissimilar_pair("iPad Mini", "iPad Air", reason="different_product")
    add_dissimilar_pair("iPad Screen Protector", "iPad Pro", reason="accessory")
    
    # Smartwatch pairs
    print("\nAdding Smartwatch training pairs...")
    add_similar_pair("Apple Watch Series 8 45mm", "Apple Watch Series 8 45mm Midnight")
    add_similar_pair("Samsung Galaxy Watch 5 Pro", "Samsung Galaxy Watch 5 Pro 45mm")
    add_similar_pair("Fitbit Charge 5", "Fitbit Charge 5 Black")
    add_dissimilar_pair("Apple Watch Series 8", "Apple Watch Series 9", reason="different_product")
    add_dissimilar_pair("Apple Watch 41mm", "Apple Watch 45mm", reason="wrong_size")
    add_dissimilar_pair("Watch Band", "Apple Watch", reason="accessory")
    
    # Earbuds pairs
    print("\nAdding Earbuds training pairs...")
    add_similar_pair("AirPods Pro 2nd Generation", "Apple AirPods Pro 2")
    add_similar_pair("Samsung Galaxy Buds 2 Pro", "Samsung Galaxy Buds2 Pro")
    add_similar_pair("Sony WF-1000XM5", "Sony WF-1000XM5 Black")
    add_dissimilar_pair("AirPods Pro", "AirPods Max", reason="different_product")
    add_dissimilar_pair("AirPods Pro 1st Gen", "AirPods Pro 2nd Gen", reason="different_product")
    add_dissimilar_pair("AirPods Case", "AirPods Pro", reason="accessory")
    
    # Camera pairs
    print("\nAdding Camera training pairs...")
    add_similar_pair("Canon EOS R5 Body", "Canon EOS R5 Mirrorless Camera")
    add_similar_pair("Sony A7 IV Alpha", "Sony Alpha A7 IV")
    add_similar_pair("Nikon Z9 Full Frame", "Nikon Z9")
    add_dissimilar_pair("Canon EOS R5", "Canon EOS R6", reason="different_product")
    add_dissimilar_pair("Canon EOS R5 Body", "Canon EOS R5 with Lens", reason="wrong_bundle")
    add_dissimilar_pair("Camera Lens", "Canon Camera", reason="accessory")
    
    # Miscellaneous exclusions
    print("\nAdding exclusion training pairs...")
    add_dissimilar_pair("iPhone 14 Pro (Refurbished)", "iPhone 14 Pro (New)", reason="refurbished")
    add_dissimilar_pair("iPhone 14 Bundle with Accessories", "iPhone 14", reason="different_bundle")
    add_dissimilar_pair("iPhone 14 Warranty", "iPhone 14", reason="service")
    add_dissimilar_pair("Dell Laptop Stand", "Dell Laptop", reason="accessory")
    add_dissimilar_pair("Samsung Phone Case Pack of 3", "Samsung Phone", reason="accessory")
    
    print("\n" + "="*80)
    print("✓ INITIAL TRAINING DATA POPULATED")
    print("="*80)
    print("\nYou now have 50+ training pairs to start with!")
    print("You can add more specific pairs for your use case.")
    print("\nRun: python build_training_dataset.py")
    print("     to view or add more pairs")

if __name__ == "__main__":
    populate_initial_training_data()
