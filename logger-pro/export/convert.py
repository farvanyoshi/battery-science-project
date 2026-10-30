from pathlib import Path
import gzip,re,json,hashlib,csv,ast
import os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/logger-mpl-cache")
import numpy as np
from render_graphs import render
try:
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
except ImportError:
 plt=None
import html
from urllib.parse import quote
OUT=Path('converted');OUT.mkdir(exist_ok=True)
manifest=[];links=[]
def txt(e,k,d=''):return e.findtext(k,d).strip()
def writejson(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False))
for p in sorted(Path('.').glob('*.cmbl')):
 import xml.etree.ElementTree as ET
 raw=p.read_bytes();b=gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw
 s=b.decode('utf-8-sig');fixed=re.sub(r'&(?!#\d+;|#x[0-9a-fA-F]+;|amp;|lt;|gt;|quot;|apos;)', '&amp;',s);r=ET.fromstring(fixed)
 folder=OUT/p.stem;folder.mkdir(exist_ok=True);(folder/'source.xml').write_text(fixed)
 warnings=[];meta={'source':p.name,'sha256':hashlib.sha256(raw).hexdigest(),'gzip':raw[:2]==b'\x1f\x8b','xml_repaired':s!=fixed,'datasets':[],'graphs':[],'warnings':warnings};cols={};values={};models={txt(e,'ID'):e for e in r.findall('.//FunctionModel')}
 for ds in r.findall('.//DataSet'):
  dm={'id':txt(ds,'ID'),'name':txt(ds,'DataSetName'),'columns':[]};local={}
  for c in ds.findall('DataColumn'):
   cid=txt(c,'ID');name=txt(c,'DataObjectName');lines=(c.findtext('ColumnCells') or '').strip('\n').splitlines();v=[];special={}
   for i,line in enumerate(lines):
    try:v.append(float(line))
    except ValueError:v.append(float('nan'));special[str(i)]=line
   cm={'id':cid,'name':name,'units':txt(c,'ColumnUnits'),'dataset':dm['name'],'error_enabled':txt(c,'ColumnUseErrorCalculations')=='1','error_constant':txt(c,'ColumnErrorConstant'),'error_value':txt(c,'ColumnErrorValue','0'),'error_column':txt(c,'ColumnErrorColumnID','0'),'stored':c.find('ColumnCells') is not None,'special_cells':special,'xml':ET.tostring(c,encoding='unicode') if not lines else None};dm['columns'].append(cm);cols[cid]=cm;values[cid]=np.array(v);local[name]=cid
   if special:warnings.append(f'{cid}: special cell tokens retained as missing values; original tokens in metadata')
  for calc in r.findall('.//CalcColumnSource2'):
   cid=txt(calc,'CalcOutColumnID');formula=txt(calc,'CalcEquation')
   if cid not in [c['id'] for c in dm['columns']]:continue
   cols[cid]['formula']=formula
   if cols[cid]['stored']:continue
   try:
    env={};expr=formula
    for j,name in enumerate(re.findall(r'"([^"]+)"',formula)):
     key=f'v{j}';env[key]=values[local[name]];expr=expr.replace('"'+name+'"',key)
    tree=ast.parse(expr,mode='eval')
    if any(not isinstance(n,(ast.Expression,ast.BinOp,ast.UnaryOp,ast.Name,ast.Load,ast.Constant,ast.Mult,ast.Div,ast.Add,ast.Sub,ast.USub,ast.Pow)) for n in ast.walk(tree)):raise ValueError('unsupported expression')
    with np.errstate(all='ignore'):values[cid]=np.asarray(eval(compile(tree,'formula','eval'),{'__builtins__':{}},env))
   except Exception as ex:warnings.append(f'calculation {cid}: {ex}')
  n=max([len(values[c['id']]) for c in dm['columns']]+[0]);filename=f'dataset_{dm["id"]}.csv';dm['csv']=filename;dm['rows']=n
  with (folder/filename).open('w',newline='') as f:
   w=csv.writer(f);w.writerow([f'{c["name"]} [{c["units"]}] (id {c["id"]})' for c in dm['columns']])
   for i in range(n):w.writerow([repr(float(values[c['id']][i])) if i<len(values[c['id']]) and np.isfinite(values[c['id']][i]) else '' for c in dm['columns']])
  meta['datasets'].append(dm)
 for g in r.findall('.//PageGraphCartesian'):
  gid=txt(g,'ID');pairs=txt(g,'GraphPlotTraceIDPairs').split()[1:];gm={'id':gid,'xml':ET.tostring(g,encoding='unicode'),'files':[]};meta['graphs'].append(gm)
  if plt is None:
   warnings.append(f'graph {gid}: rendering unavailable; install matplotlib and rerun')
   continue
  gm.update(render(g,r,folder,cols,values,models,warnings))
  links.append(f'<h3>{html.escape(p.name)} — graph {gid}</h3><a href="{quote(p.stem)}/graph_{gid}_paper.svg"><img width="600" src="{quote(p.stem)}/graph_{gid}_paper.png"></a>')
 helpers=[ET.tostring(e,encoding='unicode') for e in r.iter() if e.tag.startswith('PageHelper')];meta['analysis_helpers_xml']=helpers

 writejson(folder/'metadata.json',meta);manifest.append(meta)
 print(p.name,flush=True)
writejson(OUT/'manifest.json',manifest)
(OUT/'index.html').write_text('<meta charset="utf-8"><title>Logger Pro archive</title><h1>Experimental figures</h1>'+''.join(links))

from validate_archive import validate
validate()
