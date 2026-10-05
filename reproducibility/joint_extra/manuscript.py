"""从本轮已验收输出生成局部出版文案；不拟合、不求根、不覆盖主稿。"""
from __future__ import annotations

import argparse
import bisect
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


def pct(new, old):
    return 100.0 * (float(new) / float(old) - 1.0)


def control_rows(path, strategy):
    """读取已验收轨迹中某一分配的平台控制段，按时间排序。"""
    rows = [row for row in load_rows(path) if row["strategy"] == strategy and row["phase"] == "control"]
    if len(rows) < 10:
        raise ValueError(f"{path} 缺少 {strategy} 的平台控制段。")
    return sorted(rows, key=lambda row: row["t"])


def case_parameters(res, case):
    """常规接触率等参数取自本轮输入清单，不从受控轨迹的首行推断。"""
    return load_json(res / "input_manifest.json")["cases"][case]["parameters"]


def check_default_weights(res):
    """默认权重的文案须绑定本轮清单，不能由近邻相图网格推断。"""
    manifest = load_json(res / "input_manifest.json")
    weights = manifest["settings"]["weights"]
    if len(weights) != 2 or not all(math.isclose(float(a), b, rel_tol=0., abs_tol=1e-12)
                                  for a, b in zip(weights, (1., 2.))):
        raise ValueError("默认二次权重不是 w_c=1,w_q=2，需重写对应句子。")
    for case in ("baseline", "xian"):
        parameters = manifest["cases"][case]["parameters"]
        if not (math.isclose(value(parameters, "wc"), 1., rel_tol=0., abs_tol=1e-12)
                and math.isclose(value(parameters, "wq"), 2., rel_tol=0., abs_tol=1e-12)
                and value(parameters, "c0") > 0):
            raise ValueError(f"{case} 输入参数与默认权重文案不符。")


def boundary_time(diagnostics, state):
    """由已验收的名义分段诊断读取 S 到达分段边界 state 的时刻（S 沿时间下降）。"""
    for segment in diagnostics["nominal_segment_methods"]:
        lower, upper = segment["S_bounds"]
        if math.isclose(lower, state, rel_tol=1e-9):
            return float(segment["interval"][1])
    raise ValueError(f"名义分段诊断中没有 S={state} 的边界。")


def default_switch(diagnostics, S_sw):
    """默认权重下单独候选比较给出的切换点；须唯一、连续且位于 S_sw。"""
    switches = diagnostics["candidate_checks"]["switches"]
    if (len(switches) != 1 or switches[0]["jump"]
            or not math.isclose(switches[0]["S"], S_sw, rel_tol=1e-9)):
        raise ValueError("默认权重的切换点不是 S_sw 处唯一的连续切换，需重写对应句子。")
    return switches[0]


def allocation_structure(res, case, phase_case, rows, task_a):
    """最低成本分配（w_c=1,w_q=2）的仅隔离段与混合段；时刻与极值取自任务A诊断。"""
    s_star, s_sw = float(phase_case["s_star"]), float(phase_case["s_sw"])
    S_sw = float(phase_case["S_sw"])
    if not s_star > s_sw:
        raise ValueError(f"{case} 的启动状态不大于 S_sw，分配结构文案不适用。")
    c0 = float(case_parameters(res, case)["c0"])
    record = task_a["cases"][case]["strategies"]["minimum_cost"]
    default_switch(record, S_sw)
    diag = record["time_diagnostics"]
    t1 = float(diag["t1"])
    t_sw = boundary_time(diag, S_sw)
    duration = value(rows["minimum_cost"], "duration_state", "duration")
    # 只作核查：S>S_sw 上的已验收轨迹须为 c=c0。
    traj = control_rows(res / f"trajectories_{case}.csv", "minimum_cost")
    upper = [row for row in traj if row["S"] > S_sw * (1 + 1e-6)]
    if not upper or any(abs(row["c"] - c0) > 1e-8 * c0 for row in upper):
        raise ValueError(f"{case} 的最低成本分配在 S>S_sw 上不是仅隔离，结构文案不适用。")
    q_peak, m_peak = rows["quarantine_only"], rows["minimum_cost"]
    peak_time = float(q_peak["t_peak_I_plus_Iq"]) - float(q_peak["t1"])
    same_peak = (float(q_peak["t_peak_I_plus_Iq"]) <= t_sw
                 and math.isclose(float(q_peak["t_peak_I_plus_Iq"]), float(m_peak["t_peak_I_plus_Iq"]), rel_tol=1e-9)
                 and math.isclose(float(q_peak["peak_I_plus_Iq_over_eta"]),
                                  float(m_peak["peak_I_plus_Iq_over_eta"]), rel_tol=1e-9))
    return {"s_star": s_star, "s_sw": s_sw, "q_only_days": t_sw - t1,
            "q_only_time_share": 100 * (t_sw - t1) / duration,
            "q_only_state_share": 100 * (s_star - s_sw) / (s_star - 1),
            "max_contact_reduction": 100 * (1 - float(diag["c_min"]) / c0),
            "peak_days": peak_time, "same_peak": same_peak}


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


