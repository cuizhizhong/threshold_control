"""沿用原脚本的绘图语句，只调整合图布局；不改原脚本、不拟合数据。

图 14/18 直接编译原 panel_A / plot_B 的绘图代码段，注入旧缓存与目标轴。
原程序的求解和文件输出入口不执行。缺失的八成员包络按原函数恢复一次。
"""
from pathlib import Path
import ast
import hashlib
import json
import pickle
import sys
from types import SimpleNamespace
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator, StrMethodFormatter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE.parent / "figures" / "style_restored"
QA = HERE / "qa"
DATA = HERE / "data"
OLD_DATA = HERE.parent / "revision_v4" / "data"
SNAP = ROOT / "archive_unused" / "generated_snapshots"
XIAN = SNAP / "xian_control_comparison_main"
SKILL = Path.home() / ".codex" / "skills" / "nature-figure" / "scripts"
sys.path.insert(0, str(SKILL))
from audit_panel_alignment import require_matplotlib_panel_alignment
sys.path.insert(0, str(ROOT / "xian_control_comparison"))
import paper_plot_style as pps
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "STIXGeneral"],
                     "pdf.fonttype": 42, "svg.fonttype": "none"})
if not hasattr(np, "trapz"):
    np.trapz = np.trapezoid

META = json.loads((OLD_DATA / "dominance_metadata.json").read_text(encoding="utf-8"))
RECORDS = [r for group in META["cases"] for r in group] + META["fixed_eta"]
CONTENT_CHECKS = []


def source(path):
    return (ROOT / path).read_text(encoding="utf-8-sig")


def functions_from(path, names, env):
    tree = ast.parse(source(path))
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert len(nodes) == len(names)
    text = "from __future__ import annotations\n" + "\n".join(ast.unparse(n) for n in nodes)
    exec(compile(text, str(ROOT / path), "exec"), env)


def original_environment(path):
    env = dict(np=np, pd=pd, plt=plt, Line2D=Line2D, Patch=Patch,
               MaxNLocator=MaxNLocator, StrMethodFormatter=StrMethodFormatter)
    # 只取不带调用的常量和原 rcParams；排除导入、I/O、求根和主程序。
    for n in ast.parse(source(path)).body:
        if isinstance(n, ast.Assign) and not any(isinstance(x, ast.Call) for x in ast.walk(n)):
            try:
                exec(ast.unparse(n), env)
            except NameError:
                pass
        if isinstance(n, ast.Expr) and ast.unparse(n).startswith("plt.rcParams.update("):
            exec(ast.unparse(n), env)
    return env


def cached_solution(N, eta):
    rec = next(r for r in RECORDS if np.isclose(r["N"], N, rtol=1e-10)
               and np.isclose(r["eta"], eta, rtol=1e-10))
    p = SimpleNamespace(N=N, beta=.1498, gamma=.2953, c0=12.8872, q0=.323)
    sb = p.gamma * N * (1-p.beta) / (p.beta*p.c0)
    # 从原缓存的拐点解析恒等式恢复 S*，不从低密度点重新近似启动状态。
    ss = sb * (1 + np.exp(p.c0*eta/N*(rec["ti"]-rec["t1"])))
    d = dict(t1=rec["t1"], t2=rec["t2"], clear_time=rec["t_end"],
             Sbar=sb, S_star=ss, Sc=p.gamma*N/(p.beta*p.c0*(1-p.q0)))
    df = pd.read_csv(OLD_DATA / (rec["stem"] + ".csv"))
    assert np.all(np.diff(df.t) > 0)
    return p, df, d


def cached_prep(N):
    rec = next(r for r in RECORDS if np.isclose(r["N"], N, rtol=1e-10))
    return None, None, pd.read_csv(OLD_DATA / (rec["stem"] + "_routine.csv"))


