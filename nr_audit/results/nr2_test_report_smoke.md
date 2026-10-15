# nr_audit 测试结果（smoke）

- 运行：2026-10-15T22:36:28，48.7 s；pytest 退出码 0
- 计数：passed 104
- 运行时 HEAD：`60c2b2fd73115ec0369b8f2d432ff585e83f5e40`；nr_audit 未提交改动：有（见 JSON）
- 环境：Python 3.10.20，numpy 2.2.5，scipy 1.15.3，sympy 1.14.0，pytest 9.1.1；Windows-10-10.0.26200-SP0

| 测试 | 结果 | 耗时 (s) | 记录的实测量 |
|---|---|---|---|
| `test_allocation.py::test_poly_x_is_derivative_numerator` | passed | 0.17 |  |
| `test_allocation.py::test_poly_x_matches_manuscript_eq_5_4` | passed | 0.16 |  |
| `test_allocation.py::test_poly_y_is_derivative_numerator` | passed | 1.406 |  |
| `test_allocation.py::test_argmin_triple_root_minimum` | passed | 0.001 |  |
| `test_allocation.py::test_argmin_double_root_saddle` | passed | 0.0 |  |
| `test_allocation.py::test_argmin_tie` | passed | 0.0 |  |
| `test_allocation.py::test_capacity_bounds_formula` | passed | 0.0 |  |
| `test_allocation.py::test_capacity_infeasible_and_equality` | passed | 1.309 |  |
| `test_allocation.py::test_switch_equals_S_sw[base]` | passed | 1.705 | z_switch = 2.27；z_sw_formula = 2.27 |
| `test_allocation.py::test_structure_classes[base-r1.0]` | passed | 1.678 |  |
| `test_allocation.py::test_structure_classes[base-r5.0]` | passed | 2.244 |  |
| `test_allocation.py::test_structure_classes[base-r20.0]` | passed | 2.683 |  |
| `test_allocation.py::test_switch_regression_phase[base-baseline-4.977]` | passed | 2.113 | S_rel_diff = 4.48e-12 |
| `test_allocation.py::test_switch_regression_phase[base-baseline-12.17]` | passed | 2.787 | S_rel_diff = 5.11e-13 |
| `test_allocation.py::test_default_weight_labels[base]` | passed | 0.287 |  |
| `test_allocation.py::test_terminal_share[0.5]` | passed | 0.016 |  |
| `test_allocation.py::test_terminal_share[2.0]` | passed | 0.013 |  |
| `test_allocation.py::test_terminal_share[7.0]` | passed | 0.014 |  |
| `test_allocation.py::test_capacity_structure_matches_reference` | passed | 3.698 |  |
| `test_allocation.py::test_continuous_switch_is_endpoint[base-3.2143]` | passed | 1.834 |  |
| `test_allocation.py::test_continuous_switch_is_endpoint[base-3.17]` | passed | 1.863 |  |
| `test_model.py::test_mass_and_susceptible_flux` | passed | 0.002 |  |
| `test_model.py::test_no_return_term` | passed | 0.001 |  |
| `test_model.py::test_plateau_balance[base]` | passed | 0.001 |  |
| `test_model.py::test_intensities_and_cost` | passed | 0.0 |  |
| `test_numbers.py::test_tex_matches_map` | passed | 0.001 |  |
| `test_numbers.py::test_map_values_trace_to_results` | passed | 0.002 |  |
| `test_numbers.py::test_registry_has_no_stop` | passed | 0.002 |  |
| `test_simulate.py::test_conservation_positivity[base-q_only]` | passed | 0.105 | mass_residual_persons = 5.45e-11；min_compartment_persons = 0 |
| `test_simulate.py::test_conservation_positivity[base-c_only]` | passed | 0.166 | mass_residual_persons = 5.45e-11；min_compartment_persons = 0 |
| `test_simulate.py::test_conservation_positivity[base-alpha]` | passed | 0.104 | mass_residual_persons = 5.45e-11；min_compartment_persons = 0 |
| `test_simulate.py::test_conservation_positivity[base-opt]` | passed | 3.424 | mass_residual_persons = 5.45e-11；min_compartment_persons = 0 |
| `test_simulate.py::test_control_feasibility[base-q_only]` | passed | 0.0 |  |
| `test_simulate.py::test_control_feasibility[base-c_only]` | passed | 0.0 |  |
| `test_simulate.py::test_control_feasibility[base-alpha]` | passed | 0.0 |  |
| `test_simulate.py::test_control_feasibility[base-opt]` | passed | 0.0 |  |
| `test_simulate.py::test_events[base-q_only]` | passed | 0.031 | t1_rel = 1.83e-14；exit_S_error_persons = -2.31e-12 |
| `test_simulate.py::test_events[base-c_only]` | passed | 0.01 | t1_rel = 1.83e-14；exit_S_error_persons = -4.07e-12 |
| `test_simulate.py::test_events[base-alpha]` | passed | 0.014 | t1_rel = 1.83e-14；exit_S_error_persons = -1.91e-12 |
| `test_simulate.py::test_events[base-opt]` | passed | 1.375 | t1_rel = 1.83e-14；exit_S_error_persons = 1.5e-11 |
| `test_simulate.py::test_flux_identities[base-q_only]` | passed | 0.0 | identity_residual_rel = 3.34e-16 |
| `test_simulate.py::test_flux_identities[base-c_only]` | passed | 0.0 | identity_residual_rel = 3.34e-16 |
| `test_simulate.py::test_flux_identities[base-alpha]` | passed | 0.0 | identity_residual_rel = 3.89e-16 |
| `test_simulate.py::test_flux_identities[base-opt]` | passed | 0.0 | identity_residual_rel = 2.78e-16 |
| `test_simulate.py::test_plateau_not_reset[base-q_only]` | passed | 0.0 | plateau_abs_dev_persons = 2.09e-11 |
| `test_simulate.py::test_plateau_not_reset[base-c_only]` | passed | 0.0 | plateau_abs_dev_persons = 4.85e-12 |
| `test_simulate.py::test_plateau_not_reset[base-alpha]` | passed | 0.0 | plateau_abs_dev_persons = 7.82e-12 |
| `test_simulate.py::test_plateau_not_reset[base-opt]` | passed | 0.0 | plateau_abs_dev_persons = 1.41e-11 |
| `test_simulate.py::test_open_loop_sensitivity` | passed | 0.093 | perturbed_plateau_rel_dev = 4.07e-07；unperturbed_plateau_rel_dev = 5.47e-13 |
| `test_simulate.py::test_ode_vs_state_path[base-q_only]` | passed | 0.0 | max_rel = 2.98e-13 |
| `test_simulate.py::test_ode_vs_state_path[base-c_only]` | passed | 0.0 | max_rel = 5.22e-14 |
| `test_simulate.py::test_ode_vs_state_path[base-alpha]` | passed | 0.0 | max_rel = 4.57e-13 |
| `test_simulate.py::test_ode_vs_state_path[base-opt]` | passed | 0.0 | max_rel = 1.06e-12 |
| `test_simulate.py::test_regression_compare_ode[base-q_only]` | passed | 0.003 | max_rel = 1.19e-13 |
| `test_simulate.py::test_regression_compare_ode[base-c_only]` | passed | 0.0 | max_rel = 1.19e-13 |
| `test_simulate.py::test_regression_compare_ode[base-alpha]` | passed | 0.0 | max_rel = 1.19e-13 |
| `test_simulate.py::test_regression_compare_ode[base-opt]` | passed | 0.0 | max_rel = 1.73e-12 |
| `test_simulate.py::test_q_only_closed_form_trajectory[base]` | passed | 0.005 | S_max_rel = 6.71e-14 |
| `test_simulate.py::test_whole_epidemic_shift[base]` | passed | 0.0 | max_rel = 9.14e-13 |
| `test_simulate.py::test_post_exit_monotone[base-q_only]` | passed | 0.002 |  |
| `test_simulate.py::test_post_exit_monotone[base-c_only]` | passed | 0.002 |  |
| `test_simulate.py::test_post_exit_monotone[base-alpha]` | passed | 0.002 |  |
| `test_simulate.py::test_post_exit_monotone[base-opt]` | passed | 0.002 |  |
| `test_simulate.py::test_infinite_time_tail[base-q_only]` | passed | 0.001 |  |
| `test_simulate.py::test_infinite_time_tail[base-c_only]` | passed | 0.0 |  |
| `test_simulate.py::test_infinite_time_tail[base-alpha]` | passed | 0.002 |  |
| `test_simulate.py::test_infinite_time_tail[base-opt]` | passed | 0.001 |  |
| `test_simulate.py::test_capacity_ode[base-opt]` | passed | 7.317 | max_rel = 4.6e-12 |
| `test_simulate.py::test_capacity_ode[base-cap_upper]` | passed | 0.143 |  |
| `test_simulate.py::test_capacity_ode[base-cap_lower]` | passed | 0.146 |  |
| `test_sources.py::test_manifest_current` | passed | 0.021 |  |
| `test_sources.py::test_pinned_files_unchanged` | passed | 0.004 |  |
| `test_sources.py::test_params_equal_source_fields[base]` | passed | 0.004 |  |
| `test_sources.py::test_derived_rules` | passed | 0.001 |  |
| `test_sources.py::test_audit_notes_I0` | passed | 0.001 |  |
| `test_sources.py::test_manuscript_table1_display` | passed | 0.002 |  |
| `test_sources.py::test_default_weights_in_manuscript` | passed | 0.001 |  |
| `test_sources.py::test_capacity_points` | passed | 0.001 |  |
| `test_sources.py::test_reference_columns` | passed | 0.002 |  |
| `test_sources.py::test_code_reuse_blobs` | passed | 0.115 |  |
| `test_state_integrals.py::test_start_state[base]` | passed | 0.001 | S_star = 708 |
| `test_state_integrals.py::test_post_exit[base]` | passed | 0.001 |  |
| `test_state_integrals.py::test_closed_forms[base]` | passed | 0.001 | max_rel = 3.81e-13 |
| `test_state_integrals.py::test_simpson_vs_quad[base-q_only]` | passed | 0.0 | max_rel = 2.98e-13 |
| `test_state_integrals.py::test_simpson_vs_quad[base-c_only]` | passed | 0.0 | max_rel = 2.23e-14 |
| `test_state_integrals.py::test_simpson_vs_quad[base-alpha]` | passed | 0.0 | max_rel = 3.81e-13 |
| `test_state_integrals.py::test_simpson_vs_quad[base-opt]` | passed | 0.001 | max_rel = 1.5e-13 |
| `test_state_integrals.py::test_arc_identities[base-q_only]` | passed | 0.0 |  |
| `test_state_integrals.py::test_arc_identities[base-c_only]` | passed | 0.0 |  |
| `test_state_integrals.py::test_arc_identities[base-alpha]` | passed | 0.0 |  |
| `test_state_integrals.py::test_arc_identities[base-opt]` | passed | 0.0 |  |
| `test_state_integrals.py::test_duration_ordering[base]` | passed | 0.045 |  |
| `test_state_integrals.py::test_regression_compare_state[base-q_only]` | passed | 0.0 | max_rel = 2.98e-13 |
| `test_state_integrals.py::test_regression_compare_state[base-c_only]` | passed | 0.0 | max_rel = 1.01e-13 |
| `test_state_integrals.py::test_regression_compare_state[base-alpha]` | passed | 0.0 | max_rel = 3.81e-13 |
| `test_state_integrals.py::test_regression_compare_state[base-opt]` | passed | 0.0 | max_rel = 2.36e-13 |
| `test_state_integrals.py::test_capacity_state[base]` | passed | 0.0 | max_rel = 4.96e-13 |
| `test_state_integrals.py::test_Nz_convergence[base]` | passed | 2.448 | max_rel = 3.43e-13 |
| `test_state_integrals.py::test_exit_lower_bound[base]` | passed | 0.0 |  |
| `test_state_integrals.py::test_minimum_cost_decreases_with_threshold` | passed | 6.48 |  |
| `test_tdinn.py::test_controls_at_origin` | passed | 0.001 |  |
| `test_tdinn.py::test_reference_regression` | passed | 0.001 | max_rel = 1.76e-11 |
| `test_tdinn.py::test_conservation` | passed | 0.0 |  |
| `test_tdinn.py::test_fit_objective_reconstruction` | passed | 0.978 | objective_rel = 4.91e-14 |
