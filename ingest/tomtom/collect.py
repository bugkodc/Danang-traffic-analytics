"""
Thu thap du lieu toc do giao thong tu TomTom Traffic Flow Segment Data API.

Chay dinh ky (khuyen nghi 15 phut/lan) qua Windows Task Scheduler.
Moi lan chay: goi API cho tung doan trong segments.csv, ghi noi tiep vao
data/YYYY-MM-DD.parquet

Cach dung:
    set TOMTOM_API_KEY=xxxxx
    python collect.py
"""

import os
import sys
import csv
import time
import logging
from datetime import datetime, timezone, timedelta

import requests
import pandas as pd

# ---------------------------------------------------------------- cau hinh
HERE = os.path.dirname(os.path.abspath(__file__))
SEGMENTS_FILE = os.path.join(HERE, "segments.csv")
DATA_DIR = os.path.join(HERE, "data")
LOG_FILE = os.path.join(HERE, "collect.log")

API_URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
ZOOM = 10
SLEEP_BETWEEN_CALLS = 0.5   # giay - tranh goi don dap
TIMEOUT = 20

VN_TZ = timezone(timedelta(hours=7))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


def doc_segments(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def goi_api(api_key, lat, lon):
    """Tra ve dict du lieu luu luong cho 1 diem, hoac None neu loi."""
    params = {"key": api_key, "point": f"{lat},{lon}", "unit": "KMPH"}
    r = requests.get(API_URL, params=params, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json().get("flowSegmentData")


def main():
    api_key = os.environ.get("TOMTOM_API_KEY")
    if not api_key:
        log.error("Chua dat bien moi truong TOMTOM_API_KEY. Dung lai.")
        sys.exit(1)

    os.makedirs(DATA_DIR, exist_ok=True)
    segments = doc_segments(SEGMENTS_FILE)
    now = datetime.now(VN_TZ)
    rows = []

    for seg in segments:
        try:
            d = goi_api(api_key, seg["lat"], seg["lon"])
            if not d:
                log.warning("%s: API tra ve rong", seg["segment_id"])
                continue

            cur = d.get("currentSpeed")
            free = d.get("freeFlowSpeed")
            rows.append({
                "ts_utc":               now.astimezone(timezone.utc),
                "ts_local":             now,
                "segment_id":           seg["segment_id"],
                "ten":                  seg["ten"],
                "lat":                  float(seg["lat"]),
                "lon":                  float(seg["lon"]),
                "frc":                  d.get("frc"),
                "current_speed":        cur,
                "freeflow_speed":       free,
                "current_travel_time":  d.get("currentTravelTime"),
                "freeflow_travel_time": d.get("freeFlowTravelTime"),
                # ty le toc do hien tai / toc do dong tu do: cang nho cang tac
                "speed_ratio":          round(cur / free, 4) if cur and free else None,
                "confidence":           d.get("confidence"),
                "road_closure":         d.get("roadClosure"),
            })
        except Exception as e:
            log.warning("%s: loi - %s", seg["segment_id"], e)
        time.sleep(SLEEP_BETWEEN_CALLS)

    if not rows:
        log.error("Khong thu duoc ban ghi nao.")
        sys.exit(2)

    df_moi = pd.DataFrame(rows)
    out = os.path.join(DATA_DIR, f"{now:%Y-%m-%d}.parquet")

    if os.path.exists(out):
        df_moi = pd.concat([pd.read_parquet(out), df_moi], ignore_index=True)

    df_moi.to_parquet(out, index=False)
    log.info("Ghi %d/%d doan -> %s (tong %d ban ghi trong ngay)",
             len(rows), len(segments), os.path.basename(out), len(df_moi))


if __name__ == "__main__":
    main()