def recovery_cache(env):
    cache = DATA / "original_reference_cache.pkl"
    if cache.exists():
        return pickle.loads(cache.read_bytes())
    sys.path.insert(0, str(ROOT / "xian_control_comparison" / "threshold_landscape_analysis"))
    import xian_control_comparison as xcc
    import threshold_landscape_analysis as tla
    I0 = .00100662823352  # 原 panels.py 的固定绝对初值，不重新拟合。
    def solve(N, td=False):
        p = tla.LandscapeParams(N=float(N))
        fit = xcc.InitialFit(S0=N-I0, I0=I0, R0_initial=0., objective=float("nan"),
                            raw_rmse=float("nan"), residual_type="fixed_I0_abs")
        return tla.solve_time_control_param("TDINN" if td else "routine", fit, p,
                                            xcc.c_real if td else tla.c_const(p),
                                            xcc.q_real if td else tla.q_const(p))
    td = solve(13_163_000., True)
    end = 1.05*max(r["t_end"] for r in META["fixed_eta"])
    tg = np.linspace(0, end, 1400)
    populations = np.geomspace(META["fixed_eta"][0]["N"], META["fixed_eta"][-1]["N"], 8)
    routine = [solve(N) for N in populations]
    stack = np.vstack([np.interp(tg, df.t, df.I, left=np.nan, right=np.nan) for df in routine])
    stack = np.where(np.isfinite(stack), stack, 1.)
    result = dict(td=td, tend=end, tg=tg, Nrib=populations,
                  rlo=np.maximum(stack.min(axis=0), 1.), rhi=stack.max(axis=0),
                  rep_r={float(populations[i]): routine[i][["t", "I"]].to_dict("list") for i in [0, -1]})
    cache.write_bytes(pickle.dumps(result))
    print("RECOVERED original TDINN reference and 8-member routine envelope; no refit", flush=True)
    return result


def original_A_code(env):
    functions_from("xian_control_comparison/effective_population_sensitivity/plot_eta_80_100_150_inflection.py",
                   ["build_plot_series", "compute_inflection"], env)
    functions_from("xian_dom/panels.py", ["cumulative_at_clearance"], env)
    env.update(solve_threshold=cached_solution, prep=cached_prep,
               TH=dict(zip(["dur150", "cost", "dur45"], META["theta"])))
    fn = next(n for n in ast.parse(source("xian_dom/panels.py")).body
              if isinstance(n, ast.FunctionDef) and n.name == "panel_A")
    body = []
    for n in fn.body:
        if isinstance(n, ast.Assign) and ast.unparse(n).startswith("pdf_path ="):
            break
        if isinstance(n, ast.Assign) and "plt.subplots(" in ast.unparse(n):
            n = ast.parse("fig, (axi, axq) = _target").body[0]
        body.append(n)
    fn.body = body
    exec(compile("from __future__ import annotations\n"+ast.unparse(fn), "original_panel_A", "exec"), env)


def original_B_code(env, ref):
    functions_from("xian_dom/plot_B.py", ["threshold_q_parts", "cumulative_at_cached_clearance"], env)
    roles = ["clear", "cum", "dur45", "cost", "dur150"]
    D = {k: ref[k] for k in ["tend", "tg", "rlo", "rhi", "rep_r"]}
    D.update(roles=roles, tdinn_I=ref["td"][["t", "I"]].to_dict("list"),
             tdinn_q=ref["td"][["t", "q"]].to_dict("list"), built={})
    for role, rec in zip(roles, META["fixed_eta"]):
        p, df, d = cached_solution(rec["N"], 100.)
        s = env["build_plot_series"](100., p, df, d, rec["ti"], ref["tend"])
        D["built"][role] = dict(t=s.t.to_numpy(), I=s.I.to_numpy(), q=s.q.to_numpy(),
                                N=rec["N"], ti=rec["ti"], qi=rec["qi"])
    env["D"] = D
    text = source("xian_dom/plot_B.py")
    text = text[text.index("roles = [r for r in D"):text.index('fig.savefig(OUT / "fig_panel_B.pdf"')]
    nodes = ast.parse(text).body
    for i, n in enumerate(nodes):
        if isinstance(n, ast.Assign) and "plt.subplots(" in ast.unparse(n):
            nodes[i] = ast.parse("fig, (axi, axq) = _target").body[0]
    return compile(ast.unparse(ast.Module(body=nodes, type_ignores=[])), "original_panel_B", "exec")


def label(ax, letter):
    for txt in list(ax.texts):
        if txt.get_text() in ["(a)", "(b)"]:
            txt.remove()
    ax.text(-.008, 1.02, f"({letter})", transform=ax.transAxes,
            fontsize=9, weight="bold", ha="left", va="bottom", color="#222")


def save(fig, name):
    fig.canvas.draw()
    require_matplotlib_panel_alignment(fig, json_out=QA/(name+".alignment.json"),
                                       tolerance_pt=1.5, gutter_tolerance_pt=1.5, strict=True)
    fig.savefig(OUT/(name+".pdf"))
    fig.savefig(OUT/(name+".svg"))
    fig.savefig(OUT/(name+".png"), dpi=300)
    plt.close(fig)
    print("EXPORTED", name, flush=True)


