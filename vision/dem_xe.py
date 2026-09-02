"""
Duong ong dem phuong tien: PHAT HIEN -> BAM VET -> DEM QUA VACH -> PARQUET

Day la mat xich tao ra du lieu LUU LUONG cho toan bo luan van. Xem so do co
che o vision/README.md

Cach dung:
    python vision/dem_xe.py --video video.mp4 --site S01
    python vision/dem_xe.py --video video.mp4 --site S01 --vach 0.6 --xem

Tham so:
    --vach   Vi tri vach dem theo ty le chieu cao khung hinh (0.5 = giua)
    --xem    Hien cua so xem truc tiep trong luc chay
    --gioi-han  Chi xu ly N khung hinh dau (de thu nhanh)
"""

import os
import sys
import argparse
from collections import defaultdict
from datetime import datetime, timezone, timedelta

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import cv2
import numpy as np
import pandas as pd
from ultralytics import YOLO

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cau_hinh import (COCO_XE, TEN_VIET, PCU, NGUONG_TIN_CAY, NGUONG_IOU,
                      KICH_THUOC_ANH, QUANG_DUONG_TOI_THIEU, SO_KHUNG_TOI_THIEU,
                      KHOANG_GOP_PHUT)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VN = timezone(timedelta(hours=7))

MAU = {
    "motorcycle": (0, 200, 255),    # vang cam - noi bat vi day la doi tuong chinh
    "car":        (100, 220, 100),
    "bus":        (255, 150, 0),
    "truck":      (0, 120, 255),
    "bicycle":    (200, 200, 200),
}


