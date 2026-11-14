"""Interactive map: colorful street tiles, satellite toggle, locate me, address search, nearest-first list,
and Apple Maps / Google Maps hand-off. Runs in the browser with Leaflet."""
import json

import streamlit.components.v1 as components

DEFAULT_CENTER = (37.8719, -122.2585)  # UC Berkeley campus

TEMPLATE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{box-sizing:border-box}
html,body{margin:0;height:100%;font-family:'Nunito',system-ui,-apple-system,'Segoe UI',sans-serif;color:#2B3A33;background:#FFF8EC}
#app{display:grid;grid-template-columns:380px 1fr;height:100%;gap:14px}
#panel{display:flex;flex-direction:column;min-height:0;background:#fff;border-radius:24px;box-shadow:0 10px 30px rgba(31,92,69,.12);overflow:hidden}
#mapwrap{border-radius:24px;overflow:hidden;box-shadow:0 10px 30px rgba(31,92,69,.12);position:relative;min-height:320px}
#map{position:absolute;inset:0}
.top{padding:14px 14px 10px;background:linear-gradient(120deg,#1F5C45,#2F7D5B);color:#FFF8EC}
.top h4{margin:0 0 8px;font-size:17px;font-weight:800}
.row{display:flex;gap:8px}
input[type=text]{flex:1;min-width:0;border:0;border-radius:999px;padding:10px 14px;font:inherit;font-size:14px}
button{border:0;border-radius:999px;font:inherit;font-weight:800;cursor:pointer}
.go{background:#F6B93B;color:#1F5C45;padding:10px 16px;font-size:14px}
.loc{margin-top:8px;width:100%;background:rgba(255,248,236,.18);color:#FFF8EC;padding:9px;font-size:14px}
.loc:hover{background:rgba(255,248,236,.3)}
#status{font-size:13px;margin-top:8px;min-height:16px;opacity:.95}
.chips{display:flex;flex-wrap:wrap;gap:6px;padding:10px 12px 4px}
.chip{padding:5px 11px;font-size:13px;border:2px solid;background:#fff}
.chip.off{opacity:.4}
.modes{display:flex;gap:6px;padding:4px 12px 8px;align-items:center;font-size:13px;font-weight:700}
.mode{padding:4px 11px;background:#F3E9D2;color:#1F5C45;font-size:13px}
.mode.on{background:#1F5C45;color:#fff}
#list{flex:1;overflow:auto;padding:4px 12px 12px}
.item{border-radius:18px;padding:11px 13px;margin-bottom:9px;background:#FFF8EC;cursor:pointer;border:2px solid transparent}
.item:hover,.item.sel{border-color:#F6B93B;background:#fff}
.item b{font-size:15px}
.dist{float:right;font-size:12px;font-weight:800;color:#1F5C45;background:#D3EEDD;border-radius:999px;padding:2px 9px}
.pill{display:inline-block;border-radius:999px;padding:2px 9px;font-size:11.5px;font-weight:800;margin:3px 0}
.sub{font-size:13px;color:#5d6b64;margin:2px 0 6px}
.nav{display:flex;flex-wrap:wrap;gap:6px}
a.b{display:inline-block;background:#1F5C45;color:#FFF8EC;text-decoration:none;border-radius:999px;padding:6px 12px;font-size:12.5px;font-weight:800}
a.b.g{background:#E4572E}
.leaflet-popup-content-wrapper{border-radius:18px}
.leaflet-popup-content{margin:14px 16px;font-size:13.5px;line-height:1.45;min-width:210px}
.empty{padding:18px;text-align:center;color:#5d6b64;font-size:14px}
@media (max-width:820px){#app{grid-template-columns:1fr;grid-template-rows:340px 1fr}#mapwrap{order:-1}}
</style></head><body>
<div id="app">
 <div id="panel">
  <div class="top">
   <h4>__TITLE__</h4>
   <div class="row"><input id="q" type="text" placeholder="Type an address or neighborhood"><button class="go" id="go">Search</button></div>
   <button class="loc" id="loc">Use my current location</button>
   <div id="status"></div>
  </div>
  <div class="chips" id="chips"></div>
  <div class="modes"><span>Directions by</span>
   <button class="mode on" data-m="walking">Walk</button><button class="mode" data-m="driving">Drive</button><button class="mode" data-m="transit">Transit</button></div>
  <div id="list"></div>
 </div>
 <div id="mapwrap"><div id="map"></div></div>
</div>
<script>
const D = __DATA__;
const pts = D.points; let origin = null, mode = 'walking', selected = null;
const hidden = new Set(); const markers = {};
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

const map = L.map('map', {zoomControl: true}).setView(D.center, 13);
const esri = 'Tiles &copy; Esri';
const streets = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {maxZoom: 19, attribution: esri});
const soft = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {subdomains: 'abcd', maxZoom: 20, attribution: '&copy; OpenStreetMap contributors &copy; CARTO'});
const sat = L.layerGroup([
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {maxZoom: 19, attribution: esri}),
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}', {maxZoom: 19})
]);
streets.addTo(map);
L.control.layers({'Colorful map': streets, 'Soft map': soft, 'Satellite': sat}, null, {position: 'topright'}).addTo(map);

function pin(color, size) {
  const w = size || 34, h = Math.round(w * 1.3);
  return L.divIcon({className: '', iconSize: [w, h], iconAnchor: [w / 2, h - 2], popupAnchor: [0, -h + 8],
    html: `<svg width="${w}" height="${h}" viewBox="0 0 34 44"><path d="M17 43C7 30 2 24 2 16a15 15 0 0 1 30 0c0 8-5 14-15 27z" fill="${color}" stroke="#fff" stroke-width="2.5"/><circle cx="17" cy="16" r="6" fill="#fff"/></svg>`});
}

const dest = p => p.nav_query ? encodeURIComponent(p.nav_query) : p.lat + ',' + p.lon;
const gUrl = p => 'https://www.google.com/maps/dir/?api=1&destination=' + dest(p) + '&travelmode=' + mode + (origin ? '&origin=' + origin.lat + ',' + origin.lon : '');
const aUrl = p => 'https://maps.apple.com/?daddr=' + dest(p) + '&dirflg=' + ({walking: 'w', driving: 'd', transit: 'r'}[mode]) + (origin ? '&saddr=' + origin.lat + ',' + origin.lon : '');

function miles(a, b, c, d) {
  const R = 3958.8, r = x => x * Math.PI / 180, dLat = r(c - a), dLon = r(d - b);
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(r(a)) * Math.cos(r(c)) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(h));
}
function distText(p) {
  if (!origin) return '';
  const m = miles(origin.lat, origin.lon, p.lat, p.lon);
  const walk = Math.round(m * 20);
  return (m < 0.1 ? '<0.1' : m.toFixed(1)) + ' mi' + (walk <= 90 ? ' · ' + walk + ' min walk' : '');
}
function body(p) {
  const bits = [];
  if (p.description) bits.push(`<div class="sub">${esc(p.description)}</div>`);
  if (p.extra) bits.push(`<div class="sub"><b>${esc(p.extra)}</b></div>`);
  if (p.address) bits.push(`<div class="sub">${esc(p.address)}${p.contact ? ' · ' + esc(p.contact) : ''}</div>`);
  return bits.join('');
}
function navButtons(p) {
  return `<div class="nav"><a class="b" target="_blank" rel="noopener" href="${aUrl(p)}">Apple Maps</a><a class="b g" target="_blank" rel="noopener" href="${gUrl(p)}">Google Maps</a>` +
    (p.url ? `<a class="b" style="background:#8E5EA2" target="_blank" rel="noopener" href="${esc(p.url)}">More info</a>` : '') + '</div>';
}
function popup(p) {
  const d = distText(p);
  return `<b style="font-size:15px">${esc(p.name)}</b><br><span class="pill" style="background:${p.soft};color:${p.color}">${esc(p.kind_label)}</span>${d ? ' <b>' + d + '</b>' : ''}${body(p)}${navButtons(p)}`;
}

pts.forEach(p => {
  markers[p.id] = L.marker([p.lat, p.lon], {icon: pin(p.color)}).bindPopup(() => popup(p));
  markers[p.id].on('click', () => { selected = p.id; renderList(false); });
});

function visible() { return pts.filter(p => !hidden.has(p.kind)); }
function renderChips() {
  const kinds = [...new Map(pts.map(p => [p.kind, p])).values()];
  document.getElementById('chips').innerHTML = kinds.map(p =>
    `<button class="chip ${hidden.has(p.kind) ? 'off' : ''}" data-k="${p.kind}" style="color:${p.color};border-color:${p.color}">${esc(p.kind_label)}</button>`).join('');
  document.querySelectorAll('.chip').forEach(b => b.onclick = () => {
    hidden.has(b.dataset.k) ? hidden.delete(b.dataset.k) : hidden.add(b.dataset.k); refresh();
  });
}
function renderList(scroll) {
  let items = visible();
  if (origin) items = items.slice().sort((a, b) => miles(origin.lat, origin.lon, a.lat, a.lon) - miles(origin.lat, origin.lon, b.lat, b.lon));
  const el = document.getElementById('list');
  if (!items.length) { el.innerHTML = '<div class="empty">Nothing to show. Turn a filter back on.</div>'; return; }
  el.innerHTML = items.map(p => `<div class="item ${selected === p.id ? 'sel' : ''}" data-id="${p.id}">
    <span class="dist">${distText(p)}</span><b>${esc(p.name)}</b><br>
    <span class="pill" style="background:${p.soft};color:${p.color}">${esc(p.kind_label)}</span>${body(p)}${navButtons(p)}</div>`).join('');
  el.querySelectorAll('.item').forEach(div => div.onclick = ev => {
    if (ev.target.closest('a')) return;
    const p = pts.find(x => String(x.id) === div.dataset.id); selected = p.id;
    map.flyTo([p.lat, p.lon], Math.max(map.getZoom(), 15)); markers[p.id].openPopup(); renderList(false);
  });
  if (scroll) el.scrollTop = 0;
}
function refresh() {
  pts.forEach(p => hidden.has(p.kind) ? map.removeLayer(markers[p.id]) : markers[p.id].addTo(map));
  renderChips(); renderList(true);
}
function fit() {
  const v = visible().map(p => [p.lat, p.lon]); if (origin) v.push([origin.lat, origin.lon]);
  if (v.length > 1) map.fitBounds(v, {padding: [40, 40], maxZoom: 15}); else if (v.length) map.setView(v[0], 14);
}
let youMarker = null;
function setOrigin(lat, lon, label) {
  origin = {lat, lon, label};
  if (youMarker) map.removeLayer(youMarker);
  youMarker = L.marker([lat, lon], {icon: pin('#1F5C45', 38), zIndexOffset: 1000}).addTo(map).bindPopup('<b>' + esc(label) + '</b>');
  document.getElementById('status').textContent = 'Showing nearest first, from ' + label + '.';
  refresh(); fit();
}
const say = t => document.getElementById('status').textContent = t;

document.getElementById('loc').onclick = () => {
  if (!navigator.geolocation) return say('Location is not available in this browser. Try typing an address.');
  say('Finding you...');
  navigator.geolocation.getCurrentPosition(
    pos => setOrigin(pos.coords.latitude, pos.coords.longitude, 'your location'),
    () => say('Could not get your location. Allow location access, or type an address instead.'),
    {enableHighAccuracy: true, timeout: 10000});
};
async function search() {
  const q = document.getElementById('q').value.trim(); if (!q) return;
  say('Searching...');
  try {
    const url = 'https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=us&viewbox=-122.6,38.1,-121.7,37.4&q=' + encodeURIComponent(q);
    const r = await (await fetch(url)).json();
    if (!r.length) return say('No match for that address. Try adding the city.');
    setOrigin(parseFloat(r[0].lat), parseFloat(r[0].lon), r[0].display_name.split(',').slice(0, 2).join(','));
  } catch (err) { say('Search is unavailable right now. Try "Use my current location".'); }
}
document.getElementById('go').onclick = search;
document.getElementById('q').onkeydown = ev => { if (ev.key === 'Enter') search(); };
document.querySelectorAll('.mode').forEach(b => b.onclick = () => {
  mode = b.dataset.m; document.querySelectorAll('.mode').forEach(x => x.classList.toggle('on', x === b)); renderList(false);
});

refresh(); fit();
</script></body></html>"""


def explorer(points: list[dict], title: str = "Find places near you", height: int = 700) -> None:
    """points: id, name, kind, kind_label, color, soft, lat, lon, address, nav_query, description, extra, contact, url"""
    data = json.dumps({"points": points, "center": DEFAULT_CENTER}).replace("</", "<\\/")
    html = TEMPLATE.replace("__DATA__", data).replace("__TITLE__", title)
    components.html(html, height=height)
