"""
Script to build a training dataset for SBERT fine-tuning
Collects similar and dissimilar product pairs from your searches
"""
import json
import os
from datetime import datetime

TRAINING_DATA_FILE = 'training_data.jsonl'

def add_similar_pair(product1_name, product2_name, platform1='amazon', platform2='flipkart'):
    """
    Add a similar product pair to training data (label: 1.0)
    
    Args:
        product1_name: First product name
        product2_name: Second product name
        platform1: Platform of first product
        platform2: Platform of second product
    """
    pair = {
        'sentence1': product1_name.strip(),
        'sentence2': product2_name.strip(),
        'label': 1.0,
        'platform1': platform1,
        'platform2': platform2,
        'timestamp': datetime.now().isoformat()
    }
    
    with open(TRAINING_DATA_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(pair, ensure_ascii=False) + '\n')
    
    print(f"✓ Added similar pair:")
    print(f"  '{product1_name[:60]}' ≈ '{product2_name[:60]}'")

def add_dissimilar_pair(product1_name, product2_name, reason='different_product', platform1='amazon', platform2='flipkart'):
    """
    Add a dissimilar product pair to training data (label: 0.0)
    
    Args:
        product1_name: First product name
        product2_name: Second product name
        reason: Reason for dissimilarity (e.g., 'different_product', 'wrong_color', 'wrong_storage')
        platform1: Platform of first product
        platform2: Platform of second product
    """
    pair = {
        'sentence1': product1_name.strip(),
        'sentence2': product2_name.strip(),
        'label': 0.0,
        'reason': reason,
        'platform1': platform1,
        'platform2': platform2,
        'timestamp': datetime.now().isoformat()
    }
    
    with open(TRAINING_DATA_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(pair, ensure_ascii=False) + '\n')
    
    print(f"✗ Added dissimilar pair ({reason}):")
    print(f"  '{product1_name[:60]}' ≠ '{product2_name[:60]}'")

def view_training_data(limit=10):
    """View current training dataset"""
    if not os.path.exists(TRAINING_DATA_FILE):
        print("No training data file yet. Start adding pairs!")
        return
    
    similar_count = 0
    dissimilar_count = 0
    
    print("\n" + "="*100)
    print("TRAINING DATA SUMMARY")
    print("="*100 + "\n")
    
    with open(TRAINING_DATA_FILE, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i < limit:
                pair = json.loads(line)
                label = pair['label']
                s1 = pair['sentence1'][:60]
                s2 = pair['sentence2'][:60]
                
                if label == 1.0:
                    similar_count += 1
                    print(f"{i+1}. ✓ SIMILAR: '{s1}' ≈ '{s2}'")
                else:
                    dissimilar_count += 1
                    reason = pair.get('reason', 'different')
                    print(f"{i+1}. ✗ DISSIMILAR ({reason}): '{s1}' ≠ '{s2}'")
            else:
                similar_count += (1 if json.loads(line)['label'] == 1.0 else 0)
    
    # Count total
    with open(TRAINING_DATA_FILE, 'r', encoding='utf-8') as f:
        total = sum(1 for _ in f)
    
    print("\n" + "="*100)
    print(f"TOTAL PAIRS: {total}")
    print("="*100 + "\n")

def interactive_builder():
    """Interactive mode to add training pairs"""
    print("\n" + "="*100)
    print("TRAINING DATA BUILDER - Interactive Mode")
    print("="*100)
    print("\nYou can add product pairs that are similar or dissimilar")
    print("This data will be used to fine-tune the SBERT model for better accuracy\n")
    
    while True:
        print("\nOPTIONS:")
        print("1. Add similar product pair (same product on different platforms)")
        print("2. Add dissimilar product pair (different products or variants)")
        print("3. View current training data")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            print("\n--- Adding Similar Pair ---")
            p1 = input("Product 1 name (Amazon): ").strip()
            p2 = input("Product 2 name (Flipkart): ").strip()
            
            if p1 and p2:
                add_similar_pair(p1, p2)
            else:
                print("❌ Empty product name!")
        
        elif choice == '2':
            print("\n--- Adding Dissimilar Pair ---")
            p1 = input("Product 1 name: ").strip()
            p2 = input("Product 2 name: ").strip()
            print("\nReason for dissimilarity:")
            print("1. Different product")
            print("2. Wrong color")
            print("3. Wrong storage capacity")
            print("4. Accessory/case (should exclude)")
            print("5. Refurbished (should exclude)")
            print("6. Other")
            
            reason_choice = input("Select reason (1-6): ").strip()
            reason_map = {
                '1': 'different_product',
                '2': 'wrong_color',
                '3': 'wrong_storage',
                '4': 'accessory',
                '5': 'refurbished',
                '6': 'other'
            }
            reason = reason_map.get(reason_choice, 'other')
            
            if p1 and p2:
                add_dissimilar_pair(p1, p2, reason=reason)
            else:
                print("❌ Empty product name!")
        
        elif choice == '3':
            view_training_data(limit=20)
        
        elif choice == '4':
            print("\nExiting training data builder...")
            break
        
        else:
            print("❌ Invalid choice!")

if __name__ == "__main__":
    # Check if training data exists
    if os.path.exists(TRAINING_DATA_FILE):
        size = os.path.getsize(TRAINING_DATA_FILE)
        lines = sum(1 for _ in open(TRAINING_DATA_FILE))
        print(f"Found existing training data: {lines} pairs ({size:,} bytes)")
    else:
        print("Creating new training dataset...")
        open(TRAINING_DATA_FILE, 'w').close()
        print("✓ Created training_data.jsonl")
    
    # Start interactive builder
    interactive_builder()
