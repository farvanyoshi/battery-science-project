"""Reconstruct saved Logger Pro graphs with Matplotlib (no refitting)."""
import ast
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from urllib.parse import quote

def text(e,k,d=''):
    return e.findtext(k,d).strip()

def expression(expr, env):
    tree=ast.parse(expr.replace('^','**'), mode='eval')
    allowed=(ast.Expression,ast.BinOp,ast.UnaryOp,ast.Name,ast.Load,ast.Constant,
             ast.Mult,ast.Div,ast.Add,ast.Sub,ast.USub,ast.UAdd,ast.Pow,ast.Call)
    if any(not isinstance(n,allowed) for n in ast.walk(tree)):
        raise ValueError('Unsupported expression')
    for n in ast.walk(tree):
        if isinstance(n,ast.Call) and (not isinstance(n.func,ast.Name) or n.func.id!='exp'):
            raise ValueError('Unsupported function')
    with np.errstate(all='ignore'):
        return eval(compile(tree,'saved expression','eval'), {'__builtins__':{}}, env)

def model_values(m,x):
    env=dict(zip(text(m,'FunctionModelParameterNames').split(),
                 map(float,text(m,'FunctionCoefficientArray').split()[1:])))
    if text(m,'FunctionModelTimeOffset')=='1':
        x=x-float(text(m,'FunctionModelTimeOffsetValue','0'))
    return expression(text(m,'FunctionModelString'),dict(env,x=x,exp=np.exp))

