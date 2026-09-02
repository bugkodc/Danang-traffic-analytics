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
        ket_qua.append({
            "segment_id":     r.segment_id,
            "ten":            r.ten,
            "lat":            float(r.lat),
            "lon":            float(r.lon),
            "current_speed":  None if pd.isna(r.current_speed) else int(r.current_speed),
            "freeflow_speed": None if pd.isna(r.freeflow_speed) else int(r.freeflow_speed),
            "speed_ratio":    None if pd.isna(ratio) else round(float(ratio), 3),
            "muc_tac":        muc_tac_nghen(ratio),
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
    return FileResponse(f, media_type="application/geo+json")


# --- phuc vu trang web tinh ---
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    def trang_chu():
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
