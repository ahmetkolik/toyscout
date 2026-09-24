// Paste into javascript_tool on an open https://www.amazon.com/dp/... tab (Claude in Chrome).
// Needs receiver.py running:  python3 products/browser_import/receiver.py products/browser_import/res
// and a candidates file served by the receiver at GET / as {"first":[{asin,cat,src,rank,sub,rating,rc,price},...]}
// (the receiver reads ../cands.json relative to its result dir). Results land in res/<ASIN>.json;
// then run products/browser_import/import_results.py.
window.__one = async (asin, meta) => {
  const r = await fetch('/dp/'+asin, {credentials:'include'});
  const h = await r.text();
  if (h.length < 50000 || /api-services-support@amazon|Enter the characters you see/i.test(h)) return {asin, err:'captcha', len:h.length};
  const doc = new DOMParser().parseFromString(h,'text/html');
  const t = s => (doc.querySelector(s)?.textContent||'').replace(/\s+/g,' ').trim();
  const name = t('#productTitle');
  let rating = (doc.querySelector('#acrPopover')?.getAttribute('title')||'').match(/([\d.]+) out of 5/)?.[1] || (h.match(/([\d.]+) out of 5 stars/)||[])[1];
  const rc = parseInt((t('#acrCustomerReviewText').match(/[\d,]+/)||['0'])[0].replace(/,/g,''))||null;
  const pm = doc.querySelector('#corePrice_feature_div .a-offscreen')?.textContent || (h.match(/"priceAmount":([\d.]+)/)||[])[1];
  const price = pm ? String(pm).replace(/[$,]/g,'') : null;
  const body = doc.body.textContent.replace(/\s+/g,' ');
  const bi = body.indexOf('Best Sellers Rank'); const bsr=[];
  if (bi>-1) { const seg = body.slice(bi, bi+700); for (const m of seg.matchAll(/#([\d,]+)\s*in\s*([^(#]{2,60}?)(?=\s*\(|\s*#|$)/g)) { const c=m[2].trim(); if(!bsr.some(x=>x.cat===c)) bsr.push({rank:parseInt(m[1].replace(/,/g,'')),cat:c}); } }
  const bullets = [...doc.querySelectorAll('#feature-bullets li')].map(l=>l.textContent.replace(/\s+/g,' ').trim()).filter(x=>x.length>15 && !/Make sure this fits/.test(x)).slice(0,6);
  const i = h.indexOf("'colorImages': { 'initial'"); const imgs=[];
  if (i>-1) for (const m of h.slice(i,i+60000).matchAll(/"hiRes":"(https:[^"]+)"/g)) if(!imgs.includes(m[1])) imgs.push(m[1]);
  if (!imgs.length) { const m = doc.querySelector('#landingImage')?.getAttribute('data-old-hires'); if (m) imgs.push(m); }
  const out = {asin, name, rating: rating?parseFloat(rating):null, rc, price, bsr, bullets, images: imgs.slice(0,6), meta};
  await fetch('http://localhost:8765/', {method:'POST', body: JSON.stringify(out)});
  return {asin, ok:true};
};
// Loop (delay is done SERVER-side because setTimeout is throttled in hidden tabs):
const j = await (await fetch('http://localhost:8765/')).json(); window.__list = j.first;
const P = {done:0, ok:0, err:0, capt:0, run:true, stop:false, log:[]}; window.__prog = P;
(async () => { let cc=0; for (const c of window.__list) { if (P.stop) break;
  try { const r = await window.__one(c.asin, {cat:c.cat, src:c.src, rank:c.rank, sub:c.sub, lrating:c.rating, lrc:c.rc, lprice:c.price});
    if (r.ok) {P.ok++; cc=0;} else {P.err++; P.capt++; cc++; P.log.push(r.asin+':'+r.err);} } catch(e) { P.err++; P.log.push(c.asin+':'+e.message); }
  P.done++; if (cc>=4) {P.stop=true; P.log.push('STOP captcha x4');}
  try { await fetch('http://localhost:8765/sleep'); } catch(e) {} } P.run=false; })();
// Poll with:  ({...window.__prog, log: window.__prog.log.slice(-5)})
