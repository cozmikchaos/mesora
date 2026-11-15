"""National ridge-regression prototype. Real USDA labels; NASA climate covariates.
Run from workspace after national_weather.py. Model frozen at 2023, evaluated 2024–25.
County training-mean yield is a baseline feature; unknown crops are never inferred.
"""
import json,csv,calendar,pathlib,numpy as np
r=pathlib.Path('work/data/national');out=pathlib.Path('mesora-site/dist/data');out.mkdir(exist_ok=True)
geo=json.load(open(r/'counties.geojson'));ys=json.load(open(r/'yields.json'));idx=json.load(open(r/'index.json'));states={k:v['alpha'] for k,v in idx['states'].items()};states.update({'02':'AK','09':'CT','11':'DC','15':'HI','23':'ME','25':'MA','33':'NH','44':'RI','50':'VT'})
with open('work/data/water.csv',encoding='utf-8-sig') as f:
 next(f);water={v['FIPS']:v for v in csv.DictReader(f)}
def number(w,k):
 try:return float(w[k])
 except:return None
counties={};weather={}
for f in geo['features']:
 p=f['properties'];g=p['GEOID'];w=water.get(g,{})
 counties[g]={'name':p['NAME'],'state':states.get(p['STATE'],p['STATE']),'lat':float(p['CENTLAT']),'lon':float(p['CENTLON']),'water':{'year':2015,'irrigationMGD':number(w,'IR-WFrTo'),'publicMGD':number(w,'PS-Wtotl'),'totalMGD':number(w,'TO-Wtotl')},'crops':{}}
 for crop in ['corn','soybeans','wheat']:
  cr=[x for x in ys if x['geoid']==g and x['crop']==crop and x['year']<=2023]
  if len(cr)>=4:counties[g]['crops'][crop]={'mean':float(np.mean([x['yield'] for x in cr])),'n':len(cr)}
 path=r/'weather'/(g+'.json')
 if path.exists():
  raw=json.load(open(path))['properties']['parameter'];weather[g]={}
  for y in range(2016,2026):
   ym=[(y-1,m) for m in [10,11,12]]+[(y,m) for m in range(1,10)]
   rain=[raw['PRECTOTCORR'][f'{yr}{m:02}']*calendar.monthrange(yr,m)[1] for yr,m in ym];temp=[raw['T2M'][f'{yr}{m:02}'] for yr,m in ym]
   if any(t<=-900 for t in temp) or any(p<0 for p in rain):continue
   weather[g][str(y)]={'rain':list(np.round(rain,3)),'temp':temp}
# Feature set uses broad crop-year weather Oct–Sep; not crop-specific phenology.
def means(rows):
 return {g:np.mean([x['yield'] for x in rows if x['geoid']==g]) for g in set(x['geoid'] for x in rows)}
def X(rows,baseline):
 arr=[]
 for x in rows:
  c=counties[x['geoid']];w=weather[x['geoid']][str(x['year'])]
  arr.append(w['rain']+w['temp']+[c['lat'],c['lon'],np.log1p(c['water']['irrigationMGD']),np.log1p(c['water']['publicMGD']),baseline[x['geoid']],x['year']-2016])
 return np.array(arr)
def fit(rows,alpha):
 b=means(rows);xx=X(rows,b);mu=xx.mean(0);sd=xx.std(0);sd[sd==0]=1;z=(xx-mu)/sd;y=np.array([x['yield'] for x in rows]);ym=y.mean();coef=np.linalg.solve(z.T@z+alpha*np.eye(z.shape[1]),z.T@(y-ym));return (b,mu,sd,ym,coef)
def predict(m,rows):
 b,mu,sd,ym,coef=m;return ((X(rows,b)-mu)/sd)@coef+ym
models={};holdout=[];training=[]
for crop in ['corn','soybeans','wheat']:
 rows=[x for x in ys if x['crop']==crop and x['geoid'] in weather and str(x['year']) in weather[x['geoid']] and crop in counties[x['geoid']]['crops'] and counties[x['geoid']]['water']['irrigationMGD'] is not None and counties[x['geoid']]['water']['publicMGD'] is not None]
 early=[x for x in rows if x['year']<=2021];em=means(early);valid=[x for x in rows if 2022<=x['year']<=2023 and x['geoid'] in em];train=[x for x in rows if x['year']<=2023];tm=means(train);test=[x for x in rows if x['year']>=2024 and x['geoid'] in tm]
 alpha=min([1,10,50,100,500,1000],key=lambda a:np.mean(abs(predict(fit(early,a),valid)-[x['yield'] for x in valid])))
 model=fit(train,alpha);pred=predict(model,test);truth=np.array([x['yield'] for x in test]);base=np.array([tm[x['geoid']] for x in test]);b,mu,sd,ym,coef=model
 models[crop]={'mean':mu.tolist(),'scale':sd.tolist(),'intercept':float(ym),'coefficients':coef.tolist(),'alpha':alpha,'trainN':len(train),'testN':len(test),'mae':float(np.mean(abs(pred-truth))),'baselineMAE':float(np.mean(abs(base-truth))),'rmse':float(np.sqrt(np.mean((pred-truth)**2))),'r2':float(1-sum((pred-truth)**2)/sum((truth-truth.mean())**2)),'trainMin':X(train,b).min(0).tolist(),'trainMax':X(train,b).max(0).tolist(),'states':len(set(x['geoid'][:2] for x in train)),'counties':len(b)}
 for x,p in zip(test,pred):holdout.append(dict(x,predicted=float(p)))
 training+=train
 print(crop,{k:models[crop][k] for k in ['trainN','testN','mae','baselineMAE','states','counties']})
meta={'algorithm':'Standardized ridge regression','trainingYears':'2016–2023','validationYears':'2022–2023, fitted on 2016–2021','testYears':'2024–2025','features':['Oct(previous year)–Sep precipitation: 12 monthly totals (mm)','Oct(previous year)–Sep temperature: 12 monthly means (°C)','Latitude','Longitude','log1p(2015 irrigation withdrawal, MGD)','log1p(2015 public-supply withdrawal, MGD)','County/crop mean yield from training years only','Year minus 2016'],'catalogRows':len(ys),'trainRows':len(training),'mappedCounties':len(counties),'weatherCounties':len(weather),'models':models,'sourceSnapshot':json.load(open(r/'commit.json'))['sha'],'usdaSource':idx['source'],'limitations':['County-level, not field-level validation.','Full crop-year weather is a conditional input, not a weather forecast.','Water covariates are historical 2015 withdrawals, not current supply.','Data-center demand enters a separate user-controlled water-sharing scenario, not a learned causal yield effect.','Training labels are individual crop yields, not observed rotation outcomes.','Validation spans two years; geographic transfer to unsampled counties is unvalidated.','All-production-practice yields mix irrigated and rainfed farming.']}
for name,obj in [('model.json',meta),('observations.json',{'counties':counties,'weather':weather}),('counties.geojson',geo),('holdout-predictions.json',holdout)]:json.dump(obj,open(out/name,'w'),allow_nan=False,separators=(',',':'))
with open(out/'training-records.csv','w') as f:
 wr=csv.DictWriter(f,fieldnames=['geoid','county','crop','year','yield']);wr.writeheader();wr.writerows(training)
# Compact frozen weather inputs and complete source catalog support reproducibility.
json.dump(ys,open(out/'yield-catalog.json','w'),separators=(',',':'))
