// Télécharge et recadre les photos retenues en 480x270 JPEG (q=0.62) -> window.IMS = {id: dataURL}.
// Définir avant : window.PF=[[id, "Nom_du_fichier_Commons.jpg"], ...]  (page commons.wikimedia.org)
window.IMS={};window.IP={done:0,err:[]};
(async()=>{for(const [id,f] of PF){try{const b=await fetch(`https://commons.wikimedia.org/wiki/Special:FilePath/${f}?width=640`).then(r=>{if(!r.ok)throw r.status;return r.blob()});
 const bm=await createImageBitmap(b);const W=480,H=270,c=document.createElement("canvas");c.width=W;c.height=H;const g=c.getContext("2d");const s=Math.max(W/bm.width,H/bm.height);
 g.drawImage(bm,(W-bm.width*s)/2,(H-bm.height*s)/2,bm.width*s,bm.height*s);IMS[id]=c.toDataURL("image/jpeg",0.62)}catch(e){IP.err.push([id,String(e)])}IP.done++;await new Promise(r=>setTimeout(r,120))}})();
// Export : JSON.stringify(IMS) -> enregistrer dans src/tools/out/new_photos.json, puis python3 src/tools/photos_merge.py
