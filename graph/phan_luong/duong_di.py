"""
Tim duong ngan nhat theo trong so cho truoc (Dijkstra, scipy.sparse.csgraph)
va gan toan bo nhu cau len duong ngan nhat (all-or-nothing).
"""

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

# csgraph coi cac o bang 0 la "khong co canh" o mot so cho; cong them mot luong
# rat nho de canh dai 0 m (hiem gap trong OSM) van duoc tinh.
_EPS = 1e-6


class DoThiTrongSo:
    """Ma tran ke cua mang luoi voi bo trong so w (moi canh mot gia tri)."""

    def __init__(self, ml, w):
        n = ml.so_nut
        # OSM co the co nhieu canh song song giua hai nut: giu canh co w nho nhat
        thu_tu = np.lexsort((w, ml.den, ml.tu))
        u, v = ml.tu[thu_tu], ml.den[thu_tu]
        dau_nhom = np.ones(len(u), dtype=bool)
        dau_nhom[1:] = (u[1:] != u[:-1]) | (v[1:] != v[:-1])
        chon = thu_tu[dau_nhom]

        self.n = n
        self.A = csr_matrix((w[chon] + _EPS, (ml.tu[chon], ml.den[chon])), shape=(n, n))
        khoa = ml.tu[chon].astype(np.int64) * n + ml.den[chon]
        sap = np.argsort(khoa)
        self._khoa = khoa[sap]
        self._canh = chon[sap]

    def canh_giua(self, u, v):
        """Chi so canh duoc chon giua hai nut ke nhau."""
        i = np.searchsorted(self._khoa, np.int64(u) * self.n + v)
        return int(self._canh[i])

    def cay(self, goc):
        """Khoang cach va mang nut cha tu mot hoac nhieu nut goc."""
        return dijkstra(self.A, indices=goc, return_predecessors=True)


def duong_ngan_nhat(dt, nguon, dich):
    """Danh sach chi so canh tren duong ngan nhat; rong neu khong co duong."""
    _, cha = dt.cay(nguon)
    canh = []
    x = dich
    while x != nguon:
        p = cha[x]
        if p < 0:
            return []
        canh.append(dt.canh_giua(p, x))
        x = p
    return canh[::-1]


def gan_tat_ca_hoac_khong(dt, so_canh, vung, nhu_cau):
    """
    Gan nhu cau len duong ngan nhat cua tung cap OD.

    vung     : chi so nut dai dien cho tung vung (do dai k)
    nhu_cau  : ma tran k x k, nhu_cau[i, j] = so xe/gio tu vung i den vung j
    tra ve   : luu luong tren tung canh (do dai so_canh)
    """
    luu_luong = np.zeros(so_canh)
    _, cha = dt.cay(vung)
    for i, goc in enumerate(vung):
        for j, dich in enumerate(vung):
            q = nhu_cau[i, j]
            if q <= 0 or goc == dich:
                continue
            x = dich
            while x != goc:
                p = cha[i, x]
                if p < 0:
                    raise ValueError(f"Khong co duong tu vung {i} den vung {j}")
                luu_luong[dt.canh_giua(p, x)] += q
                x = p
    return luu_luong
