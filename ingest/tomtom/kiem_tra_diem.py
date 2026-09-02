"""
Kiem tra chat luong cac diem do trong segments.csv TRUOC khi de job chay dai han.

Phat hien:
  - Hai diem roi vao CUNG mot doan duong (trung lap, lang phi quota)
  - Doan qua dai (gia tri trung binh khong phan anh tac cuc bo)
  - Doan qua ngan (nhieu, khong on dinh)
  - Phan lop duong thap (FRC5+ = duong nho, khong phai truc chinh)

Cach dung:
    set TOMTOM_API_KEY=xxxxx
    python kiem_tra_diem.py
"""

import os
import sys
import csv
import time
import math

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
SEGMENTS_FILE = os.path.join(HERE, "segments.csv")
API_URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"

# nguong danh gia
DAI_TOI_DA = 3000    # m - dai hon thi gia tri trung binh bi pha loang
DAI_TOI_THIEU = 200  # m - ngan hon thi do nhieu
# FRC4 la muc pho bien cua duong truc do thi Viet Nam trong du lieu TomTom,
# nen van tinh la dat. Chi canh bao tu FRC5 tro xuong (duong nho, ngo).
FRC_TOT = {"FRC0", "FRC1", "FRC2", "FRC3", "FRC4"}


def haversine(a, b):
    R = 6371000.0
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp = p2 - p1
    dl = math.radians(b[1] - a[1])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def do_dai(coords):
    pts = [(c["latitude"], c["longitude"]) for c in coords]
    return sum(haversine(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def main():
    key = os.environ.get("TOMTOM_API_KEY")
    if not key:
        print("Chua dat TOMTOM_API_KEY")
        sys.exit(1)

    with open(SEGMENTS_FILE, encoding="utf-8") as f:
        segments = list(csv.DictReader(f))

    ket_qua = []
    for seg in segments:
        try:
            d = requests.get(API_URL, timeout=20, params={
                "key": key, "point": f"{seg['lat']},{seg['lon']}", "unit": "KMPH"
            }).json()["flowSegmentData"]
            coords = d["coordinates"]["coordinate"]
            ket_qua.append({
                "id": seg["segment_id"],
                "ten": seg["ten"],
                "frc": d["frc"],
                "free": d["freeFlowSpeed"],
                "dai_m": round(do_dai(coords)),
                "n_pts": len(coords),
                # dau van tay cua doan: dung de phat hien trung lap
                "vantay": (round(coords[0]["latitude"], 5), round(coords[0]["longitude"], 5),
                           round(coords[-1]["latitude"], 5), round(coords[-1]["longitude"], 5)),
            })
        except Exception as e:
            ket_qua.append({"id": seg["segment_id"], "ten": seg["ten"], "loi": str(e)})
        time.sleep(0.5)

    # phat hien trung lap
    dem = {}
    for r in ket_qua:
        if "vantay" in r:
            dem.setdefault(r["vantay"], []).append(r["id"])
    trung = {v[0]: v for v in dem.values() if len(v) > 1}

    print(f"\n{'ID':5s} {'Ten':22s} {'FRC':5s} {'Free':>5s} {'Dai(m)':>7s} {'Diem':>5s}  Danh gia")
    print("-" * 88)
    for r in ket_qua:
        if "loi" in r:
            print(f"{r['id']:5s} {r['ten']:22s} LOI: {r['loi'][:40]}")
            continue

        canh_bao = []
        if r["frc"] not in FRC_TOT:
            canh_bao.append("duong nho (FRC thap)")
        if r["dai_m"] > DAI_TOI_DA:
            canh_bao.append(f"doan qua dai")
        if r["dai_m"] < DAI_TOI_THIEU:
            canh_bao.append("doan qua ngan")
        for ids in dem.values():
            if len(ids) > 1 and r["id"] in ids:
                canh_bao.append(f"TRUNG voi {','.join(i for i in ids if i != r['id'])}")
                break

        trang_thai = "OK" if not canh_bao else "  ".join(canh_bao)
        dau = " " if not canh_bao else "!"
        print(f"{r['id']:5s} {r['ten']:22s} {r['frc']:5s} {r['free']:5d} {r['dai_m']:7d} {r['n_pts']:5d} {dau} {trang_thai}")

    n_loi = sum(1 for r in ket_qua if "loi" in r)
    n_ok = sum(1 for r in ket_qua if "vantay" in r
               and r["frc"] in FRC_TOT and DAI_TOI_THIEU <= r["dai_m"] <= DAI_TOI_DA
               and r["id"] not in {i for ids in dem.values() if len(ids) > 1 for i in ids})
    print("-" * 88)
    print(f"Dat: {n_ok}/{len(segments)}   Loi API: {n_loi}   Nhom trung lap: {len(trung)}")
    print("\nDiem 'OK' la diem dung duoc lau dai. Diem co '!' nen doi toa do.")


if __name__ == "__main__":
    main()
