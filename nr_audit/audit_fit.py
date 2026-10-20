"""NR-3 N5：西安拟合误差的重建（不重新拟合，不优化新的 I0）。

原定义（只读复核，原文件未改动、未运行）：
- 观测数据：真实数据/Xianguankong.xlsx，由 xian_control_comparison/xian_control_comparison.py 的 load_observed_data
  处理（列 Date、I_new、Iq_new；按日期排序；t = 距首日的天数；累计 = 当日及以前的日新增之和）；处理结果存于
  reproducibility/results/20261003_release_final/xian/observed.csv。本脚本按同一规则独立读取原始表格，并与 observed.csv 核对。
- 拟合准则：reproducibility/xian.py 的 fit_initial——时间原点 t = 0 为 2021-12-09 的开始，第 k 行观测对应日区间 [k, k+1]；
  模型日新增为进入 I（社区）与进入 I_q（隔离）的流量在该区间上的积分，模型累计为 k+1 时刻的累计流量（自 t = 0 起，
  不含初始感染者）；四项为社区日新增、隔离日新增、社区累计、隔离累计的均方误差，等权相加。
- 控制函数：稿件式 (7.1) 的 TDINN 函数（tdinn.py）。
本脚本在给定的未取整 I0（fit.json）下重算四项误差，并重算补充表 tab:sup:initial 的拟合行与固定 I0 = 1 的对照行。

运行：conda run --no-capture-output -n thesis python nr_audit/audit_fit.py
输出：results/fit_reconstruction.json、results/fit_reconstruction.md
"""
import numpy as np
import pandas as pd

import params as PR
import sources as SRC
import tdinn as TD
from audit_common import RESULTS, ROOT, Registry, dump, rel, tex_table_rows

# S3 及 S2tab 证据 ID 保留 NR 历史身份；当前稿件表格位于 NEW-4g 的 S6。
S3 = 'paper/supplement_sections/S6_xian.tex'
XT = 'paper/sections/07_xian.tex'


def load_raw():
    raw = pd.read_excel(ROOT / '真实数据' / 'Xianguankong.xlsx')
    df = raw.rename(columns={'Date': 'date', 'I_new': 'community_new', 'Iq_new': 'quarantine_new'}).copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    df['t'] = (df['date'] - df['date'].iloc[0]).dt.days.astype(float)
    df['community_cum'] = df['community_new'].cumsum()
    df['quarantine_cum'] = df['quarantine_new'].cumsum()
    return df


def errors(P, obs):
    out, sol = TD.run(P, TD.tdinn, t_stop=float(len(obs)))
    m = TD.daily(P, sol, days=len(obs))
    keys = ('community_new', 'quarantine_new', 'community_cum', 'quarantine_cum')
    mse = {k: float(np.mean((m[k] - obs[k].to_numpy(float)) ** 2)) for k in keys}
    pred = np.r_[m['community_new'], m['quarantine_new']]
    data = np.r_[obs['community_new'].to_numpy(float), obs['quarantine_new'].to_numpy(float)]
    return dict(mse=mse, objective=sum(mse.values()), raw_rmse_daily=float(np.sqrt(np.mean((pred - data) ** 2))),
                cumulative_40=float(m['community_cum'][-1] + m['quarantine_cum'][-1]),
                community_daily_peak=float(m['community_new'].max()), quarantine_daily_peak=float(m['quarantine_new'].max()),
                mass_residual_persons=out['mass_residual_persons'], identity_residual_rel=out['identity_residual_rel'],
                model_daily={k: m[k].tolist() for k in keys})


