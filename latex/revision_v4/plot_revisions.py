"""按已确认的图表方案重排，读取旧输出，不运行拟合或覆盖研究模块输出。"""
from pathlib import Path
import sys, json, hashlib, argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import LogLocator, NullLocator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE.parent / "figures" / "revision_v4"
DATA, QA = HERE / "data", HERE / "qa"
SKILL = Path.home() / ".codex" / "skills" / "nature-figure" / "scripts"
sys.path.insert(0, str(SKILL))
from audit_panel_alignment import require_matplotlib_panel_alignment
SNAP = ROOT / "archive_unused" / "generated_snapshots"
XIAN = SNAP / "xian_control_comparison_main"
BASE = SNAP / "scenario1_threshold_landscape_current_run" / "output_csv"
SOURCES = json.loads((QA / "source_hashes.json").read_text(encoding="utf-8")) if (QA / "source_hashes.json").exists() else {}

def read_csv(path):
    SOURCES[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return pd.read_csv(path)

def style():
    plt.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
        "mathtext.fontset": "stix", "font.size": 9, "axes.labelsize": 10,
        "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.linewidth": .7, "lines.linewidth": 1.25,
        "pdf.fonttype": 42, "svg.fonttype": "none", "legend.frameon": False,
        "axes.unicode_minus": False, "savefig.dpi": 200,
    })

def letters(axes):
    for i, ax in enumerate(axes):
        ax.annotate(chr(97+i), xy=(0, 1), xycoords="axes fraction",
                    xytext=(-22, 8), textcoords="offset points",
                    fontsize=10, fontweight="bold", annotation_clip=False)
        ax.tick_params(direction="out", length=3)

def save(fig, name):
    fig.canvas.draw()
    require_matplotlib_panel_alignment(
        fig, json_out=str(QA / (name+".alignment.json")),
        tolerance_pt=1.5, gutter_tolerance_pt=1.5, strict=True)
    # 固定画布宽度为论文通栏宽度，避免 tight 裁剪改变最终字号。
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.svg")
    fig.savefig(OUT / f"{name}.png", dpi=300)
    plt.close(fig)
    print("EXPORTED", name, flush=True)

def baseline_q():
    c = read_csv(BASE / "main_c0_summary.csv")
    e = read_csv(BASE / "main_eta_summary.csv")
    c = c[c.c0.isin([4,5,8,10,12])]
    assert len(c)==5 and len(e)==4
    fig, ax = plt.subplots(1, 2, figsize=(6.27, 3.25), sharey=True)
    fig.subplots_adjust(left=.09,right=.98,bottom=.17,top=.91,wspace=.18)
    exported = []
    for a, frame, parameter in zip(ax, [c,e], ["c0","eta"]):
        for k, r in enumerate(frame.itertuples()):
            # 与原 MATLAB 绘图代码采用相同采样数、同一保存参数和同一解析函数。
            tau = np.linspace(0,r.Delta_t,max(350,int(np.ceil(12*r.Delta_t))))
            t = r.t1 + tau
            S = r.S_bar+(r.S_star-r.S_bar)*np.exp(-r.c0*r.eta*tau/r.N)
            q = 1-r.gamma*r.N/(r.beta*r.c0*S)
            color=plt.cm.Blues(.38+.55*k/(len(frame)-1))
            label=rf"$c_0={r.c0:g}$" if parameter=="c0" else rf"$\eta/N={100*r.eta_frac:g}\%$"
            a.plot(t,q,color=color,label=label)
            a.plot(r.t1,r.q_max,"^",ms=4,mfc="white",color=color)
            a.plot(r.t2,r.q0,"|",ms=7,color=color)
            ti=r.t1+r.N/(r.c0*r.eta)*np.log((r.S_star-r.S_bar)/r.S_bar)
            if r.S_c<2*r.S_bar<r.S_star:
                a.plot(ti,1-1/(2*(1-r.beta)),"o",ms=4,color="#b14343")
            exported.append(pd.DataFrame({"family":parameter,"c0":r.c0,"eta":r.eta,"t":t,"q":q}))
        a.axhline(r.q0,color=".5",ls="--",lw=.8)
        a.axhline(1-1/(2*(1-r.beta)),color=".5",ls=":",lw=.8)
        a.set(xlabel="$t$ (d)",ylim=(0,.9),xlim=(0,float((frame.t2+.08*frame.Delta_t).max())))
        a.legend(loc="upper right",fontsize=8)
    ax[0].set_ylabel("$q(t)$")
    letters(ax)
    pd.concat(exported).to_csv(DATA/"baseline_q_plot_samples.csv",index=False)
    save(fig,"baseline_q_joint")

