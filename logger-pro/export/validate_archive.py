"""Independent source-to-CSV verification, lossless cell exports, and archive index."""
from pathlib import Path
import csv,json,gzip,re,hashlib,html
from urllib.parse import quote
import xml.etree.ElementTree as ET
import numpy as np

def validate():
 root=Path('converted');manifest=json.loads((root/'manifest.json').read_text());report={'sources':len(manifest),'datasets':0,'columns':0,'graphs':0,'figures':0,'numeric_cells_checked':0,'special_cells_preserved':0,'calculated_columns_checked':0,'errors':[],'warnings':[]};sections=[]
 for m in manifest:
  p=Path(m['source']);folder=root/p.stem;raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==m['sha256']
  source=ET.parse(folder/'source.xml').getroot();datasets={e.findtext('ID').strip():e for e in source.findall('.//DataSet')};report['warnings'] += [p.name+': '+w for w in m['warnings']]
  section=f'<section><h2>{html.escape(p.name)}</h2><p><a href="{quote(p.stem)}/metadata.json">Metadata and warnings</a> · <a href="{quote(p.stem)}/source.xml">XML</a></p><ul>'
  for ds in m['datasets']:
   report['datasets']+=1;report['columns']+=len(ds['columns']);rds=datasets[ds['id']];rc={c.findtext('ID').strip():c for c in rds.findall('DataColumn')};rows=list(csv.reader((folder/ds['csv']).open(newline='')));assert len(rows)-1==ds['rows'];arrays={};rawcols=[]
   for j,c in enumerate(ds['columns']):
    lines=(rc[c['id']].findtext('ColumnCells') or '').strip('\n').splitlines();rawcols.append(lines);a=np.array([float(row[j]) if row[j] else np.nan for row in rows[1:]]);arrays[c['name']]=a
    for i,line in enumerate(lines):
     try:v=float(line)
     except ValueError:
      assert c['special_cells'][str(i)]==line;assert np.isnan(a[i]);report['special_cells_preserved']+=1;continue
     assert (a[i]==v) or (np.isnan(a[i]) and not np.isfinite(v)),(p.name,c['id'],i)
     report['numeric_cells_checked']+=1
    if not c['stored'] and 'formula' in c:report['calculated_columns_checked']+=1
   from render_graphs import expression
   for j,c in enumerate(ds['columns']):
    if not c['stored'] and 'formula' in c:
     env={};expr=c['formula']
     for k,name in enumerate(re.findall(r'"([^"]+)"',expr)):
      key=f'v{k}';env[key]=arrays[name];expr=expr.replace('"'+name+'"',key)
     expected=expression(expr,env);assert np.allclose(expected,arrays[c['name']],rtol=0,atol=0,equal_nan=True),(p.name,c['id'])
   rawname='dataset_'+ds['id']+'_raw_cells.csv'
   with (folder/rawname).open('w',newline='') as f:
    w=csv.writer(f);w.writerow(rows[0]);w.writerows([[col[i] if i<len(col) else '' for col in rawcols] for i in range(max(map(len,rawcols),default=0))])
   section+=f'<li>{html.escape(ds["name"])}: <a href="{quote(p.stem)}/{ds["csv"]}">CSV</a> · <a href="{quote(p.stem)}/{rawname}">Original cell text</a> ({ds["rows"]:,} rows)</li>'
  section+='</ul>'
  for g in m['graphs']:
   report['graphs']+=1
   assert len(g['files'])==6,(p.name,g['id'])
   for fn in g['files']:assert (folder/fn).stat().st_size>100;report['figures']+=1
   if not any(t['finite_pairs'] for t in g['traces']):report['warnings'].append(f'{p.name} graph {g["id"]}: no finite data')
   section+=f'<article><h3>Graph {g["id"]}</h3><img loading="lazy" width="720" src="{quote(p.stem)}/graph_{g["id"]}_paper.png"><p>'
   section+=' · '.join(f'<a href="{quote(p.stem)}/{fn}">{fn.split("_")[-1]}</a>' for fn in g['files'])+'</p></article>'
  sections.append(section+'</section>')
 (root/'verification.json').write_text(json.dumps(report,indent=2))
 (root/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Logger Pro experimental archive</title><style>body{font:16px system-ui;max-width:1100px;margin:40px auto;padding:0 20px;color:#17212b}img{max-width:100%;height:auto}section{border-top:1px solid #ccc;margin-top:35px}a{color:#006699}</style><h1>Logger Pro experimental archive</h1><p>CSV data and faithful/paper figure reconstructions. Integrals and statistics are recomputed in Python. Special Z tokens remain unresolved and appear as gaps; original cell text is preserved. See <a href="verification.json">verification report</a> and <a href="../README.md">README</a>.</p>'+''.join(sections))
 print(json.dumps({k:v for k,v in report.items() if k!='warnings'},indent=2));return report
if __name__=='__main__':validate()
