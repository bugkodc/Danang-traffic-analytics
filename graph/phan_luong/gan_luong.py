"""
Gan luong can bang nguoi dung (nguyen ly Wardrop thu nhat) bang thuat toan
Frank-Wolfe (LeBlanc, Morlok & Pierskalla, 1975).

Bai toan: tim luu luong x tren cac canh cuc tieu ham Beckmann
    Z(x) = sum_a  tich phan tu 0 den x_a cua t_a(w) dw
voi rang buoc bao toan luu luong cho moi cap OD. Tai diem can bang, moi
duong duoc dung giua mot cap OD co cung thoi gian va khong lon hon duong
khong duoc dung - khong ai doi duong ma di nhanh hon.

Moi vong lap:
    1. t = BPR(x)                       thoi gian hien tai tren tung canh
    2. y = gan tat ca hoac khong theo t  (huong toi uu tuyen tinh hoa)
    3. tim lambda trong [0, 1] cuc tieu Z(x + lambda (y - x))  (chia doi)
    4. x = x + lambda (y - x)
Dung khi khoang cach tuong doi (relative gap) < nguong.
"""

from dataclasses import dataclass, field

import numpy as np

from . import bpr
from .duong_di import DoThiTrongSo, gan_tat_ca_hoac_khong


@dataclass
class KetQuaGanLuong:
    luu_luong: np.ndarray          # xe/gio tren tung canh
    thoi_gian: np.ndarray          # giay tren tung canh, tai luu luong do
    so_vong: int
    khoang_cach: list = field(default_factory=list)   # relative gap qua tung vong

    @property
    def tong_thoi_gian(self):
        """Tong thoi gian di chuyen cua toan mang (xe.gio) trong mot gio."""
        return float(self.luu_luong @ self.thoi_gian) / 3600.0


def _buoc_toi_uu(t0, C, x, d, alpha, beta, so_lan_chia=30):
    """Dao ham cua Z theo lambda la sum t(x + lambda d) * d, tang dan; tim nghiem bang chia doi."""
    def dao_ham(lam):
        return float(bpr.thoi_gian(t0, x + lam * d, C, alpha, beta) @ d)

    if dao_ham(1.0) <= 0:
        return 1.0
    thap, cao = 0.0, 1.0
    for _ in range(so_lan_chia):
        giua = (thap + cao) / 2
        if dao_ham(giua) > 0:
            cao = giua
        else:
            thap = giua
    return (thap + cao) / 2


def gan_luong_can_bang(ml, vung, nhu_cau, t0=None, C=None, alpha=bpr.ALPHA, beta=bpr.BETA,
                       nguong=1e-4, toi_da=100):
    """
    ml        : MangLuoi
    vung      : chi so nut cua cac vung (diem phat sinh / thu hut chuyen di)
    nhu_cau   : ma tran k x k (xe/gio)
    t0, C     : cho phep truyen gia tri da sua (vd. kich ban dong cau); mac dinh lay tu ml
    """
    t0 = ml.t0 if t0 is None else t0
    C = ml.C if C is None else C

    x = gan_tat_ca_hoac_khong(DoThiTrongSo(ml, t0), ml.so_canh, vung, nhu_cau)
    khoang_cach = []
    vong = 0
    for vong in range(1, toi_da + 1):
        t = bpr.thoi_gian(t0, x, C, alpha, beta)
        y = gan_tat_ca_hoac_khong(DoThiTrongSo(ml, t), ml.so_canh, vung, nhu_cau)

        tong_hien_tai = float(t @ x)
        gap = (tong_hien_tai - float(t @ y)) / tong_hien_tai
        khoang_cach.append(gap)
        if gap < nguong:
            break

        d = y - x
        lam = _buoc_toi_uu(t0, C, x, d, alpha, beta)
        x = x + lam * d

    return KetQuaGanLuong(x, bpr.thoi_gian(t0, x, C, alpha, beta), vong, khoang_cach)
