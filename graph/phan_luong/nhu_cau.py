"""
Nhu cau di lai (ma tran OD) cho bai toan gan luong.

HIEN TAI LA NHU CAU GIA DINH: chua co so dem phuong tien (muc tieu 1) nen chua
uoc luong duoc OD that. Ma tran duoc dung theo mo hinh hap dan don gian giua
cac vung dat tai 12 diem do TomTom, chi de chay thu thuat toan va giao dien.
Khi co so dem, thay bang ma tran uoc luong tu luu luong canh (bai toan nguoc,
binh phuong toi thieu co rang buoc khong am).
"""

import numpy as np

# Vung = diem phat sinh / thu hut chuyen di, dat tai cac diem do (lat, lon).
# Trong so the hien muc do hap dan tuong doi (trung tam, cua ngo > khu dan cu).
VUNG = {
    "S01": ("Cầu Rồng", 16.06109, 108.22790, 1.0),
    "S02": ("Cầu Sông Hàn", 16.07215, 108.22679, 1.0),
    "S03": ("Cầu Trần Thị Lý", 16.05049, 108.23070, 0.8),
    "S04": ("Ngã ba Huế", 16.06304, 108.17994, 1.2),
    "S05": ("Nguyễn Văn Linh", 16.06086, 108.21950, 1.0),
    "S06": ("Điện Biên Phủ", 16.06588, 108.18803, 0.9),
    "S07": ("Ngô Quyền", 16.07014, 108.23168, 0.8),
    "S08": ("Võ Nguyên Giáp", 16.06000, 108.24654, 1.0),
    "S09": ("Lê Duẩn", 16.07087, 108.21671, 1.0),
    "S10": ("Nguyễn Tri Phương", 16.05621, 108.20691, 0.8),
    "S11": ("Sân bay Đà Nẵng", 16.05435, 108.20213, 1.2),
    "S12": ("Phạm Văn Đồng", 16.07022, 108.23896, 0.8),
}


def nhu_cau_gia_dinh(ml, tong_chuyen_di=12000, he_so_khoang_cach=1.0):
    """
    Ma tran OD theo mo hinh hap dan: T_ij ~ w_i * w_j / d_ij ** he_so, chuan hoa
    ve tong_chuyen_di (xe/gio, gio cao diem). Tra ve (ma_vung, chi_so_nut, ma_tran).
    """
    ma = list(VUNG)
    nut = np.array([ml.nut_gan_nhat(VUNG[m][1], VUNG[m][2], chi_duong_lon=True) for m in ma])
    w = np.array([VUNG[m][3] for m in ma])
    lat = np.array([VUNG[m][1] for m in ma])
    lon = np.array([VUNG[m][2] for m in ma])

    # khoang cach duong chim bay (km) giua cac vung
    dy = (lat[:, None] - lat[None, :]) * 111.0
    dx = (lon[:, None] - lon[None, :]) * 111.0 * np.cos(np.radians(lat.mean()))
    d = np.hypot(dx, dy)
    np.fill_diagonal(d, np.inf)

    T = np.outer(w, w) / np.maximum(d, 0.3) ** he_so_khoang_cach
    np.fill_diagonal(T, 0)
    T *= tong_chuyen_di / T.sum()
    return ma, nut, T
