import pdfplumber,json,re,pathlib
root=pathlib.Path('work/data')
geo=json.load(open(root/'counties.geojson')); print(len(geo['features']),geo['features'][0]['properties'])
rows=[]
with pdfplumber.open(root/'yields.pdf') as pdf:
 for page in pdf.pages:
  words=page.extract_words(x_tolerance=2,y_tolerance=2)
  lines={}
  for w in words:lines.setdefault(round(w['top']),[]).append(w)
  crop=None; centers=[]
  for top,ws in sorted(lines.items()):
   ws.sort(key=lambda w:w['x0']); text=' '.join(w['text'] for w in ws)
   if 'Yields' in text and '2016' in text:
    crop='corn' if 'Corn' in text else 'soybean';centers=[(int(w['text']),(w['x0']+w['x1'])/2) for w in ws if re.fullmatch('20(1[6-9]|2[0-5])',w['text'])];continue
   if not crop or not centers:continue
   nums=[w for w in ws if re.fullmatch(r'\d+\.\d',w['text'])]
   if not nums:continue
   name=' '.join(w['text'] for w in ws if w['x1']<centers[0][1]-12)
   match=next((f for f in geo['features'] if f['properties']['NAME'].replace(' County','')==name),None)
   if not match:continue
   for w in nums:
    x=(w['x0']+w['x1'])/2; yr,c=min(centers,key=lambda v:abs(v[1]-x))
    if abs(c-x)<12:rows.append({'county':name,'geoid':match['properties']['GEOID'],'year':yr,'crop':crop,'yield':float(w['text'])})
json.dump(rows,open(root/'yields.json','w'));print('yield rows',len(rows));print([r for r in rows if r['county']=='Pottawattamie'])
