#!/usr/bin/env python3
"""
Test script to verify imports work correctly
"""

try:
    from model_loader import load_model, predict_attributes_from_bytes
    print("✅ Successfully imported load_model and predict_attributes_from_bytes")
    
    # Test if load_model function exists and is callable
    if callable(load_model):
        print("✅ load_model is callable")
    else:
        print("❌ load_model is not callable")
        
    if callable(predict_attributes_from_bytes):
        print("✅ predict_attributes_from_bytes is callable")
    else:
        print("❌ predict_attributes_from_bytes is not callable")
        
    print("✅ All imports successful!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
