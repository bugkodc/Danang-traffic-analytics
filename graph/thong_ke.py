"""
Lap BANG 1 cua de cuong: thong ke do thi duong bo Da Nang.

Sinh ra:
    results/bang1_do_thi.csv   - de xu ly tiep
    results/bang1_do_thi.md    - dan thang vao de cuong

Hai con so quan trong nhat la % canh thieu maxspeed va % canh thieu lanes:
chung dinh luong khoi luong cong viec bo khuyet thuoc tinh, va ban than
viec bo khuyet do la mot muc dong gop chinh danh cua luan van.

Cach dung:
    python graph/thong_ke.py
"""

import os
import sys

# Console Windows mac dinh dung cp1252, khong in duoc tieng Viet.
# Ep stdout/stderr sang UTF-8 de tranh UnicodeEncodeError khi in duong dan.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import glob
from collections import Counter

import networkx as nx
import osmnx as ox
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OSM_DIR = os.path.join(ROOT, "data", "raw", "osm")
RESULTS_DIR = os.path.join(ROOT, "results")


def _co_gia_tri(v):
    """OSM tra ve gia tri co the la None, chuoi rong, hoac list."""
    if v is None:
        return False
    if isinstance(v, (list, tuple)):
        return len(v) > 0 and any(_co_gia_tri(x) for x in v)
    return str(v).strip() not in ("", "none", "None", "unknown")


