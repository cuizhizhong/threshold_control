import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from core import *
from analysis import setup, CASES, rAc, Ucc, jumpU
plt.rcParams.update({"font.size":9.5,"axes.spines.top":False,"axes.spines.right":False,
                     "axes.grid":True,"grid.color":"#e6e5e1","grid.linewidth":0.6,"savefig.bbox":"tight"})
BLUE,ORANGE,GREEN,RED,PURPLE,GRAY,INK="#2a78d6","#eb6834","#2f9e6e","#c8303a","#7b5bd6","#8a8984","#0b0b0b"
RCOL=["#2a78d6","#2f9e6e","#7b5bd6","#eb6834","#c8303a"]
res=json.load(open("results.json")); ext=json.load(open("extra.json"))
D={k:setup(p) for k,p in CASES.items()}
FIG="figs/"

# ---------- F1 阈值随 b ----------
bb=np.linspace(0.001,0.999,800)
fig,ax=plt.subplots(1,2,figsize=(10,3.6))
a=ax[0]
a.plot(bb,rAc(bb),color=BLUE,lw=2,label=r"$r_{A'}(b)$ (continuity lost)")
a.plot(bb,rhat(bb),color=RED,lw=2,label=r"$\hat r(b)$ (switch leaves $S_{\rm sw}$)")
a.plot(bb,rloc(bb),color=GRAY,lw=1.4,ls="--",label=r"$r_{\rm loc}(b)$ (local, at $S_{\rm sw}$)")
a.plot(bb,rinf(bb),color=PURPLE,lw=1.4,ls="-.",label=r"$r_\infty(b)$ (branch splits)")
a.axhline(2,color=INK,lw=0.9,ls=":"); a.text(0.01,2.05,"default $r=2$",fontsize=8.5,va="bottom")
for k,mk in [("base","o"),("xian","s")]:
    b=D[k]["b"]
    for f in (rAc,rhat): a.plot(b,f(b),mk,mfc="white",mec=INK,ms=5,zorder=5)
a.set_yscale("log"); a.set_ylim(1.8,30); a.set_xlim(0,1)
a.set_yticks([2,3,4,6,10,20,30]); a.set_yticklabels(["2","3","4","6","10","20","30"])
a.set_xlabel(r"$b=\bar S/S_c=(1-\beta)(1-q_0)$"); a.set_ylabel(r"weight ratio $r=w_q/w_c$")
a.legend(frameon=False,fontsize=8,loc="upper left"); a.set_title("(a) Weight thresholds",loc="left",fontsize=10)
a=ax[1]
a.plot(bb,Usw(bb),color=RED,lw=2,label=r"$S_{\rm sw}/S_c$")
a.plot(bb,Ucc(bb),color=BLUE,lw=2,label=r"$U_c=S_{\rm cusp}/S_c$")
for k,mk in [("base","o"),("xian","s")]:
    b=D[k]["b"]; a.plot([b,b],[Ucc(b),Usw(b)],mk,mfc="white",mec=INK,ms=5,zorder=5)
    a.annotate("Baseline" if k=="base" else "Xi'an",(b,Usw(b)),xytext=(4,6),textcoords="offset points",fontsize=8.5)
a.set_xlim(0,1); a.set_ylim(1.95,3.05); a.set_xlabel(r"$b$"); a.set_ylabel(r"state $S/S_c$")
a.legend(frameon=False,fontsize=8.5,loc="upper right"); a.set_title("(b) Switch state and cusp state",loc="left",fontsize=10)
fig.savefig(FIG+"F1_thresholds.pdf"); plt.close(fig)