def comparison_text(baseline, xian, changes, structure):
    q, m = baseline["quarantine_only"], baseline["minimum_cost"]
    sb, sx = structure["baseline"], structure["xian"]
    if sb["same_peak"] or not sx["same_peak"]:
        raise ValueError("(I+I_q) 峰值与分配分叉时刻的先后关系已改变，需重写对应句子。")
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
        + r"两组参数下，最低成本分配都分为前后两段。"
        + f"基准和西安参数的启动状态分别为 $S^*/S_c\\approx{fixed(sb['s_star'], 3)}$ 和 ${fixed(sx['s_star'], 3)}$，"
        + f"均大于 $S_{{\\rm sw}}/S_c\\approx{fixed(sb['s_sw'], 3)}$ 和 ${fixed(sx['s_sw'], 3)}$。"
        + r"由命题\ref{prop:joint:global-structure}，任一类内最小成本可测控制在 $S_c<S<S_{\rm sw}$ 上几乎处处同时使用两种措施；$S>S_{\rm sw}$ 时该命题只说明仅隔离是局部最小点。"
        + r"对 $w_c=1,w_q=2$ 比较全部候选后，数值结果显示 $S>S_{\rm sw}$ 上的全局最小点就是仅隔离，切换发生在 $S=S_{\rm sw}$ 处且分配连续；退出时两种控制回到常规水平（权重的影响见第\ref{sec:joint:weights-numerics}节）。"
        + f"基准参数下，仅隔离段约为 ${fixed(sb['q_only_days'])}$ d，占控制时长的 ${fixed(sb['q_only_time_share'], 0)}\\%$，"
        + f"但 $S$ 在该段的下降占平台期总下降的 ${fixed(sb['q_only_state_share'], 0)}\\%$；此后接触率最大降低约 ${fixed(sb['max_contact_reduction'], 1)}\\%$。"
        + f"西安参数下相应为 ${fixed(sx['q_only_days'])}$ d、${fixed(sx['q_only_time_share'], 0)}\\%$、${fixed(sx['q_only_state_share'], 0)}\\%$ 和 ${fixed(sx['max_contact_reduction'], 1)}\\%$。"
        + r"平台期成本和控制时长都是关于 $S$ 的积分，两种分配在 $S\ge S_{\rm sw}$ 一段的贡献相同，表\ref{tab:joint:compare}中二者 $J$ 与 $\Delta t$ 的差别只来自 $S_c<S<S_{\rm sw}$ 一段。"
        + r"在这一段，最低成本分配取 $c_c(S)<c_0$，由 $\dot S=-(\eta/N)[c_c(S)S-c_0\bar S]$，相较仅隔离，$S$ 下降较慢，控制时间因而延长；隔离强度相应降低，二次成本减小。"
        + "\n\n"
        + r"感染人数上限约束的是 $I$，不是 $I+I_q$。在各自 $[0,t_{\rm end}]$ 上，"
        + f"基准参数下仅隔离、最低成本分配与仅减少接触的 $\\max(I+I_q)/\\eta$ 分别约为 ${fixed(q['peak_I_plus_Iq_over_eta'])}$、${fixed(m['peak_I_plus_Iq_over_eta'])}$ 和 ${fixed(baseline['contact_only']['peak_I_plus_Iq_over_eta'])}$；"
        + f"西安参数下相应为 ${fixed(xian['quarantine_only']['peak_I_plus_Iq_over_eta'])}$、${fixed(xian['minimum_cost']['peak_I_plus_Iq_over_eta'])}$ 和 ${fixed(xian['contact_only']['peak_I_plus_Iq_over_eta'])}$。"
        + f"西安参数下，仅隔离与最低成本分配的这一峰值都出现在启动后约 ${fixed(sx['peak_days'])}$ d，此时两者仍处于分配相同的 $S>S_{{\\rm sw}}$ 一段，故峰值相同；"
        + r"基准参数下仅隔离的峰值出现在两者分开之后，最低成本分配的峰值略低。"
        + r"这些是现存感染人数，不是医疗或 ICU 占用；图\ref{fig:joint:compare}(c)中的水平线 $1$ 只作归一化参照。"
    )
    return text + "\n\n" + comparison_table(baseline, xian)