COL = ["#246da6","#bf543c","#777777"]
LS = ["-","--",":"]
LABEL = ["TDINN","Threshold control","Routine control"]

def xian_figures():
    df=read_csv(XIAN/"xian_control_comparison_timeseries.csv")
    obs=read_csv(XIAN/"xian_observed_data_processed.csv")
    names=list(df.strategy.drop_duplicates())
    frames=[df[df.strategy==n] for n in names]
    td=frames[0]
    assert len(obs)==40 and np.all(np.diff(td.t)>0)
    days=np.arange(41)
    fitted=[np.diff(np.interp(days,td.t,td[c])) for c in ["Cc","Cq"]]
    pd.DataFrame({"date":obs.date,"day":obs.t,"community_obs":obs.community_new,
                  "quarantine_obs":obs.quarantine_new,"community_fit":fitted[0],
                  "quarantine_fit":fitted[1]}).to_csv(DATA/"xian_daily_from_main_trajectory.csv",index=False)
    fig,axes=plt.subplots(1,2,figsize=(6.27,3.25))
    fig.subplots_adjust(left=.09,right=.96,bottom=.20,top=.77,wspace=.27)
    for ax,y,col,title in zip(axes,fitted,["community_new","quarantine_new"],["Community","Quarantined"]):
        ax.plot(obs.t,y,color=COL[0],label="TDINN reconstruction")
        ax.scatter(obs.t,obs[col],s=13,facecolors="white",edgecolors=".2",linewidths=.7,label="Observed")
        ax.set(xlim=(-.5,39.5),ylim=(0,None),ylabel="Daily new cases",title=title,xlabel="Date")
        ax.set_xticks([0,12,24,39],["Dec 09","Dec 21","Jan 02","Jan 17"])
    fig.legend(*axes[0].get_legend_handles_labels(),loc="upper center",bbox_to_anchor=(.53,1),ncol=2,fontsize=8)
    letters(axes);save(fig,"xian_observed_fit")
    fig=plt.figure(figsize=(6.27,6.4))
    gs=fig.add_gridspec(3,2,left=.10,right=.98,bottom=.09,top=.90,wspace=.28,hspace=.43)
    axes=[fig.add_subplot(gs[0,:]),fig.add_subplot(gs[1,0]),fig.add_subplot(gs[1,1]),
          fig.add_subplot(gs[2,0]),fig.add_subplot(gs[2,1])]
    for sub,color,ls,label in zip(frames,COL,LS,LABEL):
        for ax,y in zip(axes,[sub.I,sub.Cc+sub.Cq,sub.Rt,sub.c,sub.q]):
            ax.plot(sub.t,y,color=color,ls=ls,label=label)
    for ax,ylabel in zip(axes,["$I(t)$",r"$I_{t_{\mathrm{cum}}}(t)$","$R_e(t)$","$c(t)$","$q(t)$"]):
        ax.set(xlabel="$t$ (d)",ylabel=ylabel,xlim=(0,df.t.max()*1.025))
    axes[0].set_yscale("log");axes[0].set_ylim(1e-3,3e6)
    axes[0].set_xlabel("")
    axes[1].yaxis.label.set_fontsize(11)
    axes[1].set_yscale("symlog",linthresh=1);axes[1].set_ylim(0,6e6)
    axes[2].axhline(1,color=".4",ls="--",lw=.7)
    axes[3].set_ylim(0,14);axes[4].set_ylim(0,1.04)
    fig.legend(*axes[0].get_legend_handles_labels(),loc="upper center",ncol=3,bbox_to_anchor=(.54,.995))
    letters(axes);save(fig,"xian_strategy_process")

