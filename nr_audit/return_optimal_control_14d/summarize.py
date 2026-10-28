"""只读取本轮结果，生成汇总、保护审计和科学图；不运行优化或ODE。"""
import csv
import hashlib
import json
import pathlib
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.family']=['Microsoft YaHei','DejaVu Sans']
plt.rcParams['axes.unicode_minus']=False

HERE=pathlib.Path(__file__).resolve().parent
REPO=HERE.parents[1]
OUT=HERE/'results'


def read(path):
    return json.loads(pathlib.Path(path).read_text(encoding='utf-8'))


def dump(path,obj):
    pathlib.Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')


def sha(path):
    h=hashlib.sha256()
    with pathlib.Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()


def full(item):
    return read(HERE/item['saved_path'])


def main():
    final=read(OUT/'final_evaluations.json')
    acceptance_path=OUT/'final_acceptance_v2.json'
    if not acceptance_path.exists():
        raise RuntimeError('等待经过审计修复的v2最终验收，禁止复用旧分类作最终结论')
    acceptance=read(acceptance_path)
    if not acceptance.get('complete'):
        raise RuntimeError('v2验收尚未齐备')
    entries=[]
    chosen={}
    for case in ['base','xian']:
        chosen[case]={}
        for objective in ['time','infections','cost']:
            result=full(acceptance['representatives'][f'{case}_{objective}']['DOP853'])
            if objective=='infections':
                # 感染目标平坦：选已核验的仅隔离作分辨率内最短代表，不声称形态唯一。
                role='感染分辨率内的仅隔离代表；感染最优形态未作唯一性判断'
            else:
                role='经核验的Radau160最佳数值候选'
            chosen[case][objective]=result
            interval=result['C_infinity_interval']
            row=dict(case=case,control=objective,duration_days=result['duration'],
                C_infinity_lower=interval[0],C_infinity_upper=interval[1],
                C_infinity_midpoint=sum(interval)/2,J_days=result['J'],
                C_infinity_estimate=interval[1],
                threshold_peak_ratio=result['threshold_peak_ratio'],feasible=result['feasible'],
                Sq_exit=result['Sq_exit'],role=role,evaluation_id=result['evaluation_id'])
            entries.append(row)
        for kind in ['q_only','c_only','opt_noreturn']:
            result=(chosen[case]['infections'] if kind=='q_only' else
                    read(OUT/'references'/f'{case}_{kind}.json'))
            chosen[case][kind]=result
            lo,hi=result['C_infinity_interval']
            entries.append(dict(case=case,control=kind,duration_days=result['duration'],
                C_infinity_lower=lo,C_infinity_upper=hi,C_infinity_midpoint=(lo+hi)/2,
                C_infinity_estimate=hi,
                J_days=result['J'],threshold_peak_ratio=result['threshold_peak_ratio'],
                feasible=result['feasible'],Sq_exit=result['Sq_exit'],role='同一14天模型的参照控制',
                evaluation_id=result['evaluation_id']))
    with (OUT/'summary.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=list(entries[0]))
        writer.writeheader();writer.writerows(entries)

    comparisons=[]
    for case in ['base','xian']:
        cost=next(r for r in entries if r['case']==case and r['control']=='cost')
        for kind in ['q_only','c_only','opt_noreturn']:
            ref=next(r for r in entries if r['case']==case and r['control']==kind)
            comparisons.append(dict(case=case,optimized='cost',reference=kind,
                duration_difference=cost['duration_days']-ref['duration_days'],
                duration_percent=100*(cost['duration_days']/ref['duration_days']-1),
                infections_difference=cost['C_infinity_estimate']-ref['C_infinity_estimate'],
                infections_percent=100*(cost['C_infinity_estimate']/ref['C_infinity_estimate']-1),
                cost_difference=cost['J_days']-ref['J_days'],
                cost_percent=100*(cost['J_days']/ref['J_days']-1)))

    optimize_log=[]
    for path in [OUT/'optimization_log.jsonl']:
        if path.exists():
            optimize_log += [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line]
    shooting=list((OUT/'shooting_attempts').glob('*.json'))
    eval_log=[json.loads(line) for line in (OUT/'evaluation_log.jsonl').read_text(encoding='utf-8').splitlines() if line]
    counts={'primary_NLP_calls':len(optimize_log),
        'primary_solver_success':sum(bool(r.get('solver_success')) for r in optimize_log),
        'shooting_NLP_calls':len(shooting),
        'shooting_solver_success':sum(bool(read(p).get('solver_success')) for p in shooting),
        'evaluation_log_entries':len(eval_log),
        'independent_solve_ivp_segment_calls':sum(r.get('ode_calls',0) for r in eval_log),
        'complete_trajectory_evaluations':sum('evaluation_id' in r and r.get('ode_calls',0)>0 for r in eval_log),
        'independent_start_integrations':sum(r.get('ode_calls',0) for r in eval_log if r.get('kind')=='prepare_start'),
        'initial_guess_solve_ivp_calls':len((OUT/'initial_guess_ode_log.jsonl').read_text(encoding='utf-8').splitlines()),
        'count_note':'完整轨迹可由多次分段ODE调用组成；不把分段调用数等同疫情轨迹数。优化内CVODES及shooting尾段评价另见求解器日志，不冒充独立验证。'}
    if (OUT/'shooting_overview.json').exists():
        shot=read(OUT/'shooting_overview.json')
        counts.update(shooting_internal_tail_IVP=shot['tail_internal_ivp_calls'],
                      shooting_independent_start_IVP=shot['independent_start_ivp_calls_outside_selfcheck'],
                      shooting_selfcheck_IVP=shot['selfcheck_ivp_calls'])
    testfile=OUT/'pytest_all.xml'
    tests={}
    if testfile.exists():
        suites=ET.parse(testfile).getroot().findall('testsuite')
        tests={key:sum(int(s.get(key,0)) for s in suites) for key in ['tests','failures','errors','skipped']}
    protected=read(OUT/'protected_initial.json')
    changed=[]
    for path,identity in protected.items():
        actual=REPO/path
        if not actual.exists() or sha(actual)!=identity['sha256']:
            changed.append(path)
    protection={'checked_files':len(protected),'changed':changed,'pass':not changed}
    dump(OUT/'protection_audit.json',protection)
    summary={'generated_utc':datetime.now(timezone.utc).isoformat(),'entries':entries,
             'cost_comparisons':comparisons,'counts':counts,'protection':protection,'tests':tests,
             'interpretation':'有限场景的数值最优候选；不证明一般全局最优。感染代表按数值分辨率选择仅隔离，不声明形态唯一。'}
    dump(OUT/'summary.json',summary)
    initial_manifest=OUT/'manifest_preflight.json'
    if not initial_manifest.exists():
        initial_manifest.write_bytes((OUT/'manifest.json').read_bytes())
    manifest=read(initial_manifest)
    manifest['preflight_snapshot']='results/manifest_preflight.json'
    manifest['execution_status']='completed'
    manifest['execution_counts']=counts
    manifest['scope']['new_scientific_optimization_calls']=counts['primary_NLP_calls']+counts['shooting_NLP_calls']
    manifest['current_code_sha256']={str(p.relative_to(HERE)):sha(p) for p in HERE.rglob('*.py')
        if '_runtime' not in p.parts and '__pycache__' not in p.parts and 'tmp' not in p.parts}
    manifest['final_acceptance']='results/final_acceptance_v2.json'
    manifest['final_protection']=protection
    dump(OUT/'manifest.json',manifest)

    # 科学图：曲线仅来自独立ODE验证轨迹，不重求或平滑科学数据。
    colors={'q_only':'#0072B2','cost':'#D55E00','opt_noreturn':'#009E73','c_only':'#CC79A7'}
    labels={'q_only':'仅隔离（最短时长；感染代表）', 'cost':'重新优化：最低成本',
            'opt_noreturn':'无回流最优律迁移','c_only':'仅减少接触'}
    for case in ['base','xian']:
        fig,axes=plt.subplots(2,3,figsize=(13,7.4),constrained_layout=True)
        for kind in ['q_only','cost','opt_noreturn','c_only']:
            data=chosen[case][kind];tr=data['trajectory'];t1=data['t1']
            tp=np.asarray(tr['t_platform'])-t1;yp=np.asarray(tr['states_platform'])
            tt=np.asarray(tr['t_post'])-t1;yt=np.asarray(tr['states_post'])
            color=colors[kind]
            axes[0,0].plot(tp,np.asarray(tr['c_platform'])/(10 if case=='base' else 12.8872),color=color,label=labels[kind])
            axes[0,1].plot(tp,tr['q_platform'],color=color)
            times=np.r_[tp,tt];states=np.vstack([yp,yt])
            theta=.05 if case=='base' else .002
            sc=(175.1601700006617/763) if case=='base' else (0.2953/(.1498*12.8872*(1-.323)))
            axes[0,2].plot(times,np.exp(states[:,1])/theta,color=color)
            axes[1,0].plot(times,states[:,0]/sc,color=color)
            axes[1,1].plot(times,states[:,2],color=color)
            axes[1,2].plot(tp,yp[:,6],color=color)
            axes[0,2].plot(data['duration'],1.,marker='o',ms=3,color=color)
            axes[1,0].plot(data['duration'],1.,marker='o',ms=3,color=color)
        for ax,title in zip(axes.ravel(),['接触率 c/c0','隔离比例 q','非隔离感染者 I/eta',
            '社区易感者 S/Sc','隔离易感者 Sq/N','累计二次强度成本 J']):
            ax.set_title(title);ax.set_xlabel('启动后的时间（天）');ax.grid(alpha=.2)
        axes[0,2].axhline(1,color='black',ls='--',lw=.8)
        axes[1,0].axhline(1,color='black',ls='--',lw=.8)
        axes[0,0].legend(fontsize=7)
        fig.suptitle(f"{'基准' if case=='base' else '西安'}参数：指数回流，平均停留14天；圆点表示退出")
        fig.savefig(OUT/f'{case}_controls_and_states.png',dpi=180)
        fig.savefig(OUT/f'{case}_controls_and_states.pdf')
        plt.close(fig)

    names={'time':'最短时长','infections':'最少全过程感染（分辨率内代表）','cost':'最低成本',
           'q_only':'仅隔离','c_only':'仅减少接触','opt_noreturn':'迁移律'}
    lines=['# 14天指数回流数值研究结果','',
        '本轮只研究两组固定参数与阈值策略；所有主结果要求退出后仍满足I≤eta，首次S=Sc退出后永久恢复常规措施，不释放、不重启。',
        '', '## 结果表','',
        '全过程累计感染不含初始感染者；不是首次I=1截断值。表中显示C(T)+B(T)的数值上界估计，具体区间保存在summary.json，尾界不包含控制离散化误差。J为原定义的控制期二次强度成本，单位为天。',
        '', '| 参数组 | 控制 | 控制时长（天） | 全过程累计感染（人） | J（天） | 退出后阈值 |',
        '|---|---|---:|---:|---:|---|']
    for row in entries:
        lines.append(f"| {row['case']} | {names[row['control']]} | {row['duration_days']:.6f} | {row['C_infinity_estimate']:.6f} | {row['J_days']:.9f} | {'数值核验通过' if row['feasible'] else '未通过'} |")
    lines += ['', '## 比较与解释','',
        '1. 两组最短时长均收敛到仅隔离。未发现全过程累计感染显著低于仅隔离的可行候选；感染目标存在平坦方向，西安部分不同控制时长的候选在感染上无法分辨。表中选仅隔离作为分辨率内且时长最短的代表；只能说本轮精度不能唯一确定感染最优形态，不是已证明非唯一性。',
        '2. 两组最低成本候选均在开始时接近仅隔离，随后两种措施并用；这只是本轮固定情景的数值结构。',
        '3. 重新优化相对参照的变化如下（正值表示增加）：', '',
        '| 参数组 | 参照 | 时长变化（天） | 全过程感染变化（人） | 成本变化（%） |',
        '|---|---|---:|---:|---:|']
    for row in comparisons:
        lines.append(f"| {row['case']} | {names[row['reference']]} | {row['duration_difference']:+.6f} | {row['infections_difference']:+.6f} | {row['cost_percent']:+.6f} |")
    lines += ['',
        '基准参数下，重新优化最低成本控制相对迁移律同时降低时长、全过程感染和成本。西安参数下，重新优化相对迁移律降低成本和累计感染，但控制期延长。',
        '', '## 核验证据与保留项','',
        '- 主方法为三阶Radau配点+IPOPT，八粗网格初值，20/40/80/160区间；独立方法为分段常控制的矩阵指数shooting+SLSQP。',
        '- 最终主候选用DOP853及Radau完整五仓室回放，未将I硬设为eta，未改duration使其通过。所有退出后峰值用S=Sc事件和稠密输出检查；取得U<Sc后用解析衰减和剩余感染界覆盖无限时间。',
        '- 粗网格失败原样保存：西安感染n20/n40及西安成本n20/n40/n80存在独立回放失败检查；n160最终候选通过。不能用求解器success代替独立核验。',
        '- 感染目标最初按C/N缩放时，局部停止导致比已知仅隔离略差的解；保留原结果，增加10000倍等价目标缩放的精度复核。西安感染最优形态在当前精度下无法唯一确定，不把较长的近等感染控制解释为独特最优结构。',
        '- 数值尾界与ODE/网格误差分开报告；结果不是区间算术认证，也没有一般全局最优证明。',
        '- 独立shooting80段与主配点160段的成本目标相对差：基准约1.87e-5、西安约5.75e-6。完整ODE核验后的最低成本候选附带累计感染跨离散差约0.00005人、1.50人；西安成本解的感染人数应按约2人的离散不确定度解释，不能把0.001人的尾界当作全部精度。',
        '- 审计修复了旧评价器把1e-7正超限直接通过、终端根记录为null仍通过的分类问题；v2重新评价并绑定评价器SHA，旧收据保留。最终峰值只出现约1e-14量级舍入偏差，记录为数值边界，不宣称严格认证。',
        f"- 本目录测试：{tests.get('tests',0)}项，失败{tests.get('failures',0)}、错误{tests.get('errors',0)}；不启动OCP的数学身份、事件与判定回归均通过。测试中的必要ODE评价另计入轨迹记录。",
        '- shooting80段的两组最低成本候选另外通过v2完整五仓ODE核验，见results/shooting_validation_v2.json。',
        '', '## 运行统计','', '```json',json.dumps(counts,ensure_ascii=False,indent=2),'```','',
        '优化内部的CVODES目标/约束及shooting尾段评价是优化计算的一部分，不属于独立完整轨迹核验。',
        '', '## 文件保护','',
        f"已重新核对{protection['checked_files']}个受保护文件；变更数{len(changed)}。未修改论文、冻结来源、参考文献或既有结果；没有推送。",
        '', '机器可读结果见summary.json/summary.csv；所有原始尝试、完整轨迹与核验见同目录子文件夹。']
    (HERE/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'summary_rows':len(entries),'counts':counts,'protection':protection},ensure_ascii=False))


if __name__=='__main__':
    main()