def capacity_structure(res, case, item, phase_case, compare, task_a, task_b):
    """能力代表点的受限最低成本分配：上限段、仅隔离段与混合段；分段时刻取自任务B诊断。"""
    q0, qcap, umax = float(item["q0"]), float(item["point"]["q_cap"]), float(item["point"]["u_max"])
    s_star, s_sw = float(phase_case["s_star"]), float(phase_case["s_sw"])
    Sc = float(phase_case["S_sw"]) / s_sw
    s_cap = (1 - q0) / (1 - qcap)
    if not s_star > s_cap > s_sw:
        raise ValueError(f"{case} 能力代表点不满足 S*>S_cap>S_sw，时间结构文案不适用。")
    c0 = float(case_parameters(res, case)["c0"])
    if not math.isclose(c0, float(task_b["cases"][case]["minimum_cost"]["time_diagnostics"]["c_max"]), rel_tol=1e-12):
        raise ValueError(f"{case} 受限分配的常规接触率与输入参数不符。")
    record = task_b["cases"][case]["minimum_cost"]
    default_switch(record, float(phase_case["S_sw"]))
    diag = record["time_diagnostics"]
    t1 = float(diag["t1"])
    t_cap, t_sw = boundary_time(diag, s_cap * Sc), boundary_time(diag, s_sw * Sc)
    # 启动时 q=q_cap，接触率由平衡式确定：c/c0 = s_cap/s_star；以诊断的 c_min 交叉核对。
    start_reduction = 1 - s_cap / s_star
    if not math.isclose(1 - float(diag["c_min"]) / c0, start_reduction, rel_tol=1e-6):
        raise ValueError(f"{case} 受限分配启动时的接触减少与平衡式不符。")
    traj = control_rows(res / f"capacity_traj_{case}.csv", "minimum_cost")
    free = control_rows(res / f"trajectories_{case}.csv", "minimum_cost")
    head = [row for row in traj if row["S"] > s_cap * Sc * (1 + 1e-6)]
    if not head or any(abs(row["q"] - qcap) > 1e-8 for row in head):
        raise ValueError(f"{case} 受限分配在 S>S_cap 上未停在隔离上限。")
    # 无额外限制的逐状态最小点在 S<=S_cap 上若满足能力限制，即为受限最小点；这里按同一 S 核对两者的控制。
    free_cmin = float(task_a["cases"][case]["strategies"]["minimum_cost"]["time_diagnostics"]["c_min"])
    if 1 - free_cmin / c0 > umax:
        raise ValueError(f"{case} 无限制最低成本分配的接触减少超过能力上限。")
    order = sorted(free, key=lambda row: row["S"])
    states = [row["S"] for row in order]
    def interp(S, key):
        index = bisect.bisect_left(states, S)
        if index == 0 or index == len(states):
            raise ValueError("状态越出无限制轨迹范围。")
        a, b = order[index - 1], order[index]
        return a[key] if b["S"] == a["S"] else a[key] + (S - a["S"]) * (b[key] - a[key]) / (b["S"] - a["S"])
    tail = [row for row in traj if Sc * (1 + 1e-4) < row["S"] < s_cap * Sc * (1 - 1e-4)]
    if not tail:
        raise ValueError(f"{case} 缺少受限与无限制逐状态控制的对照样本。")
    gap = max(max(abs(interp(row["S"], "c") - row["c"]) / c0, abs(interp(row["S"], "q") - row["q"])) for row in tail)
    if gap > 1e-4:
        raise ValueError(f"{case} 受限分配在 S<=S_cap 上与无限制分配不一致：{gap}")
    free_row = compare["minimum_cost"]
    metric = item.get("metrics", item)
    return {"s_cap": s_cap, "cap_days": t_cap - t1, "q_only_days": t_sw - t_cap,
            "start_reduction": 100 * start_reduction,
            "cost_pct": pct(value(metric, "J_state", "J"), value(free_row, "J_state", "J")),
            "duration_pct": pct(value(metric, "duration_state", "duration"), value(free_row, "duration_state", "duration"))}


