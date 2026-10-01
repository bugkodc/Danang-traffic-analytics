// Ban do MapLibre: nen, mat nuoc, mang luoi duong, toa nha 3D, diem do va tuyen.
import { MAU_MUC, TEN_MUC } from './mau.js';

const TAM_HAI_CHAU = [108.2215, 16.0625];

const NEN = {
  version: 8,
  sources: {
    toi: {
      type: 'raster',
      tiles: ['https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}'],
      tileSize: 256,
      maxzoom: 16,                       // nguon nay khong co tile sau hon 16
      attribution: 'Nền: Esri · Dữ liệu đường: © OpenStreetMap',
    },
    've-tinh': {
      type: 'raster',
      tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],
      tileSize: 256,
      maxzoom: 19,
      attribution: 'Ảnh vệ tinh: Esri',
    },
  },
  layers: [
    { id: 'nen-toi', type: 'raster', source: 'toi' },
    { id: 'nen-ve-tinh', type: 'raster', source: 've-tinh', layout: { visibility: 'none' } },
  ],
};

// Do rong duong theo cap (thuoc tinh h trong duong_chinh.geojson)
const RONG_THEO_CAP = [
  'match', ['get', 'h'],
  ['trunk', 'trunk_link'], 3,
  ['primary', 'primary_link'], 2.4,
  ['secondary', 'secondary_link'], 1.6,
  ['tertiary', 'tertiary_link'], 1.1,
  0.6,
];

let banDo = null;
const danhDau = new Map();           // segment_id -> maplibregl.Marker

export function taoBanDo(idKhung) {
  banDo = new maplibregl.Map({
    container: idKhung,
    style: NEN,
    center: TAM_HAI_CHAU,
    zoom: 14,
    pitch: 45,
    bearing: -15,
  });
  banDo.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'top-right');
  banDo.addControl(new maplibregl.ScaleControl(), 'bottom-right');
  banDo.on('error', (e) => console.error('Ban do:', e.error?.message || e));

  return new Promise((xong) => banDo.on('load', () => {
    themLop();
    xong(banDo);
  }));
}

function themLop() {
  banDo.addSource('mat-nuoc', { type: 'geojson', data: '/api/mat-nuoc' });
  banDo.addLayer({
    id: 'mat-nuoc', type: 'fill', source: 'mat-nuoc',
    paint: { 'fill-color': '#1c3f5e', 'fill-opacity': 0.6 },
  });

  banDo.addSource('duong', { type: 'geojson', data: '/api/duong-chinh' });
  banDo.addLayer({
    id: 'duong', type: 'line', source: 'duong',
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: {
      'line-color': ['match', ['get', 'h'], ['trunk', 'primary'], '#8a94a3', '#5f6875'],
      'line-width': ['interpolate', ['linear'], ['zoom'], 12, ['*', RONG_THEO_CAP, 0.5], 16, ['*', RONG_THEO_CAP, 2]],
    },
  });

  banDo.addSource('toa-nha', { type: 'geojson', data: '/api/toa-nha' });
  banDo.addLayer({
    id: 'toa-nha', type: 'fill-extrusion', source: 'toa-nha', minzoom: 13,
    paint: {
      'fill-extrusion-color': ['interpolate', ['linear'], ['get', 'c'], 5, '#2b323c', 40, '#3c4654', 100, '#55606f'],
      'fill-extrusion-height': ['get', 'c'],
      'fill-extrusion-opacity': 0.85,
    },
  });

  // Ket qua gan luong (an cho toi khi mo tab Phan luong)
  banDo.addSource('pl-canh', { type: 'geojson', data: RONG });
  banDo.addLayer({
    id: 'pl-canh', type: 'line', source: 'pl-canh',
    layout: { visibility: 'none', 'line-cap': 'round', 'line-join': 'round' },
  });
  banDo.addSource('pl-dong', { type: 'geojson', data: RONG });
  banDo.addLayer({
    id: 'pl-dong', type: 'line', source: 'pl-dong',
    paint: { 'line-color': '#f8f9fa', 'line-width': 7, 'line-dasharray': [1, 1] },
  });

  // Hai duong de so sanh: theo ban do thong thoang (net dut) va tranh tac nghen
  banDo.addSource('tuyen', { type: 'geojson', data: RONG });
  banDo.addLayer({
    id: 'tuyen-tinh', type: 'line', source: 'tuyen', filter: ['==', ['get', 'loai'], 'tinh'],
    paint: { 'line-color': '#c9ced6', 'line-width': 3, 'line-dasharray': [2, 2] },
  });
  banDo.addLayer({
    id: 'tuyen-tac-nghen', type: 'line', source: 'tuyen', filter: ['==', ['get', 'loai'], 'tac-nghen'],
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: { 'line-color': MAU_MUC[1], 'line-width': 5 },
  });
}

