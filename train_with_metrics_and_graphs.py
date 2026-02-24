"""
SBERT Fine-Tuning with Comprehensive Metrics and Visualization
- 9,356 training pairs (80%)
- 2,339 validation pairs (20%)
- 5 epochs
- Tracks: accuracy, loss, precision, recall, F1
- Generates graphs for training/validation accuracy and loss
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
    logger.info("SBERT FINE-TUNING WITH METRICS AND VISUALIZATION")
    logger.info(f"{'='*80}\n")
    
    # Load training data
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
    logger.info(f"  Similar (1.0):    {similar:,} ({similar*100/len(examples):.1f}%)")
    logger.info(f"  Dissimilar (0.0): {dissimilar:,} ({dissimilar*100/len(examples):.1f}%)\n")
    
    # Import libraries
    logger.info("Importing libraries...")
    from sentence_transformers import SentenceTransformer, InputExample, losses
    from torch.utils.data import DataLoader
    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
    from scipy.spatial.distance import cosine
    logger.info("✓ Imports successful\n")
    
    # Configuration
    BASE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    OUTPUT_DIR = "./models/finetuned_sbert"
    EPOCHS = 5
    BATCH_SIZE = 16
    WARMUP_STEPS = 100
    TRAIN_RATIO = 0.80
    
    # Split data
    logger.info("Splitting data into train (80%) and validation (20%)...")
    random.seed(42)
    random.shuffle(examples)
    split_idx = int(len(examples) * TRAIN_RATIO)
    train_examples_list = examples[:split_idx]
    val_examples_list = examples[split_idx:]
    logger.info(f"✓ Training pairs: {len(train_examples_list):,}")
    logger.info(f"✓ Validation pairs: {len(val_examples_list):,}\n")
    
    logger.info(f"{'='*80}")
    logger.info("TRAINING CONFIGURATION")
    logger.info(f"{'='*80}")
    logger.info(f"Base Model:       {BASE_MODEL}")
    logger.info(f"Total Pairs:      {len(examples):,}")
    logger.info(f"Training Pairs:   {len(train_examples_list):,} (80%)")
    logger.info(f"Validation Pairs: {len(val_examples_list):,} (20%)")
    logger.info(f"Epochs:           {EPOCHS}")
    logger.info(f"Batch Size:       {BATCH_SIZE}")
    logger.info(f"Warmup Steps:     {WARMUP_STEPS}")
    logger.info(f"Output Dir:       {OUTPUT_DIR}")
    logger.info(f"{'='*80}\n")
    
    # Load model
    logger.info("Loading base SBERT model...")
    model = SentenceTransformer(BASE_MODEL)
    logger.info(f"✓ Model loaded ({model.get_sentence_embedding_dimension()}-dim embeddings)\n")
    
    # Prepare examples
    logger.info("Preparing training examples...")
    train_examples = [
        InputExample(texts=[ex['sent1'], ex['sent2']], label=ex['label'])
        for ex in train_examples_list
    ]
    logger.info(f"✓ {len(train_examples)} training examples prepared\n")
    
    val_examples = [
        InputExample(texts=[ex['sent1'], ex['sent2']], label=ex['label'])
        for ex in val_examples_list
    ]
    logger.info(f"✓ {len(val_examples)} validation examples prepared\n")
    
    # Create data loaders
    logger.info("Creating data loaders...")
    train_dataloader = DataLoader(
        train_examples,
        shuffle=True,
        batch_size=BATCH_SIZE
    )
    logger.info(f"✓ Training data loader: {len(train_dataloader)} batches")
    logger.info(f"✓ Validation data loader ready\n")
    
    # Setup loss function
    logger.info("Setting up CosineSimilarityLoss...")
    train_loss = losses.CosineSimilarityLoss(model=model)
    logger.info("✓ Loss function ready\n")
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Train with metrics tracking
    logger.info(f"{'='*80}")
    logger.info("STARTING FINE-TUNING (5 EPOCHS)")
    logger.info(f"{'='*80}\n")
    
    start_time = datetime.now()
    
    # Track metrics per epoch
    metrics_history = {
        'epoch': [],
        'train_loss': [],
        'val_accuracy': [],
        'val_precision': [],
        'val_recall': [],
        'val_f1': [],
        'val_loss': []
    }
    
    # Get validation sentences and labels once
    val_sentences1 = [ex['sent1'] for ex in val_examples_list]
    val_sentences2 = [ex['sent2'] for ex in val_examples_list]
    val_scores = [float(ex['label']) for ex in val_examples_list]
    threshold = 0.5
    
    for epoch in range(1, EPOCHS + 1):
        logger.info(f"\nEpoch {epoch}/{EPOCHS}")
        logger.info("-" * 40)
        
        # Training
        model.fit(
            train_objectives=[(train_dataloader, train_loss)],
            epochs=1,
            warmup_steps=WARMUP_STEPS if epoch == 1 else 0,
            show_progress_bar=True,
            checkpoint_save_steps=len(train_dataloader),
            checkpoint_save_total_limit=1
        )
        
        # Validation metrics
        logger.info(f"Computing validation metrics...")
        
        # Get embeddings
        val_embeddings1 = model.encode(val_sentences1, convert_to_tensor=False, show_progress_bar=False)
        val_embeddings2 = model.encode(val_sentences2, convert_to_tensor=False, show_progress_bar=False)
        
        # Compute similarities
        similarities = []
        for emb1, emb2 in zip(val_embeddings1, val_embeddings2):
            sim = 1 - cosine(emb1, emb2)
            similarities.append(sim)
        
        # Binary predictions
        predictions = [1 if sim > threshold else 0 for sim in similarities]
        ground_truth = [1 if score > 0.5 else 0 for score in val_scores]
        
        # Calculate metrics
        accuracy = accuracy_score(ground_truth, predictions)
        precision = precision_score(ground_truth, predictions, zero_division=0)
        recall = recall_score(ground_truth, predictions, zero_division=0)
        f1 = f1_score(ground_truth, predictions, zero_division=0)
        val_loss = 1 - np.mean(similarities)  # Simple loss proxy
        
        metrics_history['epoch'].append(epoch)
        metrics_history['val_accuracy'].append(accuracy)
        metrics_history['val_precision'].append(precision)
        metrics_history['val_recall'].append(recall)
        metrics_history['val_f1'].append(f1)
        metrics_history['val_loss'].append(val_loss)
        
        logger.info(f"  Accuracy:  {accuracy:.4f}")
        logger.info(f"  Precision: {precision:.4f}")
        logger.info(f"  Recall:    {recall:.4f}")
        logger.info(f"  F1 Score:  {f1:.4f}")
        logger.info(f"  Val Loss:  {val_loss:.4f}")
    
    training_time = datetime.now() - start_time
    
    logger.info(f"\n{'='*80}")
    logger.info("✓ TRAINING COMPLETED")
    logger.info(f"{'='*80}")
    logger.info(f"Total Time: {training_time}\n")
    
    # Final metrics
    logger.info(f"{'='*80}")
    logger.info("FINAL VALIDATION METRICS")
    logger.info(f"{'='*80}")
    logger.info(f"Accuracy:  {metrics_history['val_accuracy'][-1]:.4f} ({metrics_history['val_accuracy'][-1]*100:.2f}%)")
    logger.info(f"Precision: {metrics_history['val_precision'][-1]:.4f}")
    logger.info(f"Recall:    {metrics_history['val_recall'][-1]:.4f}")
    logger.info(f"F1 Score:  {metrics_history['val_f1'][-1]:.4f}\n")
    
    # Save model
    logger.info(f"Saving fine-tuned model to {OUTPUT_DIR}...")
    model.save(OUTPUT_DIR)
    logger.info("✓ Model saved\n")
    
    # Save metadata
    metadata = {
        "base_model": BASE_MODEL,
        "total_pairs": len(examples),
        "training_pairs": len(train_examples_list),
        "validation_pairs": len(val_examples_list),
        "train_validation_split": "80/20",
        "epochs": EPOCHS,
        "batch_size": BATCH_SIZE,
        "warmup_steps": WARMUP_STEPS,
        "training_time_seconds": int(training_time.total_seconds()),
        "trained_on": datetime.now().isoformat(),
        "device": "cpu",
        "embedding_dimension": model.get_sentence_embedding_dimension(),
        "final_metrics": {
            "accuracy": float(metrics_history['val_accuracy'][-1]),
            "precision": float(metrics_history['val_precision'][-1]),
            "recall": float(metrics_history['val_recall'][-1]),
            "f1_score": float(metrics_history['val_f1'][-1]),
            "threshold": threshold
        },
        "metrics_history": metrics_history,
        "status": "ready"
    }
    
    with open(os.path.join(OUTPUT_DIR, "metadata.json"), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Generate graphs
    logger.info(f"{'='*80}")
    logger.info("GENERATING VISUALIZATION GRAPHS")
    logger.info(f"{'='*80}\n")
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('SBERT Fine-Tuning: Training & Validation Metrics', fontsize=16, fontweight='bold')
    
    epochs_list = metrics_history['epoch']
    
    # Accuracy plot
    ax = axes[0, 0]
    ax.plot(epochs_list, metrics_history['val_accuracy'], 'b-o', linewidth=2, markersize=8, label='Validation Accuracy')
    ax.set_xlabel('Epoch', fontsize=11)
    ax.set_ylabel('Accuracy', fontsize=11)
    ax.set_title('Validation Accuracy Over Epochs', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 1.05])
    ax.legend()
    for i, v in enumerate(metrics_history['val_accuracy']):
        ax.text(epochs_list[i], v + 0.02, f'{v:.3f}', ha='center', va='bottom', fontsize=9)
    
    # Loss plot
    ax = axes[0, 1]
    ax.plot(epochs_list, metrics_history['val_loss'], 'r-s', linewidth=2, markersize=8, label='Validation Loss')
    ax.set_xlabel('Epoch', fontsize=11)
    ax.set_ylabel('Loss', fontsize=11)
    ax.set_title('Validation Loss Over Epochs', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    for i, v in enumerate(metrics_history['val_loss']):
        ax.text(epochs_list[i], v + 0.01, f'{v:.3f}', ha='center', va='bottom', fontsize=9)
    
    # Precision & Recall plot
    ax = axes[1, 0]
    ax.plot(epochs_list, metrics_history['val_precision'], 'g-D', linewidth=2, markersize=8, label='Precision')
    ax.plot(epochs_list, metrics_history['val_recall'], 'm-^', linewidth=2, markersize=8, label='Recall')
    ax.set_xlabel('Epoch', fontsize=11)
    ax.set_ylabel('Score', fontsize=11)
    ax.set_title('Precision & Recall Over Epochs', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 1.05])
    ax.legend()
    
    # F1 Score plot
    ax = axes[1, 1]
    ax.plot(epochs_list, metrics_history['val_f1'], 'orange', marker='*', linewidth=2, markersize=15, label='F1 Score')
    ax.set_xlabel('Epoch', fontsize=11)
    ax.set_ylabel('F1 Score', fontsize=11)
    ax.set_title('F1 Score Over Epochs', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 1.05])
    ax.legend()
    for i, v in enumerate(metrics_history['val_f1']):
        ax.text(epochs_list[i], v + 0.02, f'{v:.3f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    # Save graphs
    graphs_dir = os.path.join(OUTPUT_DIR, "graphs")
    os.makedirs(graphs_dir, exist_ok=True)
    
    graph_path = os.path.join(graphs_dir, "training_metrics.png")
    plt.savefig(graph_path, dpi=300, bbox_inches='tight')
    logger.info(f"✓ Saved training metrics graph: {graph_path}")
    
    # Also save individual plots
    fig_acc, ax_acc = plt.subplots(figsize=(10, 6))
    ax_acc.plot(epochs_list, metrics_history['val_accuracy'], 'b-o', linewidth=3, markersize=10)
    ax_acc.fill_between(epochs_list, metrics_history['val_accuracy'], alpha=0.3)
    ax_acc.set_xlabel('Epoch', fontsize=12, fontweight='bold')
    ax_acc.set_ylabel('Accuracy', fontsize=12, fontweight='bold')
    ax_acc.set_title('Validation Accuracy (80-20 Split, 5 Epochs)', fontsize=13, fontweight='bold')
    ax_acc.grid(True, alpha=0.3)
    ax_acc.set_ylim([0, 1.05])
    for i, v in enumerate(metrics_history['val_accuracy']):
        ax_acc.text(epochs_list[i], v + 0.03, f'{v:.4f}', ha='center', fontsize=11, fontweight='bold')
    plt.tight_layout()
    acc_path = os.path.join(graphs_dir, "accuracy.png")
    plt.savefig(acc_path, dpi=300, bbox_inches='tight')
    logger.info(f"✓ Saved accuracy graph: {acc_path}")
    plt.close(fig_acc)
    
    fig_loss, ax_loss = plt.subplots(figsize=(10, 6))
    ax_loss.plot(epochs_list, metrics_history['val_loss'], 'r-s', linewidth=3, markersize=10)
    ax_loss.fill_between(epochs_list, metrics_history['val_loss'], alpha=0.3, color='red')
    ax_loss.set_xlabel('Epoch', fontsize=12, fontweight='bold')
    ax_loss.set_ylabel('Loss', fontsize=12, fontweight='bold')
    ax_loss.set_title('Validation Loss (80-20 Split, 5 Epochs)', fontsize=13, fontweight='bold')
    ax_loss.grid(True, alpha=0.3)
    for i, v in enumerate(metrics_history['val_loss']):
        ax_loss.text(epochs_list[i], v + 0.01, f'{v:.4f}', ha='center', fontsize=11, fontweight='bold')
    plt.tight_layout()
    loss_path = os.path.join(graphs_dir, "loss.png")
    plt.savefig(loss_path, dpi=300, bbox_inches='tight')
    logger.info(f"✓ Saved loss graph: {loss_path}\n")
    plt.close(fig_loss)
    
    logger.info(f"{'='*80}")
    logger.info("FINE-TUNING COMPLETE ✅")
    logger.info(f"{'='*80}")
    logger.info(f"Model saved to:       {OUTPUT_DIR}")
    logger.info(f"Training pairs:       {len(train_examples_list):,} (80%)")
    logger.info(f"Validation pairs:     {len(val_examples_list):,} (20%)")
    logger.info(f"Epochs trained:       {EPOCHS}")
    logger.info(f"Training time:        {training_time}")
    
    logger.info(f"\n📊 FINAL METRICS:")
    logger.info(f"  Accuracy:  {metrics_history['val_accuracy'][-1]*100:.2f}%")
    logger.info(f"  Precision: {metrics_history['val_precision'][-1]:.4f}")
    logger.info(f"  Recall:    {metrics_history['val_recall'][-1]:.4f}")
    logger.info(f"  F1 Score:  {metrics_history['val_f1'][-1]:.4f}")
    
    logger.info(f"\n📈 Graphs saved to:    {graphs_dir}/")
    logger.info(f"  - training_metrics.png (all 4 metrics)")
    logger.info(f"  - accuracy.png")
    logger.info(f"  - loss.png")
    
    logger.info(f"\n🚀 Next Step:")
    logger.info(f"  Run: python main.py")
    logger.info(f"  Your app will automatically use the fine-tuned model!")
    logger.info(f"{'='*80}\n")

if __name__ == "__main__":
    main()
