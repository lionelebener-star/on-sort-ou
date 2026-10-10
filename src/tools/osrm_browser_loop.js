// Boucle exécutée dans le navigateur (origine router.project-osrm.org). 10 départs x 90 destinations par requête, 1 req/s.
window.ALPH=[...Array(92)].map((_,i)=>String.fromCharCode(35+i)).filter(c=>c!=="\\").join("");
window.RES={d:OS.map(()=>Array(AC.length).fill(null)),k:OS.map(()=>Array(AC.length).fill(null))};window.P={done:0,total:0,err:[]};
(async()=>{const oc=10,dc=90,jobs=[];for(let i=0;i<OS.length;i+=oc)for(let j=0;j<AC.length;j+=dc)jobs.push([i,j]);P.total=jobs.length;
 for(const [i,j] of jobs){const so=OS.slice(i,i+oc),de=AC.slice(j,j+dc);const pts=[...so,...de].map(p=>p.join(",")).join(";");
  const url=`https://router.project-osrm.org/table/v1/driving/${pts}?sources=${so.map((_,k)=>k).join(";")}&destinations=${de.map((_,k)=>k+so.length).join(";")}&annotations=duration,distance`;
  let ok=false;for(let tr=0;tr<4&&!ok;tr++){try{const r=await fetch(url);const js=await r.json();if(js.code!=="Ok")throw js.code;
   js.durations.forEach((row,a)=>row.forEach((v,b)=>{RES.d[i+a][j+b]=v;RES.k[i+a][j+b]=js.distances[a][b]}));ok=true}catch(e){await new Promise(r=>setTimeout(r,2000*(tr+1)));if(tr===3)P.err.push([i,j,String(e)])}}
  P.done++;await new Promise(r=>setTimeout(r,1100))}})();
// Encodage : 1 caractère par paire, pas de 5 min (durée) et 5 km (distance), "!" = pas de route. Ligne = "<durées>|<distances>" (couper par position, pas par "|").
window.ENC=(a,b)=>RES.d.slice(a,b).map((row,i)=>row.map(v=>v==null?"!":ALPH[Math.min(90,Math.round(v/300))]).join("")+"|"+RES.k[a+i].map(v=>v==null?"!":ALPH[Math.min(90,Math.round(v/5000))]).join("")).join("\n");
"started "+OS.length+"x"+AC.length
