# NR-3 N5：西安拟合误差的重建

原始表格 40 行（2021-12-09 至 2022-01-17），按原规则处理后与 observed.csv 逐项相同：True。在给定 I0 = 0.00100659188867187（不重新拟合）下：

| 项 | 均方误差 |
|---|---|
| community_new | 47.32769946 |
| quarantine_new | 130.3831602 |
| community_cum | 387.2155458 |
| quarantine_cum | 471.8350566 |
| 合计（拟合准则） | 1036.761462（fit.json：1036.761462，相对差 4.9e-14） |
| 日新增均方根（两类合并） | 9.426315815（fit.json：9.426315815） |

登记 16 个数字：{'consistent': 16}。

| id | 显示 | 复算 | 判定 |
|---|---|---|---|
| fit.objective | 1036.7614620871 | 1036.761462 | consistent |
| fit.raw_rmse | 9.4263158152 | 9.426315815 | consistent |
| S2tab.obs.cum40 | 2050 | 2050 | consistent |
| S2tab.obs.peak_c | 60 | 60 | consistent |
| S2tab.obs.peak_q | 141 | 141 | consistent |
| S2tab.fit.I0 | 0.001007 | 0.001006591889 | consistent |
| S2tab.fit.cum40 | 2099 | 2098.974686 | consistent |
| S2tab.fit.peak_c | 53.88 | 53.88177981 | consistent |
| S2tab.fit.peak_q | 115.93 | 115.9334787 | consistent |
| S2tab.I0=1.cum40 | 1083553 | 1083553.043 | consistent |
| S2tab.I0=1.peak_c | 36873.64 | 36873.63712 | consistent |
| S2tab.I0=1.peak_q | 63966.50 | 63966.50133 | consistent |
| s71.community_total | 583 | 583 | consistent |
| s71.quarantine_total | 1467 | 1467 | consistent |
| s71.total | 2050 | 2050 | consistent |
| s71.I0_one_cum40 | 1.08e6 | 1083553.043 | consistent |
