"""
Direct SBERT Fine-Tuning Script (Non-Interactive)
Trains the model with 11,695 pairs automatically
"""

import os
import json
import logging
from sentence_transformers import SentenceTransformer, InputExample, losses
from sentence_transformers import models, util
from torch.utils.data import DataLoader
import torch
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BASE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
OUTPUT_DIR = "./models/finetuned_sbert"
TRAINING_DATA_FILE = "training_data.jsonl"
EPOCHS = 4
BATCH_SIZE = 16
WARMUP_STEPS = 100


def load_training_data(filepath):
    """Load training data from JSONL file"""
    logger.info(f"Loading training data from {filepath}...")
    
    examples = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            data = json.loads(line)
            examples.append(InputExample(
                texts=[data['sentence1'], data['sentence2']],
                label=float(data['label'])
            ))
    
    logger.info(f"✓ Loaded {len(examples)} training examples")
    return examples


def validate_training_data(examples):
    """Validate training data"""
    logger.info("\nValidating training data...")
    
    if len(examples) < 100:
        logger.warning(f"⚠️  Only {len(examples)} examples (recommended: 1000+)")
    
    # Count similar and dissimilar
    similar = sum(1 for ex in examples if ex.label >= 0.5)
    dissimilar = sum(1 for ex in examples if ex.label < 0.5)
    
    logger.info(f"  Similar pairs (label=1.0): {similar}")
    logger.info(f"  Dissimilar pairs (label=0.0): {dissimilar}")
    logger.info(f"  Total: {len(examples)}")
    
    # Check balance
    total = len(examples)
    similar_pct = (similar / total) * 100
    dissimilar_pct = (dissimilar / total) * 100
    
    logger.info(f"  Balance: {similar_pct:.1f}% similar, {dissimilar_pct:.1f}% dissimilar")
    
    if similar_pct < 10 or similar_pct > 90:
        logger.warning("⚠️  Dataset is imbalanced (recommend 30-70 split)")
    
    logger.info("✓ Validation complete\n")
    return True


def train_model(examples):
    """Fine-tune SBERT model"""
    
    logger.info(f"\n{'='*80}")
    logger.info(f"FINE-TUNING SBERT MODEL")
    logger.info(f"{'='*80}")
    logger.info(f"Base Model:      {BASE_MODEL}")
    logger.info(f"Training Pairs:  {len(examples):,}")
    logger.info(f"Epochs:          {EPOCHS}")
    logger.info(f"Batch Size:      {BATCH_SIZE}")
    logger.info(f"Warmup Steps:    {WARMUP_STEPS}")
    logger.info(f"Output Dir:      {OUTPUT_DIR}")
    logger.info(f"{'='*80}\n")
    
    # Load base model
    logger.info("Loading base SBERT model...")
    model = SentenceTransformer(BASE_MODEL)
    logger.info(f"✓ Model loaded: {model.get_sentence_embedding_dimension()}-dim embeddings\n")
    
    # Create data loader
    logger.info("Creating data loader...")
    train_dataloader = DataLoader(examples, shuffle=True, batch_size=BATCH_SIZE)
    logger.info(f"✓ Data loader created ({len(examples)} samples, batch_size={BATCH_SIZE})\n")
    
    # Use CosineSimilarityLoss
    logger.info("Setting up training loss function...")
    train_loss = losses.CosineSimilarityLoss(model=model)
    logger.info("✓ Using CosineSimilarityLoss\n")
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Train
    logger.info(f"Starting training for {EPOCHS} epochs...\n")
    start_time = datetime.now()
    
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=EPOCHS,
        warmup_steps=WARMUP_STEPS,
        show_progress_bar=True,
        checkpoint_save_steps=len(train_dataloader),
        checkpoint_save_total_limit=1
    )
    
    training_time = datetime.now() - start_time
    
    logger.info(f"\n✓ Training completed in {training_time}\n")
    
    # Save model
    logger.info(f"Saving fine-tuned model to {OUTPUT_DIR}...")
    model.save(OUTPUT_DIR)
    logger.info(f"✓ Model saved\n")
    
    # Save metadata
    metadata = {
        "base_model": BASE_MODEL,
        "training_pairs": len(examples),
        "epochs": EPOCHS,
        "batch_size": BATCH_SIZE,
        "warmup_steps": WARMUP_STEPS,
        "training_time_seconds": int(training_time.total_seconds()),
        "trained_on": datetime.now().isoformat(),
        "embedding_dimension": model.get_sentence_embedding_dimension(),
    }
    
    with open(os.path.join(OUTPUT_DIR, "metadata.json"), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info("✓ Metadata saved\n")
    
    return model, metadata


def test_model(model):
    """Test the fine-tuned model"""
    logger.info(f"\n{'='*80}")
    logger.info("TESTING FINE-TUNED MODEL")
    logger.info(f"{'='*80}\n")
    
    test_pairs = [
        ("iPhone 15 Pro Max 256GB", "iPhone 15 Pro Max (256GB)", True),
        ("iPhone 15 Pro Max", "iPhone 14 Pro Max", False),
        ("Samsung Galaxy S24 Ultra", "Galaxy S24 Ultra", True),
        ("MacBook Air M3", "MacBook Air M3 Case", False),
        ("iPad Pro 12.9", "iPad Pro 11", False),
        ("Google Pixel 8 Pro", "Pixel 8 Pro", True),
    ]
    
    logger.info("Sample test predictions:\n")
    
    for sent1, sent2, should_match in test_pairs:
        embedding1 = model.encode(sent1, convert_to_tensor=True)
        embedding2 = model.encode(sent2, convert_to_tensor=True)
        
        similarity = util.pytorch_cos_sim(embedding1, embedding2).item()
        prediction = "✓ MATCH" if similarity > 0.65 else "✗ NO MATCH"
        
        correct = "✓" if (similarity > 0.65) == should_match else "✗"
        
        logger.info(f"{correct} {prediction:15} | Similarity: {similarity:.3f} | '{sent1}' vs '{sent2}'")
    
    logger.info(f"\n{'='*80}\n")


def main():
    """Main function"""
    
    logger.info(f"\n{'='*80}")
    logger.info("SBERT FINE-TUNING SYSTEM")
    logger.info(f"{'='*80}\n")
    
    # Load training data
    if not os.path.exists(TRAINING_DATA_FILE):
        logger.error(f"Training data file not found: {TRAINING_DATA_FILE}")
        return
    
    examples = load_training_data(TRAINING_DATA_FILE)
    
    # Validate
    validate_training_data(examples)
    
    # Train
    model, metadata = train_model(examples)
    
    # Test
    test_model(model)
    
    # Summary
    logger.info(f"{'='*80}")
    logger.info("FINE-TUNING COMPLETE ✅")
    logger.info(f"{'='*80}")
    logger.info(f"Model saved to: {OUTPUT_DIR}")
    logger.info(f"Training pairs: {len(examples):,}")
    logger.info(f"Training time: {metadata['training_time_seconds']} seconds")
    logger.info(f"\nNext step: python main.py")
    logger.info(f"Your app will automatically use the fine-tuned model!\n")
    logger.info(f"{'='*80}\n")


if __name__ == "__main__":
    main()
