"""
Tang phuc vu - FastAPI doc du lieu TomTom da thu va phuc vu web demo.

Day la TANG SERVING trong kien truc Lambda: chi doc, khong tinh toan nang.
Xem docs/plan/B-kien-truc-ky-thuat.md

Chay:
    pip install -r services/requirements.txt
    python -m uvicorn services.api.main:app --reload --port 8000
    -> mo http://localhost:8000
"""

import os
import json
import glob
from datetime import datetime

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DATA_GLOB = os.path.join(ROOT, "ingest", "tomtom", "data", "*.parquet")
STATIC_DIR = os.path.join(HERE, "static")

# Toa do hien thi cua 12 diem do: diem truy van trong segments.csv duoc keo ve
# diem gan nhat tren dung con duong mang ten do (do thi OSM, 01/10/2026).
# Diem truy van goc co diem cach duong toi vai tram met, ve thang len ban do
# thi roi xuong song hoac vao trong san bay.
TOA_DO_CHUAN = {
    "S01": (16.06109, 108.22790),  # Cau Rong (lech 1 m)
    "S02": (16.07215, 108.22679),  # Cau Song Han (5 m)
    "S03": (16.05049, 108.23070),  # Cau Tran Thi Ly (1 m)
    "S04": (16.06304, 108.17994),  # cau vuot Nga ba Hue (23 m)
    "S05": (16.06086, 108.21950),  # Nguyen Van Linh (6 m)
    "S06": (16.06588, 108.18803),  # Dien Bien Phu (36 m)
    "S07": (16.07014, 108.23168),  # Ngo Quyen (266 m)
    "S08": (16.06000, 108.24654),  # Vo Nguyen Giap (4 m)
    "S09": (16.07087, 108.21671),  # Le Duan (105 m)
    "S10": (16.05621, 108.20691),  # Nguyen Tri Phuong (259 m)
    "S11": (16.05435, 108.20213),  # duong noi bo khu san bay (560 m)
    "S12": (16.07022, 108.23896),  # Pham Van Dong (87 m)
}

# Cac diem co van de ve du lieu, phat hien khi doi chieu voi do thi OSM va
# chuoi toc do (01/10/2026). Can kiem tra lai bang toa do doan ma TomTom tra ve.
CANH_BAO = {
    "S05": "Đo trùng đoạn với S10 (tốc độ giống nhau 98% số lần đo), đoạn dài khoảng 12 km.",
    "S10": "Đo trùng đoạn với S05; điểm truy vấn gần đường Duy Tân hơn Nguyễn Tri Phương.",
    "S07": "Điểm truy vấn gần đường Phạm Văn Đồng hơn Ngô Quyền, có thể đo nhầm đường.",
    "S09": "Điểm truy vấn gần đường Ngô Gia Tự hơn Lê Duẩn.",
    "S11": "Điểm truy vấn nằm trong khu sân bay, cách đường gần nhất khoảng 560 m.",
    "S08": "Đoạn TomTom dài khoảng 23 km, tốc độ là trung bình cả tuyến ven biển.",
}

# segments.csv luu ten khong dau (de chay on dinh tren GitHub Actions);
# ten hien thi tren web lay o day.
TEN_HIEN_THI = {
    "S01": "Cầu Rồng",
    "S02": "Cầu Sông Hàn",
    "S03": "Cầu Trần Thị Lý",
    "S04": "Ngã ba Huế",
    "S05": "Nguyễn Văn Linh",
    "S06": "Điện Biên Phủ",
    "S07": "Ngô Quyền",
    "S08": "Võ Nguyên Giáp",
    "S09": "Lê Duẩn",
    "S10": "Nguyễn Tri Phương",
    "S11": "Sân bay Đà Nẵng",
    "S12": "Phạm Văn Đồng",
}

app = FastAPI(title="Da Nang Traffic Analytics", version="0.1.0")

_cache = {"mtime": None, "df": None}


def doc_du_lieu() -> pd.DataFrame:
    """Doc toan bo parquet, cache theo thoi diem sua file moi nhat."""
    files = sorted(glob.glob(DATA_GLOB))
    if not files:
        return pd.DataFrame()

    mtime = max(os.path.getmtime(f) for f in files)
    if _cache["mtime"] == mtime and _cache["df"] is not None:
        return _cache["df"]

    df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    df["ts_local"] = pd.to_datetime(df["ts_local"], utc=True).dt.tz_convert("Asia/Ho_Chi_Minh")
    df["ten"] = df["segment_id"].map(TEN_HIEN_THI).fillna(df["ten"])
    df = df.sort_values("ts_local")
    _cache.update(mtime=mtime, df=df)
    return df


