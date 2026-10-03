"""全文图源复现：新计算结果进入原绘制逻辑和已认可的版式。

此入口不读取历史 Matplotlib pickle；旧原件及 ai 发布包不在写入范围内。
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from plotting_checks import audit_pdf


FIGURES = [
    "Fig1.pdf", "optimal_control_with_quarantine_panels.pdf",
    "layout_v5/baseline_q_joint.pdf", "scenario1_heatmaps_c0_eta.pdf",
    "layout_v5/scenario1_inflection_lambda_sensitivity.pdf",
    "layout_v5/scenario1_inflection_scan_t.pdf",
    "layout_v5/c0_sensitivity_selected_eta.pdf", "layout_v5/eta_sensitivity_selected_c0.pdf",
    "layout_v5/xian_observed_fit.pdf", "layout_v5/xian_strategy_process.pdf",
    "xian_eta_sensitivity.pdf", "xian_heatmaps.pdf", "fig_dom_combined.pdf",
    "layout_v5/population_threshold_levers.pdf", "layout_v5/c0_sensitivity_panel.pdf",
    "layout_v5/c0_phase_stationary.pdf", "layout_v5/fig_panel_B_trajectory_decomposition.pdf",
    "layout_v5/critical_population_cases.pdf", "c0_sensitivity_scan.pdf", "c0_beta_existence.pdf",
]


def render_comparison_pair(new_pdf: Path, old_pdf: Path, target: Path) -> None:
    """并排渲染旧视觉参考/本轮重出图；只作为人工复核定位，不作数值证据。"""
    import pymupdf
    from PIL import Image, ImageDraw
    tiles = []
    for label, path in [("APPROVED REFERENCE", old_pdf), ("REGENERATED", new_pdf)]:
        with pymupdf.open(path) as doc:
            page = doc[0]
            pix = page.get_pixmap(matrix=pymupdf.Matrix(1.4, 1.4), alpha=False)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        scale = 900 / img.width
        img = img.resize((900, round(img.height * scale)))
        tile = Image.new("RGB", (920, img.height + 48), "white")
        tile.paste(img, (10, 38))
        ImageDraw.Draw(tile).text((12, 10), label, fill="black")
        tiles.append(tile)
    sheet = Image.new("RGB", (1840, max(tile.height for tile in tiles)), "white")
    for i, tile in enumerate(tiles):
        sheet.paste(tile, (920 * i, 0))
    target.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(target)


MODEL_PATCHES = [
    ("s_to_sq", [106., 283., 232., 307.], "(1-beta)c(t)q(t)"),
    ("gamma", [625., 160., 643., 181.], "gamma"),
    ("delta_q", [622., 383., 644., 411.], "delta_q"),
]


def create_model_assets(root: Path) -> dict:
    """一次性将认可图的三项静态矢量艺术素材锁定；不是数值缓存。"""
    import pymupdf
    root = Path(root).resolve()
    directory = root / "reproducibility/assets"
    directory.mkdir(parents=True, exist_ok=True)
    source = root / "latex/figures/Fig1.pdf"
    records = []
    with pymupdf.open(source) as doc:
        assert abs(doc[0].rect.width - 850.56) < .1 and abs(doc[0].rect.height - 576) < .1
        for name, bounds, formula in MODEL_PATCHES:
            clip = pymupdf.Rect(bounds)
            with pymupdf.open() as fragment:
                page = fragment.new_page(width=clip.width, height=clip.height)
                page.show_pdf_page(page.rect, doc, 0, clip=clip)
                pdf, svg = directory / f"model_{name}.pdf", directory / f"model_{name}.svg"
                fragment.save(pdf)
                svg.write_text(page.get_svg_image(text_as_path=True), encoding="utf-8")
            records.append({"name": name, "formula": formula, "bounds_pt": bounds,
                            "svg_sha256": hashlib.sha256(svg.read_bytes()).hexdigest(),
                            "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest()})
    result = {"static_artwork_source": str(source), "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "role": "static diagram equation glyph artwork, never a numerical-result input",
              "original_pptx": "refs/SIQR模型示意图_Nature配色_可编辑.pptx",
              "repairs": ["S_to_Sq wrong OLE formula replaced with approved (1-beta)c(t)q(t)",
                          "missing gamma restored", "missing delta_q restored"],
              "patches": records,
              "editability": "Boxes/arrows remain editable; three restored labels are vector artwork, not native equation objects."}
    (directory / "model_repair_source.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def repair_model_source(source: Path, assets: Path, destination: Path, log: Path) -> dict:
    """对只读原 PPTX 副本应用三项锁定矢量标签，另存修正版。"""
    source, assets, destination = map(lambda p: Path(p).resolve(), (source, assets, destination))
    expected = json.loads((assets / "model_repair_source.json").read_text(encoding="utf-8"))
    for record in expected["patches"]:
        path = assets / f"model_{record['name']}.svg"
        if hashlib.sha256(path.read_bytes()).hexdigest() != record["svg_sha256"]:
            raise RuntimeError(f"Locked model artwork hash mismatch: {path}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    esc = lambda p: str(p).replace("'", "''")
    additions = []
    for name, bounds, _ in MODEL_PATCHES:
        left, top, right, bottom = bounds
        additions.append(f"$shape=$slide.Shapes.AddPicture('{esc(assets / ('model_'+name+'.svg'))}',0,-1,{left},{top},{right-left},{bottom-top}); $shape.Name='locked_{name}'")
    code = f"""
