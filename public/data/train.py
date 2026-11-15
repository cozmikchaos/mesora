"""Reproducible ridge-regression yield model. No synthetic training labels.
Run from the workspace with the downloaded public files in work/data.
Train 2016-2021 / tune 2022-2023 / refit 2016-2023 / test 2024-2025.
"""
import json,csv,calendar,pathlib,numpy as np
root=pathlib.Path('work/data');out=pathlib.Path('mesora-site/dist/data');out.mkdir(exist_ok=True)
geo=json.load(open(root/'counties.geojson'));ys=json.load(open(root/'yields.json'))
with open(root/'water.csv',encoding='utf-8-sig') as f:
 next(f);water={r['FIPS']:r for r in csv.DictReader(f) if r['STATE']=='IA'}
def val(r,k):
 try:return float(r[k])
 except:return None
counties={};weather={};features={}
for f in geo['features']:
 p=f['properties'];g=p['GEOID'];w=water[g];lat=float(p['CENTLAT']);lon=float(p['CENTLON'])
 counties[g]={'name':p['NAME'].replace(' County',''),'lat':lat,'lon':lon,'water':{'year':2015,'irrigationMGD':val(w,'IR-WFrTo'),'publicMGD':val(w,'PS-Wtotl'),'totalMGD':val(w,'TO-Wtotl'),'irrigatedThousandAcres':val(w,'IR-IrTot')}}
 raw=json.load(open(root/'weather'/(g+'.json')))['properties']['parameter'];weather[g]={}
 for y in range(2016,2026):
  rain=[raw['PRECTOTCORR'][f'{y}{m:02}']*calendar.monthrange(y,m)[1] for m in range(4,10)]
  temp=[raw['T2M'][f'{y}{m:02}'] for m in range(4,10)]
  assert all(v>-100 for v in temp+rain)
  weather[g][str(y)]={'rain':list(np.round(rain,3)),'temp':temp}
  features[g,y]=rain+temp+[sum(rain)**2/1e6,np.mean(temp)**2,lat,lon,np.log1p(counties[g]['water']['irrigationMGD']),np.log1p(counties[g]['water']['publicMGD']),y-2016]
models={};predictions=[]
def fit(rows,alpha):
 X=np.array([features[r['geoid'],r['year']] for r in rows]);Y=np.array([r['yield'] for r in rows]);mu=X.mean(0);sd=X.std(0);sd[sd==0]=1;Z=(X-mu)/sd;ym=Y.mean();coef=np.linalg.solve(Z.T@Z+alpha*np.eye(X.shape[1]),Z.T@(Y-ym));return mu,sd,ym,coef
def predict(model,rows):
 mu,sd,ym,coef=model;return ((np.array([features[r['geoid'],r['year']] for r in rows])-mu)/sd)@coef+ym
for crop in ['corn','soybean']:
 rows=[r for r in ys if r['crop']==crop];early=[r for r in rows if r['year']<=2021];valid=[r for r in rows if 2022<=r['year']<=2023];train=[r for r in rows if r['year']<=2023];test=[r for r in rows if r['year']>=2024]
 alpha=min([1,10,50,100,500,1000],key=lambda a:np.mean(abs(predict(fit(early,a),valid)-[r['yield'] for r in valid])))
 model=fit(train,alpha);pr=predict(model,test);truth=np.array([r['yield'] for r in test]);means={g:np.mean([r['yield'] for r in train if r['geoid']==g] or [r['yield'] for r in train]) for g in counties};base=np.array([means[r['geoid']] for r in test]);mae=np.mean(abs(pr-truth));baseline=np.mean(abs(base-truth));mu,sd,ym,coef=model
 models[crop]={'mean':mu.tolist(),'scale':sd.tolist(),'intercept':float(ym),'coefficients':coef.tolist(),'alpha':alpha,'trainN':len(train),'testN':len(test),'validationN':len(valid),'mae':float(mae),'baselineMAE':float(baseline),'rmse':float(np.sqrt(np.mean((pr-truth)**2))),'r2':float(1-sum((pr-truth)**2)/sum((truth-truth.mean())**2)),'trainMin':np.min([features[r['geoid'],r['year']] for r in train],axis=0).tolist(),'trainMax':np.max([features[r['geoid'],r['year']] for r in train],axis=0).tolist(),'countyMeans':means}
 for r,p in zip(test,pr):predictions.append(dict(r,predicted=float(p)))
 print(crop,models[crop]['trainN'],models[crop]['testN'],'MAE',round(mae,2),'baseline',round(baseline,2),'alpha',alpha)
meta={'algorithm':'Standardized ridge regression','trainingYears':'2016–2023','validationYears':'2022–2023 (trained on 2016–2021)','testYears':'2024–2025','features':['Apr–Sep precipitation (6 monthly totals, mm)','Apr–Sep temperature (6 monthly means, °C)','Squared seasonal precipitation / 1e6','Squared mean seasonal temperature','County centroid latitude','County centroid longitude','log1p(2015 irrigation withdrawal MGD)','log1p(2015 public-supply withdrawal MGD)','year minus 2016'],'rows':len(ys),'counties':len(counties),'models':models}
json.dump(meta,open(out/'model.json','w'),allow_nan=False)
json.dump({'counties':counties,'weather':weather},open(out/'observations.json','w'),allow_nan=False)
json.dump(geo,open(out/'counties.geojson','w'))
json.dump(predictions,open(out/'holdout-predictions.json','w'))
with open(out/'training-records.csv','w') as f:
 writer=csv.DictWriter(f,fieldnames=['county','geoid','year','crop','yield']);writer.writeheader();writer.writerows(ys)