@app.get("/api/tong-quan")
def tong_quan():
    """Thong tin chung ve du lieu da thu duoc."""
    df = doc_du_lieu()
    if df.empty:
        raise HTTPException(404, "Chua co du lieu. Chay ingest/tomtom/collect.py truoc.")
    return {
        "so_ban_ghi": len(df),
        "so_doan": int(df.segment_id.nunique()),
        "so_lan_do": int(df.ts_local.nunique()),
        "tu_ngay": df.ts_local.min().isoformat(),
        "den_ngay": df.ts_local.max().isoformat(),
        "so_ngay": int(df.ts_local.dt.date.nunique()),
    }


@app.get("/api/thoi-diem")
def danh_sach_thoi_diem():
    """Cac thoi diem do da co, de dung cho thanh truot thoi gian."""
    df = doc_du_lieu()
    if df.empty:
        return []
    ts = sorted(df.ts_local.unique())
    return [pd.Timestamp(t).isoformat() for t in ts]


@app.get("/api/doan")
def cac_doan(thoi_diem: str | None = None):
    """
    Tra ve trang thai cac doan duong tai mot thoi diem.
    Neu khong truyen thoi_diem, lay lan do moi nhat.
    """
    df = doc_du_lieu()
    if df.empty:
        raise HTTPException(404, "Chua co du lieu")

    if thoi_diem:
        muc_tieu = pd.Timestamp(thoi_diem)
        lat = df[df.ts_local == muc_tieu]
        if lat.empty:                       # lay lan do gan nhat
            idx = (df.ts_local - muc_tieu).abs().idxmin()
            lat = df[df.ts_local == df.loc[idx, "ts_local"]]
    else:
        lat = df[df.ts_local == df.ts_local.max()]

    ket_qua = []
    for _, r in lat.iterrows():
        ratio = r.get("speed_ratio")
        sid = r.segment_id
        c_lat, c_lon = TOA_DO_CHUAN.get(sid, (float(r.lat), float(r.lon)))
        ket_qua.append({
            "segment_id":     sid,
            "ten":            r.ten,
            "lat":            c_lat,
            "lon":            c_lon,
            "current_speed":  None if pd.isna(r.current_speed) else int(r.current_speed),
            "freeflow_speed": None if pd.isna(r.freeflow_speed) else int(r.freeflow_speed),
            "speed_ratio":    None if pd.isna(ratio) else round(float(ratio), 3),
            "muc_tac":        muc_tac_nghen(ratio),
            "canh_bao":       CANH_BAO.get(sid),
        })
    return {
        "thoi_diem": lat.ts_local.iloc[0].isoformat(),
        "doan": sorted(ket_qua, key=lambda x: x["segment_id"]),
    }


def muc_tac_nghen(ratio) -> int:
    """Quy doi ty le toc do sang 4 muc de to mau ban do."""
    if ratio is None or pd.isna(ratio):
        return 0
    if ratio >= 0.85:
        return 1        # thong thoang
    if ratio >= 0.65:
        return 2        # hoi dong
    if ratio >= 0.45:
        return 3        # dong
    return 4            # tac


@app.get("/api/doan/{segment_id}/chuoi-thoi-gian")
def chuoi_thoi_gian(segment_id: str):
    """Toan bo lich su do cua mot doan - dung ve bieu do."""
    df = doc_du_lieu()
    d = df[df.segment_id == segment_id]
    if d.empty:
        raise HTTPException(404, f"Khong co du lieu cho doan {segment_id}")
    return {
        "segment_id": segment_id,
        "ten": d.ten.iloc[0],
        "diem": [
            {
                "ts": t.isoformat(),
                "current_speed": None if pd.isna(c) else int(c),
                "freeflow_speed": None if pd.isna(f) else int(f),
                "speed_ratio": None if pd.isna(r) else round(float(r), 3),
            }
            for t, c, f, r in zip(d.ts_local, d.current_speed, d.freeflow_speed, d.speed_ratio)
        ],
    }


@app.get("/api/theo-gio")
def ho_so_theo_gio():
    """
    Ho so toc do trung binh theo gio trong ngay, cho tung doan.
    Day chinh la dang du lieu se tro thanh TRONG SO DONG cua canh do thi.
    """
    df = doc_du_lieu()
    if df.empty:
        return []
    df = df.copy()
    df["gio"] = df.ts_local.dt.hour
    g = (df.groupby(["segment_id", "ten", "gio"])
           .agg(ratio_tb=("speed_ratio", "mean"),
                toc_do_tb=("current_speed", "mean"),
                so_mau=("speed_ratio", "size"))
           .reset_index())
    g["ratio_tb"] = g.ratio_tb.round(3)
    g["toc_do_tb"] = g.toc_do_tb.round(1)
    return g.to_dict("records")


