"""
Fine-tune SBERT model on product matching dataset
Trains the model to understand product similarity better for your specific use case
"""
import json
import logging
import os
from datetime import datetime
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BASE_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
TRAINING_DATA_FILE = 'training_data.jsonl'
FINETUNED_MODEL_DIR = './models/finetuned_sbert'
EPOCHS = 4
BATCH_SIZE = 16
WARMUP_STEPS = 100

def load_training_data(filepath=TRAINING_DATA_FILE):
    """Load training data from JSONL file"""
    if not os.path.exists(filepath):
        logger.error(f"Training data file not found: {filepath}")
        return []
    
    examples = []
    total_lines = sum(1 for _ in open(filepath))
    
    logger.info(f"Loading training data from {filepath} ({total_lines} pairs)...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            try:
                pair = json.loads(line)
                example = InputExample(
                    texts=[pair['sentence1'], pair['sentence2']],
                    label=float(pair['label'])
                )
                examples.append(example)
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Skipped line {i}: {e}")
                continue
    
    logger.info(f"Loaded {len(examples)} training examples")
    return examples

def validate_training_data(min_pairs=50):
    """Check if we have enough training data"""
    if not os.path.exists(TRAINING_DATA_FILE):
        logger.error("No training data file found!")
        logger.error("Please run: python build_training_dataset.py")
        return False
    
    with open(TRAINING_DATA_FILE, 'r') as f:
        count = sum(1 for _ in f)
    
    if count < min_pairs:
        logger.error(f"Not enough training data! Need at least {min_pairs} pairs, have {count}")
        logger.error("Please add more product pairs using build_training_dataset.py")
        return False
    
    # Count similar vs dissimilar
    similar = 0
    dissimilar = 0
    with open(TRAINING_DATA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            pair = json.loads(line)
            if pair['label'] == 1.0:
                similar += 1
            else:
                dissimilar += 1
    
    logger.info(f"Training data: {similar} similar pairs, {dissimilar} dissimilar pairs")
    
    if similar < 10 or dissimilar < 10:
        logger.warning("⚠️ Imbalanced data! Try to have at least 10 pairs of each type")
    
    return True

def finetune_model(epochs=EPOCHS, batch_size=BATCH_SIZE):
    """Fine-tune SBERT model on training data"""
    logger.info("="*70)
    logger.info("SBERT FINE-TUNING")
    logger.info("="*70 + "\n")
    
    # Validate training data
    if not validate_training_data():
        return False
    
    # Load base model
    logger.info(f"Loading base model: {BASE_MODEL}")
    model = SentenceTransformer(BASE_MODEL)
    
    # Load training data
    train_examples = load_training_data()
    if not train_examples:
        logger.error("No training examples loaded!")
        return False
    
    # Create data loader
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=batch_size)
    
    # Define loss function
    train_loss = losses.CosineSimilarityLoss(model)
    
    # Fine-tune
    logger.info(f"\nStarting fine-tuning:")
    logger.info(f"  Epochs: {epochs}")
    logger.info(f"  Batch size: {batch_size}")
    logger.info(f"  Training examples: {len(train_examples)}")
    logger.info(f"  Warmup steps: {WARMUP_STEPS}\n")
    
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=epochs,
        warmup_steps=WARMUP_STEPS,
        show_progress_bar=True
    )
    
    # Save fine-tuned model
    Path(FINETUNED_MODEL_DIR).mkdir(parents=True, exist_ok=True)
    model.save(FINETUNED_MODEL_DIR)
    
    logger.info(f"\n✓ Fine-tuned model saved to: {FINETUNED_MODEL_DIR}")
    logger.info(f"✓ Fine-tuning completed at: {datetime.now().isoformat()}")
    
    # Save training metadata
    metadata = {
        'base_model': BASE_MODEL,
        'epochs': epochs,
        'batch_size': batch_size,
        'training_pairs': len(train_examples),
        'finetuned_date': datetime.now().isoformat(),
        'training_file': TRAINING_DATA_FILE
    }
    
    with open(os.path.join(FINETUNED_MODEL_DIR, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return True

def test_finetuned_model():
    """Quick test of fine-tuned model"""
    if not os.path.exists(FINETUNED_MODEL_DIR):
        logger.error("Fine-tuned model not found!")
        return
    
    logger.info("\n" + "="*70)
    logger.info("TESTING FINE-TUNED MODEL")
    logger.info("="*70 + "\n")
    
    model = SentenceTransformer(FINETUNED_MODEL_DIR)
    
    # Test examples
    test_pairs = [
        ("iPhone 14 Pro 256GB", "Apple iPhone 14 Pro 256GB"),  # Should be high
        ("iPhone 14 Pro", "iPhone 15 Pro"),  # Should be medium
        ("iPhone 14 Case", "iPhone 14 Screen Protector"),  # Should be low
        ("Samsung Galaxy S23", "Samsung Galaxy S24"),  # Should be medium
    ]
    
    logger.info("Testing similarity scores:\n")
    for text1, text2 in test_pairs:
        embedding1 = model.encode(text1, convert_to_tensor=True)
        embedding2 = model.encode(text2, convert_to_tensor=True)
        
        from sentence_transformers.util import cos_sim
        similarity = cos_sim(embedding1, embedding2).item()
        
        logger.info(f"'{text1}' vs '{text2}'")
        logger.info(f"  Similarity: {similarity:.4f}\n")

def main():
    """Main function"""
    print("\n" + "="*70)
    print("SBERT FINE-TUNING TOOL")
    print("="*70 + "\n")
    
    while True:
        print("\nOPTIONS:")
        print("1. Fine-tune model (requires training data)")
        print("2. Validate training data")
        print("3. Test fine-tuned model")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            if finetune_model():
                logger.info("\n✓ Fine-tuning successful!")
                logger.info(f"✓ Model location: {FINETUNED_MODEL_DIR}")
                logger.info("✓ Update product_matcher.py to use this model")
            else:
                logger.error("✗ Fine-tuning failed!")
        
        elif choice == '2':
            validate_training_data()
        
        elif choice == '3':
            test_finetuned_model()
        
        elif choice == '4':
            print("\nExiting...")
            break
        
        else:
            print("❌ Invalid choice!")

if __name__ == "__main__":
    main()
