"""论文排版适配入口：沿用原绘图语句与缓存，仅改变批准的版式属性。"""
from pathlib import Path
from types import SimpleNamespace
from contextlib import contextmanager
import ast
import hashlib
import importlib.util
import json
import pickle
import re
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.text import Text
from matplotlib.transforms import ScaledTranslation
from matplotlib.path import Path as MPath
from matplotlib.gridspec import GridSpec

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE.parent/'figures'/'layout_v5'
QA = HERE/'qa'
DATA = HERE/'data'
SKILL = Path.home()/'.codex'/'skills'/'nature-figure'/'scripts'
sys.path.insert(0,str(SKILL))
from audit_panel_alignment import require_matplotlib_panel_alignment
sys.path.insert(0,str(HERE.parent/'revision_style_restore'))
import restore_figures as old

SAVE = Figure.savefig
CHECKS = []


def import_original(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT/path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def axes_all(fig):
    return [a for ax in fig.axes for a in [ax,*ax.child_axes]]


def scientific_fingerprint(fig):
    """比较数据、颜色、线型与标记；不把字号、坐标上界、标签位置当成数据。"""
    result=[]
    for ax in axes_all(fig):
        records=[]
        for l in ax.lines:
            records.append(('line',hashlib.sha256(l.get_xydata().tobytes()).hexdigest(),
                            str(l.get_color()),l.get_linewidth(),l.get_linestyle(),
                            l.get_marker(),l.get_markersize(),l.get_alpha()))
        for c in ax.collections:
            records.append(('collection',hashlib.sha256(np.asarray(c.get_offsets()).tobytes()).hexdigest(),
                            str(c.get_facecolors()),str(c.get_edgecolors()),str(c.get_linewidths()),
                            [hashlib.sha256(p.vertices.tobytes()).hexdigest() for p in c.get_paths()]))
        for p in ax.patches:
            records.append(('patch',p.get_path().vertices.tolist(),p.get_facecolor(),p.get_edgecolor(),
                            getattr(p,'get_height',lambda:None)()))
        result.append(records)
    return result


def panel(ax, letter):
    for t in list(ax.texts):
        if re.fullmatch(r'\(?[a-f]\)?',t.get_text()):
            t.remove()
    transform=ax.transAxes+ScaledTranslation(-1.5/72,2/72,ax.figure.dpi_scale_trans)
    ax.text(0,1,f'({letter})',transform=transform,fontfamily='Times New Roman',
            fontsize=11,fontweight='bold',ha='left',va='bottom',color='#222222',clip_on=False)


def time_labels(fig):
    for ax in fig.axes:
        if ax.get_xlabel() in [r'time $t$ (days)',r'$t$ (days)']:
            ax.set_xlabel(r'$t$')


def min_fonts(fig):
    for ax in axes_all(fig):
        for t in ax.findobj(match=Text):
            if not t.get_text():
                continue
            floor=7.3 if '$' in t.get_text() else 6.0
            if r'I_{t_' in t.get_text():
                floor=10.5
            if t.get_fontsize()<floor:
                t.set_fontsize(floor)


def move_legend(ax, *, population=False, keep=True, ncol=2):
    leg=ax.get_legend()
    handles=list(leg.legend_handles)
    labels=[t.get_text() for t in leg.get_texts()]
    if population:
        labels=[re.sub(r'\s*\(\$N.*','',s,flags=re.S) for s in labels]
        assert not any('$N' in s for s in labels)
    leg.remove()
    if keep:
        ax.legend(handles,labels,loc='upper right',ncol=ncol,fontsize=7.3,
                  handlelength=1.65,columnspacing=.8,handletextpad=.5,
                  borderaxespad=.35,labelspacing=.24,frameon=False)


def reserve_legend(ax):
    """保持右上角位置，必要时只提高上限；不能用白框盖住轨迹。"""
    if ax.get_legend() is None:
        return
    for _ in range(50):
        ax.figure.canvas.draw()
        box=ax.get_legend().get_window_extent().expanded(1.035,1.10)
        collides=False
        for line in ax.lines:
            if not line.get_visible(): continue
            path=line.get_transform().transform_path(line.get_path())
            if path.intersects_bbox(box,filled=False):
                collides=True; break
        if not collides:
            return
        lo,hi=ax.get_ylim()
        ax.set_ylim(lo,hi*1.20 if ax.get_yscale()=='log' else lo+(hi-lo)*1.10)
    raise RuntimeError('图例仍遮挡曲线')


def place_inset(ax, *, population=False, c0=False):
    ins=ax.child_axes[0]
    ins.set_axes_locator(None)
    b=ax.get_position()
    x,w=(.36,.62) if population else ((.55,.43) if c0 else (.47,.51))
    ins.set_position([b.x0+x*b.width,b.y0+.57*b.height,w*b.width,.36*b.height])
    ins.tick_params(labelsize=6.3,pad=1)
    ins.xaxis.label.set_size(8)
    ins.yaxis.label.set_size(8.5)
    if c0:
        ins.title.set_size(6.4)
        for t in ins.texts: t.set_fontsize(6.1)
    # 数值与数学记号仍是原文本，不以删减元素换空间。


def adapt(fig,name):
    time_labels(fig)
    if name=='xian_observed_fit':
        for a,l in zip(fig.axes,'ab'): panel(a,l)
        return
    if name=='xian_strategy_process':
        fig.set_size_inches(135/25.4,125/25.4)
        fig.axes[0].get_gridspec().update(left=.12,right=.98,bottom=.09,top=.945,wspace=.38,hspace=.52)
        for leg in list(fig.legends): leg.remove()
        fig.axes[0].legend(handles=old.pps.strategy_handles(include_observed=True),
                           loc='upper right',ncol=2,fontsize=7.3,frameon=False,
                           handlelength=1.7,columnspacing=.8)
        for a,l in zip(fig.axes,'abcde'): panel(a,l)
        reserve_legend(fig.axes[0])
    elif name in ['population_threshold_levers','critical_population_cases']:
        is14=name=='population_threshold_levers'
        fig.axes[0].get_gridspec().update(left=.09,right=.98,bottom=.10 if is14 else .07,
                                         top=.945,hspace=.40 if is14 else .48,wspace=.28)
        if is14:
            pairs=[(fig.axes[0],fig.axes[2]),(fig.axes[1],fig.axes[3])]
        else:
            pairs=[tuple(fig.axes[2*i:2*i+2]) for i in range(3)]
        for i,(ai,aq) in enumerate(pairs):
            move_legend(ai,population=is14 and i==1,keep=is14 or i==0)
            for txt in list(ai.texts):
                if 'N_{' in txt.get_text() and 'eff' in txt.get_text(): txt.remove()
            reserve_legend(ai)
            place_inset(aq,population=is14 and i==1)
        for a,l in zip(fig.axes,'abcdef'): panel(a,l)
    elif name=='c0_phase_stationary':
        fig.set_size_inches(120/25.4,87/25.4)
        fig.subplots_adjust(left=.14,right=.98,bottom=.16,top=.97)
        ax=fig.axes[0]
        handles,labels=ax.get_legend_handles_labels()
        ax.legend(handles,labels,loc='upper right',fontsize=7.3,frameon=False,
                  handlelength=2.1,handletextpad=.6,labelspacing=.30)
        for t in ax.texts:
            if t.get_text()==r'$\theta=0.002$': t.set_y(.002*1.18)
    elif name=='c0_sensitivity_panel':
        fig.set_layout_engine(None)
        fig.set_size_inches(112/25.4,90/25.4)
        fig.subplots_adjust(left=.14,right=.98,bottom=.14,top=.93,hspace=.30)
        ai,aq=fig.axes
        ai.set_ylim(0,80); ai.set_yticks([0,20,40,60,80])
        leg=ai.get_legend(); handles=list(leg.legend_handles)
        labels=[t.get_text().split(' (')[0] for t in leg.get_texts()]
        leg.remove()
        ai.legend(handles,labels,loc='upper right',ncol=2,fontsize=7.3,
                  columnspacing=1,handlelength=1.7,frameon=False,labelspacing=.15)
        for a,l in zip(fig.axes,'ab'): panel(a,l)
        place_inset(aq,c0=True)
        # 上限取整为 80，主刻度为 20；为三行图例保留可读空间。
        reserve_legend(ai)
    elif name=='scenario1_inflection_lambda_sensitivity':
        fig.set_size_inches(127.36/25.4,93/25.4)
        fig.subplots_adjust(left=.10,right=.98,bottom=.12,top=.97,wspace=.20,hspace=.30)
        for ax in fig.axes:
            ax.tick_params(labelsize=7.3)
            ax.xaxis.label.set_size(9); ax.yaxis.label.set_size(9)
        # 原图两个图例分别保留右上、左上，不改变内容。
    elif name=='scenario1_inflection_scan_t':
        fig.set_size_inches(127.36/25.4,91/25.4)
        for ax in fig.axes:
            ax.tick_params(labelsize=7.3)
            ax.xaxis.label.set_size(9); ax.yaxis.label.set_size(9)
        fig.tight_layout(pad=.6)
    elif name=='fig_panel_B_trajectory_decomposition':
        fig.set_layout_engine(None)
        fig.set_size_inches(451.28/72,296.4/72)
        fig.axes[0].get_gridspec().update(left=.105,right=.98,bottom=.12,top=.93,
                                         wspace=.28,hspace=.37)
        for a,l in zip(fig.axes,'abcdef'): panel(a,l)
    min_fonts(fig)


def export(fig,name,*,cache=True):
    if cache:
        (DATA/(name+'.pickle')).write_bytes(pickle.dumps(fig))
    before=scientific_fingerprint(fig)
    # 新建图例也沿用原脚本的 Times/STIX，缓存重绘不依赖前一个图的全局设置。
    with plt.rc_context({'font.family':'serif',
                         'font.serif':['Times New Roman','STIXGeneral'],
                         'mathtext.fontset':'stix'}):
        adapt(fig,name)
    assert before==scientific_fingerprint(fig),name+'：曲线、颜色或标记发生非排版变化'
    fig.canvas.draw()
    require_matplotlib_panel_alignment(fig,json_out=QA/(name+'.alignment.json'),
                                        tolerance_pt=1.5,gutter_tolerance_pt=1.5,strict=True)
    plt.rcParams.update({'pdf.fonttype':42,'svg.fonttype':'none'})
    SAVE(fig,OUT/(name+'.pdf'),dpi=300)
    SAVE(fig,OUT/(name+'.svg'),dpi=300)
    SAVE(fig,OUT/(name+'.png'),dpi=300)
    CHECKS.append({'figure':name,'scientific_artists_unchanged':True,
                   'size_mm':(fig.get_size_inches()*25.4).tolist(),
                   'axes':[{'xlabel':a.get_xlabel(),'yscale':a.get_yscale(),
                            'ylim':a.get_ylim(),'lines':len(a.lines),
                            'legend':[] if a.get_legend() is None else [t.get_text() for t in a.get_legend().get_texts()]}
                           for a in fig.axes]})
    path=QA/'artist_preservation.json'
    prior=json.loads(path.read_text(encoding='utf-8')) if path.exists() else []
    prior=[r for r in prior if r['figure']!=name]
    path.write_text(json.dumps(prior+[CHECKS[-1]],ensure_ascii=False,indent=2),encoding='utf-8')
    plt.close(fig)
    print('EXPORTED',name,flush=True)


@contextmanager
def intercept(name):
    seen=set()
    def wrapped(fig,*args,**kwargs):
        if id(fig) not in seen:
            seen.add(id(fig)); export(fig,name)
    Figure.savefig=wrapped
    try: yield
    finally: Figure.savefig=SAVE


def inflection():
    plt.rcdefaults()
    sys.path.insert(0,str(ROOT/'scenario1_inflection'))
    mod=import_original('original_lambda','scenario1_inflection/fig_lambda_sensitivity.py')
    with intercept('scenario1_inflection_lambda_sensitivity'): mod.main()
    path=ROOT/'scenario1_inflection/fig_scan_t.py'
    with intercept('scenario1_inflection_scan_t'):
        exec(compile(path.read_text(encoding='utf-8-sig'),str(path),'exec'),{'__file__':str(path)})


def c0_panel():
    mod=import_original('original_c0','c0_sensitivity/run_c0_sensitivity.py')
    mod.configure_plot_style()
    d=old.SNAP/'c0_sensitivity_outputs'
    summary=pd.read_csv(d/'c0_representative_summary.csv')
    ts=pd.read_csv(d/'c0_representative_timeseries.csv')
    scenarios=[]
    for row in summary.to_dict('records'):
        m=SimpleNamespace(**row)
        t=np.linspace(m.t1,m.t2,4001)
        s=m.s_bar+(m.s_star-m.s_bar)*np.exp(-m.c0*mod.P.theta*(t-m.t1))
        q=1-mod.P.gamma/(mod.P.beta*m.c0*s)
        scenarios.append(mod.Scenario(m,ts[ts.role==m.role].copy(),t,q,(t-m.t1)/(m.t2-m.t1)))
    with intercept('c0_sensitivity_panel'):
        mod.plot_main(scenarios,y_scale='linear',inset_mode='cumulative')


def phase():
    # 等值线文字的断口必须按最终尺寸计算，不能缩小画布后沿用旧断口。
    tree=ast.parse(Path(old.__file__).read_text(encoding='utf-8-sig'))
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='phase')
    source=ast.unparse(fn)
    for a,b in [('figsize=(6.27, 4.55)','figsize=(120 / 25.4, 87 / 25.4)'),
                ('left=0.11, right=0.98, bottom=0.13, top=0.97',
                 'left=0.14, right=0.98, bottom=0.16, top=0.97'),
                ('fontsize=7.2','fontsize=7.3')]:
        assert a in source,a
        source=source.replace(a,b)
    env=dict(vars(old)); env['save']=export
    exec(compile(source,'final_size_phase','exec'),env)
    env['phase']()


