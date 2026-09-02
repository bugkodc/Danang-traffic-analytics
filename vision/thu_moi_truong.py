"""Kiem tra moi truong truoc khi chay cac script khac."""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

print("=" * 56)
print("KIEM TRA MOI TRUONG THI GIAC MAY TINH")
print("=" * 56)

ok = True
for m in ("torch", "ultralytics", "cv2", "numpy", "pandas"):
    try:
        x = __import__(m)
        print(f"  {m:14s} {getattr(x, '__version__', '?')}")
    except ImportError:
        print(f"  {m:14s} CHUA CAI")
        ok = False

try:
    import torch
    co_cuda = torch.cuda.is_available()
    print(f"\n  CUDA         {'CO' if co_cuda else 'KHONG (dang chay CPU)'}")
    if co_cuda:
        print(f"  GPU          {torch.cuda.get_device_name(0)}")
        vram = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"  VRAM         {vram:.1f} GB")
        print()
        if vram < 5:
            print("  -> Du de SUY LUAN thoai mai.")
            print("  -> Fine-tune yolo11n/s o 640px: duoc, batch 8-16.")
            print("  -> Fine-tune o 960px: batch 2-4, cham.")
            print("  -> yolo11m: thieu VRAM. Dung Kaggle (30h GPU/tuan mien phi).")
        else:
            print("  -> Du de fine-tune thoai mai.")
    else:
        print("\n  Dang chay CPU. Suy luan van duoc, chi cham hon.")
        print("  Muon huan luyen thi cai ban CUDA:")
        print("    pip install torch torchvision \\")
        print("      --index-url https://download.pytorch.org/whl/cu121")
except ImportError:
    pass

print("\n" + "=" * 56)
print("San sang." if ok else "Chay: pip install -r vision/requirements.txt")