def render(g,r,folder,cols,values,models,warnings):
    gid=text(g,'ID');pairs=text(g,'GraphPlotTraceIDPairs').split()[1:]
    result={'id':gid,'files':[],'analysis':[],'traces':[]}
    helpers=[e for e in r.iter() if e.tag.startswith('PageHelperData') and text(e,'SubordinateToID')==gid]
    notes=[]
    for h in helpers:
        entry={'id':text(h,'ID'),'type':h.tag,'recomputed':False};result['analysis'].append(entry)
        try:
            xid=text(h,'GUIHelperBaseColumnID');yid=text(h,'GUIHelperTraceColumnID')
            x,y=values[xid],values[yid];n=min(len(x),len(y));x,y=x[:n],y[:n]
            lo=float(text(h,'GUIHelperRangeMin','-inf'));hi=float(text(h,'GUIHelperRangeMax','inf'))
            mask=np.isfinite(x)&np.isfinite(y)
            if text(h,'GUIHelperUseEntireRange')!='1':mask&=(x>=lo)&(x<=hi)
            label=cols[yid]['dataset'];suffix=f'{label}, x={lo:g}–{hi:g}'
            if h.tag=='PageHelperDataCurveFit':
                m=models[text(h,'CurveFitFunctionID')]
                entry.update(equation=text(m,'FunctionModelString'),parameters=text(m,'FunctionCoefficientArray'),uncertainties=text(m,'FunctionCoefficientUncertaintyArray'),range=[lo,hi],rmse=text(h,'CurveFitError'),correlation=text(h,'CurveFitCorrelation'))
                notes.append(f'{suffix}: fit {entry["equation"]}; coefficients {entry["parameters"]}; RMSE {entry["rmse"]}')
            elif h.tag=='PageHelperDataIntegral':
                # Integrate only adjacent valid source rows: gaps are never bridged.
                valid=mask[:-1]&mask[1:]
                area=float(np.sum((np.diff(x)*(y[:-1]+y[1:])/2)[valid]))
                entry.update(recomputed=True,method='trapezoids between adjacent finite samples within saved range; no gap bridging',value=area,range=[lo,hi],unit=cols[yid]['units']+' '+cols[xid]['units'])
                notes.append(f'{suffix}: integral (Python) = {area:.6g} {entry["unit"]}')
            else:
                v=y[mask];stats={'count':int(len(v))}
                if len(v):stats.update(min=float(v.min()),max=float(v.max()),mean=float(v.mean()),median=float(np.median(v)),std_sample=float(np.std(v,ddof=1)) if len(v)>1 else None)
                entry.update(recomputed=True,range=[lo,hi],statistics=stats)
                notes.append(f'{suffix}: statistics (Python) '+', '.join(f'{k}={v:.6g}' for k,v in stats.items() if v is not None))
        except Exception as ex:
            warnings.append(f'analysis {entry["id"]}: {ex}')
    for style in ['faithful','paper']:
        with plt.rc_context({'font.size':10,'svg.fonttype':'none','pdf.fonttype':42,'path.simplify':False,'axes.prop_cycle':plt.cycler(color=['#0072B2','#D55E00','#009E73','#CC79A7','#E69F00','#56B4E9','#000000'])}):
            fig=plt.figure(figsize=(9,5.5+0.34*len(notes)),layout='constrained')
            if notes:
                grid=fig.add_gridspec(2,1,height_ratios=[5,max(.6,.34*len(notes))]);ax=fig.add_subplot(grid[0]);na=fig.add_subplot(grid[1]);na.axis('off')
                import textwrap
                na.text(0,1,'\n'.join(textwrap.fill(s,140) for s in notes),va='top',fontsize=7,transform=na.transAxes)
            else:ax=fig.add_subplot()
            ynames=[];xnames=[];traces=[]
            for xid,yid in zip(pairs[::2],pairs[1::2]):
                try:
                    x=values[xid]
                    if yid in models:
                        finite=x[np.isfinite(x)];x=np.linspace(finite.min(),finite.max(),600);y=model_values(models[yid],x);label='Fit: '+text(models[yid],'FunctionModelString');isfit=True
                    else:
                        y=values[yid];label=cols[yid]['dataset']+' — '+cols[yid]['name'];isfit=False
                        yl=cols[yid]['name']+(f' ({cols[yid]["units"]})' if cols[yid]['units'] else '')
                        if yl not in ynames:ynames.append(yl)
                    xl=cols[xid]['name']+(f' ({cols[xid]["units"]})' if cols[xid]['units'] else '')
                    if xl not in xnames:xnames.append(xl)
                    n=min(len(x),len(y));x,y=x[:n],y[:n]
                    connected=isfit or text(g,'GraphConnectLines')=='1'
                    line,=ax.plot(x,y,ls='--' if isfit else '-' if connected else 'None',marker=None if connected else '.',markersize=3,linewidth=1.2,label=label)
                    c=cols.get(yid,{})
                    if c.get('error_enabled') and text(g,'GraphShowTraceErrorBars')=='1':
                        err=values.get(c.get('error_column')) if c.get('error_column')!='0' else None
                        if err is None:err=float(c['error_value']) if c['error_constant']=='1' else np.abs(y)*float(c['error_value'])/100
                        if isinstance(err,np.ndarray):err=err[:n]
                        ax.errorbar(x,y,yerr=err,fmt='none',ecolor=line.get_color(),alpha=.5,capsize=2)
                    traces.append({'x':xid,'y':yid,'samples':n,'finite_pairs':int(np.sum(np.isfinite(x)&np.isfinite(y)))})
                except Exception as ex:
                    if style=='faithful':warnings.append(f'graph {gid} trace {xid}/{yid}: {ex}')
            if not any(t['finite_pairs'] for t in traces):
                ax.text(.5,.5,'No samples saved for the selected run',ha='center',va='center',transform=ax.transAxes,color='#666666')
                result['empty_source_run']=True
            if style=='faithful':result['traces']=traces
            for axis in ['X','Y']:
                if text(g,'Log'+axis+'Axis')=='1':getattr(ax,'set_'+axis.lower()+'scale')('log')
                if style=='faithful':
                    try:
                        low=float(text(g,'GraphPlot'+axis+'Min'));high=float(text(g,'GraphPlot'+axis+'Max'))
                        if high>low:getattr(ax,'set_'+axis.lower()+'lim')(low,high)
                    except ValueError:pass
            ax.set_xlabel(text(g,'GraphPlotXLabel') or ' / '.join(xnames))
            ax.set_ylabel(text(g,'GraphPlotYLabel') or ' / '.join(ynames))
            ax.set_title(text(g,'GraphTitle') or folder.name,fontsize=11,wrap=True)
            if ax.lines:ax.legend(fontsize=7,loc='best')
            if style=='paper':ax.spines[['top','right']].set_visible(False);ax.grid(alpha=.18)
            for ext in ['png','pdf','svg']:
                fn=f'graph_{gid}_{style}.{ext}';fig.savefig(folder/fn,dpi=200);result['files'].append(fn)
            plt.close(fig)
    return result
