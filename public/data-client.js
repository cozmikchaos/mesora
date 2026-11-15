(function(root){
 const cache=new Map();
 const bridge='https://mesora-field-shift.jishahareesh.chatgpt.site/api/';
 function errorText(status,type){return type.includes('html')?'The data route returned a web page. Trying another route.':status===429?'The source is busy. Please retry shortly.':'The source request could not be completed.';}
 async function get(path,options={}){
  const csv=path.startsWith('water-sites?')||path.startsWith('water-results?');
  const bases=options.bases||['/api/','/.netlify/functions/mesora/',...(typeof location==='undefined'||location.origin!=='https://mesora-field-shift.jishahareesh.chatgpt.site'?[bridge]:[])];
  const key=bases.join('|')+path;if(cache.has(key)&&!options.refresh)return cache.get(key);
  let last;
  for(const base of bases){try{const signal=options.signal?AbortSignal.any([options.signal,AbortSignal.timeout(65000)]):AbortSignal.timeout(65000);const r=await (options.fetch||fetch)(base+path,{signal,headers:{Accept:csv?'text/csv':'application/json'},credentials:'omit'});const type=(r.headers.get('content-type')||'').toLowerCase(),text=await r.text();
   if(!r.ok){let message=errorText(r.status,type);try{const e=JSON.parse(text);if(e.error)message=e.error;}catch{}throw Error(message);}
   if(type.includes('html')||/^\s*(?:<!doctype|<html|The page)/i.test(text))throw Error('Data service is not connected on this address.');
   let value;if(csv){if(!text.startsWith('OrganizationIdentifier,')&&!text.startsWith('"OrganizationIdentifier"'))throw Error('The monitoring source returned an unexpected format.');value=text;}else{try{value=JSON.parse(text);}catch{throw Error('The source returned an unreadable response.');}if(value?.error)throw Error(value.error);}
   cache.set(key,value);return value;
  }catch(e){if(options.signal?.aborted)throw e;last=e;}}
  throw Error(last?.message||'Data service unavailable.');
 }
 const api={get,errorText,clear:()=>cache.clear()};root.MesoraData=api;if(typeof module!=='undefined')module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
