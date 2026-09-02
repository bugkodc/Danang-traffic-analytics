"""
Xuat du lieu ve ban do tu OpenStreetMap ra GeoJSON de web tu ve.

Ly do khong dung may chu tile ben ngoai: mang o Viet Nam hay chan CARTO /
OpenFreeMap / OSM tiles. Ve thang tu du lieu cua luan van thi:
  - Khong can internet, khong bao gio hong
  - Hien dung MANG LUOI DUONG la doi tuong nghien cuu
  - Khong ton quota TomTom (tile ban do tinh chung han muc voi API giao thong)

Sinh ra 2 file trong serving/:
  duong_chinh.geojson  - mang luoi duong theo cap
  mat_nuoc.geojson     - song, bien, ho  (thu nay quan trong: thieu no thi
                         ban do chi con may duong ke lo lung, khong ra hinh)

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
THU_MUC = os.path.join(ROOT, "serving")

ox.settings.use_cache = True
ox.settings.cache_folder = os.path.join(ROOT, "data", "raw", "osm", "cache")
ox.settings.requests_timeout = 300

# Do rong tuong doi khi ve. tertiary/residential mong de tao ket cau do thi
# ma khong lam roi mat.
LOAI_LAY = {
    "motorway": 2.6, "motorway_link": 1.3,
    "trunk": 2.2, "trunk_link": 1.2,
    "primary": 1.8, "primary_link": 1.0,
    "secondary": 1.3, "secondary_link": 0.8,
    "tertiary": 0.8, "tertiary_link": 0.6,
}

# Bo residential (144k doan) va unclassified (15k): chung chiem 83% so doan
# nhung o muc nhin ca thanh pho thi chi lam ban do bi be. Muon chi tiet hon
# thi them lai va thu hep BBOX ve hanh lang nghien cuu.

# Bao Da Nang cu - dung de lay mat nuoc
BBOX = (107.96, 15.92, 108.40, 16.20)      # west, south, east, north


def lam_gon(toa_do, buoc=15):
    ra = []
    for i, (x, y) in enumerate(toa_do):
        if i == 0 or i == len(toa_do) - 1 or i % buoc == 0:
            ra.append([round(x, 5), round(y, 5)])
    return ra if len(ra) >= 2 else [[round(x, 5), round(y, 5)] for x, y in toa_do[:2]]


def xuat_duong():
    if not os.path.exists(NGUON):
        print(f"Chua co {NGUON}")
        print("Chay truoc: python graph/tai_do_thi.py --chi danang_cu")
        sys.exit(1)

    print("Doc do thi duong...")
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

        geom = d.get("geometry")
        toa_do = (list(geom.coords) if geom is not None
                  else [(G.nodes[u]["x"], G.nodes[u]["y"]),
                        (G.nodes[v]["x"], G.nodes[v]["y"])])

        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": lam_gon(toa_do)},
            "properties": {"h": hw, "w": LOAI_LAY[hw]},
        })
        dem[hw] = dem.get(hw, 0) + 1

    ghi("duong_chinh.geojson", features)
    print("\nPhan bo theo loai duong:")
    for k in sorted(dem, key=lambda k: -dem[k]):
        print(f"  {k:<18} {dem[k]:>7,}")


def xuat_mat_nuoc():
    """Song, bien, ho. Khong co lop nay thi ban do khong ra hinh thanh pho."""
    print("\nTai mat nuoc tu OSM (co the mat 1-3 phut)...")
    features = []
    try:
        import geopandas as gpd
        from shapely.geometry import mapping

        w, s, e, n = BBOX
        gdf = ox.features_from_bbox(
            bbox=(w, s, e, n),
            tags={"natural": ["water", "coastline"],
                  "waterway": ["riverbank"],
                  "landuse": ["reservoir"]},
        )
        for _, row in gdf.iterrows():
            g = row.geometry
            if g is None or g.geom_type not in ("Polygon", "MultiPolygon", "LineString"):
                continue
            gj = mapping(g.simplify(0.0002, preserve_topology=True))
            features.append({"type": "Feature", "geometry": gj, "properties": {}})
        print(f"  Lay duoc {len(features):,} vung nuoc")
    except Exception as ex:
        print(f"  Khong lay duoc mat nuoc: {type(ex).__name__}: {str(ex)[:120]}")
        print("  Ban do van chay, chi thieu song/bien.")

    ghi("mat_nuoc.geojson", features)


def ghi(ten, features):
    os.makedirs(THU_MUC, exist_ok=True)
    dich = os.path.join(THU_MUC, ten)
    with open(dich, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": features},
                  f, ensure_ascii=False, separators=(",", ":"))
    print(f"\n-> {ten}: {len(features):,} doi tuong, "
          f"{os.path.getsize(dich)/1024:,.0f} KB")


if __name__ == "__main__":
    xuat_duong()
    xuat_mat_nuoc()
    print("\nXong. Tai lai trang web de xem.")
