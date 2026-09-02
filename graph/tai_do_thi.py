"""
Tai do thi duong bo Da Nang tu OpenStreetMap va luu ra dia.

Tai HAI pham vi de so sanh:
  - danang_cu   : Da Nang truoc sap nhap
  - danang_moi  : Da Nang + Quang Nam cu (sau sap nhap 7/2025)

Chenh lech giua hai pham vi la lap luan truc tiep cho quy mo du lieu lon
trong de cuong. Xem docs/plan/00b-giai-doan-0-de-cuong.md muc 1.1

Cach dung:
    python graph/tai_do_thi.py
    python graph/tai_do_thi.py --chi danang_cu     # chi tai mot pham vi
"""

import os
import sys

# Console Windows mac dinh dung cp1252, khong in duoc tieng Viet.
# Ep stdout/stderr sang UTF-8 de tranh UnicodeEncodeError khi in duong dan.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import time
import argparse

import osmnx as ox

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_DIR = os.path.join(ROOT, "data", "raw", "osm")

# Cau hinh OSMnx: bat cache de khong tai lai khi chay lan hai
ox.settings.use_cache = True
ox.settings.cache_folder = os.path.join(OUT_DIR, "cache")
ox.settings.log_console = True
ox.settings.requests_timeout = 300

# Cac pham vi can tai.
# Moi pham vi thu lan luot cac truy van trong danh sach cho den khi thanh cong.
# Neu truy van theo ten that bai (ranh gioi sau sap nhap chua cap nhat trong OSM),
# roi ve bbox thu cong.
PHAM_VI = {
    "danang_cu": {
        "mo_ta": "Da Nang truoc sap nhap",
        "truy_van": ["Da Nang, Vietnam", "Thanh pho Da Nang, Vietnam"],
        # (west, south, east, north) - bao Da Nang cu
        "bbox": (107.96, 15.92, 108.35, 16.20),
    },
    "danang_moi": {
        "mo_ta": "Da Nang + Quang Nam cu (sau sap nhap 7/2025)",
        "truy_van": [
            ["Da Nang, Vietnam", "Quang Nam, Vietnam"],   # ghep hai don vi cu
        ],
        # bbox bao ca hai - dung khi truy van theo ten that bai
        "bbox": (107.13, 14.90, 108.80, 16.35),
    },
}


def tai_theo_ten(truy_van):
    """Thu tai theo ten dia danh. Tra ve graph hoac None."""
    try:
        if isinstance(truy_van, list):
            print(f"  Thu ghep nhieu don vi: {truy_van}")
            return ox.graph_from_place(truy_van, network_type="drive")
        print(f"  Thu truy van: {truy_van!r}")
        return ox.graph_from_place(truy_van, network_type="drive")
    except Exception as e:
        print(f"  -> That bai: {type(e).__name__}: {str(e)[:120]}")
        return None


def tai_theo_bbox(bbox):
    """Roi ve tai theo hop toa do."""
    print(f"  Roi ve bbox: {bbox}")
    try:
        # OSMnx >= 2.0 nhan bbox dang (west, south, east, north)
        return ox.graph_from_bbox(bbox=bbox, network_type="drive")
    except TypeError:
        # OSMnx < 2.0 nhan (north, south, east, west)
        w, s, e, n = bbox
        return ox.graph_from_bbox(north=n, south=s, east=e, west=w,
                                  network_type="drive")


def tai_mot_pham_vi(ma, cau_hinh):
    dich = os.path.join(OUT_DIR, f"{ma}.graphml")
    if os.path.exists(dich):
        print(f"[{ma}] Da co san: {dich} — bo qua. Xoa file de tai lai.")
        return dich

    print(f"\n[{ma}] {cau_hinh['mo_ta']}")
    t0 = time.time()

    G = None
    for tv in cau_hinh["truy_van"]:
        G = tai_theo_ten(tv)
        if G is not None:
            print(f"  -> Thanh cong bang truy van theo ten")
            break

    if G is None:
        print("  Tat ca truy van theo ten deu that bai.")
        G = tai_theo_bbox(cau_hinh["bbox"])
        print("  -> Thanh cong bang bbox. GHI RO trong de cuong la dung bbox thu cong.")

    os.makedirs(OUT_DIR, exist_ok=True)
    ox.save_graphml(G, dich)
    phut = (time.time() - t0) / 60
    print(f"[{ma}] Xong sau {phut:.1f} phut: "
          f"{G.number_of_nodes():,} dinh, {G.number_of_edges():,} canh")
    print(f"[{ma}] Luu tai: {dich}")
    return dich


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chi", choices=list(PHAM_VI), default=None,
                    help="Chi tai mot pham vi")
    args = ap.parse_args()

    can_tai = {args.chi: PHAM_VI[args.chi]} if args.chi else PHAM_VI

    print("=" * 70)
    print("TAI DO THI DUONG BO TU OPENSTREETMAP")
    print("=" * 70)
    print("Luu y: pham vi 'danang_moi' rat lon, co the mat 10-40 phut")
    print("va can bo nho >8GB. Neu that bai, chay rieng --chi danang_cu truoc.")

    for ma, ch in can_tai.items():
        try:
            tai_mot_pham_vi(ma, ch)
        except MemoryError:
            print(f"[{ma}] HET BO NHO. Bo qua pham vi nay, dung danang_cu "
                  f"cho cac thi nghiem chinh.")
        except Exception as e:
            print(f"[{ma}] LOI: {type(e).__name__}: {e}")

    print("\nTiep theo: python graph/thong_ke.py")


if __name__ == "__main__":
    main()