def arrange_pair(ai, aq, letters, *, population=False):
    def fingerprint(ax):
        marks=[]
        for line in ax.lines:
            values=np.asarray(line.get_xydata(),dtype=float).tobytes()
            marks.append(("line",hashlib.sha256(values).hexdigest(),str(line.get_color()),
                          line.get_linewidth(),line.get_linestyle(),line.get_alpha()))
        for coll in ax.collections:
            marks.append(("collection",hashlib.sha256(np.asarray(coll.get_offsets()).tobytes()).hexdigest(),
                          coll.get_facecolors().tolist(),coll.get_edgecolors().tolist(),
                          coll.get_linewidths().tolist(),coll.get_alpha()))
        for patch in ax.patches:
            marks.append(("patch",patch.get_path().vertices.tolist(),
                          patch.get_facecolor(),patch.get_edgecolor()))
        return marks
    all_axes=[ai,aq,*aq.child_axes]
    before=[fingerprint(ax) for ax in all_axes]
    label(ai, letters[0]); label(aq, letters[1])
    for ax in [ai, aq]:
        ax.tick_params(labelsize=7.2, pad=2)
        ax.xaxis.label.set_size(8.5); ax.yaxis.label.set_size(8.5)
    aq.set_yticks(np.arange(.3,1.01,.1))
    for text in aq.texts:
        if text.get_text() == r"$q_0$":
            text.set_position((.90*aq.get_xlim()[1], .335))
    # 图例保留原有全部条目；只在窄列中折行、调整文字大小和位置。
    leg = ai.get_legend()
    handles = leg.legend_handles
    texts = [t.get_text() for t in leg.get_texts()]
    if population:
        texts = [t.replace("  ($N", "\n($N") for t in texts]
    leg.remove()
    ai.legend(handles, texts, loc="lower right", bbox_to_anchor=(1, 1.13),
              ncol=2, fontsize=7.3, handlelength=1.7, columnspacing=.8, borderaxespad=0)
    # 内嵌小图仍位于 q 轴右上角。加宽内嵌区域，不缩小文字或删数据。
    inset = aq.child_axes[0]
    inset.set_axes_locator(None)
    b = aq.get_position()
    inset.set_position([b.x0+(.38 if population else .48)*b.width,
                        b.y0+.56*b.height, (.60 if population else .50)*b.width, .40*b.height])
    inset.xaxis.label.set_size(9); inset.yaxis.label.set_size(10.5)
    inset.tick_params(labelsize=6.2)
    for t in inset.texts:
        t.set_fontsize(max(6.0, t.get_fontsize()))
        t.set_linespacing(1.15)
        x,y=t.get_position()
        t.set_y(y+.035*inset.get_ylim()[1])
    if population:
        inset.set_xlim(-.5,6.5)
        for t in inset.texts:
            if t.get_text().startswith("TDINN"):
                t.set_x(6.4)
            elif t.get_text() in ["945","2,097"]:
                t.set_y(2096.76+.055*inset.get_ylim()[1])
    assert before==[fingerprint(ax) for ax in all_axes], "合图改变了原绘图对象"
    CONTENT_CHECKS.append({"panels":letters,"population_family":population,
                           "curve_marker_reference_style_unchanged":True,
                           "I_lines":len(ai.lines),"I_marker_groups":len(ai.collections),
                           "q_lines":len(aq.lines),"q_marker_groups":len(aq.collections),
                           "inset_bar_values":[p.get_height() for p in inset.patches],
                           "I_ylim":ai.get_ylim(),"q_ylim":aq.get_ylim()})