def phia_nao(diem, a, b):
    """Diem nam phia nao cua vach a->b. Dau doi = da cat qua vach."""
    return np.sign((b[0] - a[0]) * (diem[1] - a[1]) - (b[1] - a[1]) * (diem[0] - a[0]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--site", default="S00", help="Ma diem do, khop voi sites.csv")
    ap.add_argument("--mo-hinh", default="yolo11n.pt",
                    help="yolo11n/s/m.pt hoac duong dan model da fine-tune")
    ap.add_argument("--vach", type=float, default=0.5,
                    help="Vi tri vach dem theo ty le chieu cao (0.5 = giua)")
    ap.add_argument("--xem", action="store_true", help="Hien cua so xem truc tiep")
    ap.add_argument("--gioi-han", type=int, default=0, help="Chi xu ly N khung dau")
    a = ap.parse_args()

    if not os.path.exists(a.video):
        print(f"Khong thay video: {a.video}")
        sys.exit(1)

    cap = cv2.VideoCapture(a.video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    tong_khung = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"Video : {os.path.basename(a.video)}")
    print(f"        {W}x{H}, {fps:.1f} fps, {tong_khung:,} khung "
          f"(~{tong_khung/fps/60:.1f} phut)")
    print(f"Mo hinh: {a.mo_hinh}")

    # --- vach dem ao: ngang khung hinh, o do cao chi dinh ---
    y = int(H * a.vach)
    VACH_A, VACH_B = (0, y), (W, y)
    print(f"Vach dem: ngang, y = {y}px ({a.vach:.0%} chieu cao)\n")

    model = YOLO(a.mo_hinh)

    # --- trang thai bam vet ---
    vet = {}              # id -> {'phia', 'diem_dau', 'so_khung', 'lop', 'da_dem'}
    su_kien = []          # moi lan mot xe qua vach
    dem_theo_lop = defaultdict(int)

    # --- ghi video danh dau de kiem tra bang mat ---
    thu_muc_ra = os.path.join(ROOT, "results", "dem_xe")
    os.makedirs(thu_muc_ra, exist_ok=True)
    duong_ra = os.path.join(thu_muc_ra, f"{a.site}_danhdau.mp4")
    ghi = cv2.VideoWriter(duong_ra, cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))

    khung = 0
    print("Dang xu ly... (Ctrl+C de dung)\n")

    # persist=True -> ByteTrack giu ID xuyen suot cac khung hinh
    for kq in model.track(source=a.video, stream=True, persist=True,
                          tracker="bytetrack.yaml", conf=NGUONG_TIN_CAY,
                          iou=NGUONG_IOU, imgsz=KICH_THUOC_ANH,
                          classes=list(COCO_XE), verbose=False):
        khung += 1
        if a.gioi_han and khung > a.gioi_han:
            break

        anh = kq.orig_img.copy()
        cv2.line(anh, VACH_A, VACH_B, (0, 0, 255), 2)

        if kq.boxes is not None and kq.boxes.id is not None:
            ids = kq.boxes.id.int().cpu().tolist()
            hop = kq.boxes.xyxy.cpu().numpy()
            lops = kq.boxes.cls.int().cpu().tolist()

            for vid, (x1, y1, x2, y2), c in zip(ids, hop, lops):
                lop = COCO_XE.get(c, "khac")
                tam = ((x1 + x2) / 2, (y1 + y2) / 2)
                p = phia_nao(tam, VACH_A, VACH_B)

                if vid not in vet:
                    vet[vid] = {"phia": p, "diem_dau": tam, "so_khung": 1,
                                "lop": lop, "da_dem": False, "lops": [lop]}
                else:
                    v = vet[vid]
                    v["so_khung"] += 1
                    v["lops"].append(lop)

                    # --- DEM: doi phia = da cat qua vach ---
                    quang_duong = abs(tam[1] - v["diem_dau"][1])
                    if (not v["da_dem"] and p != v["phia"] and p != 0
                            and v["so_khung"] >= SO_KHUNG_TOI_THIEU
                            and quang_duong >= QUANG_DUONG_TOI_THIEU):
                        # lop = lop xuat hien nhieu nhat trong ca vet,
                        # KHONG lay lop o dung khung cat vach (de bi nham)
                        lop_cuoi = max(set(v["lops"]), key=v["lops"].count)
                        huong = "xuong" if tam[1] > v["diem_dau"][1] else "len"
                        su_kien.append({
                            "khung": khung,
                            "giay": khung / fps,
                            "track_id": vid,
                            "lop": lop_cuoi,
                            "huong": huong,
                        })
                        dem_theo_lop[lop_cuoi] += 1
                        v["da_dem"] = True
                    v["phia"] = p

                # --- ve ---
                m = MAU.get(lop, (200, 200, 200))
                cv2.rectangle(anh, (int(x1), int(y1)), (int(x2), int(y2)), m, 2)
                cv2.putText(anh, f"{vid}", (int(x1), int(y1) - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, m, 1)

        # --- bang dem goc tren trai ---
        cv2.rectangle(anh, (8, 8), (250, 30 + 22 * (len(dem_theo_lop) + 1)),
                      (0, 0, 0), -1)
        cv2.putText(anh, f"Khung {khung}  |  Tong {sum(dem_theo_lop.values())}",
                    (16, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        for i, (lop, n) in enumerate(sorted(dem_theo_lop.items(), key=lambda x: -x[1])):
            cv2.putText(anh, f"{lop:12s} {n:4d}", (16, 50 + 22 * i),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, MAU.get(lop, (200,)*3), 1)

        ghi.write(anh)
        if a.xem:
            cv2.imshow("dem xe", anh)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        if khung % 200 == 0:
            print(f"  khung {khung:6,}  |  da dem {sum(dem_theo_lop.values()):5,} xe")

    cap.release(); ghi.release(); cv2.destroyAllWindows()

    # -----------------------------------------------------------------
    # Ket qua
    # -----------------------------------------------------------------
    print(f"\n{'='*58}")
    print(f"Da xu ly {khung:,} khung ({khung/fps/60:.1f} phut video)")
    print(f"{'='*58}\n")
    print(f"{'Loai xe':<14}{'So dem':>8}{'PCU':>10}")
    print("-" * 34)
    tong_pcu = 0
    for lop, n in sorted(dem_theo_lop.items(), key=lambda x: -x[1]):
        pcu = n * PCU.get(lop, 1.0)
        tong_pcu += pcu
        print(f"{TEN_VIET.get(lop, lop):<14}{n:>8,}{pcu:>10.1f}")
    print("-" * 34)
    print(f"{'TONG':<14}{sum(dem_theo_lop.values()):>8,}{tong_pcu:>10.1f}")

    phut = khung / fps / 60
    if phut > 0:
        print(f"\nQuy ra gio: {sum(dem_theo_lop.values())/phut*60:,.0f} xe/gio"
              f"  |  {tong_pcu/phut*60:,.0f} PCU/gio")

    # -----------------------------------------------------------------
    # Ghi Parquet theo dung hop dong du lieu (docs/plan/B-kien-truc-ky-thuat.md)
    # -----------------------------------------------------------------
    if su_kien:
        df = pd.DataFrame(su_kien)
        moc = datetime.now(VN).replace(second=0, microsecond=0)
        df["ts_15min"] = df.giay.apply(
            lambda g: moc + timedelta(minutes=int(g // 60 // KHOANG_GOP_PHUT) * KHOANG_GOP_PHUT))

        gop = (df.groupby(["ts_15min", "huong", "lop"])
                 .size().reset_index(name="count"))
        gop["site_id"] = a.site
        gop["edge_id"] = -1          # dien o Giai doan 4 khi anh xa len do thi
        gop["vehicle_class"] = gop.lop
        gop["direction"] = gop.huong
        gop["pcu"] = gop.apply(lambda r: r["count"] * PCU.get(r.lop, 1.0), axis=1)
        gop = gop[["site_id", "edge_id", "ts_15min", "direction",
                   "vehicle_class", "count", "pcu"]]

        d = os.path.join(ROOT, "data", "processed")
        os.makedirs(d, exist_ok=True)
        f = os.path.join(d, "counts.parquet")
        if os.path.exists(f):
            gop = pd.concat([pd.read_parquet(f), gop], ignore_index=True)
        gop.to_parquet(f, index=False)
        print(f"\nDa ghi {len(gop):,} dong -> data/processed/counts.parquet")

    print(f"Video danh dau -> {duong_ra}")
    print("\nMo video do de KIEM TRA BANG MAT truoc khi tin so lieu.")


if __name__ == "__main__":
    main()
