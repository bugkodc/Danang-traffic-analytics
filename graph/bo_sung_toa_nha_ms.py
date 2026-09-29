"""
Bo sung toa nha 3D con thieu trong OSM bang Microsoft Building Footprints.

VAN DE: OSM chi co 2.144 building-polygon cho ca quan Hai Chau (22,8 km2),
tap trung gan het vao khu trung tam/gan song - phan lon khu dan cu KHONG
duoc cong dong OSM ve toi. Xem results/ hoac lich su chat de biet chi tiet
so lieu kiem chung.

Microsoft Building Footprints la bo du lieu cong khai (ODbL), suy ra hinh
dang toa nha bang AI tu anh ve tinh, phu gan nhu toan bo Viet Nam - dung de
LAP DAY cho vung OSM con trong, KHONG thay the OSM (OSM uu tien hon vi la
du lieu do nguoi ve, chinh xac hon AI).

Cach dung (chi chay 1 lan, hoac khi doi khu vuc):
    1. Tai file quadkey phu hop tu dataset-links.csv (xem huong dan trong
       README hoac lich su chat - can tinh quadkey bang toa do bbox).
    2. python graph/bo_sung_toa_nha_ms.py \
         --nguon data/raw/ms_buildings/132213001.csv.gz \
         --bbox 108.18883 16.02131 108.236 16.10365
"""

import os
import sys
import gzip
import json
import argparse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from shapely.geometry import shape, mapping, box
from shapely.strtree import STRtree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DICH = os.path.join(ROOT, "serving", "toa_nha.geojson")

M2_TOI_THIEU_MAC_DINH = 300   # cao hon nguong OSM (120) - MS qua nhieu, tam
                              # giac hoa het se treo trinh duyet vai chuc giay
SAI_SO_HINH = 0.00003
CAO_MAC_DINH_MS = 8.0   # MS phan lon height=-1 (khong uoc luong duoc)


def doc_osm_hien_co():
    if not os.path.exists(DICH):
        print(f"Chua co {DICH} - chay graph/xuat_geojson.py truoc.")
        sys.exit(1)
    with open(DICH, encoding="utf-8") as f:
        gj = json.load(f)
    polys = []
    for feat in gj["features"]:
        try:
            polys.append(shape(feat["geometry"]))
        except Exception:
            continue
    return gj["features"], polys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nguon", required=True, help="File .csv.gz da tai tu bfppub")
    ap.add_argument("--bbox", nargs=4, type=float, required=True,
                    metavar=("TAY", "NAM", "DONG", "BAC"))
    ap.add_argument("--nguong-m2", type=float, default=M2_TOI_THIEU_MAC_DINH,
                    help=f"Dien tich toi thieu (m2) de giu building tu MS "
                         f"(mac dinh {M2_TOI_THIEU_MAC_DINH})")
    a = ap.parse_args()
    m2_toi_thieu = a.nguong_m2

    w, s, e, n = a.bbox
    khung = box(w, s, e, n)

    print("Doc toa nha OSM hien co...")
    feat_osm, poly_osm = doc_osm_hien_co()
    print(f"  {len(feat_osm):,} toa nha OSM")

    cay_osm = STRtree(poly_osm) if poly_osm else None

    print(f"Doc va loc {a.nguon} theo bbox...")
    them = 0
    trung = 0
    qua_nho = 0
    loi = 0
    feat_ms = []

    with gzip.open(a.nguon, "rt", encoding="utf-8") as f:
        for dong in f:
            dong = dong.strip()
            if not dong:
                continue
            try:
                obj = json.loads(dong)
                geom = shape(obj["geometry"])
            except Exception:
                loi += 1
                continue

            if not geom.intersects(khung):
                continue

            # dien tich xap xi m2 (1 do ~ 111.000 m o kinh do, ~ 111.000*cos(lat) o vi do)
            if geom.area * (111000 ** 2) < m2_toi_thieu:
                qua_nho += 1
                continue

            # bo qua neu da co building OSM trung vi tri (uu tien du lieu OSM)
            if cay_osm is not None:
                tam = geom.centroid
                gan_nhat = cay_osm.query(tam.buffer(0.00005))
                trung_that = False
                for idx in gan_nhat:
                    if poly_osm[idx].intersects(tam.buffer(0.00005)):
                        trung_that = True
                        break
                if trung_that:
                    trung += 1
                    continue

            cao = obj["properties"].get("height", -1.0)
            cao = cao if cao and cao > 0 else CAO_MAC_DINH_MS

            g_gon = geom.simplify(SAI_SO_HINH, preserve_topology=True)
            feat_ms.append({
                "type": "Feature",
                "geometry": mapping(g_gon),
                "properties": {"c": round(float(cao), 1), "nguon": "ms"},
            })
            them += 1

    print(f"\n  Them moi (MS, khong trung OSM): {them:,}")
    print(f"  Bo vi trung voi OSM:            {trung:,}")
    print(f"  Bo vi qua nho (<{m2_toi_thieu:.0f} m2):    {qua_nho:,}")
    if loi:
        print(f"  Dong loi khong doc duoc:         {loi:,}")

    tong = feat_osm + feat_ms
    with open(DICH, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": tong},
                  f, ensure_ascii=False, separators=(",", ":"))
    print(f"\n-> Da ghi {DICH}: {len(tong):,} toa nha "
          f"({len(feat_osm):,} OSM + {them:,} MS), "
          f"{os.path.getsize(DICH)/1024:,.0f} KB")


if __name__ == "__main__":
    main()
