import torch
import gc
import os

def optimize_memory():
    """Configure memory optimization settings for PyTorch"""
    # Force CPU mode
    os.environ['PYTORCH_NO_CUDA'] = '1'
    
    # Disable GPU memory caching
    os.environ['PYTORCH_NO_CUDA_MEMORY_CACHING'] = '1'
    
    # Empty CUDA cache if available
    if hasattr(torch, 'cuda'):
        torch.cuda.empty_cache()
    
    # Force garbage collection
    gc.collect()
    
    # Set PyTorch to use lower precision
    torch.set_default_dtype(torch.float32)
    
    # Disable gradient calculation by default
    torch.set_grad_enabled(False)

def cleanup_after_prediction():
    """Clean up memory after making predictions"""
    gc.collect()
    if hasattr(torch, 'cuda'):
        torch.cuda.empty_cache()