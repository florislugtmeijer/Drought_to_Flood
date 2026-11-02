#!/bin/sh
# Every step of the R2 analysis in order, with the environment variables used
# for the reported runs. Run from the repository root after `uv sync --frozen`.
# Each script writes a dated folder under results/ and a manifest.yaml.
# Times are for a 2024 laptop; the three long steps are marked.
set -e
run() { echo; echo "== $*"; "$@"; }
P="uv run --frozen python"

run $P scripts/00_check_data.py

# --- ECA at the main definition: SRI < -1, flood quantile 0.8413, window 4 weeks
run env CELL=1.0,0.8413,4 OUT=results/2026-10-30_eca_poisson_strict $P scripts/09_sensitivity_grid.py          # analytical p, 4 min
run env OUT=results/2026-10-30_eca_cprime_strict SRI_THRESHOLDS=1.0 FLOOD_QUANTILES=0.8413 \
    $P scripts/37_sensitivity_grid_cprime.py                                                                   # stratified null, 4 min
run env GRID=results/2026-10-30_eca_poisson_strict/grid_results.csv PROD=results/2026-10-30_eca_cprime_strict/grid.csv \
    OUT=results/2026-10-30_table3_eca_strict THRESHOLD=1.0 FLOOD_Q=0.8413 $P scripts/39_table3_eca.py         # Table 3
run $P scripts/44_figure4_map.py                                                                                # Figure 4
run env THRESHOLD=1.0 OUT=results/2026-10-30_physical_table_strict RUN_DATE=2026-10-30 \
    GRID=results/2026-10-30_eca_poisson_strict/grid_results.csv $P scripts/27_physical_results_table.py        # event quantities, 4 min
run $P scripts/45_physical_table_cprime.py                                                                      # Table G1
run env THRESHOLD=1.0 $P scripts/46_definition_stats.py                                                         # numbers in 2.3 and 2.4.1

# --- Appendix F: sensitivity under the stratified null
run $P scripts/37_sensitivity_grid_cprime.py                                                                    # full grid, 40 min
run env OUT=results/2026-10-30_sensitivity_grid_strict_column FLOOD_QUANTILES=0.8413 \
    $P scripts/37_sensitivity_grid_cprime.py                                                                   # extra row, 10 min
run $P scripts/43_sensitivity_cprime_report.py                                                                  # Figure F1, Table F1
run $P scripts/44_figure4_map.py --sri 1.0                                                                      # Figure F2

# --- the milder definition quoted in the text (pooled ratio 1.25, 40 of 48)
run $P scripts/36_run_eca_null_production.py                                                                    # 4 min
run $P scripts/39_table3_eca.py                                                                                 # results/2026-10-27_table3_eca_cprime

# --- copula side: SRI < -0.5, transition probability read at the 0.6915 quantile
run $P scripts/22_bootstrap_transition_ci.py                                                                    # LONG: 3.5 h
run env EXTRA_Q=0.6915 OUT=results/2026-10-22_copula_bootstrap_6915 $P scripts/22_bootstrap_transition_ci.py   # LONG: 3.5 h
run $P scripts/25_dependence_tests.py                                                                           # LONG: 2 h
run $P scripts/40_copula_family_and_flood_level.py
run $P scripts/41_copula_figures.py                                                                             # Figures 5 to 9
run $P scripts/42_appendix_e_copula_table.py                                                                    # Table E1
run $P scripts/29_increase_criterion_counts.py
run $P scripts/28_copula_quantile_reference.py                                                                  # 5 min
run $P scripts/47_appendix_d_figures.py                                                                         # Appendix D, 5 min

# --- copula side at the stricter drought definition (Section 4)
run $P scripts/27_strict_definition_points.py                                                                   # 10 min
run env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 $P scripts/28_strict_bootstrap_and_tests.py                   # LONG: 3.5 h
run $P scripts/30_strict_post_drought_state.py

# --- diagnostics quoted in the text
run $P scripts/02_sri_diagnostic.py
run $P scripts/06_threshold_selectivity.py
run $P scripts/07_reference_grid.py                                                                             # 65 min
run $P scripts/08_reference_grid_report.py
