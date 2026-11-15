import json,pathlib,urllib.request,concurrent.futures,time
r=pathlib.Path('work/data/national');idx=json.load(open(r/'index.json'));sha=json.load(open(r/'commit.json'))['sha'];print('SNAPSHOT',sha,idx['source'],flush=True)
(r/'rollups').mkdir(exist_ok=True)
jobs=[(state,crop) for state,v in idx['states'].items() for crop in v['crops']]
def run(job):
 s,c=job;p=r/'rollups'/f'{s}-{c}.json'
 if p.exists():return
 u=f'https://raw.githubusercontent.com/ProductOfAmerica/usda-county-yields/{sha}/data/states/{s}/crops/{c}.json'
 for i in range(3):
  try:p.write_bytes(urllib.request.urlopen(u,timeout=60).read());return
  except Exception as e:
   if i==2:print('FAIL',s,c,e,flush=True)
   time.sleep(2)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:list(ex.map(run,jobs))
print('downloaded',len(list((r/'rollups').glob('*.json'))),flush=True)
