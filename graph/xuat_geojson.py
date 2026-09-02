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
import math

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

# Vung loi do thi - dung de lay TOA NHA 3D. Hep hon nhieu vi so toa nha
# rat lon; lay ca thanh pho thi file nang hang chuc MB va may ve khong noi.
BBOX_NHA = (108.175, 16.020, 108.255, 16.095)

# Chieu cao mac dinh theo loai nha, dung khi OSM khong ghi height/levels.
# Du lieu chieu cao o Viet Nam rat thua nen phan lon se dung gia tri nay.
CAO_MAC_DINH = {
    "apartments": 18, "commercial": 15, "retail": 10, "office": 24,
    "hotel": 30, "hospital": 20, "school": 12, "university": 18,
    "industrial": 9, "warehouse": 8, "church": 14, "public": 15,
    "house": 7, "residential": 9, "yes": 8,
}


# Sai so hinh hoc toi da khi lam gon, tinh bang do.
# 0,000012 do ~ 1,3 m tren thuc dia -> mat thuong khong phan biet duoc,
# nhung file van nho vi cac doan thang duoc gop lai.
SAI_SO = 0.000012


def lam_gon(toa_do):
    """Lam gon hinh hoc bang Douglas-Peucker (giu dung hinh dang).

    KHONG dung cach 'giu 1 diem moi N diem': cach do CAT GOC CUA, lam duong
    thang ra va lech khoi tim duong that - duong cong bi bien thanh duong gay.
    Douglas-Peucker bo diem theo SAI SO HINH HOC: doan thang thi bo nhieu
    diem, doan cong thi giu lai du diem de khong meo.
    """
    if len(toa_do) < 3:
        return [[round(x, 6), round(y, 6)] for x, y in toa_do]
    try:
        from shapely.geometry import LineString
        g = LineString(toa_do).simplify(SAI_SO, preserve_topology=False)
        c = list(g.coords)
        if len(c) >= 2:
            return [[round(x, 6), round(y, 6)] for x, y in c]
    except Exception:
        pass
    return [[round(x, 6), round(y, 6)] for x, y in toa_do]


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


def _so(v):
    """Doi sang so thuc hop le, tra ve None neu khong duoc.

    QUAN TRONG: o dong pandas, o trong tra ve NaN chu khong phai None, va
    float('nan') KHONG nem loi. Neu khong kiem tra isfinite thi NaN se lot
    vao file JSON, lam ca file khong doc duoc (JSON khong co kieu NaN).
    """
    if v is None:
        return None
    try:
        x = float(str(v).replace("m", "").split(";")[0].strip())
    except Exception:
        return None
    return x if math.isfinite(x) and 0 < x < 500 else None


def doc_chieu_cao(row):
    """Uu tien height, roi building:levels x 3,3m, cuoi cung la mac dinh."""
    for k in ("height", "building:height"):
        x = _so(row.get(k))
        if x:
            return x
    for k in ("building:levels", "levels"):
        x = _so(row.get(k))
        if x:
            return max(3.0, x * 3.3)
    loai = str(row.get("building", "yes"))
    return float(CAO_MAC_DINH.get(loai, 8))


def xuat_toa_nha():
    """Toa nha 3D: chan de + chieu cao, de Cesium dun khoi len."""
    print("Tai toa nha tu OSM (vung loi do thi, co the mat 2-5 phut)...")
    features = []
    try:
        from shapely.geometry import mapping

        w, s_, e, n = BBOX_NHA
        gdf = ox.features_from_bbox(bbox=(w, s_, e, n), tags={"building": True})
        print(f"  OSM tra ve {len(gdf):,} toa nha")

        # bo nha qua nho: giu cho canh nhin thoang va file nhe
        m2_toi_thieu = 120
        for _, row in gdf.iterrows():
            g = row.geometry
            if g is None or g.geom_type not in ("Polygon", "MultiPolygon"):
                continue
            # dien tich xap xi ra m2 (1 do ~ 111km)
            if g.area * (111000 ** 2) < m2_toi_thieu:
                continue
            gj = mapping(g.simplify(0.00003, preserve_topology=True))
            features.append({
                "type": "Feature",
                "geometry": gj,
                "properties": {"c": round(doc_chieu_cao(row), 1)},
            })
        print(f"  Giu lai {len(features):,} toa nha (bo nha < {m2_toi_thieu} m2)")
    except Exception as ex:
        print(f"  Khong lay duoc toa nha: {type(ex).__name__}: {str(ex)[:120]}")

    ghi("toa_nha.geojson", features)


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
    xuat_toa_nha()
    print("\nXong. Tai lai trang web de xem.")