def dominance_data():
    # 旧合图仅保存了 PDF，缺少轨迹缓存。使用原求解函数恢复缓存，不重新拟合。
    for path in ["xian_dom","xian_control_comparison","xian_control_comparison/threshold_landscape_analysis"]:
        sys.path.insert(0,str(ROOT/path))
    if not hasattr(np,"trapz"): np.trapz=np.trapezoid
    import caliber as cal
    import xian_control_comparison as xcc
    import threshold_landscape_analysis as tla
    th=[cal.theta_dur(150),cal.theta_cost(),cal.theta_dur(45)]
    cases=[(20000.,th),(cal.N_cum_star(),th),(cal.N_star(45),th),(cal.N_star(),th)]
    populations=[3969.7,10102.3,100/th[2],100/th[1],100/th[0]]
    cache=DATA/"dominance_metadata.json"
    if cache.exists():
        meta=json.loads(cache.read_text(encoding="utf-8"))
        return meta,cal
    meta={"cases":[],"fixed_eta":[],"N_floor":cal.N_FLOOR,"theta":th}
    routine={}
    def obtain(N,eta,stem):
        p=tla.LandscapeParams(N=float(N))
        fit=xcc.InitialFit(S0=N-cal.I0_ABS,I0=cal.I0_ABS,R0_initial=0.,
                           objective=float("nan"),raw_rmse=float("nan"),residual_type="fixed_I0_abs")
        if N not in routine:
            routine[N]=tla.solve_time_control_param("routine",fit,p,tla.c_const(p),tla.q_const(p))
        frame,d=tla.solve_threshold_fast(fit,eta,p,routine[N])
        frame.to_csv(DATA/(stem+".csv"),index=False)
        routine[N].to_csv(DATA/(stem+"_routine.csv"),index=False)
        ti=float(d["t1"])+N/(p.c0*eta)*np.log((float(d["S_star"])-float(d["Sbar"]))/float(d["Sbar"]))
        result={"N":N,"eta":eta,"stem":stem,"t1":float(d["t1"]),"t2":float(d["t2"]),
                "t_end":float(d["clear_time"]),"ti":ti,"qi":1-1/(2*(1-p.beta)),
                "Itcum":float(np.interp(float(d["clear_time"]),frame.t,frame.Cc+frame.Cq))}
        print("CACHE",stem,result["t_end"],flush=True)
        return result
    for j,(N,ths) in enumerate(cases):
        meta["cases"].append([obtain(N,t*N,f"dominance_case{j}_{k}") for k,t in enumerate(ths)])
    meta["fixed_eta"]=[obtain(N,100.,f"dominance_fixed_eta{k}") for k,N in enumerate(populations)]
    cache.write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding="utf-8")
    return meta,cal