def decomposition():
    env=old.original_environment('xian_dom/panels.py')
    old.original_A_code(env)
    ref=old.recovery_cache(env)
    old.original_B_code(env,ref)
    env.update(old.original_environment('xian_dom/plot_B_decomp.py'))
    env['GridSpec']=GridSpec
    old.functions_from('xian_dom/plot_B_decomp.py',['threshold_q_parts','_refs','_corner','render'],env)
    roles=['clear','cum','dur45','cost']
    built={r:env['D']['built'][r] for r in roles}
    rout={r:old.cached_prep(built[r]['N'])[2] for r in roles}
    parts={r:env['threshold_q_parts'](built[r]['t'],built[r]['I'],built[r]['q']) for r in roles}
    td=ref['td']
    env.update(roles=roles,built=built,rout=rout,_tdinn_t=td.t.to_numpy(),_tdinn_i=td.I.to_numpy(),
               order_e=sorted(roles,key=lambda r:rout[r].t.iloc[-1],reverse=True),
               order_f=sorted(roles,key=lambda r:parts[r]['clear'],reverse=True),
               panel_label=dict(zip(roles,['(a)','(b)','(c)','(d)'])),OUT=OUT)
    tops={r:1.05*max(parts[r]['clear'],rout[r].t.iloc[-1],td.t.iloc[-1]) for r in roles}
    with intercept('fig_panel_B_trajectory_decomposition'):
        env['render']('unused',tops,1.05*max(v.t.iloc[-1] for v in rout.values()),
                      1.05*max(max(p['clear'] for p in parts.values()),td.t.iloc[-1]))


def main():
    for p in [OUT,QA,DATA]: p.mkdir(exist_ok=True,parents=True)
    old.save=export
    old.QA=QA
    selected=sys.argv[1:]
    groups={'xian':old.xian,'dominance':old.dominance,'phase':phase,
            'inflection':inflection,'c0':c0_panel,'decomposition':decomposition}
    if selected and selected[0]=='cached':
        files=[DATA/(name+'.pickle') for name in selected[1:]] if len(selected)>1 else sorted(DATA.glob('*.pickle'))
        for f in files:
            export(pickle.loads(f.read_bytes()),f.stem,cache=False)
    else:
        for name,fn in groups.items():
            if not selected or name in selected:
                print('START',name,flush=True); fn()
    path=QA/'artist_preservation.json'
    prior=json.loads(path.read_text(encoding='utf-8')) if path.exists() else []
    prior=[r for r in prior if r['figure'] not in {v['figure'] for v in CHECKS}]
    path.write_text(json.dumps(prior+CHECKS,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__': main()
