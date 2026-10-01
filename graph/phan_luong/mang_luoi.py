"""
Mang luoi duong cho bai toan phan luong: tai do thi OSM khu vuc nghien cuu,
chuan hoa thuoc tinh va chuyen sang dang mang (numpy) de tinh nhanh.

Moi canh co:
    t0  - thoi gian di qua khi duong thong thoang (giay)
    C   - nang luc thong hanh (xe con quy doi / gio, PCU/h)

Gia tri mac dinh theo cap duong ben duoi la GIA TRI TAM, lay theo muc pho
bien trong tai lieu giao thong. Can hieu chinh lai cho dong xe hon hop do xe
may chi phoi (TCVN, du lieu TomTom) - xem docs/plan/04-giai-doan-4-do-thi-spark.md muc 3.1.
"""

import os
from dataclasses import dataclass

import numpy as np
import osmnx as ox

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FILE_DO_THI = os.path.join(ROOT, "data", "interim", "mang_luoi_hai_chau.graphml")

# Vung bao 12 diem do TomTom: Hai Chau, bo dong song Han, Nga ba Hue (tay, nam, dong, bac)
VUNG = (108.170, 16.035, 108.255, 16.085)

# toc do dong tu do (km/h) khi OSM khong co maxspeed - hau het canh o Da Nang deu thieu
TOC_DO_MAC_DINH = {
    "trunk": 50, "primary": 40, "secondary": 35, "tertiary": 30,
    "trunk_link": 35, "primary_link": 30, "secondary_link": 30, "tertiary_link": 25,
    "unclassified": 25, "residential": 20, "living_street": 15,
}
DUONG_LON = {"trunk", "primary", "secondary", "tertiary"}
# so lan moi chieu
SO_LAN_MAC_DINH = {"trunk": 3, "primary": 2, "secondary": 2}
# nang luc moi lan (PCU/h)
NANG_LUC_LAN = {
    "trunk": 1800, "primary": 1600, "secondary": 1400, "tertiary": 1200,
    "unclassified": 900, "residential": 800, "living_street": 500,
}


def _gia_tri_dau(v):
    """OSM co the tra ve list (nhieu gia tri cho mot canh gop) - lay gia tri dau."""
    return v[0] if isinstance(v, list) else v


def _so(v, mac_dinh):
    try:
        return float(str(_gia_tri_dau(v)).split()[0])
    except (TypeError, ValueError):
        return mac_dinh


@dataclass
class MangLuoi:
    nut: np.ndarray        # osmid cua tung nut, chi so = vi tri trong mang
    lon: np.ndarray
    lat: np.ndarray
    tu: np.ndarray         # chi so nut dau cua canh
    den: np.ndarray        # chi so nut cuoi
    dai: np.ndarray        # met
    t0: np.ndarray         # giay
    C: np.ndarray          # PCU/h
    cap: list              # loai duong (highway)
    ten: list              # ten duong ('' neu khong co)
    hinh: list             # danh sach [lon, lat] doc theo canh

    @property
    def so_nut(self):
        return len(self.nut)

    @property
    def so_canh(self):
        return len(self.tu)

    def nut_gan_nhat(self, lat, lon, chi_duong_lon=False):
        """
        Chi so nut gan toa do nhat (khoang cach phang, du dung o quy mo thanh pho).
        chi_duong_lon: chi xet nut nam tren duong cap tertiary tro len - dung khi
        noi vung vao mang luoi, tranh do ca vung vao mot con hem.
        """
        ung_vien = np.arange(self.so_nut)
        if chi_duong_lon:
            lon_ = [i for i, c in enumerate(self.cap) if c.replace("_link", "") in DUONG_LON]
            ung_vien = np.unique(np.concatenate([self.tu[lon_], self.den[lon_]]))
        dx = (self.lon[ung_vien] - lon) * np.cos(np.radians(lat))
        dy = self.lat[ung_vien] - lat
        return int(ung_vien[np.argmin(dx * dx + dy * dy)])

    def canh_theo_ten(self, chuoi):
        return np.array([i for i, t in enumerate(self.ten) if chuoi in t], dtype=int)


def tai_do_thi(tai_lai=False):
    """Doc do thi da luu, chua co thi tai tu OSM (mat khoang 1 phut)."""
    if os.path.exists(FILE_DO_THI) and not tai_lai:
        return ox.load_graphml(FILE_DO_THI)
    ox.settings.use_cache = True
    ox.settings.cache_folder = os.path.join(ROOT, "data", "raw", "osm", "cache")
    G = ox.graph_from_bbox(VUNG, network_type="drive")
    # chi giu thanh phan lien thong manh lon nhat de moi cap diem deu co duong di
    G = ox.truncate.largest_component(G, strongly=True)
    os.makedirs(os.path.dirname(FILE_DO_THI), exist_ok=True)
    ox.save_graphml(G, FILE_DO_THI)
    return G


def xay_mang_luoi(G=None):
    G = G if G is not None else tai_do_thi()
    nut = np.array(list(G.nodes))
    chi_so = {n: i for i, n in enumerate(nut)}
    lon = np.array([G.nodes[n]["x"] for n in nut], dtype=float)
    lat = np.array([G.nodes[n]["y"] for n in nut], dtype=float)

    tu, den, dai, t0, C, cap, ten, hinh = [], [], [], [], [], [], [], []
    for u, v, d in G.edges(data=True):
        loai = _gia_tri_dau(d.get("highway", "unclassified"))
        if loai not in TOC_DO_MAC_DINH:
            loai = "unclassified"
        toc_do = _so(d.get("maxspeed"), TOC_DO_MAC_DINH[loai])
        # OSM ghi so lan cho ca hai chieu; duong hai chieu thi chia doi
        lan = _so(d.get("lanes"), SO_LAN_MAC_DINH.get(loai.replace("_link", ""), 1))
        if not d.get("oneway", False):
            lan = max(1.0, lan / 2)
        do_dai = float(d["length"])

        tu.append(chi_so[u])
        den.append(chi_so[v])
        dai.append(do_dai)
        t0.append(do_dai / (toc_do / 3.6))
        C.append(lan * NANG_LUC_LAN.get(loai.replace("_link", ""), 800))
        cap.append(loai)
        t = d.get("name", "")
        ten.append("; ".join(t) if isinstance(t, list) else (t or ""))
        if "geometry" in d:
            hinh.append([list(p) for p in d["geometry"].coords])
        else:
            hinh.append([[lon[chi_so[u]], lat[chi_so[u]]], [lon[chi_so[v]], lat[chi_so[v]]]])

    return MangLuoi(nut, lon, lat, np.array(tu), np.array(den), np.array(dai),
                    np.array(t0), np.array(C, dtype=float), cap, ten, hinh)