def capacity_text(capacity, structure):
    item = capacity["baseline"]
    metric = item.get("metrics", item)
    point = item["point"]
    xian = capacity["xian"]
    xian_metric = xian.get("metrics", xian)
    sb, sx = structure["baseline"], structure["xian"]
    for entry in (item, xian):
        if entry["classification"] != "joint_required":
            raise ValueError("代表点不再属于需联合控制区域，需重写对应句子。")
    return (
        r"\def\jointcapacitypostexitdays{" + f"{float(item['plot_viewport']['post_exit_days']):g}" + "}\n"
        + r"图\ref{fig:joint:capacity}将能力平面分成至少一种单控制可行、两种单控制均不可行但联合可行、规定触发状态下不可行三个区域。"
        r"仅隔离可行要求 $q_{\rm cap}\ge q_{\max}$，仅减少接触可行要求 $c_{\min}\le c_0S_c/S^*$；二者均不成立时由式\eqref{eq:joint:feasibility}判断联合可行性，边界等号归入可行侧。"
        r"灰色区域的不可行只针对在 $I$ 首次达到 $\eta$ 时启动、在 $S=S_c$ 退出的平台控制。"
        + "\n\n"
        + f"基准参数代表点取 $c_{{\\min}}/c_0={fixed(1-point['u_max'], 1)}$、$q_{{\\rm cap}}={fixed(point['q_cap'], 1)}$。"
        + f"仅隔离需要 $q_{{\\max}}\\approx{fixed(item['q_required_quarantine_only'], 3)}$，仅减少接触需要把接触率降低约 ${fixed(100*item['u_required_contact_only'], 1)}\\%$，两者均超出能力限制，联合控制可行。"
        + f"受限类内最小成本约为 ${fixed(value(metric, 'J_state', 'J'), 4)}$，控制时长约为 ${fixed(value(metric, 'duration_state', 'duration'), 2)}$ d，"
        + f"比无额外能力限制时分别增加约 ${fixed(sb['cost_pct'], 1)}\\%$ 和 ${fixed(sb['duration_pct'], 1)}\\%$。"
        + f"西安代表点取 $c_{{\\min}}/c_0={fixed(1-xian['point']['u_max'], 1)}$、$q_{{\\rm cap}}={fixed(xian['point']['q_cap'], 2)}$，相应为 ${fixed(value(xian_metric, 'J_state', 'J'), 4)}$ 和 ${fixed(value(xian_metric, 'duration_state', 'duration'), 2)}$ d，"
        + f"增幅约为 ${fixed(sx['cost_pct'], 1)}\\%$ 和 ${fixed(sx['duration_pct'], 1)}\\%$。"
        + "\n\n"
        + f"图\\ref{{fig:joint:capacity}}(c)给出基准代表点的时间控制。启动后约 ${fixed(sb['cap_days'])}$ d 内，隔离比例停在上限 ${fixed(point['q_cap'], 1)}$，接触率同时降低，降幅由启动时的约 ${fixed(sb['start_reduction'], 1)}\\%$ 随 $S$ 下降而减小；"
        + f"$S$ 降至 $(1-q_0)S_c/(1-q_{{\\rm cap}})\\approx{fixed(sb['s_cap'], 3)}S_c$ 时，仅隔离已能维持平台，接触率回到 $c_0$。"
        + f"随后经过约 ${fixed(sb['q_only_days'])}$ d 的仅隔离段，$S<S_{{\\rm sw}}$ 后两种措施同时使用直至退出。"
        + r"在 $S\le(1-q_0)S_c/(1-q_{\rm cap})$ 上，无额外限制时的逐状态最小点满足两项能力限制，因而也是受限问题的逐状态最小点，数值核查显示同一 $S$ 处两者的 $c_c(S)$、$q_c(S)$ 相同。"
        + r"这里的一致只指同一易感者状态下的控制：受限分配到达同一 $S$ 的时刻较晚，$I_q$、$S_q$ 等状态也不同，并非相同时刻的完整轨迹相同。"
        + r"由于 $J$ 与 $\Delta t$ 都是关于 $S$ 的积分，能力限制只改变启动后的前一段分配，二者的增加都来自这一段。"
        + f"西安代表点的结构相同，隔离比例停在上限约 ${fixed(sx['cap_days'])}$ d。"
        + r"有能力限制时，可达到的最短和最长控制时长由实际允许区间的上下界给出，不再对应两种单控制。"
    )


