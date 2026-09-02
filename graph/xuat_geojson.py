"""
Xuat cac truc duong chinh tu do thi OSM ra GeoJSON de web tu ve.

Ly do: mang o Viet Nam hay chan cac may chu tile ban do (CARTO, OpenFreeMap,
OSM tiles). Thay vi phu thuoc CDN ben ngoai, ta ve ban do bang chinh du lieu
do thi da tai ve. Uu diem:
  - Khong can internet, khong bao gio hong
  - Hien dung MANG LUOI DUONG cua luan van, khong phai nen ban do chung chung
  - File nho, tai mot lan

Chay:
    python graph/xuat_geojson.py
"""

import os
import sys
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import osmnx as ox

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
NGUON = os.path.join(ROOT, "data", "raw", "osm", "danang_cu.graphml")
DICH = os.path.join(ROOT, "serving", "duong_chinh.geojson")

# Chi lay truc chinh - du de nhan ra hinh thanh pho, file nho
LOAI_LAY = {
    "motorway": 3.0, "motorway_link": 1.6,
    "trunk": 2.6, "trunk_link": 1.5,
    "primary": 2.2, "primary_link": 1.3,
    "secondary": 1.6, "secondary_link": 1.1,
}

# tertiary chiem gan mot nua so doan ma khong giup nhan dien thanh pho,
# bo di de file nho hon mot nua. Them lai bang --day-du neu can.


def lam_gon(toa_do, buoc=10):
    """Bot so chu so thap phan va bo bot diem trung gian de file nho."""
    ra = []
    for i, (x, y) in enumerate(toa_do):
        if i == 0 or i == len(toa_do) - 1 or i % buoc == 0:
            ra.append([round(x, 5), round(y, 5)])
    return ra if len(ra) >= 2 else [[round(x, 5), round(y, 5)] for x, y in toa_do[:2]]


def main():
    if not os.path.exists(NGUON):
        print(f"Chua co {NGUON}")
        print("Chay truoc: python graph/tai_do_thi.py --chi danang_cu")
        sys.exit(1)

    print("Dang doc do thi...")
    G = ox.load_graphml(NGUON)
    print(f"  {G.number_of_nodes():,} dinh, {G.number_of_edges():,} canh")

    features, dem = [], {}
    for u, v, d in G.edges(data=True):
        hw = d.get("highway")
        if isinstance(hw, (list, tuple)):
            hw = hw[0] if hw else None
        hw = str(hw)
        if hw not in LOAI_LAY:
            continue

        # hinh hoc: dung geometry neu co, khong thi noi thang hai dinh
        geom = d.get("geometry")
        if geom is not None:
            toa_do = list(geom.coords)
        else:
            toa_do = [(G.nodes[u]["x"], G.nodes[u]["y"]),
                      (G.nodes[v]["x"], G.nodes[v]["y"])]

        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": lam_gon(toa_do)},
            "properties": {"h": hw, "w": LOAI_LAY[hw]},
        })
        dem[hw] = dem.get(hw, 0) + 1

    os.makedirs(os.path.dirname(DICH), exist_ok=True)
    with open(DICH, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": features},
                  f, ensure_ascii=False, separators=(",", ":"))

    kb = os.path.getsize(DICH) / 1024
    print(f"\nDa xuat {len(features):,} doan duong -> {DICH}")
    print(f"Dung luong: {kb:,.0f} KB")
    print("\nPhan bo theo loai:")
    for k in sorted(dem, key=lambda k: -dem[k]):
        print(f"  {k:<18} {dem[k]:>7,}")


if __name__ == "__main__":
    main()