# ---------- F2 驻点曲线（基准 b） ----------
b=D["base"]["b"]; Usb=Usw(b)
fig,axs=plt.subplots(1,4,figsize=(13,3.5),sharey=True)
for a,(r,title) in zip(axs,[(2.0,"(a) $r=2$: monotone branch"),(3.17,"(b) $r=3.17$: fold, interior jump"),
                            (5.0,"(c) $r=5$: jump from quarantine-only"),(15.0,r"(d) $r=15>r_\infty$: split branch")]):
    uu=np.concatenate([np.linspace(1,Usb,40001)[1:-1]])
    Ub=Us_branch(uu,b,r)
    dU=np.gradient(Ub,uu)
    for mask,ls,lab in [(dU>0,"-","interior local min"),(dU<=0,"--","interior local max")]:
        y=np.where(mask,uu,np.nan); a.plot(Ub,y,color=GRAY,lw=1.2,ls=ls,label=lab)
    Ud=np.linspace(1,6,200)
    a.plot(Ud[Ud>=Usb],Ud[Ud>=Usb],color=GRAY,lw=1.2,ls="-"); a.plot(Ud[Ud<=Usb],Ud[Ud<=Usb],color=GRAY,lw=1.0,ls=":")
    # 最优路径
    Ug=np.linspace(1.0005,6,3000); us=np.array([argmin_exact(U,b,r)[0] for U in Ug])
    j=np.where(np.abs(np.diff(us))>0.02)[0]
    usp=us.copy().astype(float); usp[j+1]=np.nan if False else usp[j+1]
    yy=us.copy(); 
    for jj in j: yy[jj]=np.nan
    a.plot(Ug,yy,color=RED,lw=2.4,label="cost-optimal $u^*(S)$")
    for jj in j: a.plot([Ug[jj],Ug[jj]],[us[jj],us[jj+1]],color=RED,lw=1,ls=(0,(2,2)))
    a.axvline(Usb,color=GRAY,lw=0.8,ls=":")
    a.set_xlim(1,6); a.set_ylim(1,3.2); a.set_title(title,loc="left",fontsize=9.5); a.set_xlabel(r"$S/S_c$")
    if abs(r-3.17)<1e-9:
        ins=a.inset_axes([0.45,0.08,0.52,0.5])
        uu2=np.linspace(1.55,Usb,20001)[:-1]; Ub2=Us_branch(uu2,b,r); d2=np.gradient(Ub2,uu2)
        ins.plot(Ub2,np.where(d2>0,uu2,np.nan),color=GRAY,lw=1.1); ins.plot(Ub2,np.where(d2<=0,uu2,np.nan),color=GRAY,lw=1.1,ls="--")
        Ui=np.linspace(2.250,2.268,1500); ui=np.array([argmin_exact(U,b,r)[0] for U in Ui]); ji=np.where(np.abs(np.diff(ui))>0.02)[0]
        yi=ui.copy()
        for jj in ji: yi[jj]=np.nan
        ins.plot(Ui,yi,color=RED,lw=2)
        for jj in ji: ins.plot([Ui[jj],Ui[jj]],[ui[jj],ui[jj+1]],color=RED,lw=1,ls=(0,(2,2)))
        ins.set_xlim(2.252,2.268); ins.set_ylim(1.62,2.27); ins.tick_params(labelsize=7); ins.grid(False)
        ins.set_xticks([2.255,2.265]); a.indicate_inset_zoom(ins,edgecolor=GRAY)
axs[0].set_ylabel(r"$u=cS/(c_0S_c)=(1-q_0)/(1-q)$"); axs[0].legend(frameon=False,fontsize=7.5,loc="upper left")
axs[0].text(Usb+0.05,1.05,r"$S_{\rm sw}$",color=GRAY,fontsize=8.5)
fig.savefig(FIG+"F2_branches.pdf"); plt.close(fig)

# ---------- F3 相图 ----------
cmap=LinearSegmentedColormap.from_list("y",["#f7f7f4","#bcd4f2","#2a78d6","#0d3a73"])
fig,axs=plt.subplots(1,2,figsize=(11,4.2),constrained_layout=True)
for a,k in zip(axs,["base","xian"]):
    d=D[k]; b=d["b"]; Ust=d["Ustar"]; th=res[k]["thr"]
    Ug=np.linspace(1.002,6.0,260); rg_=np.geomspace(0.1,100,240)
    Y=np.zeros((len(rg_),len(Ug)))
    for i,r in enumerate(rg_):
        for j_,U in enumerate(Ug):
            u=argmin_exact(U,b,r)[0]; Y[i,j_]=(1-u/U)/(1-1/U)
    pc=a.pcolormesh(Ug,rg_,Y,cmap=cmap,vmin=0,vmax=1,shading="auto",rasterized=True)
    g=res[k]["gamma"]; gU=np.array([x["U"] for x in g]); gr=np.array([x["r"] for x in g])
    a.plot(gU,gr,color=RED,lw=2,label=r"jump curve $\Gamma$")
    a.plot([Usw(b),Usw(b)],[0.1,th["rhat"]],color=INK,lw=1.2,ls="-",label=r"continuous switch at $S_{\rm sw}$")
    a.plot(th["Uc"],th["rA"],"o",color=RED,mfc="white",ms=6,zorder=6,label="cusp $(U_c,r_{A'})$")
    a.plot(Usw(b),th["rhat"],"D",color=INK,mfc="white",ms=5,zorder=6)
    a.axvline(Ust,color=INK,lw=0.9,ls="--"); a.text(Ust+0.04,40,r"$S^*/S_c$",fontsize=8.5)
    a.axhline(2,color=INK,lw=0.8,ls=":"); a.text(5.95,2.1,"$r=2$",ha="right",fontsize=8.5)
    a.plot(Ust,th["rC"],"v",color=INK,ms=5,zorder=6)
    a.set_yscale("log"); a.set_xlim(1,6); a.set_ylim(0.1,100)
    ins=a.inset_axes([0.60,0.08,0.37,0.34])
    gm=(gU<Usw(b)+0.04)
    ins.plot(gU[gm],gr[gm],color=RED,lw=1.6); ins.plot([Usw(b),Usw(b)],[0.1,th["rhat"]],color=INK,lw=1)
    ins.plot(th["Uc"],th["rA"],"o",color=RED,mfc="white",ms=5); ins.plot(Usw(b),th["rhat"],"D",color=INK,mfc="white",ms=4)
    w=Usw(b)-th["Uc"]; ins.set_xlim(th["Uc"]-0.6*w,Usw(b)+0.8*w); ins.set_ylim(th["rA"]-0.6*(th["rhat"]-th["rA"]),th["rhat"]+0.9*(th["rhat"]-th["rA"]))
    ins.tick_params(labelsize=7); ins.grid(False); ins.set_facecolor("white")
    ins.text(th["Uc"],th["rA"],"  cusp",fontsize=7,va="top"); ins.text(Usw(b),th["rhat"],r"  $(S_{\rm sw},\hat r)$",fontsize=7,va="bottom",ha="right")
    a.set_xlabel(r"$S/S_c$  (time runs right $\rightarrow$ left)"); a.set_ylabel(r"$r=w_q/w_c$")
    a.set_title(("(a) Baseline" if k=="base" else "(b) Xi'an")+f",  $b={b:.4f}$",loc="left",fontsize=10)