def dominance():
    env = original_environment("xian_dom/panels.py")
    original_A_code(env)
    ref = recovery_cache(env)
    benv = original_environment("xian_dom/plot_B.py")
    benv["build_plot_series"] = env["build_plot_series"]
    bcode = original_B_code(benv, ref)
    fig, axes = plt.subplots(2, 2, figsize=(6.27, 4.80), sharex="col")
    fig.subplots_adjust(left=.075, right=.985, bottom=.11, top=.72, wspace=.24, hspace=.40)
    env["_target"] = (fig, (axes[0, 0], axes[1, 0]))
    env["panel_A"](N=20000., td=ref["td"])
    benv["_target"] = (fig, (axes[0, 1], axes[1, 1]))
    exec(bcode, benv)
    arrange_pair(axes[0, 0], axes[1, 0], "ac")
    arrange_pair(axes[0, 1], axes[1, 1], "bd", population=True)
    save(fig, "population_threshold_levers")
    original_environment("xian_dom/panels.py")
    fig, axes = plt.subplots(3, 2, figsize=(6.27, 7.60))
    fig.subplots_adjust(left=.075, right=.985, bottom=.075, top=.86, wspace=.24, hspace=.82)
    for row, records in enumerate(META["cases"][1:]):
        env["_target"] = (fig, tuple(axes[row]))
        env["panel_A"](N=records[0]["N"], td=ref["td"])
        arrange_pair(*axes[row], chr(97+2*row)+chr(98+2*row))
        axes[row, 0].set_xlabel(r"time $t$ (days)")
        axes[row, 0].text(.99, 1.08, rf"$N_{{\rm eff}}={records[0]['N']:,.0f}$",
                          transform=axes[row, 0].transAxes, ha="right", fontsize=8)
    save(fig, "critical_population_cases")
    (QA/"original_artist_preservation.json").write_text(json.dumps(CONTENT_CHECKS,indent=2),encoding="utf-8")


def xian():
    frame = pd.read_csv(XIAN/"xian_control_comparison_timeseries.csv")
    obs = pd.read_csv(XIAN/"xian_observed_data_processed.csv")
    frames = [sub for _, sub in frame.groupby("strategy", sort=False)]
    td = frames[0]
    # 图 9 保留上一版的全部几何与画法，只删除图例和英文标题。
    sys.path.insert(0, str(HERE.parent/"revision_v4"))
    import plot_revisions as old
    old.style()
    fig, axes = plt.subplots(1, 2, figsize=(6.27, 3.25))
    fig.subplots_adjust(left=.09, right=.96, bottom=.20, top=.77, wspace=.27)
    for ax, model, col in zip(axes, ["Cc", "Cq"], ["community_new", "quarantine_new"]):
        y = np.diff(np.interp(np.arange(41), td.t, td[model]))
        ax.plot(obs.t, y, color=old.COL[0])
        ax.scatter(obs.t, obs[col], s=13, facecolors="white", edgecolors=".2", linewidths=.7)
        ax.set(xlim=(-.5,39.5), ylim=(0,None), ylabel="Daily new cases", xlabel="Date")
        ax.set_xticks([0,12,24,39], ["Dec 09","Dec 21","Jan 02","Jan 17"])
    old.letters(axes)
    save(fig, "xian_observed_fit")
    with pps.paper_style_context():
        fig = plt.figure(figsize=(6.27, 6.10))
        gs = fig.add_gridspec(3,2,left=.10,right=.985,bottom=.09,top=.90,wspace=.30,hspace=.44)
        axes = [fig.add_subplot(gs[0,:]),fig.add_subplot(gs[1,0]),fig.add_subplot(gs[1,1]),
                fig.add_subplot(gs[2,0]),fig.add_subplot(gs[2,1])]
        xend = frame.t.max()
        details = pd.read_csv(XIAN/"xian_flat_control_details.csv").set_index("metric")["value"]
        t1, t2 = float(details["t1"]), float(details["t2_numeric"])
        for sub in frames:
            spec = pps.STRATEGY_STYLES[sub.strategy.iloc[0]]
            for ax, y in zip(axes,[sub.I,sub.c,sub.q,sub.Cc+sub.Cq,sub.Rt]):
                ax.plot(sub.t, y, color=spec["color"], ls=spec["linestyle"], lw=spec["linewidth"], zorder=3)
        for ax in axes:
            ax.axvline(obs.t.iloc[-1], color=pps.COLORS["light_gray"],lw=.8,ls=(0,(1.2,2)),alpha=.72,zorder=0)
        for ax in [axes[i] for i in [0,1,2,4]]:
            for time in [t1,t2]:
                ax.axvline(time,color=pps.COLORS["dark_red"],lw=.9,ls=(0,(3,2)),alpha=.32,zorder=0)
        for i, (ax, ylabel) in enumerate(zip(axes,[r"$I(t)$",r"$c(t)$",r"$q(t)$",r"$I_{t_{\rm cum}}(t)$",r"$R_e(t)$"])):
            ax.set(xlim=(0,xend),xlabel=r"time $t$ (days)",ylabel=ylabel)
            pps.style_axis(ax, f"({chr(97+i)})")
            for text in ax.texts:
                if text.get_text() == f"({chr(97+i)})":
                    text.set_position((-.01,1.03))
        axes[0].set_yscale("log"); axes[0].set_ylim(1,1.08*frame.I.max()); axes[0].set_xlabel("")
        axes[0].axhline(26326,color=pps.COLORS["gray"],lw=.9,ls="--",alpha=.7,zorder=1)
        axes[0].text(.985,26326*1.1,r"$\eta$",transform=axes[0].get_yaxis_transform(),ha="right",va="bottom",fontsize=7.4,color=pps.COLORS["gray"])
        axes[3].set_yscale("symlog",linthresh=100); axes[3].set_ylim(0,1.15*(frame.Cc+frame.Cq).max())
        axes[3].scatter(obs.t,obs.total_cum,s=14,color=pps.COLORS["coral"],edgecolors="white",linewidths=.5,zorder=6)
        axes[3].yaxis.label.set_size(11)
        axes[4].set_ylim(0,max(1.2,1.08*frame.Rt.max()))
        axes[4].axhline(1,color=pps.COLORS["dark_red"],lw=1.25,ls=(0,(4,2)),alpha=.82,zorder=1)
        axes[4].text(.985,1.05,r"$R_e(t)=1$",transform=axes[4].get_yaxis_transform(),ha="right",va="bottom",fontsize=7.4,color=pps.COLORS["dark_red"])
        fig.legend(handles=pps.strategy_handles(include_observed=True), loc="upper center",ncol=4,bbox_to_anchor=(.54,.995),columnspacing=.9)
        save(fig,"xian_strategy_process")


