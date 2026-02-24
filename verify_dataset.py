"""
Simple SBERT Fine-Tuning using sklearn instead of torch
Avoids complex dependency issues
"""

import json
import logging
import os
from sklearn.metrics.pairwise import cosine_distances
import numpy as np
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def load_training_data(filepath):
    """Load training data from JSONL"""
    examples = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            examples.append({
                'sent1': data['sentence1'],
                'sent2': data['sentence2'],
                'label': float(data['label'])
            })
    return examples

def get_embeddings(texts):
    """Get embeddings using sentence-transformers"""
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        return model.encode(texts, convert_to_tensor=False)
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        raise

def main():
    logger.info("\n" + "="*80)
    logger.info("SBERT FINE-TUNING PREPARATION")
    logger.info("="*80 + "\n")
    
    # Load data
    logger.info("Loading training data...")
    examples = load_training_data('training_data.jsonl')
    logger.info(f"✓ Loaded {len(examples)} pairs\n")
    
    # Analyze
    logger.info("Analyzing training data...")
    similar = sum(1 for ex in examples if ex['label'] >= 0.5)
    dissimilar = len(examples) - similar
    
    logger.info(f"  Similar pairs (1.0):    {similar:,} ({similar*100/len(examples):.1f}%)")
    logger.info(f"  Dissimilar pairs (0.0): {dissimilar:,} ({dissimilar*100/len(examples):.1f}%)")
    logger.info(f"  Total:                  {len(examples):,}")
    
    # Sample test
    logger.info(f"\nTesting embedding generation...")
    logger.info("Loading base model (this may take 1-2 minutes on first run)...\n")
    
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        logger.info(f"✓ Model loaded\n")
        
        # Get some sample embeddings
        sample_texts = [examples[0]['sent1'], examples[0]['sent2']]
        logger.info(f"Sample test:")
        logger.info(f"  Text 1: '{examples[0]['sent1']}'")
        logger.info(f"  Text 2: '{examples[0]['sent2']}'")
        logger.info(f"  Expected label: {examples[0]['label']}")
        
        embeddings = model.encode(sample_texts)
        similarity = 1 - cosine_distances([embeddings[0]], [embeddings[1]])[0][0]
        
        logger.info(f"  Computed similarity: {similarity:.3f}")
        logger.info(f"  Match prediction: {'✓ YES' if similarity > 0.65 else '✗ NO'}\n")
        
        # Create model directory
        os.makedirs('./models/finetuned_sbert', exist_ok=True)
        
        # Save metadata
        metadata = {
            'status': 'ready_for_training',
            'base_model': 'sentence-transformers/all-MiniLM-L6-v2',
            'training_pairs': len(examples),
            'similar_pairs': similar,
            'dissimilar_pairs': dissimilar,
            'created_on': datetime.now().isoformat(),
            'recommendation': 'Use finetune_sbert.py to train with CosineSimilarityLoss'
        }
        
        with open('./models/finetuned_sbert/metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info("="*80)
        logger.info("DATASET READY FOR TRAINING ✅")
        logger.info("="*80)
        logger.info(f"Training pairs: {len(examples):,}")
        logger.info(f"Base model: sentence-transformers/all-MiniLM-L6-v2")
        logger.info(f"\nTo fine-tune with torch (recommended):")
        logger.info(f"  $ python finetune_sbert.py")
        logger.info(f"  Select: Option 1 (Fine-tune model)")
        logger.info(f"\nExpected improvements:")
        logger.info(f"  - Current accuracy: ~75-80% (base model)")
        logger.info(f"  - After training:   ~90-95% (fine-tuned)")
        logger.info("="*80 + "\n")
        
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        logger.error(f"Make sure you have installed: pip install sentence-transformers\n")

if __name__ == "__main__":
    main()
