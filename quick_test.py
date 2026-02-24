#!/usr/bin/env python3
"""
Quick color extraction test - direct import test
"""
import sys
sys.path.insert(0, '/c/Users/grish/Downloads/amazon_flipkart')

from utils import extract_product_details

# Real product names from the scraper
products = [
    "iPhone 17 Pro 256 GB: 15.93 cm (6.3\") Display with Promotion up to 120Hz, A19 Pro Chip, Breakthrough Battery Life, Pro Fusion Camera System with Center Stage Front camera, Cosmic Orange range",
    "Apple iPhone 17 Pro (Deep Blue, 256 GB)4.7608",
    "Apple iPhone 17 Pro (Space Black, 512 GB) 5.0",
]

for p in products:
    b, c, s, sz, w, d, br = extract_product_details(p)
    print(f"Color extracted: '{c}' | Storage: {s}GB | From: {p[:60]}")