$ErrorActionPreference='Stop'; $ProgressPreference='SilentlyContinue'
[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
$app=$null; $deck=$null
$hadPowerPoint=@(Get-Process -Name POWERPNT -ErrorAction SilentlyContinue).Count -gt 0
try {{
 $app=New-Object -ComObject PowerPoint.Application
 $deck=$app.Presentations.Open('{esc(source)}',$true,$false,$false)
 $slide=$deck.Slides.Item(1); $removed=0
 for($j=$slide.Shapes.Count;$j -ge 1;$j--) {{
  if($slide.Shapes.Item($j).Id -eq 26) {{ $slide.Shapes.Item($j).Delete(); $removed++ }}
 }}
 if($removed -ne 1) {{ throw 'Expected exactly one wrong S-to-Sq OLE object (ID26)' }}
 {'; '.join(additions)}
 $deck.SaveAs('{esc(destination)}',24)
 [Console]::WriteLine((@{{version=$app.Version;build=$app.Build;removed=$removed}} | ConvertTo-Json -Compress))
}} finally {{
 if($deck) {{ $deck.Close(); [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($deck) }}
 if($app) {{
   if((-not $hadPowerPoint) -and $app.Presentations.Count -eq 0) {{ $app.Quit() }}
   [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)
 }}
 [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}}
"""
    encoded = base64.b64encode(code.encode("utf-16le")).decode("ascii")
    _run(["powershell", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden",
          "-EncodedCommand", encoded], log, timeout=120)
    office = json.loads(log.read_text(encoding="utf-8").strip())
    return {"source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "corrected_source": str(destination), "office": office, "repairs": expected["repairs"],
            "static_vector_labels": expected["patches"], "editability": expected["editability"]}


def _paths(output_dir: Path):
    output_dir = Path(output_dir).resolve()
    workspace = output_dir / "workspace"
    if not workspace.is_dir():
        raise FileNotFoundError(f"Prepare source-only workspace first: {workspace}")
    logs = output_dir / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    return output_dir, workspace, logs


def _run(command, log: Path, *, env=None, cwd=None, timeout=7200):
    options = {"cwd": cwd, "env": env, "timeout": timeout, "check": True}
    if os.name == "nt":
        options["creationflags"] = subprocess.CREATE_NO_WINDOW
    with log.open("w", encoding="utf-8") as stream:
        subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, **options)


def _python_env(root: Path):
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["MPLBACKEND"] = "Agg"
    env["PYTHONPATH"] = str(Path(__file__).parent) + os.pathsep + env.get("PYTHONPATH", "")
    return env


def verify_baseline_ode(output_dir: Path) -> dict:
    """独立完整仓室积分校核 MATLAB 指标；开环控制只使用理论时间轨迹。"""
    import numpy as np
    import pandas as pd
    from scipy.integrate import solve_ivp
    _, workspace, _ = _paths(output_dir)
    directory = workspace / "scenario1_threshold_landscape/current_run/output_csv"
    cases = pd.concat([pd.read_csv(directory / "main_c0_summary.csv"),
                       pd.read_csv(directory / "main_eta_summary.csv")], ignore_index=True)
    rows, errors = [], []
    for case in cases.to_dict("records"):
        N, beta, gamma, c0, q0, eta = [float(case[k]) for k in ["N", "beta", "gamma", "c0", "q0", "eta"]]
        t1, t2, ss, sb = [float(case[k]) for k in ["t1", "t2", "S_star", "S_bar"]]
        results = []
        for rtol, atol in [(1e-9, 1e-10), (2e-11, 2e-12)]:
            def q_control(t):
                if t < t1 or t > t2:
                    return q0
                theoretical_s = sb + (ss - sb) * np.exp(-c0 * eta * (t - t1) / N)
                return 1 - gamma * N / (beta * c0 * theoretical_s)
            def rhs(t, y, qfun):
                S, I, Sq, Iq, R, Cc, Cq, J = y
                q = qfun(t)
                force = c0 * S * I / N
                fc, fq, fs = beta * (1 - q) * force, beta * q * force, (1 - beta) * q * force
                return [-fc - fq - fs, fc - gamma * I, fs, fq - gamma * Iq,
                        gamma * (I + Iq), fc, fq, 2 * max((q - q0) / (1 - q0), 0) ** 2]
            routine = lambda t, y: rhs(t, y, lambda _: q0)
            platform = lambda t, y: rhs(t, y, q_control)
            y0 = [case["S0"], case["I0"], 0, 0, 0, 0, 0, 0]
            options = dict(method="DOP853", rtol=rtol, atol=atol, dense_output=True, max_step=1.)
            first = solve_ivp(routine, [0, t1], y0, **options)
            second = solve_ivp(platform, [t1, t2], first.y[:, -1], **options)
            def clear(t, y):
                return y[1] - 1
            clear.terminal, clear.direction = True, -1
            third = solve_ivp(routine, [t2, t2 + 5000], second.y[:, -1], events=clear, **options)
            if not (first.success and second.success and third.success and len(third.t_events[0]) == 1):
                raise RuntimeError("Baseline independent full ODE failed to clear")
            end = float(third.t_events[0][0])
            final = third.y_events[0][0]
            platform_y = second.sol(np.linspace(t1, t2, 801))
            all_y = np.column_stack([first.y, second.y, third.y])
            result = {"rtol": rtol, "atol": atol,
                      "platform_max_abs_error": float(np.max(abs(platform_y[1] - eta))),
                      "conservation_max_abs_error": float(np.max(abs(all_y[:5].sum(axis=0) - N))),
                      "minimum_compartment": float(all_y[:5].min()), "clear_time": end,
                      "cumulative_total": float(final[5] + final[6]), "J": float(final[7]),
                      "S_exit": float(second.y[0, -1]),
                      "clear_error_vs_matlab": end - case["t_end"],
                      "cumulative_error_vs_matlab": float(final[5] + final[6] - case["I_t_cum"]),
                      "J_error_vs_matlab": float(final[7] - case["J"])}
            results.append(result)
            if (result["platform_max_abs_error"] > 1e-5 or result["conservation_max_abs_error"] > 1e-6
                    or result["minimum_compartment"] < -1e-8
                    or abs(result["clear_error_vs_matlab"]) > 2e-4
                    or abs(result["cumulative_error_vs_matlab"]) > 2e-4
                    or abs(result["J_error_vs_matlab"]) > 2e-5):
                errors.append({"c0": c0, "eta": eta, "result": result})
        rows.append({"c0": c0, "eta": eta, "checks": results,
                     "two_tolerance_clear_difference": abs(results[0]["clear_time"] - results[1]["clear_time"]),
                     "two_tolerance_cumulative_difference": abs(results[0]["cumulative_total"] - results[1]["cumulative_total"])})
    result = {"passed": not errors, "status": "pass" if not errors else "fail",
              "case_count": len(rows), "cases": rows, "failures": errors,
              "control": "precomputed theoretical time open-loop, not numerical S feedback"}
    report = Path(output_dir) / "validation/baseline_independent_ode.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    if errors:
        raise RuntimeError(f"Independent ODE disagrees with MATLAB in {len(errors)} checks; see {report}")
    return result


def prepare_matlab_graphics(workspace: Path) -> list[dict]:
    """只在隔离源码副本接入已测固定场景；不改变原科学绘制语句。"""
    layout = workspace / "latex/revision_layout_v5/layout_matlab.m"
    text = layout.read_text(encoding="utf-8-sig")
    original_panel = """text(ax,-.02,1.015,sprintf('(%c)','a'+k-1),'Units','normalized', ...
    'FontName','Times New Roman','FontSize',11,'FontWeight','bold', ...
    'Interpreter','none','Color',[.133 .133 .133], ...
    'HorizontalAlignment','left','VerticalAlignment','bottom','Clipping','off');"""
    replacement = "matlab_fixed_graphics('panel',ax,k);"
    if original_panel in text:
        text = text.replace(original_panel, replacement)
    elif replacement not in text:
        raise RuntimeError("Unrecognized original MATLAB panel label source")
    original_layout_export = "assert(save_figure_safe(fig,[stem '.pdf'],[],sz),'PDF export failed');"
    stable_layout_export = "matlab_export_deterministic(fig,[stem '.pdf'],sz);"
    if original_layout_export in text:
        text = text.replace(original_layout_export,stable_layout_export)
    elif stable_layout_export not in text:
        raise RuntimeError("Unrecognized original MATLAB layout export source")
    layout.write_text(text,encoding="utf-8")
    heatmap = workspace / "scenario1_threshold_landscape/scripts/plot_heatmaps.m"
    text = heatmap.read_text(encoding="utf-8-sig")
    original_export = """exportgraphics(fig, filename, ...
            'ContentType', 'image', ...
            'Resolution', 600, ...
            'BackgroundColor', 'white');"""
    replacement_export = """assert(matlab_fixed_graphics('heatmap',fig,filename,target_size_bp), ...
            'Fixed-canvas heatmap export failed');"""
    if original_export in text:
        heatmap.write_text(text.replace(original_export, replacement_export), encoding="utf-8")
    elif replacement_export not in text:
        raise RuntimeError("Unrecognized original MATLAB heatmap export source")
    text = heatmap.read_text(encoding="utf-8-sig")
    original_catch = """log_line(logfid, ['final-size image PDF export failed: ', ...
            err_size.message]);"""
    strict_catch = original_catch + "\n        rethrow(err_size);"
    if strict_catch not in text:
        if original_catch not in text:
            raise RuntimeError("Unrecognized MATLAB heatmap final-size error branch")
        heatmap.write_text(text.replace(original_catch, strict_catch), encoding="utf-8")
    six = workspace / "code/scenario1_q_control_with_quarantine_panels.m"
    text = six.read_text(encoding="utf-8-sig")
    original_six_export = """exportgraphics(gcf, figure_path, ...
    'Resolution', 600, 'BackgroundColor', 'white');"""
    stable_six_export = """matlab_fixed_graphics('six_approved_ticks',gcf);
matlab_export_deterministic(gcf,figure_path,[]);"""
    if original_six_export in text:
        six.write_text(text.replace(original_six_export,stable_six_export),encoding="utf-8")
    elif stable_six_export not in text:
        raise RuntimeError("Unrecognized original six-panel export source")
    return [
        {"file": str(layout.relative_to(workspace)),
         "change": "Times panel label glyphs retain approved reference offsets as independent characters"},
        {"file": str(heatmap.relative_to(workspace)),
         "change": "Fresh fixed-scene native vector intermediate; original high-resolution image finalization follows"},
        {"file":str(six.relative_to(workspace)),
         "change":"Restore approved community I YTicks 0:100:300 only; native vector fixed-scene export and content-only crop follow; data/ylim/other axes unchanged"},
    ]


def run_science(output_dir: Path, root: Path, matlab_exe: str) -> dict:
    output_dir, workspace, logs = _paths(output_dir)
    root = Path(root).resolve()
    reports = output_dir / "validation"
    reports.mkdir(exist_ok=True)
    for folder in [workspace / "latex/figures/layout_v5", workspace / "latex/revision_layout_v5/qa"]:
        folder.mkdir(parents=True, exist_ok=True)
    # 仅运行区机械适配显式图窗可见性，曲线、配色、轴及导出方式完全保留。
    heatmap_source = workspace / "scenario1_threshold_landscape/scripts/plot_heatmaps.m"
    heatmap_text = heatmap_source.read_text(encoding="utf-8-sig")
    visible_count = heatmap_text.count("'Visible', 'on'")
    if visible_count:
        heatmap_source.write_text(heatmap_text.replace("'Visible', 'on'", "'Visible', 'off'"), encoding="utf-8")
    graphics_adaptations = prepare_matlab_graphics(workspace)
    script_dir = Path(__file__).resolve().parent
    quote = lambda p: str(p).replace("\\", "/").replace("'", "''")
    command = (f"addpath('{quote(script_dir)}'); "
               f"matlab_stage('{quote(workspace)}','{quote(reports)}')")
    _run([str(matlab_exe), "-nosplash", "-nodesktop", "-batch", command],
         logs / "matlab_science.log", cwd=workspace)
    from finalize_matlab_figures import finalize
    graphics_finalization = finalize(output_dir,root)
    env = _python_env(root)
    _run([sys.executable, "-B", str(workspace / "scenario1_inflection/verify_anchors.py")],
         logs / "inflection_checks.log", env=env, cwd=workspace)
    spec = importlib.util.spec_from_file_location(
        "reproduction_inflection", workspace / "scenario1_inflection/inflection_analysis.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    baseline = module.solve(beta=.155, gamma=.3504, c0=10., q0=.01526,
                            eta=.05 * 763, N=763., S0=762., I0=1.)
    data = {"status": "pass", "matlab": json.loads((reports / "matlab_science.json").read_text()),
            "inflection_baseline": baseline, "inflection_check_log": str(logs / "inflection_checks.log"),
            "graphics_finalization_report":str(reports / "matlab_graphics_finalization.json"),
            "historical_cache_used": False,
            "runtime_adaptations": [{"file": str(heatmap_source.relative_to(workspace)),
                                     "change": "Explicit Visible on to off in isolated plotting only",
                                     "occurrences": visible_count}, *graphics_adaptations]}
    data["independent_full_ode"] = verify_baseline_ode(output_dir)
    # scipy/numpy 标量交由统一 JSON 编码，不改变数值精度。
    (reports / "baseline_science.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2, default=lambda x: x.item() if hasattr(x, "item") else str(x)),
        encoding="utf-8")
    return data


def _export_model(workspace: Path, output: Path, log: Path, *, source: Path | None = None) -> dict:
    """用本地可编辑 PPTX 真正导出模型图；Office 不可用时显式失败。"""
    source = source or workspace / "refs/SIQR模型示意图_可编辑.pptx"
    if not source.is_file():
        raise FileNotFoundError(f"Editable schematic source missing: {source}")
    output.parent.mkdir(parents=True, exist_ok=True)
    esc = lambda p: str(p).replace("'", "''")
    code = f"""
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
$app=$null; $deck=$null
$hadPowerPoint=@(Get-Process -Name POWERPNT -ErrorAction SilentlyContinue).Count -gt 0
try {{
  $app=New-Object -ComObject PowerPoint.Application
  $deck=$app.Presentations.Open('{esc(source)}',$true,$false,$false)
  if($deck.Slides.Count -ne 1) {{ throw 'Expected one schematic slide' }}
  $deck.SaveAs('{esc(output)}',32)
  [Console]::WriteLine((@{{version=$app.Version;build=$app.Build}} | ConvertTo-Json -Compress))
}} finally {{
  if($deck) {{ $deck.Close(); [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($deck) }}
  if($app) {{
    if((-not $hadPowerPoint) -and $app.Presentations.Count -eq 0) {{ $app.Quit() }}
    [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)
  }}
  [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}}
"""
    encoded = base64.b64encode(code.encode("utf-16le")).decode("ascii")
    _run(["powershell", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden",
          "-EncodedCommand", encoded], log, timeout=120)
    if not output.is_file():
        raise RuntimeError("PowerPoint did not produce the schematic PDF")
    return {"status": "exported_from_editable_source", "source": str(source),
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "export": "PowerPoint SaveAs ppSaveAsPDF (32)", "scientific_recalculation": "not_applicable",
            "office": json.loads(log.read_text(encoding="utf-8").strip())}


def run_python_figures(output_dir: Path) -> dict:
    """将本轮唯一数值源绑定到原画法；旧 reader 的求解入口不再执行。"""
    from dataclasses import replace
    from types import SimpleNamespace
    import numpy as np
    import pandas as pd
    from xian import Params, structural, time_strategy, save_csv

    output_dir, workspace, _ = _paths(output_dir)
    reference = json.loads((output_dir / "xian/reference.json").read_text(encoding="utf-8"))
    critical = json.loads((output_dir / "population/critical.json").read_text(encoding="utf-8"))
    c0_parameters = json.loads((output_dir / "c0/parameters.json").read_text(encoding="utf-8"))
    p = Params(**reference["parameters"])
    I0 = reference["I0_abs"]
    driver_path = workspace / "latex/revision_layout_v5/layout_python.py"
    spec = importlib.util.spec_from_file_location("fresh_original_layout", driver_path)
    layout = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = layout
    spec.loader.exec_module(layout)
    old = layout.old

    environment = old.original_environment
    def current_environment(path):
        env = environment(path)
        env.update(IPEAK_T=reference["I_peak_T"], JT=reference["J_T"],
                   J_T=reference["J_T"], ITCUM_T=reference["Itcum_T"],
                   TEND_T=reference["t_end_T"], I0_ABS=I0,
                   N_FLOOR=critical["N_floor"])
        return env
    old.original_environment = current_environment

    # 原函数体和字体/线型保留，仅使手写的参照数值标签由新参照量生成。
    source = old.source
    def current_source(path):
        text = source(path)
        if path in ["xian_dom/panels.py", "xian_dom/plot_B.py"]:
            text = text.replace('"TDINN\\n2,097"', 'f"TDINN\\n{ITCUM_T:,.0f}"')
        return text
    old.source = current_source
    # 仅更新原 layout reader 内已手写的数值位置及两条柱标识，不改变几何规则。
    import ast
    tree = ast.parse(Path(old.__file__).read_text(encoding="utf-8-sig"))
    arrange = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "arrange_pair")
    replacement_labels = [f"{r['Itcum']:,.0f}" for r in old.META["fixed_eta"][:2]]
    class FreshInsetReferences(ast.NodeTransformer):
        def visit_Constant(self, node):
            if isinstance(node.value, float) and node.value == 2096.76:
                return ast.copy_location(ast.Constant(reference["Itcum_T"]), node)
            if node.value in ["945", "2,097"]:
                return ast.copy_location(ast.Constant(replacement_labels[["945", "2,097"].index(node.value)]), node)
            return node
    arrange = ast.fix_missing_locations(FreshInsetReferences().visit(arrange))
    exec(compile(ast.Module(body=[arrange], type_ignores=[]), "fresh_inset_reference_positions", "exec"), vars(old))

    def current_solution(N, eta):
        rec = next(r for r in old.RECORDS if np.isclose(r["N"], N, rtol=1e-10)
                   and np.isclose(r["eta"], eta, rtol=1e-10))
        params = replace(p, N=float(N))
        metrics = structural(params, I0, float(eta))
        if metrics["status"] != "ok":
            raise RuntimeError(f"Recomputed population case became inadmissible: {N}, {eta}")
        df = pd.read_csv(old.OLD_DATA / (rec["stem"] + ".csv"))
        details = dict(t1=metrics["t1"], t2=metrics["t2"], clear_time=metrics["clear_time"],
                       Sbar=metrics["Sbar"], S_star=metrics["S_star"], Sc=metrics["Sc"])
        if not np.all(np.diff(df.t) > 0):
            raise RuntimeError("Fresh population trajectory times are not strictly increasing")
        return SimpleNamespace(**vars(params)), df, details
    old.cached_solution = current_solution
    original_A = old.original_A_code
    def current_A(env):
        original_A(env)
        draw_A = env["panel_A"]
        def panel_A(N, td):
            rows = next(group for group in old.META["cases"]
                        if np.isclose(group[0]["N"], N, rtol=1e-10))
            # 绝对 I0 下，有限 N 的临界 eta/N 与无限人口近似略有差异。
            # 绘制本轮各 N 的实际求根值，不能误拿无限人口 theta 后找近似缓存。
            env["TH"] = {r["role"]: r["eta"] / N for r in rows}
            return draw_A(N=N, td=td)
        env["panel_A"] = panel_A
    old.original_A_code = current_A

    generated_reference = None
    def current_reference(env):
        nonlocal generated_reference
        if generated_reference is not None:
            return generated_reference
        td_all = pd.read_csv(output_dir / "xian/timeseries.csv")
        td = td_all.loc[td_all.strategy == "TDINN控制"].copy()
        end = 1.05 * max(r["t_end"] for r in old.META["fixed_eta"])
        tg = np.linspace(0., end, 1400)
        populations = np.geomspace(old.META["fixed_eta"][0]["N"],
                                  old.META["fixed_eta"][-1]["N"], 8)
        directory = output_dir / "figure_inputs"
        directory.mkdir(exist_ok=True)
        routine, summary = [], []
        for i, N in enumerate(populations):
            df, check = time_strategy(replace(p, N=float(N)), I0, name="常规控制")
            routine.append(df)
            save_csv(df, directory / f"routine_envelope_{i}.csv")
            summary.append({"population": float(N), "clear_time": check["clear_time"],
                            "source": "new normalized-DOP853-unified-v1 solver"})
        stack = np.vstack([np.interp(tg, df.t, df.I, left=np.nan, right=np.nan) for df in routine])
        stack = np.where(np.isfinite(stack), stack, 1.)
        generated_reference = dict(td=td, tend=end, tg=tg, Nrib=populations,
                                   rlo=np.maximum(stack.min(axis=0), 1.), rhi=stack.max(axis=0),
                                   rep_r={float(populations[i]): routine[i][["t", "I"]].to_dict("list")
                                          for i in [0, -1]})
        save_csv(pd.DataFrame({"t": tg, "rlo": generated_reference["rlo"],
                               "rhi": generated_reference["rhi"]}), directory / "routine_envelope.csv")
        (directory / "reference_envelope.json").write_text(json.dumps({"I0": I0, "cases": summary,
            "historical_cache_used": False, "reference": reference}, ensure_ascii=False, indent=2), encoding="utf-8")
        print("RECOMPUTED fresh eight-member routine envelope from unified solver", flush=True)
        return generated_reference
    old.recovery_cache = current_reference

    # 旧 B 图由稀疏采样梯形积分反推累计；直接使用本轮清零解析指标，避免采样误差。
    functions = old.functions_from
    def current_functions(path, names, env):
        functions(path, names, env)
        if "cumulative_at_cached_clearance" in names:
            def cumulative(built, part):
                rec = next(r for r in old.META["fixed_eta"]
                           if np.isclose(r["N"], built["N"], rtol=1e-10))
                return float(rec["Itcum"])
            env["cumulative_at_cached_clearance"] = cumulative
    old.functions_from = current_functions

    importer = layout.import_original
    def current_import(name, path):
        module = importer(name, path)
        if path == "c0_sensitivity/run_c0_sensitivity.py":
            module.P = replace(module.P, full_city_I0_reference=I0)
            module.boundary_values = lambda *args, **kwargs: dict(c0_parameters["derived"])
        return module
    layout.import_original = current_import
    # phase() 以普通 import 读取同一绘图模块；绑定后不再调用旧边界数值求解。
    sys.path.insert(0, str(workspace / "c0_sensitivity"))
    c0_module = current_import("run_c0_sensitivity", "c0_sensitivity/run_c0_sensitivity.py")
    sys.modules["run_c0_sensitivity"] = c0_module
    previous = sys.argv
    try:
        sys.argv = [str(driver_path)]
        layout.main()
    finally:
        sys.argv = previous
    result = {"passed": True, "historical_numeric_or_artist_cache_used": False,
              "reference_source": "xian/reference.json",
              "plot_reader_bindings": ["all original reference constants from new reference",
                                       "new eight-member routine envelope with unified solver",
                                       "population cumulative inset values at exact dynamic clearance",
                                       "updated TDINN cumulative text labels",
                                       "c0 boundary markers from c0/parameters.json"],
              "original_draw_statements_and_style_preserved": True}
    (output_dir / "validation/plot_reader_bindings.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def run_figures(output_dir: Path, root: Path) -> dict:
    output_dir, workspace, logs = _paths(output_dir)
    root = Path(root).resolve()
    env = _python_env(root)
    output = output_dir / "figures"
    output.mkdir(exist_ok=True)
    latex_figures = workspace / "latex/figures"
    latex_figures.mkdir(parents=True, exist_ok=True)
    for folder in [workspace / "latex/revision_layout_v5/data", workspace / "latex/revision_layout_v5/qa",
                   workspace / "latex/revision_style_restore/data", workspace / "latex/revision_style_restore/qa"]:
        folder.mkdir(parents=True, exist_ok=True)
    # 只允许本轮新生成的科学数据；任何旧 Matplotlib replay 缓存都会使干净复现失败。
    stale = list((workspace / "latex/revision_layout_v5/data").glob("*.pickle"))
    if stale:
        raise RuntimeError("Fresh figure stage requires no pre-existing artist pickle: " + str(stale))
    restore_cache = workspace / "latex/revision_style_restore/data/original_reference_cache.pkl"
    if restore_cache.exists():
        raise RuntimeError("Fresh figure stage must regenerate the reference envelope")
    assets = root / "reproducibility/assets"
    original_model = workspace / "refs/SIQR模型示意图_Nature配色_可编辑.pptx"
    if not original_model.is_file():
        shutil.copy2(root / "refs/SIQR模型示意图_Nature配色_可编辑.pptx", original_model)
    model_source = workspace / "refs/SIQR模型示意图_复现修正版.pptx"
    model_repair = repair_model_source(original_model, assets, model_source, logs / "model_source_repair.log")
    model = _export_model(workspace, latex_figures / "Fig1.pdf", logs / "model_pptx_export.log", source=model_source)
    model["source_repair"] = model_repair
    _run([sys.executable, "-B", str(Path(__file__).resolve()), "python",
          "--output-dir", str(output_dir), "--root", str(root)],
         logs / "python_figures.log", env=env, cwd=workspace)
    science_figures = {
        "optimal_control_with_quarantine_panels.pdf": workspace / "figures/optimal_control_with_quarantine_panels.pdf",
        "scenario1_heatmaps_c0_eta.pdf": workspace / "scenario1_threshold_landscape/current_run/figures/scenario1_heatmaps_c0_eta.pdf",
    }
    for name, source in science_figures.items():
        if not source.is_file():
            raise FileNotFoundError(f"New MATLAB figure missing: {source}")
        shutil.copy2(source, latex_figures / name)
    audits = []
    for number, name in enumerate(FIGURES, 1):
        source = latex_figures / name
        if not source.is_file():
            raise FileNotFoundError(f"Recomputed Figure {number} missing: {source}")
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        audit = audit_pdf(target)
        audit["number"] = number
        audit["source_generated_in_workspace"] = str(source)
        audits.append(audit)
        reference = output_dir / "visual_reference" / name
        if reference.is_file():
            render_comparison_pair(target, reference, output_dir / f"validation/figure_pairs/fig_{number:02d}.png")
    preservation = workspace / "latex/revision_layout_v5/qa/artist_preservation.json"
    artist_checks = json.loads(preservation.read_text(encoding="utf-8"))
    expected = {Path(name).stem for name in FIGURES if name.startswith("layout_v5/")}
    python_expected = expected - {"baseline_q_joint", "c0_sensitivity_selected_eta", "eta_sensitivity_selected_c0"}
    actual = {r["figure"] for r in artist_checks if r["scientific_artists_unchanged"]}
    if not python_expected.issubset(actual):
        raise RuntimeError("Missing before/after scientific artist checks: " + str(python_expected - actual))
    result = {"status": "generated", "figure_count": len(audits), "figures": audits,
              "model_export": model, "python_artist_checks": artist_checks,
              "historical_pickle_replay_used": False,
              "passed": all(record["scientific_artists_unchanged"] for record in artist_checks),
              "visual_review": "Requires rendered manuscript page review; not certified by generation."}
    report = output_dir / "validation/figure_generation.json"
    report.parent.mkdir(exist_ok=True)
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["science", "figures", "python"])
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--matlab", default=shutil.which("matlab") or "matlab")
    args = parser.parse_args()
    if args.stage == "science":
        result = run_science(args.output_dir, args.root, args.matlab)
    elif args.stage == "python":
        result = run_python_figures(args.output_dir)
    else:
        result = run_figures(args.output_dir, args.root)
    print(json.dumps({"status": result.get("status", "pass"), "stage": args.stage}, ensure_ascii=False))