axs[0].legend(frameon=False,fontsize=8,loc="upper left")
cb=fig.colorbar(pc,ax=axs,shrink=0.85); cb.set_label(r"$y=(1-c^*/c_0)/(1-S_c/S)$")
fig.savefig(FIG+"F3_phase.pdf",dpi=200); plt.close(fig)

# ---------- F4/F5 代表权重下的控制（状态与时间） ----------
REP={"base":[0.5,2.0,3.17,5.0,20.0],"xian":[0.5,2.0,2.63,5.0,20.0]}
def profile(d,r,n=6001):
    b=d["b"]; Ust=d["Ustar"]; Ug=np.linspace(1,Ust,n)
    us=np.array([1.0]+[argmin_exact(U,b,r)[0] for U in Ug[1:]])
    sc=1/(d["c0"]*d["th"])
    integ=1/(us-b); cum=np.concatenate([[0],np.cumsum(0.5*(integ[1:]+integ[:-1])*np.diff(Ug))])
    t=sc*(cum[-1]-cum)
    jumps=np.where(np.abs(np.diff(us))>max(0.02,30*(Ust-1)/n))[0]
    return Ug,us,t,jumps
def brk(x,y,jumps):
    x=x.astype(float).copy(); y=y.astype(float).copy()
    for j in jumps: y[j]=np.nan
    return x,y
fig,axs=plt.subplots(2,2,figsize=(10.5,6.6),constrained_layout=True)
fig2,axs2=plt.subplots(2,2,figsize=(10.5,6.6),constrained_layout=True)
for row,k in enumerate(["base","xian"]):
    d=D[k]; q0=d["q0"]; Ust=d["Ustar"]
    for ci,r in enumerate(REP[k]):
        Ug,us,t,jumps=profile(d,r); x=us/Ug; q=1-(1-q0)/us
        lab=f"$r={r:g}$"
        for a,y in [(axs[row,0],x),(axs[row,1],q)]:
            X_,Y_=brk(Ug,y,jumps); a.plot(X_,Y_,color=RCOL[ci],lw=1.8,label=lab)
            for j in jumps: a.plot([Ug[j],Ug[j]],[y[j],y[j+1]],color=RCOL[ci],lw=0.9,ls=(0,(2,2)))
        for a,y in [(axs2[row,0],x),(axs2[row,1],q)]:
            X_,Y_=brk(t,y,jumps); a.plot(X_,Y_,color=RCOL[ci],lw=1.8,label=lab)
            for j in jumps: a.plot([t[j],t[j]],[y[j],y[j+1]],color=RCOL[ci],lw=0.9,ls=(0,(2,2)))
    nm="Baseline" if k=="base" else "Xi'an"
    for a in axs[row]: a.set_xlim(Ust,1); a.axvline(Usw(d["b"]),color=GRAY,lw=0.8,ls=":"); a.set_xlabel(r"$S/S_c$  (time $\rightarrow$)")
    axs[row,0].set_ylabel(r"$c^*/c_0$"); axs[row,1].set_ylabel(r"$q^*$")
    axs[row,0].set_title(f"({'a' if row==0 else 'c'}) {nm}: contact rate",loc="left",fontsize=10)
    axs[row,1].set_title(f"({'b' if row==0 else 'd'}) {nm}: quarantine fraction",loc="left",fontsize=10)
    for a in axs2[row]: a.set_xlabel(r"$t-t_1$ (d)")
    axs2[row,0].set_ylabel(r"$c^*/c_0$"); axs2[row,1].set_ylabel(r"$q^*$")
    axs2[row,0].set_title(f"({'a' if row==0 else 'c'}) {nm}: contact rate",loc="left",fontsize=10)
    axs2[row,1].set_title(f"({'b' if row==0 else 'd'}) {nm}: quarantine fraction",loc="left",fontsize=10)
    axs[row,0].legend(frameon=False,fontsize=8,loc="center left",bbox_to_anchor=(0.0,0.42)); axs2[row,0].legend(frameon=False,fontsize=8,loc="lower right")