const RONG = { type: 'FeatureCollection', features: [] };
let daNapPhanLuong = false;

// Do rong theo luu luong (xe/gio)
const RONG_THEO_LUU_LUONG = ['interpolate', ['linear'], ['get', 'x'], 0, 1, 1500, 4, 4000, 8];

/**
 * maKichBan = null       -> an lop
 *           = 'hien-trang' -> to mau theo V/C cua hien trang
 *           = ma kich ban  -> to mau theo chenh lech luu luong so voi hien trang
 */
export function hienPhanLuong(maKichBan, canhTacDong = []) {
  if (!daNapPhanLuong && maKichBan) {
    banDo.getSource('pl-canh').setData('/api/phan-luong/canh');
    daNapPhanLuong = true;
  }
  banDo.getSource('pl-dong').setData({
    type: 'FeatureCollection',
    features: canhTacDong.map((c) => ({ type: 'Feature', properties: {}, geometry: { type: 'LineString', coordinates: c } })),
  });
  if (!maKichBan) {
    hienLop('pl-canh', false);
    return;
  }

  if (maKichBan === 'hien-trang') {
    banDo.setFilter('pl-canh', ['>=', ['get', 'x'], 30]);
    banDo.setPaintProperty('pl-canh', 'line-color',
      ['interpolate', ['linear'], ['get', 'vc'], 0.3, MAU_MUC[1], 0.7, MAU_MUC[2], 0.9, MAU_MUC[3], 1.1, MAU_MUC[4]]);
    banDo.setPaintProperty('pl-canh', 'line-width', RONG_THEO_LUU_LUONG);
  } else {
    banDo.setFilter('pl-canh', ['>=', ['abs', ['get', maKichBan]], 30]);
    banDo.setPaintProperty('pl-canh', 'line-color',
      ['interpolate', ['linear'], ['get', maKichBan], -1000, '#4dabf7', 0, '#868e96', 1000, '#ff6b6b']);
    banDo.setPaintProperty('pl-canh', 'line-width',
      ['interpolate', ['linear'], ['abs', ['get', maKichBan]], 30, 1.5, 1500, 7]);
  }
  hienLop('pl-canh', true);
}

export function hienLop(id, hien) {
  banDo.setLayoutProperty(id, 'visibility', hien ? 'visible' : 'none');
}

export function veDiemDo(dsDoan, khiChon) {
  for (const d of dsDoan) {
    let m = danhDau.get(d.segment_id);
    if (!m) {
      const el = document.createElement('div');
      el.className = 'diem-do';
      el.addEventListener('click', () => khiChon(d.segment_id));
      m = new maplibregl.Marker({ element: el }).setLngLat([d.lon, d.lat]).addTo(banDo);
      danhDau.set(d.segment_id, m);
    }
    const el = m.getElement();
    el.style.setProperty('--mau', MAU_MUC[d.muc_tac]);
    el.title = `${d.ten}\n${TEN_MUC[d.muc_tac]}` + (d.current_speed != null ? ` · ${d.current_speed} km/h` : '');
  }
}

export function danhDauDiemChon(id) {
  for (const [ma, m] of danhDau) m.getElement().classList.toggle('dang-chon', ma === id);
}

export function bayToi(lon, lat) {
  banDo.easeTo({ center: [lon, lat], zoom: Math.max(banDo.getZoom(), 15), duration: 600 });
}

function duong(toaDo, loai) {
  return { type: 'Feature', properties: { loai }, geometry: { type: 'LineString', coordinates: toaDo } };
}

// toa do dang [lon, lat]
export function veTuyen(tinh, tacNghen) {
  const features = [];
  if (tinh) features.push(duong(tinh, 'tinh'));
  if (tacNghen) features.push(duong(tacNghen, 'tac-nghen'));
  banDo.getSource('tuyen').setData({ type: 'FeatureCollection', features });

  if (features.length) {
    const khung = new maplibregl.LngLatBounds();
    features.forEach((f) => f.geometry.coordinates.forEach((c) => khung.extend(c)));
    banDo.fitBounds(khung, { padding: 60, duration: 600 });
  }
}
