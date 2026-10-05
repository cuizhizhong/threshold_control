"""从本轮已验收输出生成局部出版文案；不拟合、不求根、不覆盖主稿。"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

ORDER = ("contact_only", "alpha_0.5", "quarantine_only", "minimum_cost")
NAMES = {"contact_only": "仅减少接触", "alpha_0.5": r"显式族 $\alpha=0.5$",
         "quarantine_only": "仅隔离", "minimum_cost": "类内最小成本"}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_rows(path):
    with open(path, encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    converted = []
    for row in rows:
        result = {}
        for key, value in row.items():
            try:
                result[key] = float(value)
            except (ValueError, TypeError):
                result[key] = value
        converted.append(result)
    return converted


def passed(value):
    return value is True or value == 1 or str(value).lower() in {"true", "1", "passed"}


def value(row, *keys):
    for key in keys:
        if key in row and row[key] is not None:
            number = float(row[key])
            if not math.isfinite(number):
                raise ValueError(f"出版字段不是有限数值：{key}")
            return number
    raise KeyError(f"缺少出版字段：{keys}")


def fixed(number, digits=2):
    number = float(number)
    if not math.isfinite(number):
        raise ValueError("不能将失败或非有限结果写入正文。")
    return f"{number:.{digits}f}"


def comparison_rows(res, case):
    raw_rows = load_rows(res / f"compare_{case}.csv")
    rows = {row["strategy"]: row for row in raw_rows}
    if len(raw_rows) != 4 or set(rows) != set(ORDER):
        raise ValueError(f"{case} 的比较表必须恰含四种同条件分配，不得混入 TDINN。")
    return rows


def comparison_table(baseline, xian):
    lines = [r"\begingroup", r"\begin{table}[htbp]", r"\centering\small",
             r"\setlength{\tabcolsep}{3.5pt}", r"\renewcommand{\arraystretch}{1.25}",
             r"\begin{threeparttable}",
             r"\caption{相同阈值与启动、退出要求下四种分配的结果（$w_c=1,w_q=2$）}",
             r"\label{tab:joint:compare}",
             r"\begin{tabularx}{\linewidth}{@{}>{\raggedright\arraybackslash}Xccccc@{}}",
             r"\toprule",
             r"分配 & \shortstack{控制时长\\$\Delta t$（d）} & \shortstack{清零时刻\\$t_{\rm end}$（d）} & \shortstack{总累计\\新增感染} & \shortstack{控制期新增\\隔离易感者} & $J$（d）\\",
             r"\midrule"]
    for case, rows in (("baseline", baseline), ("xian", xian)):
        if case == "baseline":
            lines.append(r"\multicolumn{6}{@{}l}{基准参数：$N=763$，$\eta=0.05N$；新增人数单位为人}\\")
        else:
            lines.extend([r"\midrule", r"\multicolumn{6}{@{}l}{西安参数：$\eta=0.002N$；新增人数单位为 $10^6$ 人}\\"])
        for key in ORDER:
            row = rows[key]
            scale, digits = (1, 1) if case == "baseline" else (1e6, 4)
            cells = [NAMES[key], fixed(value(row, "duration_state", "duration")), fixed(row["t_end"]),
                     fixed(value(row, "total_infections_to_clearance", "total_infections") / scale, digits),
                     fixed(value(row, "Sq_increment_plateau", "plateau_new_Sq") / scale, digits),
                     fixed(value(row, "J_state", "J"), 4)]
            lines.append(" & ".join(cells) + r"\\")
    lines.extend([r"\bottomrule", r"\end{tabularx}",
                  r"\begin{tablenotes}[flushleft]\footnotesize",
                  r"\item 注：每组沿用同一完整初值、首次上升至 $I=\eta$ 的启动规则和 $S=S_c$ 的退出目标，各自恢复常规后在 $I$ 下降至 $1$ 时终止。累计新增感染不包含初始感染者；新增隔离易感者只统计控制期。$J$ 为式\eqref{eq:cost:J}的二次成本，不由线性 $J_c,J_q$ 加总。西安参数及未取整初值见第\ref{sec:xian}节；表内单位和显示精度按行组区分。",
                  r"\end{tablenotes}", r"\end{threeparttable}", r"\end{table}", r"\endgroup"])
    return "\n".join(lines)


def comparison_text(baseline, xian, changes):
    q, m = baseline["quarantine_only"], baseline["minimum_cost"]
    text = (
        r"在同一完整初值、阈值和退出目标下，比较仅减少接触、显式族 $\alpha=0.5$、仅隔离和类内最小二次成本四种分配。"
        r"基准参数沿用图\ref{fig:scenario1:single-sim}，西安参数沿用第\ref{sec:xian}节的未取整初值；两组均取 $w_c=1,w_q=2$。"
        r"名义时间控制由状态积分预先确定，再输入完整仓室方程核查，不随数值积分的实时状态纠偏。结果见表\ref{tab:joint:compare}及图\ref{fig:joint:compare}。"
        + "\n\n"
        + f"基准参数下，类内最小成本为 $J_{{\\min}}\\approx{fixed(value(m, 'J_state', 'J'), 4)}$，控制时长约为 ${fixed(value(m, 'duration_state', 'duration'), 4)}$ d；"
        + f"仅隔离的对应值为 ${fixed(value(q, 'J_state', 'J'), 4)}$ 和 ${fixed(value(q, 'duration_state', 'duration'), 4)}$ d。"
        + f"总累计新增感染分别约为 ${fixed(value(m, 'total_infections_to_clearance', 'total_infections'), 1)}$ 和 ${fixed(value(q, 'total_infections_to_clearance', 'total_infections'), 1)}$ 人。"
        + f"相对仅隔离，成本降低约 ${fixed(-changes['cost_change_pct'], 1)}\\%$，控制时间增加约 ${fixed(changes['duration_change_pct'], 1)}\\%$，总累计新增感染增加约 ${fixed(changes['total_infections_change_pct'], 1)}\\%$。"
        + r"最低成本分配的控制时间更长、累计新增感染更多、控制期新增隔离易感者更少，与式\eqref{eq:joint:cumulative}--\eqref{eq:joint:quarantine}的排序一致。"
        + "\n\n"
        + r"感染人数上限约束的是 $I$，不是 $I+I_q$。在各自 $[0,t_{\rm end}]$ 上，"
        + f"基准参数下仅隔离与仅减少接触的 $\\max(I+I_q)/\\eta$ 分别约为 ${fixed(q['peak_I_plus_Iq_over_eta'])}$ 和 ${fixed(baseline['contact_only']['peak_I_plus_Iq_over_eta'])}$；"
        + f"西安参数下相应为 ${fixed(xian['quarantine_only']['peak_I_plus_Iq_over_eta'])}$ 和 ${fixed(xian['contact_only']['peak_I_plus_Iq_over_eta'])}$。"
        + r"这些是观察区间内的现存感染人数指标，不是实际医疗或 ICU 占用；图中的水平 $1$ 只作归一化参照，不表示 $(I+I_q)/\eta\le1$ 得到保证。"
    )
    return text + "\n\n" + comparison_table(baseline, xian)


def capacity_text(capacity):
    item = capacity["baseline"]
    metric = item.get("metrics", item)
    point = item["point"]
    xian = capacity["xian"]
    xian_metric = xian.get("metrics", xian)
    return (
        r"\def\jointcapacitypostexitdays{" + f"{float(item['plot_viewport']['post_exit_days']):g}" + "}\n"
        + r"图\ref{fig:joint:capacity}将能力平面分成至少一种单控制可行、两种单控制均不可行但联合可行、规定触发状态下不可行三个区域。"
        r"仅隔离可行要求 $q_{\rm cap}\ge q_{\max}$，仅减少接触可行要求 $c_{\min}\le c_0S_c/S^*$；前两项均不成立时再由式\eqref{eq:joint:feasibility}判断联合可行性。边界等号归入可行侧。"
        + "\n\n"
        + f"基准参数代表点取 $c_{{\\min}}/c_0={fixed(1-point['u_max'], 1)}$、$q_{{\\rm cap}}={fixed(point['q_cap'], 1)}$，"
        + f"受限类内最小成本约为 ${fixed(value(metric, 'J_state', 'J'), 4)}$，控制时长约为 ${fixed(value(metric, 'duration_state', 'duration'), 2)}$ d。"
        + f"西安代表点取 $c_{{\\min}}/c_0={fixed(1-xian['point']['u_max'], 1)}$、$q_{{\\rm cap}}={fixed(xian['point']['q_cap'], 2)}$，相应为 ${fixed(value(xian_metric, 'J_state', 'J'), 4)}$ 和 ${fixed(value(xian_metric, 'duration_state', 'duration'), 2)}$ d。"
        + f"两点的受限成本比各自无额外能力限制时分别增加约 ${fixed(item['cost_increase_vs_unconstrained'], 4)}$ 和 ${fixed(xian['cost_increase_vs_unconstrained'], 4)}$ d。"
        + r"图\ref{fig:joint:capacity}(c)显示其时间控制。实际允许区间的上下界仍给出可达到的时间界，不能用不可实施的单控制代替；受限最小成本与无额外限制时的比较使用同一二次权重。"
        + r"图中不可行只指从规定首次触发状态出发不能维持该平台，不排除改变启动时机或退出目标的其他控制。"
    )


def phase_text(phase):
    return (
        r"为比较分配结构，固定 $w_c=1$ 并改变 $r=w_q/w_c$。图\ref{fig:joint:phase}给出 $r\in[0.1,20]$ 上逐状态候选比较所得的分配，"
        r"颜色为 $y=(1-c_c^*/c_0)/(1-S_c/S)$，表示相对于仅减少接触端点所需削减程度的归一化量。"
        r"有限 $S$ 时隔离强度不能简单写成 $1-y$；$S=S_c$ 的 $0/0$ 点不作为数值证据。"
        + "\n\n"
        + f"基准和西安参数的局部端点阈值分别约为 $S_{{\\rm sw}}/S_c={fixed(phase['baseline']['s_sw'], 3)}$ 和 ${fixed(phase['xian']['s_sw'], 3)}$。"
        + r"竖直虚线来自命题\ref{prop:joint:global-structure}，只区分端点的局部性质；全局选择及其数值切换边界必须比较端点与内部驻点。"
        + r"默认 $r=2$ 与前述四策略比较采用相同评价标准。充分接近退出时，接触减少的归一化份额趋于 $r/(1+r)$，这一极限及其条件见命题\ref{prop:joint:terminal-allocation}；图面横轴从左到右增大，而沿控制时间 $S$ 从右向左下降。"
        + r"改变 $r$ 同时改变成本标准，不将不同权重下的 $J$ 数值直接解释为同一成本的下降。"
    )


def duration_text(rows):
    valid = [row for row in rows if passed(row.get("passed"))]
    if not valid:
        raise ValueError("任务 D 声称通过但没有已核查乘子点。")
    return (
        r"\subsection{成本与控制持续时间}" + "\n" + r"\label{sec:joint:duration-numerics}" + "\n"
        + f"图\\ref{{fig:joint:frontier}}展示基准参数下经数值核查的 ${len(valid)}$ 个乘子解；"
        + r"每个解同时报告实际 $\Delta t$ 与原二次 $J$。由注记\ref{rem:joint:duration-constraint}，取得匹配时长的解给出相应时长限制下的充分最优性条件。"
        + r"允许时长两端之间的每个值均可由前述允许上下界的连续组合实现；这里尚未核查的是全部时长上的最低成本与匹配乘子，不是时长本身的可达性。点间连线只显示这些计算点的关系，不表示全部中间时长都已有匹配乘子，也不证明成本边界连续或凸。"
        + "\n\n"
        + r"$\kappa\ge0$ 的分支用于考察成本与较短控制时间的取舍；$\kappa<0$ 的解用于考察时长下限及其等价的新增隔离易感者人数上限，不能将整条曲线称为同时最小化成本和时长的效率前沿。"
        + r"显式 $\alpha$ 族是可行子集。图形插值不构成同一时长上的严格成本比较，有限大的 $|\kappa|$ 也不替代按公式计算的两种单控制端点。"
        + "\n\n"
        + r"\begin{figure}[htbp]" + "\n" + r"\centering" + "\n"
        + r"\includegraphics[width=0.6\textwidth]{figures/joint_v2/joint_frontier_baseline.pdf}" + "\n"
        + r"\caption{基准参数下二次成本与控制持续时间的关系。红色计算点及连线对应已核查的 $J+\kappa\Delta t$ 最小化解，红色实线和短虚线分别表示 $\kappa\ge0$ 与 $\kappa<0$；浅蓝虚线为显式 $\alpha$ 族，圆点为两种单控制和无额外时长限制的最低成本分配。横轴为对数坐标，$\Delta t$ 与 $J$ 的单位均为天。连线不表示未计算时长的最优性；扫描中大间距的相邻时长段不连接，断线不证明相应区间不可达。}" + "\n"
        + r"\label{fig:joint:frontier}" + "\n" + r"\end{figure}"
    )


def xian_text(rows, changes):
    q, m = rows["quarantine_only"], rows["minimum_cost"]
    return (
        r"在同一全市人口、未取整拟合初值及 $\eta=0.002N$ 下，第\ref{sec:joint:compare-numerics}节又比较了四种阈值分配（表\ref{tab:joint:compare}）。"
        + f"类内最小成本从仅隔离的 ${fixed(value(q, 'J_state', 'J'), 4)}$ 降至 ${fixed(value(m, 'J_state', 'J'), 4)}$，"
        + f"控制时长由 ${fixed(value(q, 'duration_state', 'duration'), 2)}$ 延长至 ${fixed(value(m, 'duration_state', 'duration'), 2)}$ d，"
        + f"总累计新增感染由约 ${fixed(value(q, 'total_infections_to_clearance', 'total_infections')/1e6, 4)}\\times10^6$ 增至 ${fixed(value(m, 'total_infections_to_clearance', 'total_infections')/1e6, 4)}\\times10^6$。"
        + f"相对变化分别约为成本 $-{fixed(-changes['cost_change_pct'], 1)}\\%$、控制时长 $+{fixed(changes['duration_change_pct'], 1)}\\%$、总累计新增感染 $+{fixed(changes['total_infections_change_pct'], 1)}\\%$。"
        + r"因此，这里的成本降低不伴随感染指标同时改善。TDINN 仍为另一终止任务下的外部参照，不属于固定启动状态、感染平台和退出状态的四策略比较类，也不据此宣称它已被联合阈值策略支配。"
    )


def build_publication_fragments(result_dir):
    """纯函数：只读取结果，返回六个唯一标识下的完整文案片段。"""
    res = Path(result_dir)
    validation = load_json(res / "validation.json")
    tasks = validation.get("tasks", {})
    if not all(passed(tasks.get(key, {}).get("passed")) for key in ("A", "B", "C")):
        raise RuntimeError("任务 A–C 未全部通过，不能生成出版文案。")
    baseline, xian = comparison_rows(res, "baseline"), comparison_rows(res, "xian")
    summary = load_json(res / "derived_summary.json")["cases"]
    fragments = {"comparison": comparison_text(baseline, xian, summary["baseline"]["minimum_vs_quarantine"]),
                 "capacity": capacity_text(load_json(res / "capacity.json")),
                 "phase": phase_text(load_json(res / "phase.json")),
                 "duration": "", "xian": xian_text(xian, summary["xian"]["minimum_vs_quarantine"]),
                 "conclusion": r"同条件数值比较进一步显示，基准和西安参数下的最低二次成本分配相对于仅隔离延长了控制期，并增加累计新增感染。有限能力代表点与权重分配图说明，能力界决定允许组合，权重则决定这些组合中的成本选择；端点局部判据不能代替全局候选比较。上述证据仍限于所核查的参数、权重范围和规定控制类，不推断提前干预、其他退出规则或回流模型下的最优性。"}
    if passed(tasks.get("D", {}).get("passed")):
        fragments["duration"] = duration_text(load_rows(res / "frontier_baseline.csv"))
    return fragments


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--res", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    fragments = build_publication_fragments(args.res)
    if args.out.exists():
        raise FileExistsError("不能覆盖已有文案核查输出。")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(fragments, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"局部出版片段：{args.out}")


if __name__ == "__main__":
    main()