def thong_ke_mot_do_thi(duong_dan):
    ma = os.path.splitext(os.path.basename(duong_dan))[0]
    print(f"\n[{ma}] Dang doc...")
    G = ox.load_graphml(duong_dan)

    n_dinh = G.number_of_nodes()
    n_canh = G.number_of_edges()

    # --- thuoc tinh canh ---
    tong_dai_m = 0.0
    thieu_maxspeed = 0
    thieu_lanes = 0
    mot_chieu = 0
    loai_duong = Counter()

    for _, _, d in G.edges(data=True):
        tong_dai_m += float(d.get("length", 0) or 0)

        if not _co_gia_tri(d.get("maxspeed")):
            thieu_maxspeed += 1
        if not _co_gia_tri(d.get("lanes")):
            thieu_lanes += 1
        if d.get("oneway") in (True, "True", "true", "yes"):
            mot_chieu += 1

        hw = d.get("highway")
        if isinstance(hw, (list, tuple)):
            hw = hw[0] if hw else "khong_ro"
        loai_duong[str(hw)] += 1

    # --- lien thong ---
    n_tp_manh = nx.number_strongly_connected_components(G)
    tp_lon_nhat = max(nx.strongly_connected_components(G), key=len)
    ty_le_tp_lon = len(tp_lon_nhat) / n_dinh * 100 if n_dinh else 0

    # --- den tin hieu ---
    den_tin_hieu = sum(
        1 for _, d in G.nodes(data=True)
        if str(d.get("highway", "")).find("traffic_signals") >= 0
    )

    return {
        "pham_vi": ma,
        "so_dinh": n_dinh,
        "so_canh": n_canh,
        "tong_chieu_dai_km": round(tong_dai_m / 1000, 1),
        "chieu_dai_canh_tb_m": round(tong_dai_m / n_canh, 1) if n_canh else 0,
        "bac_trung_binh": round(2 * n_canh / n_dinh, 2) if n_dinh else 0,
        "canh_mot_chieu": mot_chieu,
        "ty_le_mot_chieu_pct": round(mot_chieu / n_canh * 100, 1) if n_canh else 0,
        "thieu_maxspeed": thieu_maxspeed,
        "ty_le_thieu_maxspeed_pct": round(thieu_maxspeed / n_canh * 100, 1) if n_canh else 0,
        "thieu_lanes": thieu_lanes,
        "ty_le_thieu_lanes_pct": round(thieu_lanes / n_canh * 100, 1) if n_canh else 0,
        "so_tp_lien_thong_manh": n_tp_manh,
        "ty_le_tp_lon_nhat_pct": round(ty_le_tp_lon, 1),
        "nut_den_tin_hieu": den_tin_hieu,
        "_loai_duong": loai_duong,
    }


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    files = sorted(glob.glob(os.path.join(OSM_DIR, "*.graphml")))

    if not files:
        print("Chua co file .graphml nao. Chay truoc:  python graph/tai_do_thi.py")
        return

    ket_qua = [thong_ke_mot_do_thi(f) for f in files]

    # --- CSV ---
    df = pd.DataFrame([{k: v for k, v in r.items() if not k.startswith("_")}
                       for r in ket_qua])
    csv_path = os.path.join(RESULTS_DIR, "bang1_do_thi.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    # --- Markdown de dan vao de cuong ---
    nhan = {
        "so_dinh": "Số đỉnh",
        "so_canh": "Số cạnh",
        "tong_chieu_dai_km": "Tổng chiều dài mạng (km)",
        "chieu_dai_canh_tb_m": "Chiều dài cạnh trung bình (m)",
        "bac_trung_binh": "Bậc trung bình của đỉnh",
        "canh_mot_chieu": "Số cạnh một chiều",
        "ty_le_mot_chieu_pct": "Tỷ lệ một chiều (%)",
        "thieu_maxspeed": "Số cạnh thiếu `maxspeed`",
        "ty_le_thieu_maxspeed_pct": "**% cạnh thiếu `maxspeed`**",
        "thieu_lanes": "Số cạnh thiếu `lanes`",
        "ty_le_thieu_lanes_pct": "**% cạnh thiếu `lanes`**",
        "so_tp_lien_thong_manh": "Số thành phần liên thông mạnh",
        "ty_le_tp_lon_nhat_pct": "Tỷ lệ đỉnh trong thành phần lớn nhất (%)",
        "nut_den_tin_hieu": "Số nút có đèn tín hiệu",
    }
    cot = [r["pham_vi"] for r in ket_qua]

    md = ["# Bảng 1. Thống kê đồ thị đường bộ Đà Nẵng từ OpenStreetMap", "",
          f"*Sinh tự động bởi `graph/thong_ke.py` — {pd.Timestamp.now():%d/%m/%Y}*", "",
          "| Chỉ số | " + " | ".join(cot) + " |",
          "|---|" + "---|" * len(cot)]
    for k, ten in nhan.items():
        md.append(f"| {ten} | " + " | ".join(f"{r[k]:,}" if isinstance(r[k], int)
                                             else str(r[k]) for r in ket_qua) + " |")

    md += ["", "## Phân bố theo loại đường (`highway=*`)", ""]
    tat_ca_loai = sorted({l for r in ket_qua for l in r["_loai_duong"]},
                         key=lambda l: -sum(r["_loai_duong"].get(l, 0) for r in ket_qua))
    md += ["| Loại đường | " + " | ".join(cot) + " |",
           "|---|" + "---|" * len(cot)]
    for l in tat_ca_loai:
        md.append(f"| `{l}` | " + " | ".join(f"{r['_loai_duong'].get(l, 0):,}"
                                             for r in ket_qua) + " |")

    md_path = os.path.join(RESULTS_DIR, "bang1_do_thi.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    # --- in ra man hinh ---
    print("\n" + "=" * 70)
    for r in ket_qua:
        print(f"\n[{r['pham_vi']}]")
        for k, ten in nhan.items():
            ten_sach = ten.replace("**", "").replace("`", "")
            print(f"  {ten_sach:42s} {r[k]:>12,}" if isinstance(r[k], int)
                  else f"  {ten_sach:42s} {r[k]:>12}")
    print("\n" + "=" * 70)
    print(f"Da ghi: {csv_path}")
    print(f"Da ghi: {md_path}  <- dan thang vao de cuong")


if __name__ == "__main__":
    main()