def phase_grid(res, case):
    """关闭 NPZ 句柄后返回本轮相图数组，避免 Windows 文件占用。"""
    import numpy as np
    with np.load(res / f"phase_{case}.npz") as grid:
        return {key: grid[key].copy() for key in ("r", "classification")}


def phase_structure(res, case, phase_case, example_ratio=5.0):
    """由已验收相图输出读取全局切换边界的三段结构；网格值原样报告，不外推。"""
    import numpy as np
    grid = phase_grid(res, case)
    ratios, classes = grid["r"], grid["classification"]
    if (len(ratios) < 3 or classes.ndim != 2 or classes.shape[0] != len(ratios)
            or not np.isfinite(ratios).all() or not np.isfinite(classes).all()
            or not (np.diff(ratios) > 0).all()
            or not np.isin(classes, (0, 1, 2, 3)).all()
            or not np.allclose(np.diff(np.log(ratios)), np.diff(np.log(ratios))[0], rtol=1e-10, atol=1e-12)
            or not math.isclose(float(ratios[0]), .1, rel_tol=1e-12)
            or not math.isclose(float(ratios[-1]), 20., rel_tol=1e-12)):
        raise ValueError(f"{case} 相图网格与本文的有限对数网格说明不符。")
    s_sw = float(phase_case["s_sw"])
    Sc = float(phase_case["S_sw"]) / s_sw
    switches = sorted(phase_case["switches"], key=lambda item: item["r"])
    if (not switches or any(not math.isfinite(float(item[key])) for item in switches
                            for key in ("r", "S", "x_low_S", "x_high_S"))
            or any(switches[i + 1]["r"] <= switches[i]["r"] for i in range(len(switches) - 1))
            or any(not np.isclose(ratios, float(item["r"]), rtol=1e-12, atol=1e-12).any()
                   for item in switches)
            or any(switches[i + 1]["S"] < switches[i]["S"] - 1e-6 * Sc
                   for i in range(len(switches) - 1))):
        raise ValueError(f"{case} 切换点不是随网格权重非减地移向启动状态。")
    jumps = [index for index, item in enumerate(switches) if item["jump"]]
    if not jumps or jumps[0] == 0 or any(not switches[i]["jump"] for i in range(jumps[0], len(switches))):
        raise ValueError(f"{case} 切换边界不是“先连续、后跳变”的结构，需重写对应句子。")
    if any(abs(item["S"] / Sc - s_sw) > 1e-6 for item in switches[:jumps[0]]):
        raise ValueError(f"{case} 连续切换点不与 S_sw 重合。")
    # r=2 不是网格点；正文对 r=2 的陈述绑定任务A的单独候选比较，这里只核对网格结论与之不矛盾。
    if not switches[jumps[0] - 1]["r"] >= 2.0 or any(abs(float(r) - 2.0) < 1e-12 for r in ratios):
        raise ValueError("默认 r=2 与连续切换网格段的关系已改变，需重写对应句子。")
    has_quarantine = [bool((row == 1).any()) for row in classes]
    absent = [float(ratios[i]) for i, flag in enumerate(has_quarantine) if not flag]
    if not absent or any(has_quarantine[i] for i in range(has_quarantine.index(False), len(has_quarantine))):
        raise ValueError(f"{case} 仅隔离段消失的位置不唯一。")
    example = min(switches, key=lambda item: abs(item["r"] - example_ratio))
    present = [float(ratios[i]) for i, flag in enumerate(has_quarantine) if flag]
    return {"n_ratio": len(ratios), "last_continuous": switches[jumps[0] - 1]["r"],
            "first_jump": switches[jumps[0]]["r"], "no_quarantine": min(absent), "last_quarantine": max(present),
            "example_r": example["r"], "example_s": example["S"] / Sc, "example_x": example["x_low_S"]}


