# nr_audit 测试结果（full）

- 运行：2026-10-15T22:33:39，166.7 s；pytest 退出码 0
- 计数：passed 246
- 运行时 HEAD：`60c2b2fd73115ec0369b8f2d432ff585e83f5e40`；nr_audit 未提交改动：有（见 JSON）
- 环境：Python 3.10.20，numpy 2.2.5，scipy 1.15.3，sympy 1.14.0，pytest 9.1.1；Windows-10-10.0.26200-SP0

| 测试 | 结果 | 耗时 (s) | 记录的实测量 |
|---|---|---|---|
| `test_allocation.py::test_poly_x_is_derivative_numerator` | passed | 0.172 |  |
| `test_allocation.py::test_poly_x_matches_manuscript_eq_5_4` | passed | 0.162 |  |
| `test_allocation.py::test_poly_y_is_derivative_numerator` | passed | 1.402 |  |
| `test_allocation.py::test_roots_vs_grid[base-r0.1-k-0.4-free]` | passed | 0.065 | max_gap_rel = 3.26e-16 |
| `test_allocation.py::test_roots_vs_grid[base-r0.1-k-0.4-cap]` | passed | 0.067 | max_gap_rel = 4.89e-16 |
| `test_allocation.py::test_roots_vs_grid[base-r0.1-k0.0-free]` | passed | 0.09 | max_gap_rel = 5.37e-15 |
| `test_allocation.py::test_roots_vs_grid[base-r0.1-k0.0-cap]` | passed | 0.165 | max_gap_rel = 5.37e-15 |
| `test_allocation.py::test_roots_vs_grid[base-r0.1-k0.3-free]` | passed | 0.164 | max_gap_rel = 0 |
| `test_allocation.py::test_roots_vs_grid[base-r0.1-k0.3-cap]` | passed | 0.165 | max_gap_rel = 0 |
| `test_allocation.py::test_roots_vs_grid[base-r0.5-k-0.4-free]` | passed | 0.133 | max_gap_rel = 5.71e-16 |
| `test_allocation.py::test_roots_vs_grid[base-r0.5-k-0.4-cap]` | passed | 0.117 | max_gap_rel = 6.26e-16 |
| `test_allocation.py::test_roots_vs_grid[base-r0.5-k0.0-free]` | passed | 0.198 | max_gap_rel = 1.73e-14 |
| `test_allocation.py::test_roots_vs_grid[base-r0.5-k0.0-cap]` | passed | 0.173 | max_gap_rel = 1.73e-14 |
| `test_allocation.py::test_roots_vs_grid[base-r0.5-k0.3-free]` | passed | 0.163 | max_gap_rel = 0 |
| `test_allocation.py::test_roots_vs_grid[base-r0.5-k0.3-cap]` | passed | 0.153 | max_gap_rel = 0 |
| `test_allocation.py::test_roots_vs_grid[base-r2.0-k-0.4-free]` | passed | 0.118 | max_gap_rel = 3.91e-15 |
| `test_allocation.py::test_roots_vs_grid[base-r2.0-k-0.4-cap]` | passed | 0.122 | max_gap_rel = 0 |
| `test_allocation.py::test_roots_vs_grid[base-r2.0-k0.0-free]` | passed | 0.176 | max_gap_rel = 6.66e-14 |
| `test_allocation.py::test_roots_vs_grid[base-r2.0-k0.0-cap]` | passed | 0.159 | max_gap_rel = 6.66e-14 |
| `test_allocation.py::test_roots_vs_grid[base-r2.0-k0.3-free]` | passed | 0.204 | max_gap_rel = 0 |
| `test_allocation.py::test_roots_vs_grid[base-r2.0-k0.3-cap]` | passed | 0.184 | max_gap_rel = 0 |
| `test_allocation.py::test_roots_vs_grid[base-r5.0-k-0.4-free]` | passed | 0.124 | max_gap_rel = 3.7e-14 |
| `test_allocation.py::test_roots_vs_grid[base-r5.0-k-0.4-cap]` | passed | 0.105 | max_gap_rel = 0 |
| `test_allocation.py::test_roots_vs_grid[base-r5.0-k0.0-free]` | passed | 0.157 | max_gap_rel = 3.22e-14 |
| `test_allocation.py::test_roots_vs_grid[base-r5.0-k0.0-cap]` | passed | 0.149 | max_gap_rel = 3.22e-14 |
| `test_allocation.py::test_roots_vs_grid[base-r5.0-k0.3-free]` | passed | 0.174 | max_gap_rel = 3.51e-16 |
| `test_allocation.py::test_roots_vs_grid[base-r5.0-k0.3-cap]` | passed | 0.186 | max_gap_rel = 3.51e-16 |
| `test_allocation.py::test_roots_vs_grid[base-r20.0-k-0.4-free]` | passed | 0.125 | max_gap_rel = 5.67e-15 |
| `test_allocation.py::test_roots_vs_grid[base-r20.0-k-0.4-cap]` | passed | 0.123 | max_gap_rel = 0 |
| `test_allocation.py::test_roots_vs_grid[base-r20.0-k0.0-free]` | passed | 0.131 | max_gap_rel = 1.4e-13 |
| `test_allocation.py::test_roots_vs_grid[base-r20.0-k0.0-cap]` | passed | 0.149 | max_gap_rel = 1.4e-13 |
| `test_allocation.py::test_roots_vs_grid[base-r20.0-k0.3-free]` | passed | 0.18 | max_gap_rel = 2.8e-16 |
| `test_allocation.py::test_roots_vs_grid[base-r20.0-k0.3-cap]` | passed | 0.129 | max_gap_rel = 2.18e-16 |
| `test_allocation.py::test_roots_vs_grid[xian-r0.1-k-0.4-free]` | passed | 0.134 | max_gap_rel = 3.42e-16 |
| `test_allocation.py::test_roots_vs_grid[xian-r0.1-k-0.4-cap]` | passed | 0.142 | max_gap_rel = 2.52e-16 |
| `test_allocation.py::test_roots_vs_grid[xian-r0.1-k0.0-free]` | passed | 0.187 | max_gap_rel = 5.02e-14 |
| `test_allocation.py::test_roots_vs_grid[xian-r0.1-k0.0-cap]` | passed | 0.169 | max_gap_rel = 5.02e-14 |
| `test_allocation.py::test_roots_vs_grid[xian-r0.1-k0.3-free]` | passed | 0.161 | max_gap_rel = 0 |
| `test_allocation.py::test_roots_vs_grid[xian-r0.1-k0.3-cap]` | passed | 0.192 | max_gap_rel = 0 |
| `test_allocation.py::test_roots_vs_grid[xian-r0.5-k-0.4-free]` | passed | 0.131 | max_gap_rel = 1.16e-15 |
| `test_allocation.py::test_roots_vs_grid[xian-r0.5-k-0.4-cap]` | passed | 0.128 | max_gap_rel = 6.12e-16 |
| `test_allocation.py::test_roots_vs_grid[xian-r0.5-k0.0-free]` | passed | 0.167 | max_gap_rel = 1.69e-13 |
| `test_allocation.py::test_roots_vs_grid[xian-r0.5-k0.0-cap]` | passed | 0.168 | max_gap_rel = 1.69e-13 |
| `test_allocation.py::test_roots_vs_grid[xian-r0.5-k0.3-free]` | passed | 0.165 | max_gap_rel = 0 |
| `test_allocation.py::test_roots_vs_grid[xian-r0.5-k0.3-cap]` | passed | 0.162 | max_gap_rel = 0 |
| `test_allocation.py::test_roots_vs_grid[xian-r2.0-k-0.4-free]` | passed | 0.137 | max_gap_rel = 4.42e-15 |
| `test_allocation.py::test_roots_vs_grid[xian-r2.0-k-0.4-cap]` | passed | 0.115 | max_gap_rel = 0 |
| `test_allocation.py::test_roots_vs_grid[xian-r2.0-k0.0-free]` | passed | 0.167 | max_gap_rel = 1.01e-15 |
| `test_allocation.py::test_roots_vs_grid[xian-r2.0-k0.0-cap]` | passed | 0.164 | max_gap_rel = 1.01e-15 |
| `test_allocation.py::test_roots_vs_grid[xian-r2.0-k0.3-free]` | passed | 0.192 | max_gap_rel = 3.91e-16 |
| `test_allocation.py::test_roots_vs_grid[xian-r2.0-k0.3-cap]` | passed | 0.171 | max_gap_rel = 3.91e-16 |
| `test_allocation.py::test_roots_vs_grid[xian-r5.0-k-0.4-free]` | passed | 0.127 | max_gap_rel = 5.05e-15 |
| `test_allocation.py::test_roots_vs_grid[xian-r5.0-k-0.4-cap]` | passed | 0.102 | max_gap_rel = 1.4e-16 |
| `test_allocation.py::test_roots_vs_grid[xian-r5.0-k0.0-free]` | passed | 0.149 | max_gap_rel = 6.3e-16 |
| `test_allocation.py::test_roots_vs_grid[xian-r5.0-k0.0-cap]` | passed | 0.144 | max_gap_rel = 6.3e-16 |
| `test_allocation.py::test_roots_vs_grid[xian-r5.0-k0.3-free]` | passed | 0.155 | max_gap_rel = 5.47e-16 |
| `test_allocation.py::test_roots_vs_grid[xian-r5.0-k0.3-cap]` | passed | 0.156 | max_gap_rel = 5.47e-16 |
| `test_allocation.py::test_roots_vs_grid[xian-r20.0-k-0.4-free]` | passed | 0.127 | max_gap_rel = 2.3e-14 |
| `test_allocation.py::test_roots_vs_grid[xian-r20.0-k-0.4-cap]` | passed | 0.094 | max_gap_rel = 0 |
| `test_allocation.py::test_roots_vs_grid[xian-r20.0-k0.0-free]` | passed | 0.141 | max_gap_rel = 1.86e-13 |
| `test_allocation.py::test_roots_vs_grid[xian-r20.0-k0.0-cap]` | passed | 0.115 | max_gap_rel = 1.86e-13 |
| `test_allocation.py::test_roots_vs_grid[xian-r20.0-k0.3-free]` | passed | 0.154 | max_gap_rel = 3.6e-16 |
| `test_allocation.py::test_roots_vs_grid[xian-r20.0-k0.3-cap]` | passed | 0.119 | max_gap_rel = 2.77e-16 |
| `test_allocation.py::test_argmin_triple_root_minimum` | passed | 0.001 |  |
| `test_allocation.py::test_argmin_double_root_saddle` | passed | 0.001 |  |
| `test_allocation.py::test_argmin_tie` | passed | 0.001 |  |
| `test_allocation.py::test_capacity_bounds_formula` | passed | 0.001 |  |
| `test_allocation.py::test_capacity_infeasible_and_equality` | passed | 1.72 |  |
| `test_allocation.py::test_switch_equals_S_sw[base]` | passed | 1.769 | z_switch = 2.27；z_sw_formula = 2.27 |
| `test_allocation.py::test_switch_equals_S_sw[xian]` | passed | 1.855 | z_switch = 2.55；z_sw_formula = 2.55 |
| `test_allocation.py::test_structure_classes[base-r1.0]` | passed | 1.743 |  |
| `test_allocation.py::test_structure_classes[base-r5.0]` | passed | 2.095 |  |
| `test_allocation.py::test_structure_classes[base-r20.0]` | passed | 2.846 |  |
| `test_allocation.py::test_structure_classes[xian-r1.0]` | passed | 1.771 |  |
| `test_allocation.py::test_structure_classes[xian-r5.0]` | passed | 2.803 |  |
| `test_allocation.py::test_structure_classes[xian-r20.0]` | passed | 2.471 |  |
| `test_allocation.py::test_switch_regression_phase[base-baseline-4.977]` | passed | 2.211 | S_rel_diff = 4.48e-12 |
| `test_allocation.py::test_switch_regression_phase[base-baseline-12.17]` | passed | 2.91 | S_rel_diff = 5.11e-13 |
| `test_allocation.py::test_switch_regression_phase[xian-xian-3.131]` | passed | 2.215 | S_rel_diff = 1.65e-14 |
| `test_allocation.py::test_switch_regression_phase[xian-xian-4.977]` | passed | 2.724 | S_rel_diff = 1.67e-15 |
| `test_allocation.py::test_contact_only_never_selected[0.1-base]` | passed | 0.124 |  |
| `test_allocation.py::test_contact_only_never_selected[0.1-xian]` | passed | 0.121 |  |
| `test_allocation.py::test_contact_only_never_selected[1.0-base]` | passed | 0.138 |  |
| `test_allocation.py::test_contact_only_never_selected[1.0-xian]` | passed | 0.125 |  |
| `test_allocation.py::test_contact_only_never_selected[2.0-base]` | passed | 0.146 |  |
| `test_allocation.py::test_contact_only_never_selected[2.0-xian]` | passed | 0.163 |  |
| `test_allocation.py::test_contact_only_never_selected[5.0-base]` | passed | 0.194 |  |
| `test_allocation.py::test_contact_only_never_selected[5.0-xian]` | passed | 0.249 |  |
| `test_allocation.py::test_contact_only_never_selected[20.0-base]` | passed | 0.253 |  |
| `test_allocation.py::test_contact_only_never_selected[20.0-xian]` | passed | 0.236 |  |
| `test_allocation.py::test_default_weight_labels[base]` | passed | 0.282 |  |
| `test_allocation.py::test_default_weight_labels[xian]` | passed | 0.272 |  |
| `test_allocation.py::test_terminal_share[0.5]` | passed | 0.013 |  |
| `test_allocation.py::test_terminal_share[2.0]` | passed | 0.015 |  |
| `test_allocation.py::test_terminal_share[7.0]` | passed | 0.014 |  |
| `test_allocation.py::test_capacity_structure_matches_reference` | passed | 3.635 |  |
| `test_allocation.py::test_continuous_switch_is_endpoint[base-3.2143]` | passed | 1.97 |  |
| `test_allocation.py::test_continuous_switch_is_endpoint[base-3.17]` | passed | 1.865 |  |
| `test_allocation.py::test_continuous_switch_is_endpoint[xian-2.7137]` | passed | 1.948 |  |
| `test_allocation.py::test_continuous_switch_is_endpoint[xian-2.7]` | passed | 1.86 |  |
| `test_model.py::test_mass_and_susceptible_flux` | passed | 0.002 |  |
| `test_model.py::test_no_return_term` | passed | 0.001 |  |
| `test_model.py::test_plateau_balance[base]` | passed | 0.001 |  |
| `test_model.py::test_plateau_balance[xian]` | passed | 0.001 |  |
| `test_model.py::test_intensities_and_cost` | passed | 0.0 |  |
| `test_numbers.py::test_tex_matches_map` | passed | 0.001 |  |
| `test_numbers.py::test_map_values_trace_to_results` | passed | 0.002 |  |
| `test_numbers.py::test_registry_has_no_stop` | passed | 0.002 |  |
| `test_simulate.py::test_conservation_positivity[base-q_only]` | passed | 0.105 | mass_residual_persons = 5.45e-11；min_compartment_persons = 0 |
| `test_simulate.py::test_conservation_positivity[base-c_only]` | passed | 0.176 | mass_residual_persons = 5.45e-11；min_compartment_persons = 0 |
| `test_simulate.py::test_conservation_positivity[base-alpha]` | passed | 0.098 | mass_residual_persons = 5.45e-11；min_compartment_persons = 0 |
| `test_simulate.py::test_conservation_positivity[base-opt]` | passed | 3.337 | mass_residual_persons = 5.45e-11；min_compartment_persons = 0 |
| `test_simulate.py::test_conservation_positivity[xian-q_only]` | passed | 0.636 | mass_residual_persons = 3.65e-08；min_compartment_persons = 0 |
| `test_simulate.py::test_conservation_positivity[xian-c_only]` | passed | 1.24 | mass_residual_persons = 7.31e-08；min_compartment_persons = 0 |
| `test_simulate.py::test_conservation_positivity[xian-alpha]` | passed | 0.773 | mass_residual_persons = 2.78e-08；min_compartment_persons = 0 |
| `test_simulate.py::test_conservation_positivity[xian-opt]` | passed | 6.053 | mass_residual_persons = 2.05e-08；min_compartment_persons = 0 |
| `test_simulate.py::test_control_feasibility[base-q_only]` | passed | 0.0 |  |
| `test_simulate.py::test_control_feasibility[base-c_only]` | passed | 0.0 |  |
| `test_simulate.py::test_control_feasibility[base-alpha]` | passed | 0.0 |  |
| `test_simulate.py::test_control_feasibility[base-opt]` | passed | 0.0 |  |
| `test_simulate.py::test_control_feasibility[xian-q_only]` | passed | 0.0 |  |
| `test_simulate.py::test_control_feasibility[xian-c_only]` | passed | 0.0 |  |
| `test_simulate.py::test_control_feasibility[xian-alpha]` | passed | 0.0 |  |
| `test_simulate.py::test_control_feasibility[xian-opt]` | passed | 0.0 |  |
| `test_simulate.py::test_events[base-q_only]` | passed | 0.035 | t1_rel = 1.83e-14；exit_S_error_persons = -2.31e-12 |
| `test_simulate.py::test_events[base-c_only]` | passed | 0.016 | t1_rel = 1.83e-14；exit_S_error_persons = -4.07e-12 |
| `test_simulate.py::test_events[base-alpha]` | passed | 0.016 | t1_rel = 1.83e-14；exit_S_error_persons = -1.91e-12 |
| `test_simulate.py::test_events[base-opt]` | passed | 1.389 | t1_rel = 1.83e-14；exit_S_error_persons = 1.5e-11 |
| `test_simulate.py::test_events[xian-q_only]` | passed | 0.013 | t1_rel = 6.31e-16；exit_S_error_persons = -1.35e-08 |
| `test_simulate.py::test_events[xian-c_only]` | passed | 0.012 | t1_rel = 6.31e-16；exit_S_error_persons = -2.41e-08 |
| `test_simulate.py::test_events[xian-alpha]` | passed | 0.014 | t1_rel = 6.31e-16；exit_S_error_persons = -3.29e-09 |
| `test_simulate.py::test_events[xian-opt]` | passed | 1.434 | t1_rel = 6.31e-16；exit_S_error_persons = 3.93e-07 |
| `test_simulate.py::test_flux_identities[base-q_only]` | passed | 0.0 | identity_residual_rel = 3.34e-16 |
| `test_simulate.py::test_flux_identities[base-c_only]` | passed | 0.0 | identity_residual_rel = 3.34e-16 |
| `test_simulate.py::test_flux_identities[base-alpha]` | passed | 0.001 | identity_residual_rel = 3.89e-16 |
| `test_simulate.py::test_flux_identities[base-opt]` | passed | 0.0 | identity_residual_rel = 2.78e-16 |
| `test_simulate.py::test_flux_identities[xian-q_only]` | passed | 0.0 | identity_residual_rel = 1.61e-15 |
| `test_simulate.py::test_flux_identities[xian-c_only]` | passed | 0.0 | identity_residual_rel = 7.97e-15 |
| `test_simulate.py::test_flux_identities[xian-alpha]` | passed | 0.0 | identity_residual_rel = 9.99e-16 |
| `test_simulate.py::test_flux_identities[xian-opt]` | passed | 0.0 | identity_residual_rel = 6.11e-16 |
| `test_simulate.py::test_plateau_not_reset[base-q_only]` | passed | 0.0 | plateau_abs_dev_persons = 2.09e-11 |
| `test_simulate.py::test_plateau_not_reset[base-c_only]` | passed | 0.0 | plateau_abs_dev_persons = 4.85e-12 |
| `test_simulate.py::test_plateau_not_reset[base-alpha]` | passed | 0.0 | plateau_abs_dev_persons = 7.82e-12 |
| `test_simulate.py::test_plateau_not_reset[base-opt]` | passed | 0.0 | plateau_abs_dev_persons = 1.41e-11 |
| `test_simulate.py::test_plateau_not_reset[xian-q_only]` | passed | 0.0 | plateau_abs_dev_persons = 5.93e-10 |
| `test_simulate.py::test_plateau_not_reset[xian-c_only]` | passed | 0.0 | plateau_abs_dev_persons = 1.51e-09 |
| `test_simulate.py::test_plateau_not_reset[xian-alpha]` | passed | 0.0 | plateau_abs_dev_persons = 6.91e-10 |
| `test_simulate.py::test_plateau_not_reset[xian-opt]` | passed | 0.0 | plateau_abs_dev_persons = 6.44e-10 |
| `test_simulate.py::test_open_loop_sensitivity` | passed | 0.09 | perturbed_plateau_rel_dev = 4.07e-07；unperturbed_plateau_rel_dev = 5.47e-13 |
| `test_simulate.py::test_ode_vs_state_path[base-q_only]` | passed | 0.0 | max_rel = 2.98e-13 |
| `test_simulate.py::test_ode_vs_state_path[base-c_only]` | passed | 0.0 | max_rel = 5.22e-14 |
| `test_simulate.py::test_ode_vs_state_path[base-alpha]` | passed | 0.0 | max_rel = 4.57e-13 |
| `test_simulate.py::test_ode_vs_state_path[base-opt]` | passed | 0.0 | max_rel = 1.06e-12 |
| `test_simulate.py::test_ode_vs_state_path[xian-q_only]` | passed | 0.0 | max_rel = 3.75e-13 |
| `test_simulate.py::test_ode_vs_state_path[xian-c_only]` | passed | 0.0 | max_rel = 2.24e-13 |
| `test_simulate.py::test_ode_vs_state_path[xian-alpha]` | passed | 0.0 | max_rel = 3.63e-13 |
| `test_simulate.py::test_ode_vs_state_path[xian-opt]` | passed | 0.0 | max_rel = 3.93e-13 |
| `test_simulate.py::test_regression_compare_ode[base-q_only]` | passed | 0.004 | max_rel = 1.19e-13 |
| `test_simulate.py::test_regression_compare_ode[base-c_only]` | passed | 0.0 | max_rel = 1.19e-13 |
| `test_simulate.py::test_regression_compare_ode[base-alpha]` | passed | 0.0 | max_rel = 1.19e-13 |
| `test_simulate.py::test_regression_compare_ode[base-opt]` | passed | 0.0 | max_rel = 1.73e-12 |
| `test_simulate.py::test_regression_compare_ode[xian-q_only]` | passed | 0.0 | max_rel = 1.16e-13 |
| `test_simulate.py::test_regression_compare_ode[xian-c_only]` | passed | 0.0 | max_rel = 2.43e-13 |
| `test_simulate.py::test_regression_compare_ode[xian-alpha]` | passed | 0.0 | max_rel = 1.16e-13 |
| `test_simulate.py::test_regression_compare_ode[xian-opt]` | passed | 0.0 | max_rel = 1.36e-11 |
| `test_simulate.py::test_q_only_closed_form_trajectory[base]` | passed | 0.004 | S_max_rel = 6.71e-14 |
| `test_simulate.py::test_q_only_closed_form_trajectory[xian]` | passed | 0.006 | S_max_rel = 5.77e-15 |
| `test_simulate.py::test_whole_epidemic_shift[base]` | passed | 0.0 | max_rel = 9.14e-13 |
| `test_simulate.py::test_whole_epidemic_shift[xian]` | passed | 0.0 | max_rel = 5.71e-13 |
| `test_simulate.py::test_post_exit_monotone[base-q_only]` | passed | 0.002 |  |
| `test_simulate.py::test_post_exit_monotone[base-c_only]` | passed | 0.001 |  |
| `test_simulate.py::test_post_exit_monotone[base-alpha]` | passed | 0.001 |  |
| `test_simulate.py::test_post_exit_monotone[base-opt]` | passed | 0.001 |  |
| `test_simulate.py::test_post_exit_monotone[xian-q_only]` | passed | 0.007 |  |
| `test_simulate.py::test_post_exit_monotone[xian-c_only]` | passed | 0.005 |  |
| `test_simulate.py::test_post_exit_monotone[xian-alpha]` | passed | 0.006 |  |
| `test_simulate.py::test_post_exit_monotone[xian-opt]` | passed | 0.017 |  |
| `test_simulate.py::test_infinite_time_tail[base-q_only]` | passed | 0.001 |  |
| `test_simulate.py::test_infinite_time_tail[base-c_only]` | passed | 0.001 |  |
| `test_simulate.py::test_infinite_time_tail[base-alpha]` | passed | 0.001 |  |
| `test_simulate.py::test_infinite_time_tail[base-opt]` | passed | 0.001 |  |
| `test_simulate.py::test_infinite_time_tail[xian-q_only]` | passed | 0.002 |  |
| `test_simulate.py::test_infinite_time_tail[xian-c_only]` | passed | 0.001 |  |
| `test_simulate.py::test_infinite_time_tail[xian-alpha]` | passed | 0.001 |  |
| `test_simulate.py::test_infinite_time_tail[xian-opt]` | passed | 0.001 |  |
| `test_simulate.py::test_capacity_ode[base-opt]` | passed | 7.047 | max_rel = 4.6e-12 |
| `test_simulate.py::test_capacity_ode[base-cap_upper]` | passed | 0.126 |  |
| `test_simulate.py::test_capacity_ode[base-cap_lower]` | passed | 0.148 |  |
| `test_simulate.py::test_capacity_ode[xian-opt]` | passed | 9.989 | max_rel = 3.19e-12 |
| `test_simulate.py::test_capacity_ode[xian-cap_upper]` | passed | 0.683 |  |
| `test_simulate.py::test_capacity_ode[xian-cap_lower]` | passed | 0.953 |  |
| `test_sources.py::test_manifest_current` | passed | 0.019 |  |
| `test_sources.py::test_pinned_files_unchanged` | passed | 0.005 |  |
| `test_sources.py::test_params_equal_source_fields[base]` | passed | 0.004 |  |
| `test_sources.py::test_params_equal_source_fields[xian]` | passed | 0.002 |  |
| `test_sources.py::test_derived_rules` | passed | 0.001 |  |
| `test_sources.py::test_audit_notes_I0` | passed | 0.0 |  |
| `test_sources.py::test_manuscript_table1_display` | passed | 0.001 |  |
| `test_sources.py::test_default_weights_in_manuscript` | passed | 0.0 |  |
| `test_sources.py::test_capacity_points` | passed | 0.001 |  |
| `test_sources.py::test_reference_columns` | passed | 0.001 |  |
| `test_sources.py::test_code_reuse_blobs` | passed | 0.12 |  |
| `test_state_integrals.py::test_start_state[base]` | passed | 0.0 | S_star = 708 |
| `test_state_integrals.py::test_start_state[xian]` | passed | 0.001 | S_star = 1.3e+07 |
| `test_state_integrals.py::test_post_exit[base]` | passed | 0.001 |  |
| `test_state_integrals.py::test_post_exit[xian]` | passed | 0.001 |  |
| `test_state_integrals.py::test_closed_forms[base]` | passed | 0.001 | max_rel = 3.81e-13 |
| `test_state_integrals.py::test_closed_forms[xian]` | passed | 0.001 | max_rel = 3.75e-13 |
| `test_state_integrals.py::test_simpson_vs_quad[base-q_only]` | passed | 0.0 | max_rel = 2.98e-13 |
| `test_state_integrals.py::test_simpson_vs_quad[base-c_only]` | passed | 0.0 | max_rel = 2.23e-14 |
| `test_state_integrals.py::test_simpson_vs_quad[base-alpha]` | passed | 0.0 | max_rel = 3.81e-13 |
| `test_state_integrals.py::test_simpson_vs_quad[base-opt]` | passed | 0.0 | max_rel = 1.5e-13 |
| `test_state_integrals.py::test_simpson_vs_quad[xian-q_only]` | passed | 0.0 | max_rel = 3.31e-13 |
| `test_state_integrals.py::test_simpson_vs_quad[xian-c_only]` | passed | 0.0 | max_rel = 2.85e-14 |
| `test_state_integrals.py::test_simpson_vs_quad[xian-alpha]` | passed | 0.0 | max_rel = 6.57e-14 |
| `test_state_integrals.py::test_simpson_vs_quad[xian-opt]` | passed | 0.0 | max_rel = 6.65e-14 |
| `test_state_integrals.py::test_arc_identities[base-q_only]` | passed | 0.0 |  |
| `test_state_integrals.py::test_arc_identities[base-c_only]` | passed | 0.0 |  |
| `test_state_integrals.py::test_arc_identities[base-alpha]` | passed | 0.0 |  |
| `test_state_integrals.py::test_arc_identities[base-opt]` | passed | 0.0 |  |
| `test_state_integrals.py::test_arc_identities[xian-q_only]` | passed | 0.0 |  |
| `test_state_integrals.py::test_arc_identities[xian-c_only]` | passed | 0.0 |  |
| `test_state_integrals.py::test_arc_identities[xian-alpha]` | passed | 0.0 |  |
| `test_state_integrals.py::test_arc_identities[xian-opt]` | passed | 0.0 |  |
| `test_state_integrals.py::test_duration_ordering[base]` | passed | 0.039 |  |
| `test_state_integrals.py::test_duration_ordering[xian]` | passed | 0.031 |  |
| `test_state_integrals.py::test_regression_compare_state[base-q_only]` | passed | 0.0 | max_rel = 2.98e-13 |
| `test_state_integrals.py::test_regression_compare_state[base-c_only]` | passed | 0.0 | max_rel = 1.01e-13 |
| `test_state_integrals.py::test_regression_compare_state[base-alpha]` | passed | 0.0 | max_rel = 3.81e-13 |
| `test_state_integrals.py::test_regression_compare_state[base-opt]` | passed | 0.0 | max_rel = 2.36e-13 |
| `test_state_integrals.py::test_regression_compare_state[xian-q_only]` | passed | 0.0 | max_rel = 1.76e-12 |
| `test_state_integrals.py::test_regression_compare_state[xian-c_only]` | passed | 0.0 | max_rel = 9.82e-13 |
| `test_state_integrals.py::test_regression_compare_state[xian-alpha]` | passed | 0.0 | max_rel = 1.58e-12 |
| `test_state_integrals.py::test_regression_compare_state[xian-opt]` | passed | 0.0 | max_rel = 1.7e-12 |
| `test_state_integrals.py::test_capacity_state[base]` | passed | 0.0 | max_rel = 4.96e-13 |
| `test_state_integrals.py::test_capacity_state[xian]` | passed | 0.0 | max_rel = 1.49e-12 |
| `test_state_integrals.py::test_Nz_convergence[base]` | passed | 2.458 | max_rel = 3.43e-13 |
| `test_state_integrals.py::test_Nz_convergence[xian]` | passed | 2.711 | max_rel = 2.06e-13 |
| `test_state_integrals.py::test_frontier_regression` | passed | 63.902 | max_rel = 1.35e-07 |
| `test_state_integrals.py::test_exit_lower_bound[base]` | passed | 0.0 |  |
| `test_state_integrals.py::test_exit_lower_bound[xian]` | passed | 0.0 |  |
| `test_state_integrals.py::test_minimum_cost_decreases_with_threshold` | passed | 6.717 |  |
| `test_tdinn.py::test_controls_at_origin` | passed | 0.0 |  |
| `test_tdinn.py::test_reference_regression` | passed | 0.001 | max_rel = 1.76e-11 |
| `test_tdinn.py::test_conservation` | passed | 0.0 |  |
| `test_tdinn.py::test_fit_objective_reconstruction` | passed | 0.866 | objective_rel = 4.91e-14 |