def main():
    X = PR.XIAN
    raw = load_raw()
    obs_csv = pd.read_csv(ROOT / 'reproducibility/results/20261003_release_final/xian/observed.csv', encoding='utf-8-sig')
    cols = ['community_new', 'quarantine_new', 'community_cum', 'quarantine_cum', 't']
    same = all(np.array_equal(raw[c].to_numpy(float), obs_csv[c].to_numpy(float)) for c in cols)
    dates = (str(raw['date'].iloc[0].date()), str(raw['date'].iloc[-1].date()), len(raw))
    fit = SRC.load_json('xian_fit')
    e_fit = errors(X, raw)
    e_one = errors(X.with_(I0=1.0, S0=X.N - 1.0), raw)
    REG = Registry()
    REG.add('fit.objective', 'reproducibility/.../xian/fit.json:objective', f"{fit['objective']:.10f}", e_fit['objective'],
            old=fit['objective'], old_source='fit.json:objective')
    REG.add('fit.raw_rmse', 'fit.json:raw_rmse', f"{fit['raw_rmse']:.10f}", e_fit['raw_rmse_daily'],
            old=fit['raw_rmse'], old_source='fit.json:raw_rmse')
    rows = tex_table_rows(S3, 'tab:sup:initial')
    obs_row, fit_row, one_row = rows
    REG.add('S2tab.obs.cum40', f'{S3} 表 tab:sup:initial', obs_row[2], float(raw['community_cum'].iloc[-1] + raw['quarantine_cum'].iloc[-1]))
    REG.add('S2tab.obs.peak_c', f'{S3} 表 tab:sup:initial', obs_row[3], float(raw['community_new'].max()))
    REG.add('S2tab.obs.peak_q', f'{S3} 表 tab:sup:initial', obs_row[4], float(raw['quarantine_new'].max()))
    REG.add('S2tab.fit.I0', f'{S3} 表 tab:sup:initial', fit_row[1], X.I0)
    for row, e, tag in ((fit_row, e_fit, 'fit'), (one_row, e_one, 'I0=1')):
        REG.add(f'S2tab.{tag}.cum40', f'{S3} 表 tab:sup:initial', row[2], e['cumulative_40'])
        REG.add(f'S2tab.{tag}.peak_c', f'{S3} 表 tab:sup:initial', row[3], e['community_daily_peak'])
        REG.add(f'S2tab.{tag}.peak_q', f'{S3} 表 tab:sup:initial', row[4], e['quarantine_daily_peak'])
    REG.add('s71.community_total', f'{XT} §7.1', '583', float(raw['community_cum'].iloc[-1]))
    REG.add('s71.quarantine_total', f'{XT} §7.1', '1467', float(raw['quarantine_cum'].iloc[-1]))
    REG.add('s71.total', f'{XT} §7.1', '2050', float(raw['community_cum'].iloc[-1] + raw['quarantine_cum'].iloc[-1]))
    REG.add('s71.I0_one_cum40', f'{XT} §7.1', '1.08e6', e_one['cumulative_40'])
    dump('fit_reconstruction.json', dict(
        description=__doc__.split('\n\n')[0],
        data=dict(raw_file='真实数据/Xianguankong.xlsx', raw_sha256=SRC.sha256(ROOT / '真实数据' / 'Xianguankong.xlsx'),
                  first_date=dates[0], last_date=dates[1], n_days=dates[2], equals_observed_csv=same),
        definition=dict(time_origin='t = 0 为 2021-12-09 的开始；第 k 行观测对应 [k, k+1]',
                        model_observables='社区 = 进入 I 的流量；隔离 = 进入 I_q 的流量；日新增为区间积分，累计为 k+1 时刻的累计（自 t = 0）',
                        terms=['社区日新增 MSE', '隔离日新增 MSE', '社区累计 MSE', '隔离累计 MSE'], weights=[1, 1, 1, 1],
                        I0=X.I0, refit=False),
        at_fit_I0=e_fit, at_I0_one=e_one, registry=REG.rows, registry_summary=REG.summary()))
    L = ['# NR-3 N5：西安拟合误差的重建', '',
         f'原始表格 {dates[2]} 行（{dates[0]} 至 {dates[1]}），按原规则处理后与 observed.csv 逐项相同：{same}。'
         f'在给定 I0 = {X.I0}（不重新拟合）下：', '',
         '| 项 | 均方误差 |', '|---|---|']
    for k, v in e_fit['mse'].items():
        L.append(f'| {k} | {v:.10g} |')
    L += [f"| 合计（拟合准则） | {e_fit['objective']:.10g}（fit.json：{fit['objective']:.10g}，相对差 {rel(e_fit['objective'], fit['objective']):.1e}） |",
          f"| 日新增均方根（两类合并） | {e_fit['raw_rmse_daily']:.10g}（fit.json：{fit['raw_rmse']:.10g}） |", '',
          f'登记 {len(REG.rows)} 个数字：{REG.summary()}。', '',
          '| id | 显示 | 复算 | 判定 |', '|---|---|---|---|']
    for r in REG.rows:
        L.append(f"| {r['id']} | {r['display']} | {r['value']:.10g} | {r['status']} |")
    (RESULTS / 'fit_reconstruction.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
