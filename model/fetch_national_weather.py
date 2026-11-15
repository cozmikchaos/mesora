import json,pathlib,urllib.request,urllib.parse,concurrent.futures,time,numpy as np
root=pathlib.Path('work/data/national');geo=json.load(open(root/'counties.geojson'));props={f['properties']['GEOID']:f['properties'] for f in geo['features']};rows=[];sample=set()
for path in sorted((root/'rollups').glob('*.json')):
 d=json.load(open(path));state=d['state']['fips'];crop=d['commodity']['slug'];eligible=[]
 for cc,v in d['counties'].items():
  g=state+cc
  if g not in props:continue
  series=next((s for s in v['series'] if (s.get('canonical') if crop!='wheat' else s.get('class')=='WINTER' and s.get('prodn_practice')=='ALL PRODUCTION PRACTICES') and s['statistic']=='YIELD' and s['unit']=='BU / ACRE'),None)
  if not series:continue
  vals={int(y):float(x) for y,x in series['values'].items() if 2016<=int(y)<=2025 and isinstance(x,(float,int)) and x>0}
  rows += [{'geoid':g,'county':v['name'],'crop':crop,'year':y,'yield':x} for y,x in vals.items()]
  if sum(y<=2023 for y in vals)>=5 and any(y>=2024 for y in vals):eligible.append(g)
 eligible.sort(key=lambda g:(float(props[g]['CENTLAT']),float(props[g]['CENTLON'])))
 if eligible:
  sample.update(eligible[i] for i in np.linspace(0,len(eligible)-1,min(6,len(eligible)),dtype=int))
sample.update(g for g in ['06019','19155','19169','04013','51059','31153','41065'] if g in props)
json.dump(rows,open(root/'yields.json','w'));json.dump(sorted(sample),open(root/'sample.json','w'));print('records',len(rows),'sample',len(sample),flush=True)
(root/'weather').mkdir(exist_ok=True)
def fetch(g):
 p=props[g];path=root/'weather'/(g+'.json')
 if path.exists():return
 args={'parameters':'T2M,PRECTOTCORR','community':'AG','longitude':p['CENTLON'],'latitude':p['CENTLAT'],'start':'2015','end':'2025','format':'JSON'};url='https://power.larc.nasa.gov/api/temporal/monthly/point?'+urllib.parse.urlencode(args)
 for i in range(3):
  try:
   raw=json.load(urllib.request.urlopen(url,timeout=60));assert 'properties' in raw;path.write_text(json.dumps(raw));return
  except Exception as e:
   if i==2:print('FAILED',g,str(e),flush=True)
   time.sleep(2)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for i,_ in enumerate(pool.map(fetch,sorted(sample))):
  if i%40==0:print('weather',i,'/',len(sample),flush=True)
print('DONE',flush=True)
