# NR-3 N1：回归与保留数字核对

登记 265 个数字：{'consistent': 265}。判定：consistent = 复算值按显示位数舍入后与显示值一致；display_differs = 不一致但相对差 ≤ 1%；stop = 相对差 > 1%。

## 表 2（两条路径与旧值的最大相对差）

| 参数 | 控制 | 状态路径–旧值 | 完整方程–旧值 | 完整方程–状态路径 |
|---|---|---|---|---|
| base | c_only | 2.4e-14 | 7.4e-14 | 5.0e-14 |
| base | alpha | 3.8e-13 | 4.7e-14 | 3.8e-13 |
| base | q_only | 3.0e-13 | 5.3e-14 | 3.0e-13 |
| base | opt | 7.9e-13 | 8.2e-13 | 1.9e-13 |
| xian | c_only | 2.3e-13 | 2.4e-13 | 2.2e-13 |
| xian | alpha | 3.6e-13 | 6.2e-15 | 3.6e-13 |
| xian | q_only | 3.5e-13 | 2.6e-14 | 3.4e-13 |
| xian | opt | 1.1e-11 | 1.2e-11 | 3.9e-13 |

## 显示值与复算不一致或需注意的项

| id | 位置 | 显示 | 复算 | 判定 | 说明 |
|---|---|---|---|---|---|

## 定性陈述

| id | 陈述 | 成立 |
|---|---|---|
| cap.base.joint_required | 代表点只有联合控制可行 | 是 |
| cap.base.higher | 能力约束下成本最优控制的 J 与 Δt 都高于表 2 | 是 |
| cap.base.qcap_until_h | 启动后一段内隔离比例停在上限，直到 S 降到 (1-q0)S_c/(1-q_cap) | 是 |
| cap.xian.joint_required | 代表点只有联合控制可行 | 是 |
| cap.xian.higher | 能力约束下成本最优控制的 J 与 Δt 都高于表 2 | 是 |
| cap.xian.qcap_until_h | 启动后一段内隔离比例停在上限，直到 S 降到 (1-q0)S_c/(1-q_cap) | 是 |
| s62.c0_interior_max | Δt 随 c0 先增后减（所考察的范围内取得内部极大） | 是 |
| s63.base.front_half | 前段完成阈值控制期 S 下降的一半以上 | 是 |
| s63.xian.front_half | 前段完成阈值控制期 S 下降的一半以上 | 是 |
| s63.base.peak_in_back | 基准参数下峰值出现在后段（两者并用段） | 是 |
| s63.xian.peak_in_front_equal | 西安参数下峰值在前段，仅隔离与成本最优控制的峰值相同 | 是 |
| s63.base.order | 控制时长从长到短：仅减少接触、α = 0.5、成本最优、仅隔离 | 是 |
| s63.base.Sstar_above_Ssw | S* 高于 S_sw | 是 |
| s63.xian.order | 控制时长从长到短：仅减少接触、α = 0.5、成本最优、仅隔离 | 是 |
| s63.xian.Sstar_above_Ssw | S* 高于 S_sw | 是 |
| s65.frontier_points | 乘子曲线由 470 个点构成 | 是 |
| S5.interior_maxima | 三个极大值都在扫描范围内部 | 是 |
| S2.q0dagger.beta0.1.interior | q0† 在 [0, 0.39] 内部 | 是 |
| S2.q0dagger.beta0.12.interior | q0† 在 [0, 0.39] 内部 | 是 |
| S2.q0dagger.beta0.155.interior | q0† 在 [0, 0.39] 内部 | 是 |

## 旧实现的数值（不是本模块能复现的量）

| 项 | 稿件值 | 含义 | 本模块对应值 |
|---|---|---|---|
| S6_plateau_base_ode45 | 1.07e-7 | 旧 ode45 基准轨迹的阈值控制期 max|I-η|（人） | 2.09e-11 |
| S6_plateau_xian_xianpy | 1.35e-6 | 旧 xian.py 仅隔离控制的 max|I-η|（人） | 5.93e-10 |
| S6_tdinn_tolerance | 3.61e-8 | 旧 xian.py 收紧容差后 TDINN 总累计的变化（人） | 1.41e-11 |
