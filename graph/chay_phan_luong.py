"""
Chay thuat toan phan luong va ghi ket qua ra serving/ (tang xu ly theo lo).

Tinh:
  - gan luong can bang cho hien trang (Frank-Wolfe, BPR)
  - 3 kich ban dieu phoi trong graph/phan_luong/kich_ban.py
  - diem trong yeu (ty so V/C cao nhat)
  - duong di "tinh" (theo t0) va "co tac nghen" (theo thoi gian sau gan luong)
    cho moi cap trong 12 vung

Ghi ra:
  serving/phan_luong.json          so lieu tong hop + duong di
  serving/phan_luong_canh.geojson  luu luong, V/C, chenh lech theo kich ban tren tung canh
  results/phan_luong_kich_ban.csv  bang so sanh kich ban (dua vao luan van)

Chay:
    python graph/chay_phan_luong.py                    # 12.000 xe/gio
    python graph/chay_phan_luong.py --tong 15000 --tai-lai
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from graph.phan_luong import kich_ban as kb                      # noqa: E402
from graph.phan_luong.duong_di import DoThiTrongSo, duong_ngan_nhat  # noqa: E402
from graph.phan_luong.gan_luong import gan_luong_can_bang          # noqa: E402
from graph.phan_luong.mang_luoi import tai_do_thi, xay_mang_luoi   # noqa: E402
from graph.phan_luong.nhu_cau import VUNG, nhu_cau_gia_dinh        # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SERVING = os.path.join(ROOT, "serving")
RESULTS = os.path.join(ROOT, "results")
LUU_LUONG_TOI_THIEU = 30      # xe/gio - canh it hon thi khong xuat ra ban do


def hinh_duong(ml, ds_canh):
    toa_do = []
    for i in ds_canh:
        diem = ml.hinh[i]
        toa_do.extend(diem if not toa_do else diem[1:])
    return [[round(x, 6), round(y, 6)] for x, y in toa_do]


def mo_ta_duong(ml, ds_canh, trong_so):
    return {
        "thoi_gian_phut": round(float(trong_so[ds_canh].sum()) / 60, 1),
        "dai_km": round(float(ml.dai[ds_canh].sum()) / 1000, 2),
        "toa_do": hinh_duong(ml, ds_canh),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tong", type=float, default=12000, help="tong so chuyen di gio cao diem (xe/gio)")
    ap.add_argument("--tai-lai", action="store_true", help="tai lai do thi tu OSM")
    a = ap.parse_args()

    bat_dau = time.time()
    ml = xay_mang_luoi(tai_do_thi(a.tai_lai))
    print(f"Mang luoi: {ml.so_nut:,} nut, {ml.so_canh:,} canh")

    ma_vung, nut_vung, T = nhu_cau_gia_dinh(ml, a.tong)
    print(f"Nhu cau gia dinh: {T.sum():,.0f} xe/gio giua {len(ma_vung)} vung")

    hien_trang = gan_luong_can_bang(ml, nut_vung, T)
    print(f"Hien trang: {hien_trang.so_vong} vong, gap {hien_trang.khoang_cach[-1]:.1e}, "
          f"tong {hien_trang.tong_thoi_gian:,.0f} xe.gio")

    ket_qua_kb, chenh = [], {}
    thoi_gian_kb = {"hien-trang": hien_trang.thoi_gian}
    canh_dong_kb = {"hien-trang": set()}
    for k in kb.KICH_BAN.values():
        kq, canh_dong = kb.chay(ml, k, nut_vung, T)
        ss = kb.so_sanh(hien_trang, kq)
        chenh[k.ma] = ss["chenh_luu_luong"]
        thoi_gian_kb[k.ma] = kq.thoi_gian
        canh_dong_kb[k.ma] = set(canh_dong.tolist()) if k.he_so_nang_luc == 0 else set()
        ket_qua_kb.append({
            "ma": k.ma, "ten": k.ten, "mo_ta": k.mo_ta,
            "so_canh_tac_dong": int(len(canh_dong)),
            "so_vong": kq.so_vong,
            "tong_thoi_gian": ss["tong_thoi_gian_kich_ban"],
            "thay_doi_phan_tram": ss["thay_doi_phan_tram"],
            "canh_tac_dong": [hinh_duong(ml, [i]) for i in canh_dong],
        })
        print(f"  {k.ten}: {kq.so_vong} vong, tong {kq.tong_thoi_gian:,.0f} xe.gio "
              f"({ss['thay_doi_phan_tram']:+.1f}%)")

    # Duong di cho moi cap vung:
    #   ban_do     - ngan nhat theo t0, nhu ban do thong thuong (khong biet tac nghen, cau dong)
    #   phan_luong - ngan nhat theo thoi gian sau gan luong cua tung kich ban
    # Thoi gian cua ca hai deu tinh trong dieu kien cua kich ban dang xet.
    cap = [(i, j) for i in range(len(ma_vung)) for j in range(len(ma_vung)) if i != j]
    dt_ban_do = DoThiTrongSo(ml, ml.t0)
    canh_ban_do = {(i, j): duong_ngan_nhat(dt_ban_do, nut_vung[i], nut_vung[j]) for i, j in cap}

    duong = {"hinh_ban_do": {}, "kich_ban": {}}
    for (i, j), c in canh_ban_do.items():
        duong["hinh_ban_do"][f"{ma_vung[i]}-{ma_vung[j]}"] = hinh_duong(ml, c)
    for ma, t in thoi_gian_kb.items():
        dt = DoThiTrongSo(ml, t)
        dong = canh_dong_kb[ma]
        theo_cap = {}
        for (i, j), c_bd in canh_ban_do.items():
            c_pl = duong_ngan_nhat(dt, nut_vung[i], nut_vung[j])
            qua_doan_dong = bool(dong.intersection(c_bd))
            ban_do = mo_ta_duong(ml, c_bd, t)
            del ban_do["toa_do"]                       # hinh da luu o hinh_ban_do
            if qua_doan_dong:
                ban_do["thoi_gian_phut"] = None
            theo_cap[f"{ma_vung[i]}-{ma_vung[j]}"] = {
                "ban_do": {**ban_do, "qua_doan_dong": qua_doan_dong},
                "phan_luong": mo_ta_duong(ml, c_pl, t),
                "trung_nhau": c_bd == c_pl,
            }
        duong["kich_ban"][ma] = theo_cap

    # vi du mac dinh tren web: cap co duong ban do di qua Cau Rong, de khi chon kich ban
    # dong cau thay ngay su khac biet
    qua_cau_rong = [k for k, v in duong["kich_ban"]["dong-cau-rong"].items() if v["ban_do"]["qua_doan_dong"]]
    cap_goi_y = "S11-S08" if "S11-S08" in qua_cau_rong else (qua_cau_rong or ["S11-S08"])[0]

    trong_yeu = [{"ten": ten, "v_c": round(vc, 2), "toa_do": hinh_duong(ml, [i])}
                 for i, ten, vc in kb.diem_trong_yeu(ml, hien_trang)]

    # ---- ghi file ----
    os.makedirs(SERVING, exist_ok=True)
    os.makedirs(RESULTS, exist_ok=True)
    tong_hop = {
        "thoi_diem_tinh": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "nhu_cau": {"tong_xe_gio": round(float(T.sum())), "gia_dinh": True,
                    "ghi_chu": "Ma trận OD giả định theo mô hình hấp dẫn giữa 12 vùng; "
                               "sẽ thay bằng OD ước lượng từ số đếm phương tiện."},
        "mang_luoi": {"so_nut": ml.so_nut, "so_canh": ml.so_canh},
        "vung": [{"ma": m, "ten": VUNG[m][0], "lat": VUNG[m][1], "lon": VUNG[m][2]} for m in ma_vung],
        "hien_trang": {"tong_thoi_gian": round(hien_trang.tong_thoi_gian, 1),
                       "so_vong": hien_trang.so_vong,
                       "khoang_cach_cuoi": hien_trang.khoang_cach[-1],
                       "diem_trong_yeu": trong_yeu},
        "kich_ban": ket_qua_kb,
        "cap_goi_y": cap_goi_y.split("-"),
        "duong_di": duong,
    }
    with open(os.path.join(SERVING, "phan_luong.json"), "w", encoding="utf-8") as f:
        json.dump(tong_hop, f, ensure_ascii=False, separators=(",", ":"))

    v_c = hien_trang.luu_luong / ml.C
    giu = hien_trang.luu_luong >= LUU_LUONG_TOI_THIEU
    for c in chenh.values():
        giu |= np.abs(c) >= LUU_LUONG_TOI_THIEU
    features = []
    for i in np.flatnonzero(giu):
        tt = {"x": round(float(hien_trang.luu_luong[i])), "vc": round(float(v_c[i]), 3)}
        for ma, c in chenh.items():
            tt[ma] = round(float(c[i]))
        features.append({"type": "Feature", "properties": tt,
                         "geometry": {"type": "LineString", "coordinates": hinh_duong(ml, [i])}})
    with open(os.path.join(SERVING, "phan_luong_canh.geojson"), "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": features}, f, separators=(",", ":"))

    with open(os.path.join(RESULTS, "phan_luong_kich_ban.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["kich_ban", "tong_thoi_gian_xe_gio", "thay_doi_phan_tram", "so_vong_frank_wolfe"])
        w.writerow(["Hiện trạng", round(hien_trang.tong_thoi_gian, 1), 0, hien_trang.so_vong])
        for k in ket_qua_kb:
            w.writerow([k["ten"], k["tong_thoi_gian"], k["thay_doi_phan_tram"], k["so_vong"]])

    print(f"Da ghi serving/phan_luong.json, serving/phan_luong_canh.geojson ({len(features):,} canh), "
          f"results/phan_luong_kich_ban.csv - {time.time() - bat_dau:.0f} giay")


if __name__ == "__main__":
    main()