def phase_text(phase, structure):
    sb, sx = structure["baseline"], structure["xian"]
    if sb["n_ratio"] != sx["n_ratio"] or abs(sb["example_r"] - sx["example_r"]) > 1e-12:
        raise ValueError("两组相图的权重网格不同，需重写对应句子。")
    return (
        r"为比较分配结构，固定 $w_c=1$ 并改变 $r=w_q/w_c$；其余参数及状态固定时，权重对逐状态最小点的影响仅通过比值 $r$。"
        + f"图\\ref{{fig:joint:phase}}给出 $r\\in[0.1,20]$ 上 ${sb['n_ratio']}$ 个对数等距取值的结果，"
        + r"颜色 $y=(1-c_c^*/c_0)/(1-S_c/S)$ 是接触减少相对于仅减少接触端点的比例，$y=0$ 与 $y=1$ 分别对应两种单控制（隔离强度不是 $1-y$）。"
        + r"全局切换点由端点与内部驻点的成本比较确定；命题\ref{prop:joint:global-structure}中的 $S_{\rm sw}$ 只给出端点的局部性质，"
        + f"基准和西安参数分别约为 ${fixed(phase['baseline']['s_sw'], 3)}S_c$ 和 ${fixed(phase['xian']['s_sw'], 3)}S_c$。"
        + "\n\n"
        + f"在所计算的 ${sb['n_ratio']}$ 个网格点上，基准参数直到网格点 $r\\approx{fixed(sb['last_continuous'])}$、西安参数直到网格点 $r\\approx{fixed(sx['last_continuous'])}$，各点的全局切换点都与 $S_{{\\rm sw}}$ 重合且分配连续："
        + r"$S>S_{\rm sw}$ 时取仅隔离，$S<S_{\rm sw}$ 时两种措施同时使用。"
        + r"默认 $r=2$ 不是网格点；第\ref{sec:joint:compare-numerics}节在 $r=2$ 下单独完成的候选比较同样给出 $S=S_{\rm sw}$ 处的连续切换。"
        + f"从相邻的网格点 $r\\approx{fixed(sb['first_jump'])}$（基准）和 $r\\approx{fixed(sx['first_jump'])}$（西安）起，仅隔离段在 $S$ 降至 $S_{{\\rm sw}}$ 之前结束："
        + r"$S$ 略大于 $S_{\rm sw}$ 时仅隔离仍是局部最小点，但内部的另一局部最小点成本更低。"
        + r"在其后的网格点上，切换点随 $r$ 增大移向启动状态，接触率在切换处由 $c_0$ 跳到内部值；"
        + f"例如 $r\\approx{fixed(sb['example_r'])}$ 时，基准和西安的切换点约为 ${fixed(sb['example_s'], 3)}S_c$ 和 ${fixed(sx['example_s'], 3)}S_c$，"
        + f"接触率分别跳至约 ${fixed(sb['example_x'], 3)}c_0$ 和 ${fixed(sx['example_x'], 3)}c_0$。"
        + f"出现仅隔离段的最大网格点为 $r\\approx{fixed(sb['last_quarantine'])}$（基准）和 ${fixed(sx['last_quarantine'])}$（西安），"
        + f"从 $r\\approx{fixed(sb['no_quarantine'])}$ 和 ${fixed(sx['no_quarantine'])}$ 起，整个平台期不再出现仅隔离段。"
        + r"相邻网格点显示了上述两处结构变化，但未进一步确定连续权重下的精确转折位置或证明其唯一性。"
        + r"靠近退出时，各 $r$ 下的 $y$ 趋于 $r/(1+r)$，与命题\ref{prop:joint:terminal-allocation}一致。"
        + r"改变 $r$ 即改变成本标准，不同 $r$ 下的 $J$ 不直接比较。"
    )


def duration_bounds(compare, limit):
    """用未取整端点核对本文成本夹界的适用区间，仅供文案核查。"""
    lower = value(compare["quarantine_only"], "duration_state", "duration")
    upper = value(compare["minimum_cost"], "duration_state", "duration")
    return lower <= float(limit) <= upper


