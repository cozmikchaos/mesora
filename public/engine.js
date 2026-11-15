(function(root){
const cropInfo={corn:{name:'Corn',water:650,range:[500,800]},soybeans:{name:'Soybeans',water:575,range:[450,700]},wheat:{name:'Winter wheat',water:550,range:[450,650]}};
function distance(a,b){const rad=x=>x*Math.PI/180;const dlat=rad(b.lat-a.lat),dlon=rad(b.lon-a.lon);return 6371*2*Math.asin(Math.min(1,Math.sqrt(Math.sin(dlat/2)**2+Math.cos(rad(a.lat))*Math.cos(rad(b.lat))*Math.sin(dlon/2)**2)));}
function feature(c,w,year,crop){return [...w.rain,...w.temp,c.lat,c.lon,Math.log1p(c.water.irrigationMGD),Math.log1p(c.water.publicMGD),c.crops[crop].mean,year-2016];}
function predict(m,c,w,year,crop){const x=feature(c,w,year,crop);const value=m.intercept+x.reduce((sum,v,i)=>sum+(v-m.mean[i])/m.scale[i]*m.coefficients[i],0);return {value:Math.max(0,value),raw:value,outside:x.some((v,i)=>i<24&&(v<m.trainMin[i]||v>m.trainMax[i]))};}
function evaluate({county,weather,models,reported,year,warming,rainChange,allocation,growth,shared,radius,previous}){
 const w={rain:weather.rain.map(v=>v*(1+rainChange/100)),temp:weather.temp.map(v=>v+warming)};
 const near=reported.map(d=>({...d,km:distance(county,d)})).filter(d=>d.km<=radius).sort((a,b)=>a.km-b.km);
 const consumption=near.reduce((sum,d)=>sum+d.consumptionMG,0),increment=consumption*growth/100;
 const denominator=(county.water.publicMGD+county.water.irrigationMGD)*365;
 const fraction=denominator>0?Math.min(1,increment/denominator*shared/100):0;
 const available=allocation*(1-fraction);const pred={};
 for(const crop of Object.keys(county.crops)){const p=predict(models[crop],county,w,year,crop);const rainfall=(crop==='wheat'?w.rain.slice(0,9):w.rain.slice(6,12)).reduce((a,b)=>a+b,0);const need=Math.max(0,cropInfo[crop].water*(1+.04*warming)-.7*rainfall);pred[crop]={...p,need,shortfall:Math.max(0,need-available),relative:p.value/county.crops[crop].mean};}
 const crops=Object.keys(pred);const ranks=[];
 for(const a of crops)for(const b of crops)for(const c of crops){const seq=[a,b,c];if(a===b||b===c||(previous!=='unknown'&&a===previous))continue;const need=seq.reduce((s,k)=>s+pred[k].need,0);const deficit=seq.reduce((s,k)=>s+pred[k].shortfall,0);const yieldIndex=seq.reduce((s,k)=>s+pred[k].relative,0)/3;const score=yieldIndex-.5*deficit/(seq.reduce((s,k)=>s+cropInfo[k].water,0))+.03*(new Set(seq).size-1);ranks.push({seq,need,deficit,yieldIndex,score});}
 ranks.sort((a,b)=>b.score-a.score||a.seq.join().localeCompare(b.seq.join()));return {pred,ranks,near,consumption,increment,available,fraction,denominator,weather:w};
}
function waterFit({crop,weather,indices,warming=0,rainChange=0,budget=0}){
 const rainfall=indices.reduce((sum,i)=>sum+weather.rain[i]*(1+rainChange/100),0);
 const demand=crop.range.map(v=>v*(1+.04*warming));
 const irrigation=demand.map(v=>Math.max(0,v-.7*rainfall));
 const gap=irrigation.map(v=>Math.max(0,v-budget));
 const fit=irrigation[1]<=budget?'within':irrigation[0]<=budget?'borderline':'short';
 return {rainfall,effectiveRain:.7*rainfall,demand,irrigation,gap,fit,budget};
}
const api={cropInfo,distance,feature,predict,evaluate,waterFit};root.MesoraEngine=api;if(typeof module!=='undefined')module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