fig.savefig(FIG+"F4_profiles_state.pdf"); fig2.savefig(FIG+"F5_profiles_time.pdf"); plt.close(fig); plt.close(fig2)

# ---------- F6 指标随 r ----------
fig,axs=plt.subplots(1,4,figsize=(13.5,3.4),constrained_layout=True)
for k,col,mk in [("base",BLUE,"-"),("xian",ORANGE,"-")]:
    M=res[k]["metrics"]; r=np.array([m["r"] for m in M]); th=res[k]["thr"]; nm="Baseline" if k=="base" else "Xi'an"
    dt=np.array([m["dt"] for m in M]); dtq=M[0]["dt_QO"]
    J=np.array([m["J"] for m in M]); JQ=np.array([m["J_QO"] for m in M])
    fr=np.array([m["front"] for m in M]); dI=np.array([m["dI"] for m in M])
    tot=CASES[k]["QO_total"]
    axs[0].plot(r,dt/dtq,color=col,lw=1.8,label=nm)
    axs[1].plot(r,J/JQ,color=col,lw=1.8,label=nm)
    axs[2].plot(r,fr/dt,color=col,lw=1.8,label=nm)
    axs[3].plot(r,100*dI/tot,color=col,lw=1.8,label=nm)
    for a in axs:
        for key,ls in [("rA",":"),("rhat","--"),("rC","-.")]:
            a.axvline(th[key],color=col,lw=0.8,ls=ls,alpha=0.8)
for a in axs: a.set_xscale("log"); a.set_xlabel(r"$r=w_q/w_c$"); a.axvline(2,color=INK,lw=0.6)
axs[0].set_ylabel(r"$\Delta t/\Delta t_{\rm QO}$"); axs[0].set_title("(a) Control duration",loc="left",fontsize=10)
axs[1].set_ylabel(r"$J_{\min}/J_{\rm QO}$"); axs[1].set_title("(b) Cost relative to quarantine-only",loc="left",fontsize=10)
axs[2].set_ylabel("share of duration"); axs[2].set_title("(c) Quarantine-only segment",loc="left",fontsize=10)
axs[3].set_ylabel(r"extra infections (% of QO total)"); axs[3].set_title("(d) Extra cumulative infections",loc="left",fontsize=10)
axs[0].legend(frameon=False,fontsize=8.5)
fig.savefig(FIG+"F6_metrics.pdf"); plt.close(fig)

# ---------- F7 时长前沿 ----------
fig,axs=plt.subplots(1,2,figsize=(10,3.6),constrained_layout=True)
for a,k in zip(axs,["base","xian"]):
    pts=np.array(ext["front"][k]); pts=pts[np.argsort(pts[:,1])]
    d=D[k]; M=[m for m in res[k]["metrics"] if abs(m["r"]-2)<1e-12][0]
    a.plot(pts[:,1],pts[:,2]/M["J"],color=RED,lw=1.8,label=r"$V(T)=\min\{J:\Delta t=T\}$")
    a.plot(M["dt"],1,"o",color=INK,ms=5,label="cost-optimal (no duration constraint)")
    a.plot(M["dt_QO"],M["J_QO"]/M["J"],"s",color=BLUE,ms=5,label="quarantine-only")
    a.plot(pts[-1,1],pts[-1,2]/M["J"],"^",color=GREEN,ms=6,label="contact-reduction-only")
    a.set_xscale("log"); a.set_xlabel(r"control duration $T$ (d)"); a.set_ylabel(r"$V(T)/J_{\min}$")
    a.set_title("(a) Baseline" if k=="base" else "(b) Xi'an",loc="left",fontsize=10)
axs[0].legend(frameon=False,fontsize=8)
fig.savefig(FIG+"F7_frontier.pdf"); plt.close(fig)
print("figures done")
