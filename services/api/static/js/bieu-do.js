// Bieu do ve bang SVG/HTML thuan, khong dung thu vien ngoai.
import { mauLienTuc } from './mau.js';

const NS = 'http://www.w3.org/2000/svg';

function the(ten, thuocTinh = {}, chu) {
  const el = document.createElementNS(NS, ten);
  for (const [k, v] of Object.entries(thuocTinh)) el.setAttribute(k, v);
  if (chu != null) el.textContent = chu;
  return el;
}

const ngayThang = new Intl.DateTimeFormat('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh', day: '2-digit', month: '2-digit' });

// Lich su toc do cua mot diem do: toc do do duoc va toc do dong tu do
export function veLichSu(khung, diem) {
  khung.replaceChildren();
  const ds = diem.filter((d) => d.current_speed != null);
  if (ds.length < 2) {
    khung.textContent = 'Chưa đủ dữ liệu để vẽ.';
    return;
  }

  const W = 320, H = 150, trai = 28, duoi = 18, tren = 6;
  const t0 = Date.parse(ds[0].ts), t1 = Date.parse(ds[ds.length - 1].ts);
  const vMax = Math.ceil(Math.max(...ds.map((d) => Math.max(d.current_speed, d.freeflow_speed ?? 0))) / 10) * 10;
  const x = (ts) => trai + ((Date.parse(ts) - t0) / (t1 - t0)) * (W - trai - 4);
  const y = (v) => tren + (1 - v / vMax) * (H - tren - duoi);

  const svg = the('svg', { viewBox: `0 0 ${W} ${H}` });

  for (const v of [0, vMax / 2, vMax]) {
    svg.append(the('line', { class: 'truc', x1: trai, x2: W - 4, y1: y(v), y2: y(v) }));
    svg.append(the('text', { class: 'nhan-truc', x: trai - 4, y: y(v) + 3, 'text-anchor': 'end' }, v));
  }
  svg.append(the('text', { class: 'nhan-truc', x: trai, y: H - 4 }, ngayThang.format(t0)));
  svg.append(the('text', { class: 'nhan-truc', x: W - 4, y: H - 4, 'text-anchor': 'end' }, ngayThang.format(t1)));

  const toaDo = (truong) => ds.filter((d) => d[truong] != null)
    .map((d) => `${x(d.ts).toFixed(1)},${y(d[truong]).toFixed(1)}`).join(' ');
  svg.append(the('polyline', { class: 'duong-tu-do', points: toaDo('freeflow_speed') }));
  svg.append(the('polyline', { class: 'duong-hien-tai', points: toaDo('current_speed') }));

  khung.append(svg);
}

// Ban do nhiet: moi dong la mot diem do, moi cot la mot gio trong ngay
export function veNhiet(khung, banGhi, khiChon) {
  khung.replaceChildren();

  const theoDiem = new Map();
  for (const r of banGhi) {
    if (!theoDiem.has(r.segment_id)) theoDiem.set(r.segment_id, { ten: r.ten, gio: new Array(24).fill(null) });
    theoDiem.get(r.segment_id).gio[r.gio] = r;
  }

  khung.append(document.createElement('span'));
  for (let h = 0; h < 24; h++) {
    const o = document.createElement('span');
    o.className = 'gio';
    o.textContent = h % 3 === 0 ? h : '';
    khung.append(o);
  }

  for (const [ma, { ten, gio }] of [...theoDiem].sort(([a], [b]) => a.localeCompare(b))) {
    const nhan = document.createElement('span');
    nhan.className = 'ten-dong';
    nhan.textContent = ten;
    nhan.title = ten;
    nhan.addEventListener('click', () => khiChon(ma));
    khung.append(nhan);

    for (let h = 0; h < 24; h++) {
      const o = document.createElement('span');
      o.className = 'o';
      const r = gio[h];
      if (r && r.ratio_tb != null) {
        o.style.background = mauLienTuc(r.ratio_tb);
        o.title = `${ten} · ${h}h: ${r.ratio_tb.toFixed(2)} (${r.toc_do_tb} km/h, ${r.so_mau} lần đo)`;
      }
      khung.append(o);
    }
  }
}
