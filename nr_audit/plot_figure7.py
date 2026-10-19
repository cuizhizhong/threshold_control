"""图7定点纠错：保留全域背景，局部显示A'及两类跳变；不重算ODE、不改旧括区。

图件问题：有限权重网格中，连续进入内部后是否还有内部跳变？
证据：(a,b)旧全域NPZ作定位；(c,d)按已有加密权重局部逐状态求解。
类型：quantitative grid；Python；174 mm宽，最小7 pt字，PDF/SVG及源数据。
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap
from audit_common import ROOT, RESULTS
import allocation as AL
import audit_weights as AW
import params as PR
from vendor.audit_panel_alignment import require_matplotlib_panel_alignment

RES=ROOT/'reproducibility/results/20261005_sec7_v2_refinement/joint_extra'
OUT=ROOT/'paper/figures/joint_v2/joint_phase_weights'
DATA=RESULTS/'new_figure7.json'
NPZ=RESULTS/'new_figure7.npz'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_sha(path):
    """文本按CRLF→LF的内容身份计算；二进制保留原始字节。"""
    path=Path(path);raw=path.read_bytes()
    if path.suffix in ('.py','.json'):
        raw=raw.replace(b'\r\n',b'\n')
    return hashlib.sha256(raw).hexdigest()


def frozen_inputs():
    """原phase及NPZ另外保持严格原始字节校验。"""
    paths=[RES/'phase.json',RES/'phase_baseline.npz',RES/'phase_xian.npz']
    return {p.relative_to(ROOT).as_posix():sha(p) for p in paths}


def inputs():
    files=[RES/'phase.json',RES/'phase_baseline.npz',RES/'phase_xian.npz',
           RESULTS/'weight_brackets.json',ROOT/'nr_audit/allocation.py',
           ROOT/'nr_audit/audit_weights.py',ROOT/'nr_audit/params.py']
    return {p.relative_to(ROOT).as_posix():source_sha(p) for p in files}


def compute():
    wb=json.loads((RESULTS/'weight_brackets.json').read_text(encoding='utf-8'))
    arrays={}; cases={}
    for case,P in PR.CASES.items():
        weights=sorted({p['r'] for change in wb['cases'][case]['changes']
            if any(b['from_'] in ('A',"A'") for b in change['brackets'])
            for p in change['subdivision']})
        # 补入西安两个已确认A'旧网格点，完整显示该区间内部结构。
        weights=sorted(set(weights+[g['r'] for g in wb['cases'][case]['grid_disagreements']]))
        samples=[]
        for r in weights:
            c,info=AW.classify(P,r,N_z=4001,N_local=4001)
            if c=='?': raise ValueError(f'局部分类未定: {case}/{r}')
            samples.append(info)
            print(f'{case} r={r:.6f} {c}',flush=True)
        pts=[b['z'] for row in samples for b in row['breakpoints']]
        zlo,zhi=min(pts),max(pts)
        pad=max(.006,.12*(zhi-zlo))
        z=np.linspace(zlo-pad,zhi+pad,241)
        y=[]
        for row in samples:
            law=AL.make_law_opt(P,wc=1.,wq=row['r'])
            x=np.array([law(float(v)) for v in z])
            y.append((1-x)/(1-1/z))
        arrays[case+'_z']=z
        arrays[case+'_r']=np.array(weights)
        arrays[case+'_y']=np.array(y)
        # 所存默认权重与既有明确结构对应，不执行新轨迹优化。
        cases[case]=dict(samples=samples,z_sw=AL.z_sw_formula(P.z_bar),
            local_shape=[len(weights),len(z)],parameters=vars(P),
            counts={k:sum(s['class']==k for s in samples) for k in ('A',"A'",'B','C')})
    receipt=dict(description=__doc__,source_hashes=inputs(),frozen_source_hashes=frozen_inputs(),
        input_identity_policy='NEW-4b: text CRLF-to-LF SHA256; binary raw; frozen sources additionally raw',
        compute_script_sha256=sha(__file__),
        new_ode_solves=0,N_z=4001,N_local=4001,cases=cases,
        data_scope='原全域网格完整保留；仅已有加密权重及两处旧网格纠错点局部计算；非连续参数分类')
    np.savez_compressed(NPZ,**arrays)
    receipt['cache_npz_sha256']=sha(NPZ)
    DATA.write_text(json.dumps(receipt,ensure_ascii=False,indent=1),encoding='utf-8',newline='\n')
    return receipt,arrays


def edge_kind(b):
    if b['continuous'] and {b['label_left'],b['label_right']}=={'hi','int'}:
        return 'continuous'
    if not b['continuous'] and b['label_left']==b['label_right']=='int':
        return 'internal'
    if not b['continuous'] and {b['label_left'],b['label_right']}=={'hi','int'}:
        return 'endpoint'
    return None


def refine_background(d,arrays):
    """仅填补两个既有加密区之间的背景色网格间隙，不重做分支分类。"""
    if 'background_refinement' in d:
        return
    counts={}
    for case,P in PR.CASES.items():
        r,z,y=(arrays[case+'_'+v] for v in ('r','z','y'))
        step=float(np.median(np.diff(r)))
        extra=[v for a,b in zip(r[:-1],r[1:]) if b-a>2*step
               for v in np.linspace(a,b,int(np.ceil((b-a)/step))+1)[1:-1]]
        merged=sorted(set(r.tolist()+extra)); rows=[]
        for v in merged:
            match=np.flatnonzero(r==v)
            if len(match):
                rows.append(y[match[0]])
            else:
                law=AL.make_law_opt(P,wc=1.,wq=v)
                rows.append([(1-law(float(s)))/(1-1/s) for s in z])
        arrays[case+'_background_r']=np.array(merged)
        arrays[case+'_background_y']=np.array(rows)
        counts[case]=len(extra)
    d['background_refinement']=dict(added_weight_rows=counts,
        purpose='填补背景颜色网格间隙；不新增分类转折或ODE轨迹',script_sha256=sha(__file__))
    d['data_scope']=('原全域网格完整保留；已有加密权重及两处纠错点作局部分类；'
        f'另加西安{counts["xian"]}行仅填补背景颜色，不新增分类转折或ODE；非连续参数分类')
    np.savez_compressed(NPZ,**arrays)
    d['cache_npz_sha256']=sha(NPZ)
    DATA.write_text(json.dumps(d,ensure_ascii=False,indent=1),encoding='utf-8',newline='\n')


def render(d,arrays,reuse_data=False):
    plt.rcParams.update({'font.family':'serif',
        'font.serif':['Times New Roman','STIXGeneral','DejaVu Serif'],
        'mathtext.fontset':'stix',
        'font.size':8,'axes.titlesize':8,
        'axes.labelsize':9,'xtick.labelsize':8,'ytick.labelsize':8,
        'pdf.fonttype':42,'svg.fonttype':'none','axes.linewidth':.65,
        'axes.spines.top':False,'axes.spines.right':False,'legend.frameon':False})
    cmap=LinearSegmentedColormap.from_list('contact_share',['#f5f9fd','#a6cbe6','#206fb6','#062e5c'])
    fig=plt.figure(figsize=(174/25.4,145/25.4))
    gs=fig.add_gridspec(2,2,left=.095,right=.89,
                       bottom=.20,top=.94,hspace=.48,wspace=.39)
    axs=[fig.add_subplot(gs[i,j]) for i in range(2) for j in range(2)]
    summary=json.loads((RES/'phase.json').read_text(encoding='utf-8'))
    colors={'continuous':'#161616','endpoint':'#c23b22','internal':'#9b3a97'}
    for k,(case,key,name) in enumerate((('base','baseline','Baseline'),('xian','xian',"Xi'an"))):
        top,local=axs[k],axs[k+2]
        old=np.load(RES/f'phase_{key}.npz')
        mask=np.ma.masked_where(old['classification']==3,old['y'])
        pc=top.pcolormesh(old['s'],old['r'],mask,cmap=cmap,vmin=0,vmax=1,shading='auto',rasterized=True)
        top.contour(old['s'],old['r'],(old['classification']==1).astype(float),
                    levels=[.5],colors='#161616',linewidths=.7)
        sw=d['cases'][case]['z_sw']
        valid=np.isfinite(old['switch'])&(old['switch']>sw+2*np.diff(old['s'])[0])
        top.plot(np.where(valid,old['switch'],np.nan),old['r'],c=colors['endpoint'],lw=.9)
        top.axvline(sw,color='#555555',ls='--',lw=.8)
        top.axhline(2,color='#666666',ls=':',lw=.7)
        top.set(xlim=(1,summary[key]['s_star']),ylim=(old['r'][0],old['r'][-1]),yscale='log',
                xlabel=r'$S/S_c$',ylabel=r'$r=w_q/w_c$')
        top.set_title(f'({chr(97+k)}) {name}: full grid',loc='left')
        z,r,y=(arrays[case+'_'+v] for v in ('z','r','y'))
        local.pcolormesh(z,arrays[case+'_background_r'],arrays[case+'_background_y'],
            cmap=cmap,vmin=0,vmax=1,shading='auto',rasterized=True)
        samples=d['cases'][case]['samples']
        for kind in colors:
            xs=[]
            for row in samples:
                values=[b['z'] for b in row['breakpoints'] if edge_kind(b)==kind]
                if len(values)>1: raise ValueError('同类型多个断点应分别绘制，不能自动连接')
                xs.append(values[0] if values else np.nan)
            local.plot(xs,r,color=colors[kind],lw=1.15)
            local.scatter(xs,r,color=colors[kind],s=4,zorder=4,linewidths=0)
        local.axvline(sw,color='#555555',ls='--',lw=.8)
        local.set(xlim=(z[0],z[-1]),ylim=(r[0],r[-1]),xlabel=r'$S/S_c$',ylabel=r'$r=w_q/w_c$')
        local.set_title(f'({chr(99+k)}) {name}: transition detail',loc='left')
        if k==1:
            top.set_ylabel('');local.set_ylabel('')
        # 文本置于图区外以免跨过边界线，按实际采样类别的中位权重标识。
        for cls in ('A',"A'",'B'):
            rs=[s['r'] for s in samples if s['class']==cls]
            if rs:
                local.text(1.015,(float(np.median(rs))-r[0])/(r[-1]-r[0]),cls,
                    transform=local.transAxes,va='center',fontsize=7,clip_on=False)
        top.plot([z[0],z[-1],z[-1],z[0],z[0]],[r[0],r[0],r[-1],r[-1],r[0]],
                 color='#555555',lw=.7)
    cax=fig.add_axes([.92,.20,.012,.74]);cax.set_label('_colorbar')
    cb=fig.colorbar(pc,cax=cax);cb.set_label(r'$y$',rotation=0,labelpad=5)
    handles=[Line2D([],[],c=colors['continuous'],lw=1.1,label='Continuous entry'),
        Line2D([],[],c=colors['endpoint'],lw=1.1,label='Endpoint-to-interior jump'),
        Line2D([],[],c=colors['internal'],lw=1.1,label='Interior-to-interior jump'),
        Line2D([],[],c='#555555',ls='--',lw=.8,label=r'$S_{\rm sw}/S_c$: local criterion')]
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.5,.005),ncol=2,
               fontsize=8,columnspacing=2,handlelength=2.7)
    fig.canvas.draw()
    require_matplotlib_panel_alignment(fig,json_out=RESULTS/'new_figure7_alignment.json',
        overlay_svg=ROOT/'tmp/new_figure7_alignment.svg',strict=True,tolerance_pt=1.5)
    # vendor保持原样；调用端统一派生JSON的物理换行。
    alignment=RESULTS/'new_figure7_alignment.json'
    alignment.write_text(alignment.read_text(encoding='utf-8'),encoding='utf-8',newline='\n')
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(OUT.with_suffix('.pdf'),dpi=400)
    fig.savefig(OUT.with_suffix('.svg'),dpi=400)
    svg=OUT.with_suffix('.svg')
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',
                   encoding='utf-8',newline='\n')
    fig.savefig(ROOT/'paper/revision_notes/NEW_4b_figure7_after.png',dpi=300)
    plt.close(fig)
    (RESULTS/'new_figure7_render.json').write_text(json.dumps(dict(
        render_script_sha256=sha(__file__),data_sha256=sha(DATA),npz_sha256=sha(NPZ),
        pdf_sha256=sha(OUT.with_suffix('.pdf')),width_mm=174,height_mm=145,
        source_hashes_unchanged=inputs()==d['source_hashes'],reuse_data=reuse_data,
        font_family='Times New Roman',mathtext_fontset='stix',colorbar_gap_figure_fraction=.03),indent=2),encoding='utf-8',newline='\n')


def validate_cached_inputs(d):
    """文本内容允许CRLF/LF等价；冻结来源和缓存另作原始字节校验。"""
    if inputs()!=d['source_hashes']:
        raise ValueError('图7输入已变，不能复用')
    if frozen_inputs()!=d.get('frozen_source_hashes'):
        raise ValueError('冻结图7输入原始字节不符，不能复用')
    if sha(NPZ)!=d.get('cache_npz_sha256'):
        raise ValueError('图7缓存NPZ身份不符，不能复用')
    if 'background_refinement' not in d:
        raise ValueError('图7缓存缺少背景细化，reuse-data不执行新计算')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--reuse-data',action='store_true')
    args=p.parse_args()
    if args.reuse_data:
        d=json.loads(DATA.read_text(encoding='utf-8'))
        validate_cached_inputs(d)
        arrays=dict(np.load(NPZ))
    else:
        d,arrays=compute()
    if not args.reuse_data:
        refine_background(d,arrays)
    render(d,arrays,reuse_data=args.reuse_data)


if __name__=='__main__':
    main()