def plot_pair(ai,aq,records,td,colors):
    end=max(r["t_end"] for r in records)
    for k,r in reversed(list(enumerate(records))):
        d=pd.read_csv(DATA/(r["stem"]+".csv"))
        t=d.t.to_numpy()
        # 清零终点和三个阶段沿用原求解器；q 仅在控制段由理论时间函数细采样。
        ai.plot(t,d.I,color=colors[k],lw=1.25)
        # 从同一保存轨迹提取启动状态，再按理论时间函数细采样；跳变不跨日插值。
        ss=float(np.interp(r['t1'],t,d.S))
        tau=np.linspace(0,r['t2']-r['t1'],1000)
        sb=.2953*r['N']*(1-.1498)/(.1498*12.8872)
        st=sb+(ss-sb)*np.exp(-12.8872*r['eta']*tau/r['N'])
        qc=1-.2953*r['N']/(.1498*12.8872*st)
        aq.plot(np.r_[0,r['t1'],r['t1']+tau,r['t2'],r['t_end']],
                np.r_[.323,.323,qc,.323,.323],color=colors[k],lw=1.25)
        aq.plot(r["t_end"],.323,"|",color=colors[k],ms=7)
        aq.plot(r["ti"],r["qi"],"o",ms=4,mfc="white",color=colors[k])
    routines=[pd.read_csv(DATA/(r["stem"]+"_routine.csv")) for r in records]
    tg=np.linspace(0,max(x.t.max() for x in routines),1400)
    vals=np.array([np.interp(tg,x.t,x.I,left=x.I.iloc[0],right=1) for x in routines])
    if len(records)>3:
        ai.fill_between(tg,vals.min(axis=0),vals.max(axis=0),color=".7",alpha=.35,lw=0)
    if len(records)==3: ai.plot(routines[0].t,routines[0].I,color=".5",ls="--")
    ai.plot(td.t,td.I,color=".15",lw=1)
    aq.plot(td.t,td.q,color=".15",lw=1)
    ai.set(yscale="log",ylim=(1,2e4),ylabel="$I(t)$",xlim=(0,1.04*end))
    aq.set(ylim=(.29,1.03),ylabel="$q(t)$",xlabel="$t$ (d)",xlim=(0,1.04*end))
    ai.yaxis.set_major_locator(LogLocator(base=10,numticks=5))
    ai.yaxis.set_minor_locator(NullLocator())

def dominance_figures():
    meta,cal=dominance_data();style()
    df=read_csv(XIAN/"xian_control_comparison_timeseries.csv")
    td=df[df.strategy==df.strategy.iloc[0]]
    colors=["#6BADD7","#206FB6","#073068"]
    colorsB=["#9a6b5a","#238b8e","#073068","#206FB6","#6BADD7"]
    fig,axes=plt.subplots(2,2,figsize=(6.27,6.0),sharex="col")
    fig.subplots_adjust(left=.10,right=.98,bottom=.12,top=.79,wspace=.26,hspace=.25)
    plot_pair(axes[0,0],axes[1,0],meta["cases"][0],td,colors)
    plot_pair(axes[0,1],axes[1,1],meta["fixed_eta"],td,colorsB)
    axes[0,0].set_title(r"$N_{\mathrm{eff}}=20000$",pad=62)
    axes[0,1].set_title(r"$\eta=100$",pad=62)
    for ax,records,cs,key in [(axes[0,0],meta["cases"][0],colors,"eta"),(axes[0,1],meta["fixed_eta"],colorsB,"N")]:
        hs=[Line2D([],[],color=c,label=(rf"$\eta={r['eta']:.1f}$" if key=="eta" else rf"$N={r['N']:.0f}$")) for r,c in zip(records,cs)]
        ax.legend(handles=hs,loc="lower center",bbox_to_anchor=(.5,1.025),ncol=2,fontsize=8,handlelength=1.4,columnspacing=.8)
    fig.legend(handles=[Line2D([],[],color=".15",label="TDINN"),Line2D([],[],color=".5",ls="--",label="Routine control")],
               loc="lower center",ncol=2,bbox_to_anchor=(.53,-.005))
    letters(axes.flat);save(fig,"population_threshold_levers")
    fig,axes=plt.subplots(3,2,figsize=(6.27,7.35))
    fig.subplots_adjust(left=.10,right=.98,bottom=.09,top=.89,wspace=.27,hspace=.42)
    for row,records in enumerate(meta["cases"][1:]):
        plot_pair(axes[row,0],axes[row,1],records,td,colors)
        axes[row,0].set_title(rf"$N_{{\mathrm{{eff}}}}={records[0]['N']:.0f}$",fontsize=9)
        axes[row,0].set_xlabel("$t$ (d)")
    handles=[Line2D([],[],color=c,label=l) for c,l in zip(colors,["150 d condition","Cost condition","45 d condition"])]
    handles += [Line2D([],[],color=".15",label="TDINN"),Line2D([],[],color=".5",ls="--",label="Routine")]
    fig.legend(handles=handles,loc="upper center",bbox_to_anchor=(.53,1),ncol=3,fontsize=8)
    letters(axes.flat);save(fig,"critical_population_cases")

