import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sq_return import simulate, XIAN, make_alloc
plt.rcParams.update({'font.family': ['Noto Sans CJK SC', 'Noto Sans CJK TC', 'DejaVu Sans'],
                     'axes.unicode_minus': False, 'font.size': 9,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.edgecolor': '#8a8a85', 'axes.labelcolor': '#3b3b38',
                     'xtick.color': '#5c5c58', 'ytick.color': '#5c5c58'})
p = XIAN; N, eta = p['N'], p['eta']
col = {'q_only': '#2a78d6', 'optimal': '#eb6834', 'c_only': '#1baf7a'}
lab = {'q_only': '仅隔离', 'optimal': '联合（无返回下的最优分配）', 'c_only': '仅接触'}
runs = {}
for pol in col:
    al = make_alloc(p, pol)
    for lam in (0.0, 1/14):
        runs[(pol, lam)] = simulate(p, pol, lam=lam, T=4000., alloc=al, rec=1.0)
fig, ax = plt.subplots(2, 2, figsize=(10, 6.6), constrained_layout=True)
Sc = runs[('q_only', 0.0)]['Sc']
panels = [(ax[0, 0], lambda tr: tr[:, 1] / N, '(a) 社区易感者 $S/N$'),
          (ax[0, 1], lambda tr: tr[:, 3] / N, '(b) 隔离易感者存量 $S_q/N$'),
          (ax[1, 0], lambda tr: (tr[:, 2] + tr[:, 4]) / eta, '(c) 感染者总数 $(I+I_q)/\\eta$'),
          (ax[1, 1], lambda tr: tr[:, 6] / N, '(d) 累计感染 / $N$')]
for a, f, title in panels:
    for (pol, lam), r in runs.items():
        tr = r['traj']
        a.plot(tr[:, 0], f(tr), color=col[pol], lw=2 if lam > 0 else 1.4,
               ls='-' if lam > 0 else (0, (4, 2)))
    a.set_title(title, loc='left', fontsize=10, color='#1f1f1d')
    a.set_xlim(0, 1500); a.set_xlabel('时间（天）')
    a.grid(axis='y', color='#e4e4df', lw=0.6)
ax[0, 0].axhline(Sc / N, color='#8a8a85', lw=0.8, ls=':')
ax[0, 0].text(1490, Sc / N + 0.015, '$S_c/N$', ha='right', color='#5c5c58')
ax[1, 0].axhline(1, color='#8a8a85', lw=0.8, ls=':')
ax[1, 0].text(1490, 1.12, '$\\eta$', ha='right', color='#5c5c58')
from matplotlib.lines import Line2D
h = [Line2D([], [], color=col[k], lw=2, label=lab[k]) for k in col]
h += [Line2D([], [], color='#5c5c58', lw=1.4, ls=(0, (4, 2)), label='不返回（原模型，λ=0）'),
      Line2D([], [], color='#5c5c58', lw=2, label='返回（λ=1/14）')]
fig.legend(handles=h, loc='outside lower center', ncol=5, frameon=False, fontsize=9)
fig.suptitle('西安参数：隔离易感者是否返回对阈值控制的影响（η=0.002N，权重 1:2）', fontsize=11, x=0.01, ha='left')
fig.savefig('figures/sq_return_xian.png', dpi=170)
fig.savefig('figures/sq_return_xian.pdf')
for (pol, lam), r in runs.items():
    print(pol, lam, 'tctrl=%.1f' % r['tctrl'], 'inf/N=%.3f' % (r['inf'] / N), 'Sqpk/N=%.3f' % (r['pk']['Sq'] / N),
          'IIqpk/eta=%.2f' % (r['pk']['Iq_plus_I'] / eta), 'sqin/N=%.2f' % (r['sq_in'] / N))
