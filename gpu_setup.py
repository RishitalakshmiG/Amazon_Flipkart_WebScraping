"""
GPU Setup Checker and Optimizer
Checks CUDA/GPU configuration and provides setup instructions
"""

import torch
import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("\n" + "="*80)
    logger.info("GPU SETUP CHECKER")
    logger.info("="*80 + "\n")
    
    # Check PyTorch
    logger.info("1. PyTorch Installation:")
    logger.info(f"   ✓ PyTorch version: {torch.__version__}")
    
    # Check CUDA
    logger.info("\n2. CUDA Support:")
    cuda_available = torch.cuda.is_available()
    
    if cuda_available:
        logger.info(f"   ✓ CUDA Available: YES")
        logger.info(f"   ✓ CUDA Version: {torch.version.cuda}")
        logger.info(f"   ✓ cuDNN Version: {torch.backends.cudnn.version()}")
        logger.info(f"   ✓ Device Count: {torch.cuda.device_count()}")
        
        for i in range(torch.cuda.device_count()):
            name = torch.cuda.get_device_name(i)
            props = torch.cuda.get_device_properties(i)
            memory_gb = props.total_memory / 1e9
            compute_capability = f"{props.major}.{props.minor}"
            
            logger.info(f"\n   GPU {i}: {name}")
            logger.info(f"      Memory: {memory_gb:.1f} GB")
            logger.info(f"      Compute Capability: {compute_capability}")
            logger.info(f"      Max Threads per Block: {props.max_threads_per_block}")
        
        logger.info(f"\n   Status: ✅ GPU IS READY FOR TRAINING (10-50x speedup!)")
        logger.info(f"\n   Start GPU training:")
        logger.info(f"   $ python train_gpu.py")
    else:
        logger.info(f"   ✗ CUDA Available: NO")
        logger.info(f"\n   ⚠️  GPU NOT DETECTED")
        logger.info(f"\n   To enable GPU training:")
        logger.info(f"\n   Option 1: Install NVIDIA CUDA Toolkit")
        logger.info(f"   1. Download from: https://developer.nvidia.com/cuda-downloads")
        logger.info(f"   2. Select: Windows, x86_64, 11 (or your CUDA version)")
        logger.info(f"   3. Install with default settings")
        logger.info(f"\n   Option 2: Install cuDNN (optional, for faster training)")
        logger.info(f"   1. Download from: https://developer.nvidia.com/cudnn")
        logger.info(f"   2. Extract to CUDA installation directory")
        logger.info(f"\n   Option 3: Reinstall PyTorch with CUDA support")
        logger.info(f"   Run:")
        logger.info(f"   $ pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        logger.info(f"\n   After setup, run:")
        logger.info(f"   $ python gpu_setup.py  (to verify)")
        logger.info(f"   $ python train_gpu.py  (to train with GPU)")
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("QUICK START")
    logger.info("="*80)
    
    if cuda_available:
        logger.info(f"\n✅ GPU DETECTED - Ready for training!\n")
        logger.info(f"Run this to start GPU-accelerated training:\n")
        logger.info(f"    python train_gpu.py\n")
        logger.info(f"Expected time: 2-4 minutes (with GPU)\n")
    else:
        logger.info(f"\n⚠️  NO GPU DETECTED\n")
        logger.info(f"You can still train on CPU (slower):\n")
        logger.info(f"    python train_gpu.py\n")
        logger.info(f"Expected time: 30-60 minutes (with CPU)\n")
        logger.info(f"Or install CUDA first for 10-20x speedup\n")
    
    logger.info("="*80 + "\n")

if __name__ == "__main__":
    main()
