/*
 * index.html icindeki var POSTS={...} blogunu cikarip JSON'a dokum eder.
 *
 * NEDEN: blog yazilarinin govdesi bir JS fonksiyonu (body(): string dondurur),
 * string birlestirmesiyle uretiliyor. Statik sayfa uretmek icin once
 * calistirilmasi gerekiyor. Python'dan degerlendirilemez, Node sart.
 *
 * Kullanim: node products/extract_posts.js > /tmp/posts.json
 */
const fs = require('fs');
const path = require('path');

const SITE = path.dirname(__dirname);
const html = fs.readFileSync(path.join(SITE, 'index.html'), 'utf8');

// --- POSTS blogunu parantez esleyerek cikar
const start = html.indexOf('var POSTS={');
if (start === -1) throw new Error('POSTS bulunamadi');
let i = html.indexOf('{', start), depth = 0, end = -1;
for (let j = i; j < html.length; j++) {
  if (html[j] === '{') depth++;
  else if (html[j] === '}') { depth--; if (depth === 0) { end = j; break; } }
}
const block = html.slice(i, end + 1);

// --- index.html'deki yardimcilarin birebir kopyalari
const AFF = 'kolico-20';
function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
function amazonSearchUrl(name) {
  return 'https://www.amazon.com/s?k=' + encodeURIComponent(name) +
         '&i=toys-and-games&tag=' + AFF;
}
// Catalog lookup by ASIN (js/data.js is the source of truth) for the product
// photo and the /product/<cat>/<idx> details link.
const dataSrc = fs.readFileSync(path.join(SITE, 'js', 'data.js'), 'utf8');
const D = JSON.parse(dataSrc.slice(dataSrc.indexOf('{'), dataSrc.lastIndexOf('}') + 1));
const BY_ASIN = {};
for (const c of Object.keys(D)) {
  (D[c] || []).forEach((p, i) => { if (p.asin && !BY_ASIN[p.asin]) BY_ASIN[p.asin] = [c, i, p.img]; });
}
function affUrl(u) {
  u = u || '';
  if (!/amazon\./.test(u) || /[?&]tag=/.test(u)) return u;
  return u + (u.indexOf('?') >= 0 ? '&' : '?') + 'tag=' + AFF;
}
function A(u) { return u && !/^(https?:)?\//.test(u) ? '/' + u : u; }
function aProd(name, meta, url) {
  const m = (url || '').match(/\/dp\/([A-Z0-9]{10})/);
  const hit = m ? BY_ASIN[m[1]] : null;
  let img = hit && hit[2] ? A(hit[2]) : '';
  if (img && !fs.existsSync(path.join(SITE, img.replace(/^\//, '')))) img = '';
  return '<div class="a-prod">' +
    (img ? '<img class="ap-img" src="' + esc(img) + '" width="88" height="88" loading="lazy" alt="' + esc(name) + '">' : '') +
    '<div class="t"><b>' + esc(name) + '</b><span>' + esc(meta) + '</span></div>' +
    '<div class="ap-acts">' +
    (hit ? '<a class="ap-det" href="/product/' + hit[0] + '/' + hit[1] + '" data-prod="' + hit[0] + ':' + hit[1] + '">Details</a>' : '') +
    '<a class="btn btn-blue" style="padding:11px 22px;font-size:14px" target="_blank" rel="sponsored noopener" href="' +
    esc(affUrl(url)) + '">Check price on Amazon</a></div></div>';
}

const POSTS = eval('(' + block + ')');

const out = {};
for (const key of Object.keys(POSTS)) {
  const p = POSTS[key];
  out[key] = {
    meta: p.meta,
    h: p.h,
    body: typeof p.body === 'function' ? p.body() : String(p.body || ''),
  };
}
process.stdout.write(JSON.stringify(out, null, 1));
