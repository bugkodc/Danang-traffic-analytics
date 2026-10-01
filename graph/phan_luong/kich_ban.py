"""
Kich ban dieu phoi: thay doi mang luoi (dong / han che mot doan) roi gan luong
lai de so sanh voi hien trang.

Dong mot doan = nhan t0 len rat lon thay vi xoa canh, de mang luoi giu nguyen
cau truc (moi ket qua cung so canh, so sanh truc tiep duoc).
"""

from dataclasses import dataclass

import numpy as np

from .gan_luong import gan_luong_can_bang

HE_SO_DONG = 1e4


@dataclass
class KichBan:
    ma: str
    ten: str
    mo_ta: str
    ten_duong: str          # chuoi tim trong ten canh OSM
    he_so_nang_luc: float   # 0 = dong hoan toan, 0.5 = con mot nua nang luc


KICH_BAN = {
    kb.ma: kb for kb in [
        KichBan("dong-cau-rong", "Đóng Cầu Rồng",
                "Cầu Rồng cấm phương tiện, như các tối cuối tuần khi cầu phun lửa, phun nước.",
                "Cầu Rồng", 0.0),
        KichBan("han-che-cau-song-han", "Hạn chế Cầu Sông Hàn",
                "Cầu Sông Hàn chỉ còn một nửa năng lực, như khi sửa chữa một làn.",
                "Cầu Sông Hàn", 0.5),
        KichBan("dong-cau-song-han", "Đóng Cầu Sông Hàn",
                "Cầu Sông Hàn quay để tàu thuyền qua lại, phương tiện không lưu thông.",
                "Cầu Sông Hàn", 0.0),
    ]
}


def ap_dung(ml, kb):
    """Tra ve (t0, C) da sua theo kich ban va danh sach canh bi tac dong."""
    canh = ml.canh_theo_ten(kb.ten_duong)
    if len(canh) == 0:
        raise ValueError(f"Khong tim thay canh nao co ten chua '{kb.ten_duong}'")
    t0, C = ml.t0.copy(), ml.C.copy()
    if kb.he_so_nang_luc == 0:
        t0[canh] *= HE_SO_DONG
    else:
        C[canh] *= kb.he_so_nang_luc
    return t0, C, canh


def chay(ml, kb, vung, nhu_cau, **kw):
    t0, C, canh = ap_dung(ml, kb)
    return gan_luong_can_bang(ml, vung, nhu_cau, t0=t0, C=C, **kw), canh


def so_sanh(hien_trang, kich_ban, so_canh_noi_bat=40):
    """Muc thay doi tong thoi gian di chuyen va cac canh thay doi luu luong nhieu nhat."""
    T0, T1 = hien_trang.tong_thoi_gian, kich_ban.tong_thoi_gian
    chenh = kich_ban.luu_luong - hien_trang.luu_luong
    noi_bat = np.argsort(-np.abs(chenh))[:so_canh_noi_bat]
    return {
        "tong_thoi_gian_hien_trang": round(T0, 1),
        "tong_thoi_gian_kich_ban": round(T1, 1),
        "thay_doi_phan_tram": round((T1 - T0) / T0 * 100, 2),
        "canh_noi_bat": noi_bat,
        "chenh_luu_luong": chenh,
    }


def diem_trong_yeu(ml, kq, so_luong=10):
    """Cac canh co ty so luu luong / nang luc cao nhat - noi de tac nhat."""
    v_c = kq.luu_luong / ml.C
    thu_tu = np.argsort(-v_c)
    ket_qua, da_co = [], set()
    for i in thu_tu:
        ten = ml.ten[i] or f"({ml.cap[i]})"
        if ten in da_co:          # moi con duong chi lay canh tac nhat
            continue
        da_co.add(ten)
        ket_qua.append((int(i), ten, float(v_c[i])))
        if len(ket_qua) == so_luong:
            break
    return ket_qua
