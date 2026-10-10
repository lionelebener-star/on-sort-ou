// Recherche de photos libres (Wikipedia/Commons). À coller dans la console d'une page commons.wikimedia.org.
// Définir avant : window.L=[[id,name_fr,name_de,lat,lon,"fr|de|it",town],...]  (activités sans photo)
// 1) article Wikipedia (langue locale puis autre) avec coordonnées à < 3 km -> image principale
// 2) sinon photo Commons géolocalisée à < 500 m. TOUJOURS revoir le résultat à l'œil (planche contact) : ~45 % des choix automatiques étaient faux.
window.PHR={};window.PP={done:0};
const hav=(a,b,c,d)=>{const r=Math.PI/180,x=Math.sin((c-a)*r/2)**2+Math.cos(a*r)*Math.cos(c*r)*Math.sin((d-b)*r/2)**2;return 12742*Math.asin(Math.sqrt(x))};
const BAD=/map|karte|carte|logo|plan|\.svg|panneau|schild|sign|wappen|coat|flag|drapeau|diagram|locator|relief|position/i;
const api=async(host,p)=>{const u=`https://${host}/w/api.php?format=json&origin=*&${p}`;for(let t=0;t<3;t++){try{const r=await fetch(u);if(r.ok)return await r.json()}catch(e){}await new Promise(r=>setTimeout(r,1500))}return null};
async function wiki(lang,q,lat,lon){const s=await api(`${lang}.wikipedia.org`,`action=query&generator=search&gsrsearch=${encodeURIComponent(q)}&gsrlimit=4&prop=pageimages|coordinates&piprop=name&pilicense=free`);
 if(!s||!s.query)return null;const ps=Object.values(s.query.pages).sort((a,b)=>a.index-b.index);
 for(const p of ps){if(!p.pageimage)continue;const c=p.coordinates&&p.coordinates[0];if(c&&hav(lat,lon,c.lat,c.lon)<3&&!BAD.test(p.pageimage))return {f:p.pageimage,via:lang+":"+p.title}}return null}
async function geo(lat,lon){const s=await api("commons.wikimedia.org",`action=query&list=geosearch&gscoord=${lat}|${lon}&gsradius=500&gsnamespace=6&gslimit=25`);
 if(!s||!s.query)return null;const f=s.query.geosearch.find(g=>/\.jpe?g$/i.test(g.title)&&!BAD.test(g.title));return f?{f:f.title.replace(/^File:/,""),via:"geo "+Math.round(f.dist)+"m"}:null}
async function info(f){const s=await api("commons.wikimedia.org",`action=query&titles=File:${encodeURIComponent(f)}&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=800`);
 const p=s&&s.query&&Object.values(s.query.pages)[0];const ii=p&&p.imageinfo&&p.imageinfo[0];if(!ii)return null;const m=ii.extmetadata||{};
 const strip=h=>(h||"").replace(/<[^>]+>/g,"").replace(/\s+/g," ").trim().slice(0,60);
 return {file:f,a:strip(m.Artist&&m.Artist.value)||"Wikimedia Commons",l:strip(m.LicenseShortName&&m.LicenseShortName.value),pg:ii.descriptionurl}}
(async()=>{for(const [id,fr,de,lat,lon,lang,town] of L){let r=null;
 try{for(const [lg,q] of [[lang,lang==="de"?de:fr],[lang==="de"?"fr":"de",lang==="de"?fr:de],[lang,(lang==="de"?de:fr)+" "+town]]){r=await wiki(lg,q,lat,lon);if(r)break}
  if(!r)r=await geo(lat,lon);if(r){const i=await info(r.f);if(i)PHR[id]={...i,via:r.via}}}catch(e){}
 PP.done++}})();
// Planche contact pour vérifier : afficher Special:FilePath/<file>?width=220 en grille avec l'id, garder seulement les bonnes.
// Recherche de secours : list=search&srnamespace=6&srsearch=<nom court> (2 candidats par activité, choisir à l'œil).
