"""Kiem thu thuat toan phan luong tren cac mang nho co dap an biet truoc."""

import numpy as np
import pytest

from graph.phan_luong import bpr
from graph.phan_luong.duong_di import DoThiTrongSo, duong_ngan_nhat, gan_tat_ca_hoac_khong
from graph.phan_luong.gan_luong import gan_luong_can_bang
from graph.phan_luong.mang_luoi import MangLuoi


def mang(canh, so_nut):
    """canh: list (tu, den, t0, C)"""
    tu, den, t0, C = map(np.array, zip(*canh))
    n = len(tu)
    return MangLuoi(np.arange(so_nut), np.zeros(so_nut), np.zeros(so_nut), tu, den, np.ones(n),
                    t0.astype(float), C.astype(float), ["primary"] * n, [""] * n, [[]] * n)


# Hai tuyen tu nut 0 den nut 3: 0-1-3 (nhanh, hep) va 0-2-3 (cham, rong)
HAI_TUYEN = [(0, 1, 600, 1500), (1, 3, 0.1, 1e9), (0, 2, 900, 3000), (2, 3, 0.1, 1e9)]


def thoi_gian_tuyen(kq):
    return kq.thoi_gian[0] + kq.thoi_gian[1], kq.thoi_gian[2] + kq.thoi_gian[3]


def test_nhu_cau_thap_di_het_tuyen_nhanh():
    ml = mang(HAI_TUYEN, 4)
    kq = gan_luong_can_bang(ml, np.array([0, 3]), np.array([[0, 300], [0, 0]]))
    assert kq.luu_luong[0] == pytest.approx(300, rel=1e-3)
    assert kq.luu_luong[2] == pytest.approx(0, abs=1)


def test_nhu_cau_cao_hai_tuyen_bang_thoi_gian():
    """Nguyen ly Wardrop: moi tuyen duoc dung co cung thoi gian."""
    ml = mang(HAI_TUYEN, 4)
    kq = gan_luong_can_bang(ml, np.array([0, 3]), np.array([[0, 4000], [0, 0]]), nguong=1e-6, toi_da=500)
    t1, t2 = thoi_gian_tuyen(kq)
    assert kq.luu_luong[0] > 0 and kq.luu_luong[2] > 0
    assert kq.luu_luong[0] + kq.luu_luong[2] == pytest.approx(4000, rel=1e-6)
    assert t1 == pytest.approx(t2, rel=1e-2)
    assert kq.khoang_cach[-1] < 1e-4


def test_bao_toan_luu_luong_tai_nut_giua():
    ml = mang(HAI_TUYEN, 4)
    kq = gan_luong_can_bang(ml, np.array([0, 3]), np.array([[0, 4000], [0, 0]]))
    assert kq.luu_luong[0] == pytest.approx(kq.luu_luong[1])
    assert kq.luu_luong[2] == pytest.approx(kq.luu_luong[3])


def test_canh_song_song_chon_canh_ngan_hon():
    ml = mang([(0, 1, 50, 1000), (0, 1, 20, 1000), (1, 2, 10, 1000)], 3)
    dt = DoThiTrongSo(ml, ml.t0)
    assert duong_ngan_nhat(dt, 0, 2) == [1, 2]


def test_gan_tat_ca_hoac_khong_cong_don_nhieu_cap_od():
    ml = mang([(0, 1, 10, 1000), (1, 2, 10, 1000)], 3)
    x = gan_tat_ca_hoac_khong(DoThiTrongSo(ml, ml.t0), ml.so_canh, np.array([0, 1, 2]),
                              np.array([[0, 100, 200], [0, 0, 50], [0, 0, 0]]))
    assert list(x) == [300, 250]


def test_dao_nguoc_bpr():
    # tai V/C = 1, t/t0 = 1.15 => ty le toc do = 1/1.15
    assert bpr.ty_le_v_c_tu_toc_do(1 / 1.15) == pytest.approx(1.0)
    assert bpr.ty_le_v_c_tu_toc_do(1.0) == pytest.approx(0.0)
