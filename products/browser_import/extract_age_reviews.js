// Amazon /dp/ sekmesinde calistir (Claude in Chrome javascript_tool). receiver.py acik olmali:
//   python3 products/browser_import/receiver.py <res_klasoru>   (GET / -> <res_klasoru>/../cands.json = {"first":[{asin,cat},...]})
// Sonra:  python3 products/browser_import/apply_age_reviews.py <res_klasoru>
// Ilerleme:  ({...window.__prog, log: window.__prog.log.slice(-5)})   — Sekme arka planda kalirsa yavaslar (screenshot al).
window.__one = async (asin, meta) => {
  const r = await fetch('/dp/'+asin, {credentials:'include'});
  const h = await r.text();
  if (h.length < 50000 || /api-services-support@amazon|Enter the characters you see/i.test(h)) return {asin, err:'captcha', len:h.length};
  const doc = new DOMParser().parseFromString(h,'text/html');
  const t = (s,root) => ((root||doc).querySelector(s)?.textContent||'').replace(/\s+/g,' ').trim();
  const txt = doc.body.textContent.replace(/\s+/g,' ');
  const am = txt.match(/Manufacturer recommended age\s*:?\s*(\d+)\s*(years?|months?)/i);
  const ageMonths = am ? (/month/i.test(am[2]) ? parseInt(am[1]) : parseInt(am[1])*12) : null;
  const rating = (doc.querySelector('#acrPopover')?.getAttribute('title')||'').match(/([\d.]+) out of 5/)?.[1];
  const rc = parseInt((t('#acrCustomerReviewText').match(/[\d,]+/)||['0'])[0].replace(/,/g,''))||null;
  const pm = doc.querySelector('#corePrice_feature_div .a-offscreen')?.textContent;
  const price = pm ? String(pm).replace(/[$,]/g,'') : null;
  const starEl = x => (x.querySelector('[data-hook="review-star-rating"] .a-icon-alt') || x.querySelector('[data-hook="cmps-review-star-rating"] .a-icon-alt') || x.querySelector('.a-icon-alt'));
  const reviews = [...doc.querySelectorAll('[data-hook="review"]')].map(x=>({
    name: t('.a-profile-name',x), stars: parseFloat(starEl(x)?.textContent)||0,
    title: t('[data-hook="reviewTitle"], [data-hook="review-title"]',x).replace(/^[\d.]+ out of 5 stars\s*/,''),
    date: t('[data-hook="review-date"]',x).replace(/^Reviewed in .*? on /,''),
    body: t('[data-hook="reviewText"], [data-hook="review-body"]',x).replace(/Brief content visible, double tap to read full content\.?/g,'').replace(/Full content visible, double tap to read brief content\.?/g,'').replace(/Read more\s*Read less\s*$/,'').replace(/Read more\s*$/,'').trim(),
    verified: !!x.querySelector('[data-hook="avp-badge"]')}))
    .filter(v=>v.name && v.stars>=4 && v.body.length>=40 && v.body.length<=600).slice(0,3);
  const out = {asin, ageMonths, rating: rating?parseFloat(rating):null, rc, price, reviews, meta};
  await fetch('http://localhost:8765/', {method:'POST', body: JSON.stringify(out)});
  return {asin, ok:true, ageMonths, nrev:reviews.length};
};
const j = await (await fetch('http://localhost:8765/')).json(); window.__list = j.first;
const P = {done:0, ok:0, err:0, capt:0, run:true, stop:false, log:[]}; window.__prog = P;
(async () => { let cc=0; for (const c of window.__list) { if (P.stop) break;
  try { const r = await window.__one(c.asin, {cat:c.cat}); if (r.ok) {P.ok++; cc=0;} else {P.err++; P.capt++; cc++; P.log.push(r.asin+':'+r.err);} } catch(e) { P.err++; P.log.push(c.asin+':'+e.message); }
  P.done++; if (cc>=4) {P.stop=true; P.log.push('STOP captcha x4');}
  try { await fetch('http://localhost:8765/sleep'); } catch(e) {} } P.run=false; })();
