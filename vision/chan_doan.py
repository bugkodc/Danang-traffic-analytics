"""
THI NGHIEM CHAN DOAN - do ty le mo hinh goc SOT XE MAY.

Day la thi nghiem RE NHAT cho gia thuyet DAT NHAT cua luan van:
"mo hinh huan luyen tren du lieu giao thong phuong Tay suy giam manh tren
giao thong hon hop do xe may chi phoi o Viet Nam".

Neu gia thuyet sai, biet ngay hom nay - thay vi sau 4 thang gan nhan.

Cach dung:
    # Neu thu muc anh CO SAN NHAN (dinh dang YOLO) - do khach quan:
    python vision/chan_doan.py --anh duong/dan/images --nhan duong/dan/labels

    # Neu chi co anh, khong co nhan - chi thong ke so luong phat hien:
    python vision/chan_doan.py --anh duong/dan/anh

Ket qua:
    results/chan_doan_yolo.csv   bang so
    results/chan_doan/           anh co hop bao de xem mat thuong
"""

import os
import sys
import glob
import argparse
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import cv2
import numpy as np
import pandas as pd
from ultralytics import YOLO

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cau_hinh import COCO_XE, TEN_VIET, NGUONG_TIN_CAY, KICH_THUOC_ANH

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MAU = {"motorcycle": (0, 200, 255), "car": (100, 220, 100), "bus": (255, 150, 0),
       "truck": (0, 120, 255), "bicycle": (200, 200, 200)}


def doc_nhan(f, W, H):
    """Doc nhan dinh dang YOLO: <lop> <cx> <cy> <w> <h>, toa do chuan hoa."""
    hop = []
    if not os.path.exists(f):
        return hop
    for d in open(f, encoding="utf-8"):
        p = d.split()
        if len(p) < 5:
            continue
        c, cx, cy, w, h = int(p[0]), *map(float, p[1:5])
        hop.append((c, (cx - w/2)*W, (cy - h/2)*H, (cx + w/2)*W, (cy + h/2)*H))
    return hop


