"""Train reproducible NASA POWER / USDA NASS county yield models.
Fit 2016–2021, tune 2022–2023, refit 2016–2023, final untouched test 2024–2025.
No rotation-outcome or data-center causal labels are available.
Requires numpy, scipy and scikit-learn. Run from project root.
"""
import sys,pathlib,json,collections,hashlib
sys.path.insert(0,str(pathlib.Path('work/ml-python').resolve()))
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error,mean_squared_error
root=pathlib.Path('public/data') if pathlib.Path('public/data').exists() else pathlib.Path('mesora-site/dist/data');db=json.loads((root/'observations.json').read_text());rows=json.loads((root/'yield-catalog.json').read_text())
# Include the demonstration county using its frozen real NASA daily record.
import calendar
raw=json.loads((root/'v2/power-daily-union.json').read_text())['properties']['parameter']
db['weather']['37179']={}
for yr in range(2016,2026):
 months=[(yr-1,m)for m in [10,11,12]]+[(yr,m)for m in range(1,10)]
 rain=[];temp=[]
 for y,m in months:
  keys=[f'{y}{m:02}{d:02}'for d in range(1,calendar.monthrange(y,m)[1]+1)]
  rain.append(float(sum(raw['PRECTOTCORR'][k]for k in keys)));temp.append(float(np.mean([raw['T2M'][k]for k in keys])))
 db['weather']['37179'][str(yr)]={'rain':rain,'temp':temp}
names=['rain_'+str(i)for i in range(12)]+['temp_'+str(i)for i in range(12)]+['latitude','longitude','log_irrigation_2015','log_public_supply_2015','training_county_mean','year_minus_2016']
def baseline(rr):
 groups=collections.defaultdict(list)
 for r in rr:groups[r['geoid']].append(r['yield'])
 return {k:float(np.mean(v))for k,v in groups.items()}
def matrix(rr,b):
 data=[]
 for r in rr:
  c=db['counties'][r['geoid']];w=db['weather'][r['geoid']][str(r['year'])]
  data.append(w['rain']+w['temp']+[c['lat'],c['lon'],np.log1p(c['water']['irrigationMGD']),np.log1p(c['water']['publicMGD']),b[r['geoid']],r['year']-2016])
 return np.array(data),np.array([r['yield']for r in rr])
def tree(t):
 return {'feature':t.feature.tolist(),'threshold':t.threshold.tolist(),'left':t.children_left.tolist(),'right':t.children_right.tolist(),'value':t.value[:,0,0].tolist()}
output={'algorithm':'Gradient-boosted regression trees','version':'nasa-usda-gbr-1','features':names,'trainYears':[2016,2023],'tuningYears':[2022,2023],'testYears':[2024,2025],'weatherSource':'NASA POWER monthly 2015–2025','yieldSource':'USDA NASS county yields; frozen source-linked catalog','models':{},'limitations':['County yield models, not field-validated rotation outcomes.','Climate stress is a conditional sensitivity test, not a weather forecast.','Water supply is screened separately; no learned data-center causal effect.','Cotton and sorghum have no training labels in this release and are excluded from ML ranking.']}
checks=[]
for crop in ['corn','soybeans','wheat']:
 rr=[r for r in rows if r['crop']==crop and r['geoid']in db['weather'] and str(r['year'])in db['weather'][r['geoid']] and crop in db['counties'][r['geoid']]['crops'] and all(db['counties'][r['geoid']]['water'][k]is not None for k in ['irrigationMGD','publicMGD'])]
 early=[r for r in rr if r['year']<=2021];eb=baseline(early);valid=[r for r in rr if 2022<=r['year']<=2023 and r['geoid']in eb];X,y=matrix(early,eb);V,vy=matrix(valid,eb)
 candidates=[]
 for depth in [1,2,3]:
  m=GradientBoostingRegressor(n_estimators=120,max_depth=depth,min_samples_leaf=20,learning_rate=.04,loss='huber',random_state=2026);m.fit(X,y);candidates.append((mean_absolute_error(vy,m.predict(V)),depth))
 best,depth=min(candidates);train=[r for r in rr if r['year']<=2023];b=baseline(train);test=[r for r in rr if r['year']>=2024 and r['geoid']in b];X,y=matrix(train,b);T,truth=matrix(test,b)
 m=GradientBoostingRegressor(n_estimators=120,max_depth=depth,min_samples_leaf=20,learning_rate=.04,loss='huber',random_state=2026);m.fit(X,y);pred=m.predict(T);err=abs(pred-truth);base=np.array([b[r['geoid']]for r in test]);model={'init':float(m.init_.constant_[0,0]),'rate':float(m.learning_rate),'trees':[tree(t[0].tree_)for t in m.estimators_],'baselines':b,'trainN':len(train),'testN':len(test),'countyN':len(b),'depth':depth,'validationMAE':float(best),'testMAE':float(mean_absolute_error(truth,pred)),'baselineMAE':float(mean_absolute_error(truth,base)),'testRMSE':float(np.sqrt(mean_squared_error(truth,pred))),'residualP90':float(np.quantile(err,.9)),'min':X.min(0).tolist(),'max':X.max(0).tolist(),'featureImportance':m.feature_importances_.tolist(),'units':'bu/acre'}
 output['models'][crop]=model
 for i in [0,len(T)//2,len(T)-1]:checks.append({'crop':crop,'features':T[i].tolist(),'prediction':float(pred[i])})
 print(crop,{k:model[k]for k in ['trainN','testN','countyN','testMAE','baselineMAE','depth']},flush=True)
(root/'ml-model.json').write_text(json.dumps(output,separators=(',',':'),allow_nan=False));(root/'ml-verification.json').write_text(json.dumps(checks,separators=(',',':')))
print('wrote', (root/'ml-model.json').stat().st_size,'bytes',flush=True)
