# Fine-Tuning SBERT for Product Matching

## Overview
This guide explains how to fine-tune the SBERT model on your product matching data for better accuracy.

## Why Fine-Tune?
- **Better accuracy** - Model learns your specific product naming patterns
- **Reduces false positives** - Accessories and wrong variants filtered better
- **Domain-specific** - Understands e-commerce product terminology
- **Improved matching** - Works better with your Amazon/Flipkart data

## Quick Start (3 Steps)

### Step 1: Build Training Dataset
```bash
python build_training_dataset.py
```

This opens an interactive tool where you:
- Add **similar pairs** (same product on Amazon & Flipkart)
- Add **dissimilar pairs** (different products or variants)
- View your training data

**Example pairs to add:**

**Similar pairs (label: 1.0):**
```
iPhone 14 Pro 256GB Space Black      ≈ Apple iPhone 14 Pro 256GB (Space Black)
Samsung Galaxy S23 Ultra 512GB       ≈ Samsung Galaxy S23 Ultra 512GB Black
OnePlus 11 Pro 12GB                  ≈ OnePlus 11 Pro 12GB Black
```

**Dissimilar pairs (label: 0.0):**
```
iPhone 14 Pro                        ≠ iPhone 14 Pro Max (different_product)
iPhone 14 Pro 256GB                  ≠ iPhone 14 Pro 512GB (wrong_storage)
iPhone 14 Pro Space Black            ≠ iPhone 14 Pro Deep Purple (wrong_color)
iPhone 14 Charging Case              ≠ iPhone 14 Screen Protector (accessory)
iPhone 14 Pro (Refurbished)          ≠ iPhone 14 Pro (New) (refurbished)
```

### Step 2: Train the Model
```bash
python finetune_sbert.py
```

Then select option: **1. Fine-tune model**

The script will:
- Validate your training data (minimum 50 pairs recommended)
- Load base SBERT model
- Fine-tune on your data (takes 2-5 minutes)
- Save to `./models/finetuned_sbert/`

**Note:** 
- For best results, aim for **100+ training pairs**
- Include both similar and dissimilar examples
- Try to balance the number of each type

### Step 3: Use Fine-Tuned Model
The `product_matcher.py` automatically uses your fine-tuned model if it exists!

Just run your app normally:
```bash
python main.py
```

It will:
1. Check for fine-tuned model at `./models/finetuned_sbert/`
2. Use it if found, otherwise fall back to base model
3. You'll see in logs: "✓ Fine-tuned model loaded successfully"

## How to Collect Training Data

### Option A: From Your Search History
Run searches and manually note good/bad matches:
```python
python build_training_dataset.py
# Then add pairs from your searches
```

### Option B: Semi-Automatic Collection Script
Create a script that extracts pairs from scraped results:

```python
# Example: After scraping, manually review results
python main.py
# Search for products
# Note which Amazon/Flipkart pairs matched correctly
# Add them to build_training_dataset.py
```

### Option C: Bulk Import
If you have pairs in a CSV, modify `build_training_dataset.py` to import them.

## Training Data Format

The `training_data.jsonl` file contains pairs in this format:

```json
{"sentence1": "iPhone 14 Pro 256GB", "sentence2": "Apple iPhone 14 Pro 256GB", "label": 1.0}
{"sentence1": "iPhone 14 Pro", "sentence2": "iPhone 15 Pro", "label": 0.0, "reason": "different_product"}
```

- **label 1.0** = Similar products (same item on different platforms)
- **label 0.0** = Dissimilar products (different items)

## Commands Reference

```bash
# Build training dataset interactively
python build_training_dataset.py

# Fine-tune the model
python finetune_sbert.py

# View training data stats
python build_training_dataset.py  # Then choose "View current training data"

# Validate training data
python finetune_sbert.py  # Then choose "Validate training data"

# Test fine-tuned model
python finetune_sbert.py  # Then choose "Test fine-tuned model"
```

## Monitoring Improvement

Before and after fine-tuning, compare:

1. **Filter effectiveness** - Test with queries like "iphone 14"
   - Check log output for excluded vs matched products
   - Fine-tuned should exclude more accessories/wrong variants

2. **Similarity scores** - Use test function:
   ```bash
   python finetune_sbert.py  # Choose "Test fine-tuned model"
   ```

3. **Match quality** - Look at logs during `python main.py`
   - Search for products
   - Check if wrong colors/storage variants are now filtered

## Expected Results

### With Base Model (all-MiniLM-L6-v2)
- Generic similarity scoring
- May match wrong colors/storage if similarity is high
- ~60-70% accuracy for e-commerce

### With Fine-Tuned Model
- Learns your specific product patterns
- Better at distinguishing variants
- Improved exclusion of accessories
- ~85-95% accuracy after training on 100+ pairs

## Tips for Best Results

1. **Diverse examples**
   - Include different product categories
   - Cover different brands
   - Include various color/storage variants

2. **Balanced dataset**
   - Equal numbers of similar & dissimilar pairs
   - At least 20 pairs of each type

3. **Clear naming**
   - Use actual product names from Amazon/Flipkart
   - Include color and storage where relevant
   - Match the exact format

4. **Iterative improvement**
   - Train, test, add more data, retrain
   - Each iteration typically improves accuracy

## Troubleshooting

### Problem: "Not enough training data"
**Solution:** Add at least 50 pairs using `build_training_dataset.py`

### Problem: Model takes too long to train
**Solution:** Normal - takes 2-5 minutes. Check logs for progress bar.

### Problem: Fine-tuned model not used
**Solution:** Check that `./models/finetuned_sbert/` directory exists and contains:
- `pytorch_model.bin`
- `config.json`
- `metadata.json`

### Problem: Results still not accurate
**Solution:** 
- Add more training data (200+ pairs for best results)
- Ensure balanced similar/dissimilar pairs
- Include more diverse product examples

## Advanced: Custom Training

Edit `finetune_sbert.py` to adjust:

```python
EPOCHS = 4              # More epochs = better training but slower
BATCH_SIZE = 16        # Larger batch = faster but needs more memory
WARMUP_STEPS = 100     # How many steps before learning rate fully kicks in
```

## Next Steps

1. ✅ Run `python build_training_dataset.py`
2. ✅ Add 50+ product pairs (mix of similar and dissimilar)
3. ✅ Run `python finetune_sbert.py` and select option 1
4. ✅ Test with `python main.py`
5. ✅ Optionally add more pairs and retrain for better accuracy

---

**Questions?** Check the logs during training - they show detailed progress and any issues.