def iou(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    if x2 <= x1 or y2 <= y1:
        return 0.0
    giao = (x2 - x1) * (y2 - y1)
    return giao / ((a[2]-a[0])*(a[3]-a[1]) + (b[2]-b[0])*(b[3]-b[1]) - giao)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--anh", required=True, help="Thu muc chua anh")
    ap.add_argument("--nhan", default=None,
                    help="Thu muc chua nhan YOLO (.txt cung ten anh)")
    ap.add_argument("--mo-hinh", default="yolo11n.pt")
    ap.add_argument("--so-anh", type=int, default=200, help="Chi xu ly N anh dau")
    ap.add_argument("--luu-anh", type=int, default=20, help="Luu N anh co hop bao")
    ap.add_argument("--lop-2banh", type=int, default=0,
                    help="Chi so lop '2 banh' trong data.yaml cua bo du lieu")
    a = ap.parse_args()

    files = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.PNG"):
        files += glob.glob(os.path.join(a.anh, ext))
    files = sorted(files)[:a.so_anh]
    if not files:
        print(f"Khong tim thay anh trong {a.anh}")
        sys.exit(1)

    print(f"Mo hinh : {a.mo_hinh}  (TRONG SO GOC, chua fine-tune)")
    print(f"So anh  : {len(files):,}")
    print(f"Co nhan : {'CO - do khach quan' if a.nhan else 'KHONG - chi thong ke'}\n")

    model = YOLO(a.mo_hinh)
    ra = os.path.join(ROOT, "results", "chan_doan")
    os.makedirs(ra, exist_ok=True)

    phat_hien = defaultdict(int)
    that = defaultdict(int)
    bat_duoc = defaultdict(int)
    da_luu = 0

    for i, f in enumerate(files):
        anh = cv2.imread(f)
        if anh is None:
            continue
        H, W = anh.shape[:2]

        kq = model.predict(anh, conf=NGUONG_TIN_CAY, imgsz=KICH_THUOC_ANH,
                           classes=list(COCO_XE), verbose=False)[0]
        du_doan = []
        if kq.boxes is not None:
            for (x1, y1, x2, y2), c in zip(kq.boxes.xyxy.cpu().numpy(),
                                           kq.boxes.cls.int().cpu().tolist()):
                lop = COCO_XE.get(c, "khac")
                du_doan.append((lop, x1, y1, x2, y2))
                phat_hien[lop] += 1

        # --- doi chieu voi nhan that neu co ---
        if a.nhan:
            fn = os.path.join(a.nhan, os.path.splitext(os.path.basename(f))[0] + ".txt")
            for c, gx1, gy1, gx2, gy2 in doc_nhan(fn, W, H):
                # nhan cua bo du lieu ngoai co the danh so lop khac COCO;
                # o day gia dinh lop 0 = xe may (kiem tra data.yaml cua bo do)
                # Bo du lieu ngoai danh so lop KHAC COCO. Vi du bo
                # mixed-traffic gop xe may + xe dap thanh mot lop "2-wheeler",
                # trong khi COCO tach rieng motorcycle(3) va bicycle(1).
                # Phai anh xa cho dung, neu khong so lieu vo nghia.
                if c == a.lop_2banh:
                    lop_that = "2 banh (xe may/xe dap)"
                    khop = ("motorcycle", "bicycle")
                else:
                    lop_that = f"lop_{c}"
                    khop = None
                that[lop_that] += 1
                # chi tinh la BAT DUOC neu hop trung VA dung nhom lop
                for d in du_doan:
                    if iou((gx1, gy1, gx2, gy2), d[1:]) > 0.4:
                        if khop is None or d[0] in khop:
                            bat_duoc[lop_that] += 1
                            break

        if da_luu < a.luu_anh:
            for lop, x1, y1, x2, y2 in du_doan:
                m = MAU.get(lop, (200,)*3)
                cv2.rectangle(anh, (int(x1), int(y1)), (int(x2), int(y2)), m, 2)
                cv2.putText(anh, lop[:4], (int(x1), int(y1)-4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, m, 1)
            cv2.imwrite(os.path.join(ra, f"{da_luu:03d}_{os.path.basename(f)}"), anh)
            da_luu += 1

        if (i + 1) % 50 == 0:
            print(f"  {i+1:,}/{len(files):,} anh")

    # -----------------------------------------------------------------
    print(f"\n{'='*62}")
    print("KET QUA - MO HINH GOC (chua fine-tune)")
    print(f"{'='*62}\n")

    dong = []
    if a.nhan and that:
        print(f"{'Loai xe':<14}{'Nhan that':>11}{'Bat duoc':>11}{'SOT':>9}{'Ty le sot':>12}")
        print("-" * 62)
        for lop in sorted(that, key=lambda k: -that[k]):
            n, b = that[lop], bat_duoc[lop]
            sot = n - b
            ty = sot / n * 100 if n else 0
            print(f"{TEN_VIET.get(lop, lop):<14}{n:>11,}{b:>11,}{sot:>9,}{ty:>11.1f}%")
            dong.append({"lop": lop, "nhan_that": n, "bat_duoc": b,
                         "sot": sot, "ty_le_sot_pct": round(ty, 1)})
        print()
        tm = that.get("2 banh (xe may/xe dap)", 0)
        if tm:
            ty = (tm - bat_duoc.get("2 banh (xe may/xe dap)", 0)) / tm * 100
            print(f"*** TY LE SOT XE MAY: {ty:.1f}% ***\n")
            if ty < 15:
                print("  -> Khoang cach mien NHO. Luan diem yeu.")
                print("     Chuyen trong tam sang danh gia phan tang theo dieu kien")
                print("     (mua / dem / mat do cao), hoac sang bai toan DEM.")
            elif ty <= 40:
                print("  -> Khoang cach mien RO RET. Day la kich ban ly tuong.")
                print("     Viet thang con so nay vao de cuong lam bang chung.")
            else:
                print("  -> Khoang cach RAT LON. Kiem tra lai chat luong anh,")
                print("     goc chup va cach danh so lop trong data.yaml truoc khi mung.")
    else:
        print("Khong co nhan that -> chi thong ke so luong phat hien.\n")
        print(f"{'Loai xe':<14}{'So phat hien':>14}{'TB moi anh':>13}")
        print("-" * 42)
        for lop in sorted(phat_hien, key=lambda k: -phat_hien[k]):
            n = phat_hien[lop]
            print(f"{TEN_VIET.get(lop, lop):<14}{n:>14,}{n/len(files):>13.1f}")
            dong.append({"lop": lop, "so_phat_hien": n,
                         "tb_moi_anh": round(n/len(files), 2)})
        print("\nDe do duoc TY LE SOT, can bo anh CO NHAN.")
        print("Goi y: Roboflow Universe -> car-classification/vietnamese-vehicle")
        print("       (1.547 anh, co san nhan, tai ve dinh dang YOLO)")

    if dong:
        os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
        p = os.path.join(ROOT, "results", "chan_doan_yolo.csv")
        pd.DataFrame(dong).to_csv(p, index=False, encoding="utf-8-sig")
        print(f"\nDa ghi: {p}")
    print(f"Anh co hop bao: {ra}  ({da_luu} anh)")
    print("\nMO CAC ANH DO XEM BANG MAT - so lieu chi dang tin khi anh nhin dung.")


if __name__ == "__main__":
    main()
