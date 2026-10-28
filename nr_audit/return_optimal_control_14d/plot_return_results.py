"""仅绘制已存14天回流结果；不导入求解入口，不启动优化或ODE。"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

HERE=Path(__file__).resolve().parent
RESULTS=HERE/'results'
OUTPUT=RESULTS/'figures_20261028'
ORDER=['q_only','cost','opt_noreturn','c_only']
LABELS={'q_only':'仅隔离','cost':'重新优化：最低成本候选',
        'opt_noreturn':'无回流最优律迁移','c_only':'仅减少接触'}
SHORT={'q_only':'仅隔离','cost':'最低成本候选','opt_noreturn':'迁移律','c_only':'仅减少接触'}
COLORS={'q_only':'#0072B2','cost':'#D55E00','opt_noreturn':'#009E73','c_only':'#CC79A7'}
STYLES={'q_only':'-','cost':'-','opt_noreturn':'--','c_only':'-.'}
INPUTS={}

plt.rcParams.update({'font.family':['Microsoft YaHei','DejaVu Sans'],
    'font.size':10.5,'axes.titlesize':11.5,'axes.labelsize':10.5,
    'axes.unicode_minus':False,'axes.spines.top':False,'axes.spines.right':False,
    'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','savefig.facecolor':'white'})


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    path=Path(path).resolve()
    if HERE not in path.parents:
        raise ValueError('数据必须来自现有研究目录')
    INPUTS[str(path.relative_to(HERE)).replace('\\','/')]=sha(path)
    return json.loads(path.read_text(encoding='utf-8'))


def load():
    summary=read(RESULTS/'summary.json')
    accepted=read(RESULTS/'final_acceptance_v2.json')
    if not accepted['all_scientific_checks_pass']:
        raise ValueError('最终候选未通过核验，不生成批准结果图')
    data={};metrics={}
    for case in ['base','xian']:
        data[case]={};metrics[case]={}
        for kind in ORDER:
            if kind in ['q_only','cost']:
                target='infections' if kind=='q_only' else 'cost'
                receipt=accepted['representatives'][f'{case}_{target}']['DOP853']
                item=read(HERE/receipt['saved_path'])
            else:
                item=read(RESULTS/'references'/f'{case}_{kind}.json')
            if not item['feasible']:
                raise ValueError(f'{case}/{kind}未通过数值核验')
            data[case][kind]=item
            m=next(r for r in summary['entries'] if r['case']==case and r['control']==kind)
            for key in ['duration','J']:
                actual=item[key];reference=m['duration_days' if key=='duration' else 'J_days']
                if abs(actual-reference)>1e-8*max(1.,abs(reference)):
                    raise ValueError(f'{case}/{kind}/{key}来源不一致')
            metrics[case][kind]=m
    return data,metrics


def save(fig,name):
    for extension in ['png','pdf','svg']:
        fig.savefig(OUTPUT/f'{name}.{extension}',dpi=220,bbox_inches='tight',pad_inches=.12)
    plt.close(fig)


def metrics_figure(metrics):
    fig,axes=plt.subplots(2,3,figsize=(13.8,7.4))
    fig.subplots_adjust(left=.095,right=.975,bottom=.17,top=.83,wspace=.44,hspace=.64)
    letters='abcdef'
    for row,case in enumerate(['base','xian']):
        case_name='基准' if case=='base' else '西安'
        q=metrics[case]['q_only']
        for col,key in enumerate(['duration_days','delta_C','J_days']):
            ax=axes[row,col];values=[]
            for kind in ORDER:
                m=metrics[case][kind]
                value=(m['C_infinity_estimate']-q['C_infinity_estimate']) if key=='delta_C' else m[key]
                values.append(value)
            values=np.array(values)
            ax.barh(np.arange(4),values,color=[COLORS[k] for k in ORDER],height=.55,zorder=3)
            ax.scatter([0],[0],s=23,color=COLORS['q_only'],zorder=4)
            ax.set_yticks(np.arange(4),[SHORT[k] for k in ORDER]);ax.invert_yaxis()
            ax.grid(axis='x',alpha=.18,zorder=0);ax.tick_params(axis='y',length=0)
            maximum=max(values)
            ax.set_xlim(0,maximum*1.30)
            if col==0:
                title='控制时长';xlabel='天';fmt=lambda v:f'{v:.2f}'
            elif col==1:
                title='全过程累计感染增量';xlabel='人（相对仅隔离）'
                fmt=(lambda v:f'+{v:,.0f}' if v else '0') if case=='xian' else (lambda v:f'+{v:.2f}' if v else '0')
                anchor=(f"仅隔离总量：{q['C_infinity_estimate']:.2f}人" if case=='base' else
                        f"仅隔离总量：{q['C_infinity_estimate']/1e4:.2f}万人")
                ax.text(.01,1.015,anchor,transform=ax.transAxes,fontsize=9,color='#555555')
            else:
                title='二次干预强度成本';xlabel='J（天）';fmt=lambda v:f'{v:.4f}'
            for y,v in enumerate(values):
                ax.text(v+.025*maximum,y,fmt(v),va='center',ha='left',fontsize=9.5)
            ax.set_title(f'({letters[row*3+col]}) {case_name}：{title}',loc='left',pad=24)
            ax.set_xlabel(xlabel);ax.xaxis.set_major_locator(MaxNLocator(4))
    fig.suptitle('14天指数回流：控制组合仍改变时长与成本',fontsize=15,y=.98)
    fig.text(.095,.075,'仅隔离兼作最短时长候选和当前感染分辨率内的代表；感染最优形态未被唯一确定。',fontsize=10)
    fig.text(.095,.035,'感染增量仅由已有结果作差展示；西安最低成本候选的感染数按约±2人的离散不确定度解释。',fontsize=9,color='#555555')
    save(fig,'01_objectives_comparison')


def control_figure(data):
    fig,axes=plt.subplots(2,2,figsize=(12.2,7.2))
    fig.subplots_adjust(left=.08,right=.98,bottom=.24,top=.86,wspace=.20,hspace=.55)
    handles=[]
    for row,case in enumerate(['base','xian']):
        c0=10. if case=='base' else 12.8872
        for kind in ORDER:
            d=data[case][kind];tr=d['trajectory'];t=np.array(tr['t_platform'])-d['t1']
            c=np.array(tr['c_platform'])/c0;q=np.array(tr['q_platform'])
            line,=axes[row,0].plot(t,c,STYLES[kind],color=COLORS[kind],lw=2,label=LABELS[kind])
            axes[row,1].plot(t,q,STYLES[kind],color=COLORS[kind],lw=2)
            for ax,yy in [(axes[row,0],c),(axes[row,1],q)]:
                ax.plot(t[-1],yy[-1],marker='o',color=COLORS[kind],ms=4)
            if row==0:handles.append(line)
        for col,title in enumerate([r'接触率 $c/c_0$',r'隔离比例 $q$']):
            ax=axes[row,col];ax.set_title(f"({'abcd'[row*2+col]}) {'基准' if case=='base' else '西安'}：{title}",loc='left')
            ax.set_xlabel('启动后的时间（天）');ax.grid(alpha=.18)
            ax.set_xlim(left=0);ax.set_ylim(top=1.025 if col==0 else None)
    fig.suptitle('阈值控制期内的两种措施：最低成本候选先接近仅隔离，随后联合干预',fontsize=14.5,y=.98)
    fig.legend(handles,[LABELS[k] for k in ORDER],loc='lower center',bbox_to_anchor=(.53,.095),ncol=4,frameon=False,fontsize=10)
    fig.text(.08,.035,'曲线只显示各自的强化控制期；圆点表示首次S=Sc时退出。退出后均永久恢复常规措施。',fontsize=9.5,color='#555555')
    save(fig,'02_control_profiles')


def safety_figure(data):
    fig,axes=plt.subplots(2,2,figsize=(12.2,7.2))
    fig.subplots_adjust(left=.08,right=.98,bottom=.27,top=.86,wspace=.22,hspace=.55)
    handles=[];horizons={}
    for row,case in enumerate(['base','xian']):
        theta=.05 if case=='base' else .002
        sc=.3504/(.155*10*(1-.01526)) if case=='base' else .2953/(.1498*12.8872*(1-.323))
        crossings=[]
        for kind in ORDER:
            d=data[case][kind];tr=d['trajectory'];t=np.array(tr['t_post'])-d['t2'];y=np.array(tr['states_post'])
            ratio=np.exp(y[:,1])/theta
            below=np.flatnonzero(ratio<=1e-4)
            crossings.append(t[below[0]] if len(below) else t[-1])
            line,=axes[row,0].plot(t,ratio,STYLES[kind],color=COLORS[kind],lw=2,label=LABELS[kind])
            axes[row,1].plot(t,(y[:,0]+y[:,2])/sc,STYLES[kind],color=COLORS[kind],lw=2)
            if row==0:handles.append(line)
        horizon=float(np.ceil(max(crossings)/10)*10);horizons[case]=horizon
        for col,title in enumerate([r'退出后感染 $I/\eta$',r'总易感者 $(S+S_q)/S_c$']):
            ax=axes[row,col];ax.axhline(1,color='#333333',ls=':',lw=1.25)
            ax.set_xlim(0,horizon);ax.set_xlabel('各自退出后的时间（天）');ax.grid(alpha=.18)
            ax.set_title(f"({'abcd'[row*2+col]}) {'基准' if case=='base' else '西安'}：{title}",loc='left')
            if col==0:ax.set_ylim(-.015,1.09)
            ax.annotate('阈值 I/η=1' if col==0 else '总易感临界值 U/Sc=1',
                xy=(.98,1),xycoords=('axes fraction','data'),xytext=(0,5),
                textcoords='offset points',ha='right',fontsize=9,
                bbox={'facecolor':'white','edgecolor':'none','alpha':.8,'pad':1.})
    fig.suptitle('退出后的阈值核验：展示已核验的四种控制样本',fontsize=15,y=.98)
    fig.legend(handles,[LABELS[k] for k in ORDER],loc='lower center',bbox_to_anchor=(.53,.125),ncol=4,frameon=False,fontsize=10)
    fig.text(.08,.075,'退出后阈值要求已纳入本轮优化的可行类；图中样本通过核验，不代表任意回流策略自动安全。',fontsize=9.2)
    fig.text(.08,.036,'U=S+Sq降至Sc以下后，后续衰减与剩余感染由已有判据和尾界覆盖；图中仅显示尾段的一部分。',fontsize=9.2,color='#555555')
    save(fig,'03_postexit_threshold')
    return horizons


def main():
    OUTPUT.mkdir(exist_ok=True)
    protected=read(RESULTS/'protected_initial.json')
    repo=HERE.parents[1]
    before={p:sha(repo/p) for p in protected if (repo/p).is_file()}
    count_paths=['optimization_log.jsonl','evaluation_log.jsonl','shooting_overview.json','summary.json','manifest.json']
    science_before={p:sha(RESULTS/p) for p in count_paths}
    data,metrics=load()
    metrics_figure(metrics);control_figure(data);horizons=safety_figure(data)
    changed=[p for p,h in before.items() if not (repo/p).exists() or sha(repo/p)!=h]
    science_after={p:sha(RESULTS/p) for p in count_paths}
    if changed or science_after!=science_before:
        raise RuntimeError('绘图期间受保护文件或科学结果记录发生变化')
    plot_data={case:{kind:{'duration_days':metrics[case][kind]['duration_days'],
        'J_days':metrics[case][kind]['J_days'],
        'C_infinity_estimate':metrics[case][kind]['C_infinity_estimate'],
        'delta_C_relative_q_only':metrics[case][kind]['C_infinity_estimate']-metrics[case]['q_only']['C_infinity_estimate'],
        'evaluation_id':data[case][kind]['evaluation_id']} for kind in ORDER} for case in data}
    (OUTPUT/'plot_data.json').write_text(json.dumps(plot_data,ensure_ascii=False,indent=2),encoding='utf-8')
    captions='''# 14天指数回流结果图

仅绘制2026-10-27研究中已有的汇总值和独立核验轨迹，没有新增优化或ODE求解。增量、时间对齐和归一化均为展示处理；原科学结果和论文不改。

## 图1：三项指标

两行分别为基准和西安参数；三列分别为控制时长、相对仅隔离的全过程累计感染增量、二次干预强度成本。每行标出仅隔离的累计感染总量。仅隔离兼作最短时长候选和当前感染分辨率内的代表，不表示感染最优形态已被唯一确定。迁移律未经正回流重新优化。西安成本候选的累计感染存在约2人的跨离散差，不能以尾界冒充全部精度。

## 图2：控制过程

各控制采用同组共同启动状态，横轴为启动后的时间。曲线在各自首次S=Sc时结束，圆点标出退出；之后均永久恢复(c0,q0)。最低成本候选前期接近仅隔离、后期两措施并用，是本轮固定情景的数值观察。

## 图3：退出后的阈值与尾段条件

横轴为各控制各自退出后的时间。左列展示I/eta，右列展示总易感者U=S+Sq与Sc的关系。主问题将退出后的阈值要求纳入可行类；本图不构成任意回流控制在S=Sc退出都自动安全的一般结论。画面只显示已存尾段的一部分，后续由U<Sc及既有尾界核验覆盖。

## 文件

每幅图均提供PNG预览、PDF矢量版和SVG矢量版。`plot_data.json`记录指标与展示增量，`plot_receipt.json`记录所读输入、图件身份、零新增科学求解和保护核验。此前研究目录中的旧图保留。
'''
    (OUTPUT/'README.md').write_text(captions,encoding='utf-8')
    receipt={'created_utc':datetime.now(timezone.utc).isoformat(),
        'script_sha256':sha(Path(__file__)),'inputs_sha256':INPUTS,
        'new_optimization_calls':0,'new_ODE_solves':0,
        'display_processing':['已有C∞作差','时间按启动或退出对齐','按c0、eta、Sc归一化','连接已存轨迹样点'],
        'postexit_display_horizons_days':horizons,
        'protected_files_checked':len(before),'protected_files_changed':changed,
        'science_log_and_summary_unchanged':science_before==science_after,
        'outputs':{p.name:sha(p) for p in OUTPUT.iterdir() if p.suffix in ['.png','.pdf','.svg','.json','.md'] and p.name!='plot_receipt.json'}}
    (OUTPUT/'plot_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(OUTPUT),'figures':3,'formats':['png','pdf','svg'],
        'new_optimization_calls':0,'new_ODE_solves':0,'protected_files_changed':changed},ensure_ascii=False))


if __name__=='__main__':
    main()