def phase():
    sys.path.insert(0,str(ROOT/"c0_sensitivity"))
    import run_c0_sensitivity as original
    original.configure_plot_style()
    data = np.load(OLD_DATA/"phase_curves.npz")
    C,T = np.meshgrid(data["c"],data["th"])
    fig,ax = plt.subplots(figsize=(6.27,4.55))
    fig.subplots_adjust(left=.11,right=.98,bottom=.13,top=.97)
    cs = ax.contour(C,T,data["duration"],levels=[20,40,60,80,100,120],colors="#c2ccd4",linewidths=.7,zorder=1)
    ax.set(yscale="log",xlim=(3,14),ylim=(5e-4,8e-3))
    positions=[]
    for level,segments,target in zip(cs.levels,cs.allsegs,[4.5,12,12,12,12,12]):
        vertices=np.concatenate([v for v in segments if len(v)])
        positions.append(tuple(vertices[np.argmin(abs(vertices[:,0]-target))]))
    ax.clabel(cs,fmt="%d",fontsize=7.2,inline=True,manual=positions)
    for i,(color,lw,ls,legend) in enumerate([
        ("#8a8a8a",1.6,"--","trigger boundary"),
        ("#6fb4d6",1.9,"-",r"inflection onset ($s^*=2\bar s$)"),
        ("#2779b6",1.9,"-",r"Stationary curve ($\partial\Delta t/\partial c_0=0$)")]):
        ax.plot(data["curves"][:,i],data["theta"],color=color,lw=lw,ls=ls,label=legend,zorder=3)
    boundaries = original.boundary_values(float(data["initial"]))
    ax.axhline(.002,color="#333333",lw=.9,ls=":",zorder=2)
    for role,key in [("near-trigger","c0_trigger"),("post-inflection","c0_inflection_onset"),("max-duration","c0_duration_max")]:
        ax.scatter([boundaries[key]],[.002],s=36,color=original.C0_COLORS[role],edgecolor="white",linewidth=.8,zorder=6)
    ax.text(14*.985,.002*1.06,r"$\theta=0.002$",ha="right",va="bottom",fontsize=8)
    ax.set(xlabel=r"$c_0$",ylabel=r"$\theta=\eta/N$",yscale="log",xlim=(3,14),ylim=(5e-4,8e-3))
    ax.legend(loc="upper right",fontsize=8)
    ax.tick_params(length=3.2,width=.75)
    save(fig,"c0_phase_stationary")


if __name__ == "__main__":
    for p in [OUT,QA,DATA]:
        p.mkdir(parents=True,exist_ok=True)
    selected = sys.argv[1:]
    for name, function in [("xian",xian),("dominance",dominance),("phase",phase)]:
        if not selected or name in selected:
            function()