def duration_text(rows, compare, near=0.10):
    # 失败点不能通过静默过滤从出版计数和连接说明中消失。
    valid = list(rows)
    if not valid:
        raise ValueError("任务 D 声称通过但没有已核查乘子点。")
    for row in valid:
        if not passed(row.get("passed")) or row.get("status") != "passed_numeric_support":
            raise ValueError("任务 D 含失败或未验收点，不能生成对应数值结论。")
        for key, number in row.items():
            if isinstance(number, (float, int)) and not math.isfinite(number):
                raise ValueError(f"任务 D 含非有限字段：{key}")
        for key in ("kappa", "duration", "J", "connection_group"):
            value(row, key)
        if row["connection_group"] < 0 or row["connection_group"] != int(row["connection_group"]):
            raise ValueError("任务 D 的连接分组无效。")
    if len({row["kappa"] for row in valid}) != len(valid):
        raise ValueError("任务 D 重复乘子点不能重复计入出版文案。")
    # 两种单控制端点与最低成本按公式/同条件比较输出取值，有限 |kappa| 的扫描点不替代端点。
    J_min = value(compare["minimum_cost"], "J_state", "J")
    T_min = value(compare["minimum_cost"], "duration_state", "duration")
    J_quarantine = value(compare["quarantine_only"], "J_state", "J")
    T_q = value(compare["quarantine_only"], "duration_state", "duration")
    J_contact = value(compare["contact_only"], "J_state", "J")
    T_c = value(compare["contact_only"], "duration_state", "duration")
    positive = [row for row in valid if row["kappa"] >= 0]
    negative = sorted((row for row in valid if row["kappa"] < 0), key=lambda row: row["duration"])
    zero = [row for row in valid if row["kappa"] == 0.]
    if (not positive or not negative or len(zero) != 1
            or not math.isclose(zero[0]["J"], J_min, rel_tol=1e-9, abs_tol=1e-10)
            or not math.isclose(zero[0]["duration"], T_min, rel_tol=1e-9, abs_tol=1e-10)
            or not 0 < T_q < T_min <= T_c or not 0 < J_min <= J_quarantine
            or min(row["J"] for row in valid) < J_min * (1 - 1e-9)):
        raise ValueError("任务 D 的零乘子回归或单控制成本、时长排序不符。")
    if max(row["J"] for row in positive) > J_quarantine * (1 + 1e-9):
        raise ValueError("kappa>=0 一侧有计算点成本高于仅隔离端点，需重写对应句子。")
    if any(row["J"] <= J_min or row["duration"] <= T_min for row in negative):
        raise ValueError("kappa<0 一侧有计算点不同时劣于最低成本点，需重写对应句子。")
    inside = [row for row in negative if row["J"] <= (1 + near) * J_min]
    if not inside or any(row["J"] > (1 + near) * J_min for row in negative if row["duration"] <= inside[-1]["duration"]):
        raise ValueError("kappa<0 一侧近最低成本区间不连续，需重写对应句子。")
    later = [row for row in negative if row["duration"] > inside[-1]["duration"]]
    if not later:
        raise ValueError("kappa<0 一侧缺少成本增幅条件之后的计算点。")
    after = later[0]
    has_gap = any(passed(row.get("duration_gap_before")) for row in valid)
    groups = {int(row["connection_group"]) for row in valid}
    if has_gap != (len(groups) > 1):
        raise ValueError("任务 D 的缺口标识与连接分组不一致。")
    gap_note = "相邻计算点时长间距较大处不连线；" if has_gap else ""
    return (
        r"\subsection{成本与控制持续时间}" + "\n" + r"\label{sec:joint:duration-numerics}" + "\n"
        + f"图\\ref{{fig:joint:frontier}}给出基准参数下 ${len(valid)}$ 个经数值核查的乘子解，每个解报告实际 $\\Delta t$ 与原二次成本 $J$。"
        + r"注记\ref{rem:joint:duration-constraint}给出的是充分条件：取得时长匹配的乘子解 $c_\kappa$ 时，它是约束 $\Delta t=\Delta t[c_\kappa]$ 下的类内最小成本控制。"
        + r"两种单控制之间的每个时长都可由允许控制实现，但计算点之间的时长未逐一取得匹配乘子，这些时长上的最低成本未由此确定。"
        + "\n\n"
        + r"在当前参数下，计算点显示最低成本附近 $J$ 对 $\Delta t$ 不敏感。"
        + r"若要求 $\Delta t\le T$ 且 $\Delta t[c_0]\le T\le\Delta t[c_c^*]$，仅隔离满足这一限制，故成本下界为无额外时长限制的最低二次成本 $J_{\min}=J[c_c^*]$，上界为仅隔离的实际二次成本 $J[c_0]$。"
        + f"两个时长端点约为 ${fixed(T_q)}$ 和 ${fixed(T_min)}$ d，而 $J[c_0]\\approx{fixed(J_quarantine / J_min)}J_{{\\min}}$ 仅作显示近似；$\\kappa\\ge0$ 的计算点均落在上述实际成本范围内。"
        + f"$\\kappa<0$ 一侧，满足 $J\\le{fixed(1 + near)}J_{{\\min}}$ 的计算点中最大时长约为 ${fixed(inside[-1]['duration'])}$ d，下一个计算点（${fixed(after['duration'])}$ d）约为 ${fixed(after['J'] / J_min)}J_{{\\min}}$；${fixed(inside[-1]['duration'])}$ d 不是精确的临界时长。"
        + f"仅减少接触端点（${fixed(T_c)}$ d）的 $J$ 约为 ${fixed(J_contact / J_min)}J_{{\\min}}$。"
        + r"$\kappa<0$ 的解对应时长下限，由式\eqref{eq:joint:quarantine}等价于限制控制期新增隔离易感者人数；若只考虑 $J$ 与 $\Delta t$，这些解的两项都大于最低成本点，因此整条曲线不是同时最小化二者的效率前沿。"
        + r"显式 $\alpha$ 族属于同一允许控制类，只作对照。"
        + "\n\n"
        + r"\begin{figure}[htbp]" + "\n" + r"\centering" + "\n"
        + r"\includegraphics[width=0.6\textwidth]{figures/joint_v2/joint_frontier_baseline.pdf}" + "\n"
        + r"\caption{基准参数下二次成本与控制持续时间的关系。红色曲线连接已核查的 $J+\kappa\Delta t$ 最小化解，实线与短虚线分别对应 $\kappa\ge0$ 和 $\kappa<0$；"
        + gap_note + r"连线不表示中间时长已有匹配乘子。浅蓝虚线为显式 $\alpha$ 族，圆点为两种单控制与无时长限制的最低成本分配。横轴为对数坐标，$\Delta t$ 与 $J$ 的单位均为天。}" + "\n"
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
    check_default_weights(res)
    baseline, xian = comparison_rows(res, "baseline"), comparison_rows(res, "xian")
    compare = {"baseline": baseline, "xian": xian}
    summary = load_json(res / "derived_summary.json")["cases"]
    phase = load_json(res / "phase.json")
    capacity = load_json(res / "capacity.json")
    allocation = {case: allocation_structure(res, case, phase[case], compare[case], tasks["A"]) for case in compare}
    capacity_cases = {case: capacity_structure(res, case, capacity[case], phase[case], compare[case], tasks["A"], tasks["B"])
                      for case in compare}
    phase_cases = {case: phase_structure(res, case, phase[case]) for case in compare}
    fragments = {"comparison": comparison_text(baseline, xian, summary["baseline"]["minimum_vs_quarantine"], allocation),
                 "capacity": capacity_text(capacity, capacity_cases),
                 "phase": phase_text(phase, phase_cases),
                 "duration": "", "xian": xian_text(xian, summary["xian"]["minimum_vs_quarantine"]),
                 "conclusion": r"同条件数值比较进一步显示，基准和西安参数下的最低二次成本分配相对于仅隔离延长了控制期，并增加累计新增感染。有限能力代表点与权重分配图说明，能力界决定允许组合，权重则决定这些组合中的成本选择；端点局部判据不能代替全局候选比较。上述证据仍限于所核查的参数、权重范围和规定控制类，不推断提前干预、其他退出规则或回流模型下的最优性。"}
    if passed(tasks.get("D", {}).get("passed")):
        fragments["duration"] = duration_text(load_rows(res / "frontier_baseline.csv"), baseline)
    elif tasks.get("D", {}).get("status") != "not_executed":
        raise RuntimeError("任务 D 已执行但未通过，不能生成本轮出版文案。")
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