def phase_figure():
    sys.path.insert(0,str(ROOT/"c0_sensitivity"))
    import run_c0_sensitivity as m
    I0=json.loads((SNAP/"c0_sensitivity_outputs"/"experiment_parameters.json").read_text(encoding="utf-8"))
    # 从该实验记录读取初值，不从论文展示精度反推。
    def find(d):
        for k,v in d.items():
            if k in ["I0","I0_abs","full_city_I0_reference"] and isinstance(v,(int,float)): return v
        for v in d.values():
            if isinstance(v,dict):
                z=find(v)
                if z is not None:return z
    initial=find(I0)
    if initial is None: raise ValueError("No I0 found in source manifest")
    theta=np.logspace(np.log10(5e-4),np.log10(8e-3),70)
    records=[m.boundary_values(initial,theta=float(th)) for th in theta]
    curves=np.array([[b["c0_trigger"],b["c0_inflection_onset"],b["c0_duration_max"]] for b in records])
    c=np.linspace(3,14,140);th=np.logspace(np.log10(5e-4),np.log10(8e-3),120)
    C,T=np.meshgrid(c,th);D=np.full_like(C,np.nan)
    for j,v in enumerate(th):
        for i,u in enumerate(c):
            if m.background_peak_fraction(u,initial)<=v:continue
            x=m.baseline_constants(u,initial);ss=m.solve_s_star(u,initial,v)
            D[j,i]=np.log((ss-x["s_bar"])/(x["s_c"]-x["s_bar"]))/(u*v)
    np.savez(DATA/"phase_curves.npz",theta=theta,curves=curves,c=c,th=th,duration=D,initial=initial)
    style()
    fig,ax=plt.subplots(figsize=(6.27,4))
    fig.subplots_adjust(left=.11,right=.98,bottom=.16,top=.76)
    cs=ax.contour(C,T,D,levels=[20,40,60,80,100,120],colors="#b9c5cc",linewidths=.7)
    # 每条等值线单独选取远离三条边界与水平参照线的位置，避免自动标签横跨边界。
    positions=[]
    for level,segments,target in zip(cs.levels,cs.allsegs,[4.3,12,12,12,12,12]):
        vertices=np.concatenate([v for v in segments if len(v)])
        point=vertices[np.argmin(abs(vertices[:,0]-target))]
        positions.append(tuple(point))
    labels=ax.clabel(cs,manual=positions,fmt="%d",fontsize=8,inline_spacing=12)
    for label in labels: label.set_rotation(0)
    for k,(col,label) in enumerate(zip([".5","#6fb4d6","#2779b6"],["Trigger boundary",r"Inflection onset ($s^*=2\bar{s}$)",r"Stationary curve ($\partial\Delta t/\partial c_0=0$)"])):
        ax.plot(curves[:,k],theta,color=col,lw=1.5,label=label,ls="--" if k==0 else "-")
    ax.axhline(.002,color=".25",ls=":",lw=.8)
    ax.set(xlabel="$c_0$",ylabel=r"$\theta=\eta/N$",yscale="log",xlim=(3,14),ylim=(5e-4,8e-3))
    ax.legend(loc="lower center",bbox_to_anchor=(.5,1.03),fontsize=9,ncol=1)
    save(fig,"c0_phase_stationary")

def main():
    for p in [OUT,DATA,QA]:p.mkdir(parents=True,exist_ok=True)
    parser=argparse.ArgumentParser();parser.add_argument("--only",default="all");args=parser.parse_args()
    style()
    for name,fun in [("baseline",baseline_q),("xian",xian_figures),("dominance",dominance_figures),("phase",phase_figure)]:
        if args.only in [name,"all"]:fun()
    (QA/"source_hashes.json").write_text(json.dumps(SOURCES,ensure_ascii=False,indent=2),encoding="utf-8")
if __name__=="__main__":main()
