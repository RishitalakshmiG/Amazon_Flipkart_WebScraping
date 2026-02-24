"""
SBERT Fine-Tuning: 80/20 Split, 5 Epochs with Graphs
- 9,356 training pairs
- 2,339 validation pairs  
- 5 epochs
- Generates graphs for accuracy and loss
"""

import os
import json
import logging
import random
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info(f"\n{'='*80}")
    logger.info("SBERT FINE-TUNING: 80-20 SPLIT, 5 EPOCHS")
    logger.info(f"{'='*80}\n")
    
    # Load data
    logger.info("Loading training data...")
    examples = []
    with open('training_data.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            examples.append({
                'sent1': data['sentence1'],
                'sent2': data['sentence2'],
                'label': float(data['label'])
            })
    
    similar = sum(1 for ex in examples if ex['label'] >= 0.5)
    dissimilar = len(examples) - similar
    
    logger.info(f"✓ Loaded {len(examples):,} total pairs")
    logger.info(f"  Similar (1.0):    {similar:,}")
    logger.info(f"  Dissimilar (0.0): {dissimilar:,}\n")
    
    # Import libraries
    logger.info("Importing libraries...")
    from sentence_transformers import SentenceTransformer, InputExample, losses
    from torch.utils.data import DataLoader
    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
    from scipy.spatial.distance import cosine
    logger.info("✓ Imports successful\n")
    
    # Config
    BASE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    OUTPUT_DIR = "./models/finetuned_sbert"
    EPOCHS = 5
    BATCH_SIZE = 16
    WARMUP_STEPS = 100
    
    # Split data
    logger.info("Splitting data: 80% training, 20% validation...")
    random.seed(42)
    random.shuffle(examples)
    split_idx = int(len(examples) * 0.8)
    train_list = examples[:split_idx]
    val_list = examples[split_idx:]
    logger.info(f"✓ Training: {len(train_list):,} pairs")
    logger.info(f"✓ Validation: {len(val_list):,} pairs\n")
    
    logger.info(f"{'='*80}")
    logger.info("TRAINING CONFIGURATION")
    logger.info(f"{'='*80}")
    logger.info(f"Base Model:       {BASE_MODEL}")
    logger.info(f"Epochs:           {EPOCHS}")
    logger.info(f"Batch Size:       {BATCH_SIZE}")
    logger.info(f"Training Pairs:   {len(train_list):,}")
    logger.info(f"Validation Pairs: {len(val_list):,}")
    logger.info(f"{'='*80}\n")
    
    # Load model
    logger.info("Loading SBERT model...")
    model = SentenceTransformer(BASE_MODEL)
    logger.info(f"✓ Model loaded\n")
    
    # Prepare examples
    train_examples = [
        InputExample(texts=[ex['sent1'], ex['sent2']], label=ex['label'])
        for ex in train_list
    ]
    
    # Data loader
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=BATCH_SIZE)
    logger.info(f"✓ Data loader ready: {len(train_dataloader)} batches\n")
    
    # Loss function
    train_loss = losses.CosineSimilarityLoss(model=model)
    
    # Output dir
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Validation data
    val_sent1 = [ex['sent1'] for ex in val_list]
    val_sent2 = [ex['sent2'] for ex in val_list]
    val_labels = [ex['label'] for ex in val_list]
    threshold = 0.5
    
    # Metrics storage
    metrics = {
        'epoch': [],
        'accuracy': [],
        'precision': [],
        'recall': [],
        'f1': [],
        'loss': []
    }
    
    logger.info(f"{'='*80}")
    logger.info("TRAINING STARTED (5 EPOCHS)")
    logger.info(f"{'='*80}\n")
    
    start = datetime.now()
    
    for epoch in range(1, EPOCHS + 1):
        logger.info(f"Epoch {epoch}/{EPOCHS}")
        
        # Train for 1 epoch
        model.fit(
            train_objectives=[(train_dataloader, train_loss)],
            epochs=1,
            warmup_steps=WARMUP_STEPS if epoch == 1 else 0,
            show_progress_bar=True
        )
        
        # Evaluate
        logger.info("Evaluating...")
        emb1 = model.encode(val_sent1, convert_to_tensor=False, show_progress_bar=False)
        emb2 = model.encode(val_sent2, convert_to_tensor=False, show_progress_bar=False)
        
        sims = [1 - cosine(e1, e2) for e1, e2 in zip(emb1, emb2)]
        preds = [1 if s > threshold else 0 for s in sims]
        truth = [1 if l > 0.5 else 0 for l in val_labels]
        
        acc = accuracy_score(truth, preds)
        prec = precision_score(truth, preds, zero_division=0)
        rec = recall_score(truth, preds, zero_division=0)
        f1_s = f1_score(truth, preds, zero_division=0)
        loss = 1 - np.mean(sims)
        
        metrics['epoch'].append(epoch)
        metrics['accuracy'].append(acc)
        metrics['precision'].append(prec)
        metrics['recall'].append(rec)
        metrics['f1'].append(f1_s)
        metrics['loss'].append(loss)
        
        logger.info(f"  Accuracy:  {acc:.4f}")
        logger.info(f"  Precision: {prec:.4f}")
        logger.info(f"  Recall:    {rec:.4f}")
        logger.info(f"  F1:        {f1_s:.4f}")
        logger.info(f"  Loss:      {loss:.4f}\n")
    
    elapsed = datetime.now() - start
    
    logger.info(f"{'='*80}")
    logger.info("✓ TRAINING COMPLETE")
    logger.info(f"{'='*80}")
    logger.info(f"Time: {elapsed}\n")
    
    # Save model
    logger.info(f"Saving model to {OUTPUT_DIR}...")
    model.save(OUTPUT_DIR)
    logger.info("✓ Model saved\n")
    
    # Save metadata
    metadata = {
        "base_model": BASE_MODEL,
        "total_pairs": len(examples),
        "training_pairs": len(train_list),
        "validation_pairs": len(val_list),
        "train_test_split": "80/20",
        "epochs": EPOCHS,
        "batch_size": BATCH_SIZE,
        "training_time_seconds": int(elapsed.total_seconds()),
        "metrics": {
            "final_accuracy": float(metrics['accuracy'][-1]),
            "final_precision": float(metrics['precision'][-1]),
            "final_recall": float(metrics['recall'][-1]),
            "final_f1": float(metrics['f1'][-1]),
            "final_loss": float(metrics['loss'][-1])
        },
        "status": "ready"
    }
    
    with open(os.path.join(OUTPUT_DIR, "metadata.json"), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Metrics summary
    logger.info(f"{'='*80}")
    logger.info("FINAL METRICS (Epoch 5)")
    logger.info(f"{'='*80}")
    logger.info(f"Accuracy:  {metrics['accuracy'][-1]:.4f} ({metrics['accuracy'][-1]*100:.2f}%)")
    logger.info(f"Precision: {metrics['precision'][-1]:.4f}")
    logger.info(f"Recall:    {metrics['recall'][-1]:.4f}")
    logger.info(f"F1 Score:  {metrics['f1'][-1]:.4f}")
    logger.info(f"Loss:      {metrics['loss'][-1]:.4f}\n")
    
    # Generate graphs
    logger.info(f"{'='*80}")
    logger.info("GENERATING GRAPHS")
    logger.info(f"{'='*80}\n")
    
    graphs_dir = os.path.join(OUTPUT_DIR, "graphs")
    os.makedirs(graphs_dir, exist_ok=True)
    
    epochs_arr = metrics['epoch']
    
    # Combined graph
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('SBERT Fine-Tuning: 80-20 Split, 5 Epochs', fontsize=16, fontweight='bold')
    
    # Accuracy
    ax = axes[0, 0]
    ax.plot(epochs_arr, metrics['accuracy'], 'b-o', linewidth=2.5, markersize=9)
    ax.fill_between(epochs_arr, metrics['accuracy'], alpha=0.3)
    ax.set_xlabel('Epoch', fontsize=11, fontweight='bold')
    ax.set_ylabel('Accuracy', fontsize=11, fontweight='bold')
    ax.set_title('Validation Accuracy', fontsize=12, fontweight='bold')
    ax.set_ylim([0, 1.05])
    ax.grid(True, alpha=0.3)
    for i, v in enumerate(metrics['accuracy']):
        ax.text(epochs_arr[i], v + 0.02, f'{v:.3f}', ha='center', fontsize=9, fontweight='bold')
    
    # Loss
    ax = axes[0, 1]
    ax.plot(epochs_arr, metrics['loss'], 'r-s', linewidth=2.5, markersize=9)
    ax.fill_between(epochs_arr, metrics['loss'], alpha=0.3, color='red')
    ax.set_xlabel('Epoch', fontsize=11, fontweight='bold')
    ax.set_ylabel('Loss', fontsize=11, fontweight='bold')
    ax.set_title('Validation Loss', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    for i, v in enumerate(metrics['loss']):
        ax.text(epochs_arr[i], v + 0.01, f'{v:.3f}', ha='center', fontsize=9, fontweight='bold')
    
    # Precision & Recall
    ax = axes[1, 0]
    ax.plot(epochs_arr, metrics['precision'], 'g-D', linewidth=2.5, markersize=8, label='Precision')
    ax.plot(epochs_arr, metrics['recall'], 'm-^', linewidth=2.5, markersize=8, label='Recall')
    ax.set_xlabel('Epoch', fontsize=11, fontweight='bold')
    ax.set_ylabel('Score', fontsize=11, fontweight='bold')
    ax.set_title('Precision & Recall', fontsize=12, fontweight='bold')
    ax.set_ylim([0, 1.05])
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    
    # F1 Score
    ax = axes[1, 1]
    ax.plot(epochs_arr, metrics['f1'], 'orange', marker='*', linewidth=2.5, markersize=15, label='F1 Score')
    ax.fill_between(epochs_arr, metrics['f1'], alpha=0.3, color='orange')
    ax.set_xlabel('Epoch', fontsize=11, fontweight='bold')
    ax.set_ylabel('F1 Score', fontsize=11, fontweight='bold')
    ax.set_title('F1 Score', fontsize=12, fontweight='bold')
    ax.set_ylim([0, 1.05])
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    for i, v in enumerate(metrics['f1']):
        ax.text(epochs_arr[i], v + 0.02, f'{v:.3f}', ha='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    comb_path = os.path.join(graphs_dir, "all_metrics.png")
    plt.savefig(comb_path, dpi=300, bbox_inches='tight')
    logger.info(f"✓ Saved: {comb_path}")
    plt.close()
    
    # Accuracy graph
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(epochs_arr, metrics['accuracy'], 'b-o', linewidth=3, markersize=11)
    ax.fill_between(epochs_arr, metrics['accuracy'], alpha=0.3)
    ax.set_xlabel('Epoch', fontsize=12, fontweight='bold')
    ax.set_ylabel('Accuracy', fontsize=12, fontweight='bold')
    ax.set_title('Training & Validation Accuracy (80-20 Split)', fontsize=13, fontweight='bold')
    ax.set_ylim([0, 1.05])
    ax.grid(True, alpha=0.3)
    for i, v in enumerate(metrics['accuracy']):
        ax.text(epochs_arr[i], v + 0.03, f'{v:.4f}', ha='center', fontsize=11, fontweight='bold')
    plt.tight_layout()
    acc_path = os.path.join(graphs_dir, "accuracy.png")
    plt.savefig(acc_path, dpi=300, bbox_inches='tight')
    logger.info(f"✓ Saved: {acc_path}")
    plt.close()
    
    # Loss graph
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(epochs_arr, metrics['loss'], 'r-s', linewidth=3, markersize=11)
    ax.fill_between(epochs_arr, metrics['loss'], alpha=0.3, color='red')
    ax.set_xlabel('Epoch', fontsize=12, fontweight='bold')
    ax.set_ylabel('Loss', fontsize=12, fontweight='bold')
    ax.set_title('Training & Validation Loss (80-20 Split)', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    for i, v in enumerate(metrics['loss']):
        ax.text(epochs_arr[i], v + 0.01, f'{v:.4f}', ha='center', fontsize=11, fontweight='bold')
    plt.tight_layout()
    loss_path = os.path.join(graphs_dir, "loss.png")
    plt.savefig(loss_path, dpi=300, bbox_inches='tight')
    logger.info(f"✓ Saved: {loss_path}\n")
    plt.close()
    
    logger.info(f"{'='*80}")
    logger.info("✅ COMPLETE!")
    logger.info(f"{'='*80}")
    logger.info(f"Model:     {OUTPUT_DIR}")
    logger.info(f"Graphs:    {graphs_dir}/")
    logger.info(f"Train Set: {len(train_list):,} pairs (80%)")
    logger.info(f"Test Set:  {len(val_list):,} pairs (20%)")
    logger.info(f"Time:      {elapsed}")
    logger.info(f"\n🎯 Final Metrics:")
    logger.info(f"   Accuracy:  {metrics['accuracy'][-1]*100:.2f}%")
    logger.info(f"   Precision: {metrics['precision'][-1]:.4f}")
    logger.info(f"   Recall:    {metrics['recall'][-1]:.4f}")
    logger.info(f"   F1 Score:  {metrics['f1'][-1]:.4f}\n")

if __name__ == "__main__":
    main()
