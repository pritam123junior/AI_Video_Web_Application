import torch

# Check GPU memory availability
print(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU Memory Allocated: {torch.cuda.memory_allocated()} bytes")
    print(f"GPU Memory Cached: {torch.cuda.memory_reserved()} bytes")
    print(f"GPU Total Memory: {torch.cuda.get_device_properties(0).total_memory} bytes")
