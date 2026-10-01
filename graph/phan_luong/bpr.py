"""
Ham tro khang BPR (Bureau of Public Roads, 1964):

    t(V) = t0 * (1 + alpha * (V / C) ** beta)

alpha = 0.15, beta = 4 la gia tri kinh dien; se hieu chinh lai cho Da Nang.
"""

import numpy as np

ALPHA = 0.15
BETA = 4.0


def thoi_gian(t0, V, C, alpha=ALPHA, beta=BETA):
    """Thoi gian di qua canh (cung don vi voi t0) khi luu luong la V."""
    return t0 * (1.0 + alpha * (V / C) ** beta)


def tich_phan(t0, V, C, alpha=ALPHA, beta=BETA):
    """Tich phan cua t(w) tu 0 den V - tung so hang trong ham muc tieu Beckmann."""
    return t0 * (V + alpha * C * (V / C) ** (beta + 1) / (beta + 1))


def ty_le_v_c_tu_toc_do(ty_le_toc_do, alpha=ALPHA, beta=BETA):
    """
    Dao nguoc BPR: tu ty le toc do do duoc / toc do tu do (TomTom) suy ra V/C.
    t/t0 = 1/ty_le  =>  V/C = ((1/ty_le - 1) / alpha) ** (1/beta)
    Dung de doi chieu ket qua gan luong voi du lieu TomTom.
    """
    r = np.clip(np.asarray(ty_le_toc_do, dtype=float), 1e-3, 1.0)
    return ((1.0 / r - 1.0) / alpha) ** (1.0 / beta)
