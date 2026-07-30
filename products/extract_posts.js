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
function aProd(name, meta, url) {
  return '<div class="a-prod"><div class="t"><b>' + esc(name) + '</b><span>' +
    esc(meta) + '</span></div><a class="btn btn-blue" style="padding:11px 22px;' +
    'font-size:14px" target="_blank" rel="noopener sponsored" href="' + esc(url) +
    '">View on Amazon</a></div>';
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
