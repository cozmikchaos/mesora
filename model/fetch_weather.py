import json,pathlib,urllib.request,urllib.parse,concurrent.futures,time
root=pathlib.Path('work/data'); (root/'weather').mkdir(exist_ok=True)
features=json.load(open(root/'counties.geojson'))['features']
def fetch(f):
 p=f['properties'];path=root/'weather'/ (p['GEOID']+'.json')
 if path.exists():return p['GEOID']+' cached'
 args={'parameters':'T2M,PRECTOTCORR','community':'AG','longitude':p['CENTLON'],'latitude':p['CENTLAT'],'start':'2016','end':'2025','format':'JSON'}
 url='https://power.larc.nasa.gov/api/temporal/monthly/point?'+urllib.parse.urlencode(args)
 for attempt in range(3):
  try:
   data=json.load(urllib.request.urlopen(url,timeout=90));assert 'properties' in data
   path.write_text(json.dumps(data));return p['GEOID']+' OK'
  except Exception as e:
   if attempt==2:return p['GEOID']+' ERROR '+str(e)
   time.sleep(3)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for result in pool.map(fetch,features):print(result,flush=True)