@app.get("/api/duong-chinh")
def duong_chinh():
    """
    Hinh hoc cac truc duong chinh, xuat tu chinh do thi OSM da tai ve.
    Dung de web tu ve ban do ma khong phu thuoc may chu tile ben ngoai
    (mang o Viet Nam hay chan CARTO / OpenFreeMap / OSM tiles).

    Sinh file bang: python graph/xuat_geojson.py
    """
    f = os.path.join(ROOT, "serving", "duong_chinh.geojson")
    if not os.path.exists(f):
        raise HTTPException(404, "Chua co duong_chinh.geojson. "
                                 "Chay: python graph/xuat_geojson.py")
    # no-cache: file nay hay duoc xuat lai khi doi khu vuc (xuat_geojson.py
    # --khu-vuc). Khong co header nay, trinh duyet co the giu ban cu qua
    # nhieu lan F5 va lam tuong nhu thay doi khong co tac dung.
    return FileResponse(f, media_type="application/geo+json",
                        headers={"Cache-Control": "no-cache"})


@app.get("/api/mat-nuoc")
def mat_nuoc():
    """Song, bien, ho - lam nen cho ban do. Sinh boi graph/xuat_geojson.py"""
    f = os.path.join(ROOT, "serving", "mat_nuoc.geojson")
    if not os.path.exists(f):
        raise HTTPException(404, "Chua co mat_nuoc.geojson. "
                                 "Chay: python graph/xuat_geojson.py")
    return FileResponse(f, media_type="application/geo+json",
                        headers={"Cache-Control": "no-cache"})


@app.get("/api/toa-nha")
def toa_nha():
    """Chan de + chieu cao toa nha (thuoc tinh c, met) de ban do dun khoi 3D."""
    f = os.path.join(ROOT, "serving", "toa_nha.geojson")
    if not os.path.exists(f):
        raise HTTPException(404, "Chua co toa_nha.geojson. "
                                 "Chay: python graph/xuat_geojson.py")
    return FileResponse(f, media_type="application/geo+json")


# --- phan luong: chi doc ket qua da tinh boi graph/chay_phan_luong.py ---

FILE_PHAN_LUONG = os.path.join(ROOT, "serving", "phan_luong.json")
_cache_pl = {"mtime": None, "data": None}


def doc_phan_luong() -> dict:
    if not os.path.exists(FILE_PHAN_LUONG):
        raise HTTPException(404, "Chua co ket qua phan luong. Chay: python graph/chay_phan_luong.py")
    mtime = os.path.getmtime(FILE_PHAN_LUONG)
    if _cache_pl["mtime"] != mtime:
        with open(FILE_PHAN_LUONG, encoding="utf-8") as f:
            _cache_pl.update(mtime=mtime, data=json.load(f))
    return _cache_pl["data"]


@app.get("/api/phan-luong")
def phan_luong_tong_hop():
    """Hien trang, cac kich ban, diem trong yeu - khong kem duong di (lay rieng)."""
    d = doc_phan_luong()
    return {k: v for k, v in d.items() if k != "duong_di"}


@app.get("/api/phan-luong/duong-di")
def phan_luong_duong_di(tu: str, den: str, kich_ban: str = "hien-trang"):
    """
    Duong di giua hai vung trong mot kich ban: duong theo ban do thong thuong
    (khong biet tac nghen, cau dong) va duong theo ket qua phan luong.
    """
    dd = doc_phan_luong()["duong_di"]
    khoa = f"{tu}-{den}"
    d = dd["kich_ban"].get(kich_ban, {}).get(khoa)
    if d is None:
        raise HTTPException(404, f"Khong co duong di {tu} -> {den} cho kich ban {kich_ban}")
    ban_do = {**d["ban_do"], "toa_do": dd["hinh_ban_do"][khoa]}
    return {**d, "ban_do": ban_do}


@app.get("/api/phan-luong/canh")
def phan_luong_canh():
    """Luu luong, V/C va chenh lech theo kich ban tren tung canh (GeoJSON)."""
    f = os.path.join(ROOT, "serving", "phan_luong_canh.geojson")
    if not os.path.exists(f):
        raise HTTPException(404, "Chua co ket qua phan luong. Chay: python graph/chay_phan_luong.py")
    return FileResponse(f, media_type="application/geo+json", headers={"Cache-Control": "no-cache"})


# --- phuc vu trang web tinh ---
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    def trang_chu():
        return FileResponse(os.path.join(STATIC_DIR, "index.html"),
                            headers={"Cache-Control": "no-cache"})
