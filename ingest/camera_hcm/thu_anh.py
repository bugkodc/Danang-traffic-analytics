"""
Thu anh tu camera giao thong cong khai TP.HCM.

Anh nay dung de HUAN LUYEN bo phat hien (hoc "xe may trong nhu the nao"),
KHONG dung cho phan case study Da Nang. Xem docs/plan/D-cong-nghe-va-huong-moi.md
muc 2.1 - cach chia nay con tao ra thi nghiem khoang cach mien lien thanh pho.

Nguon: Cong thong tin giao thong TP.HCM (So Xay dung TP.HCM)
    https://giaothong.hochiminhcity.gov.vn
    Endpoint anh: http://camera.thongtingiaothong.vn/api/snapshot/<cam_id>

Danh sach camera lay tu API cong khai cua cong, da loc:
    - CamStatus = UP (dang hoat dong, co anh)
    - Thuoc quan noi thanh (mat do xe may cao nhat)

Cach dung:
    python ingest/camera_hcm/thu_anh.py --mau        # moi camera 1 anh, de CHON
    python ingest/camera_hcm/thu_anh.py              # thu theo danh sach da chon
    python ingest/camera_hcm/thu_anh.py --lap 20 --nghi 180

Tham so:
    --mau     Chi lay 1 anh moi camera roi dung - de xem va chon camera tot
    --lap N   Lap N vong thu anh
    --nghi S  Nghi bao nhieu giay giua hai vong
"""

import os
import sys
import csv
import time
import argparse
import logging
from datetime import datetime, timezone, timedelta

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DS_CAMERA = os.path.join(HERE, "cameras.csv")
THU_MUC_ANH = os.path.join(ROOT, "data", "raw", "anh_hcm")

# Endpoint chinh: qua cong giaothong.hochiminhcity.gov.vn - da kiem chung
# hoat dong on dinh (HTTP 200, ~50 KB JPEG, 0,25 giay).
API = "https://giaothong.hochiminhcity.gov.vn/render/ImageHandler.ashx?id={cam_id}"

# Du phong: endpoint goc do cong tra ve trong truong SnapshotUrl. Chay HTTP
# (khong phai HTTPS) va co the bi chan o mot so mang - de sau lam phuong an hai.
API_DP = "http://camera.thongtingiaothong.vn/api/snapshot/{cam_id}"

VN = timezone(timedelta(hours=7))
NGHI_GIUA_ANH = 0.4      # giay - goi lich su, dung don dap
TIMEOUT = 12          # ngan de camera hong khong lam nghen ca vong

# QUAN TRONG: may chu CHAN request khong co User-Agent (tra ve ReadTimeout).
# curl tu gui header nay nen chay duoc, con requests thi khong -> phai tu dat.
# Day la loi rat kho doan: khong bao loi ro rang, chi treo den het timeout.
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"),
    "Referer": "https://giaothong.hochiminhcity.gov.vn/",
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s",
                    handlers=[logging.FileHandler(os.path.join(HERE, "thu_anh.log"),
                                                  encoding="utf-8"),
                              logging.StreamHandler(sys.stdout)])
log = logging.getLogger(__name__)


def doc_camera(chi_da_chon=False):
    with open(DS_CAMERA, encoding="utf-8") as f:
        ds = [r for r in csv.DictReader(f) if r.get("cam_id")]
    if chi_da_chon:
        # cot 'dung' danh dau x / 1 / co  -> chi thu nhung camera nay
        loc = [r for r in ds if str(r.get("dung", "")).strip().lower() in ("x", "1", "co", "có")]
        if loc:
            return loc
        log.warning("Chua danh dau camera nao o cot 'dung' -> thu TAT CA %d camera.", len(ds))
    return ds


def tai_mot_anh(cam_id):
    """Tra ve bytes anh, hoac None."""
    for url in (API.format(cam_id=cam_id), API_DP.format(cam_id=cam_id)):
        try:
            r = requests.get(url, timeout=TIMEOUT, headers=HEADERS)
            if r.status_code == 200 and r.headers.get("content-type", "").startswith("image"):
                if len(r.content) > 3000:        # anh qua nho = anh loi / anh trang
                    return r.content
        except Exception:
            pass
    return None


def mot_vong(cams, thu_muc):
    now = datetime.now(VN)
    ok = hong = 0
    for c in cams:
        anh = tai_mot_anh(c["cam_id"])
        if anh:
            ten = f"{c['code'].replace(' ', '_').replace('.', '-')}_{now:%Y%m%d_%H%M%S}.jpg"
            d = os.path.join(thu_muc, c["code"].replace(" ", "_").replace(".", "-"))
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, ten), "wb") as f:
                f.write(anh)
            ok += 1
        else:
            hong += 1
        time.sleep(NGHI_GIUA_ANH)
    return ok, hong


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mau", action="store_true",
                    help="Chi lay 1 anh moi camera roi dung, de xem va chon")
    ap.add_argument("--lap", type=int, default=1)
    ap.add_argument("--nghi", type=int, default=180, help="Giay nghi giua hai vong")
    a = ap.parse_args()

    if not os.path.exists(DS_CAMERA):
        log.error("Khong thay %s", DS_CAMERA)
        sys.exit(1)

    if a.mau:
        cams = doc_camera(chi_da_chon=False)
        thu_muc = os.path.join(ROOT, "data", "raw", "anh_hcm_mau")
        log.info("CHE DO MAU: lay 1 anh moi camera (%d camera) de ban XEM VA CHON.", len(cams))
    else:
        cams = doc_camera(chi_da_chon=True)
        thu_muc = THU_MUC_ANH
        log.info("Thu anh tu %d camera, %d vong, nghi %ds giua cac vong.",
                 len(cams), a.lap, a.nghi)

    os.makedirs(thu_muc, exist_ok=True)

    for v in range(1, (1 if a.mau else a.lap) + 1):
        t0 = time.time()
        ok, hong = mot_vong(cams, thu_muc)
        log.info("Vong %d/%d: %d anh OK, %d hong  (%.0fs)",
                 v, 1 if a.mau else a.lap, ok, hong, time.time() - t0)
        if not a.mau and v < a.lap:
            time.sleep(a.nghi)

    log.info("Anh luu tai: %s", thu_muc)
    if a.mau:
        log.info("")
        log.info("BUOC TIEP THEO: mo thu muc tren, xem anh tung camera va chon:")
        log.info("  - GIU  camera co goc chech tu tren xuong 30-45 do, thay ro mat duong")
        log.info("  - BO   camera goc gan ngang (xe che nhau), anh mo, hoac huong vao le duong")
        log.info("Danh dau 'x' vao cot 'dung' trong cameras.csv cho nhung camera giu lai,")
        log.info("roi chay lai khong co --mau de thu anh dinh ky.")


if __name__ == "__main__":
    main()
