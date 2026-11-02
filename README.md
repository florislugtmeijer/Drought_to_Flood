# Drought-to-flood transitions in European rivers: code, data and outputs

Code, input data and outputs for

> *A twofold probabilistic dependence analysis of drought-to-flood transitions in
> European rivers*, Journal of Hydrology, manuscript HYDROL79380, revision R2
> (November 2026).

This repository holds exactly one version of the analysis: the one reported in
revision R2. Every number, table and figure in the manuscript and its
appendices can be traced to a script here and regenerated from the input data
in `data/`. The methodological differences with the submitted version (R1) are
listed in `CHANGES.md`. The R1 computation itself is preserved unchanged in
`notebooks/` and verified in `docs/reproducibility-check.md`.

Comments and docstrings in the scripts are in Dutch (the working language of
the project); this README and `CHANGES.md` are in English.

## Contents

| path | what |
|---|---|
| `data/efas_v5_dis06_48_locations_1995_2024.nc` | daily discharge at 48 locations on 16 rivers, EFAS v5, 1995 to 2024 (1.5 MB). SHA256 in `data/manifest.yaml` |
| `src/dtf/pipeline.py` | event definition (SRI, flood quantiles, event extraction) and the event coincidence analysis, ported from the R1 notebook |
| `src/dtf/copula.py` | marginal fitting, copula selection and transition probabilities |
| `scripts/` | one script per step, numbered in the order they were written. Each writes a dated folder under `results/` with a `manifest.yaml` (script, inputs with SHA256, parameters) |
| `outputs/` | the outputs used in R2: `figures/`, `tables/` and the full result folders behind them (`outputs/results/`), copied verbatim from `results/` |
| `notebooks/` | the Colab notebook that produced the R1 results, unchanged |
| `docs/reproducibility-check.md` | proof that the notebook reproduces Table 3 of R1 exactly |
| `docs/function-provenance.md` | which notebook cell became which function in `src/dtf/` |
| `run_all.sh` | every step in order, with the exact environment variables used for the reported runs |
| `pyproject.toml`, `uv.lock` | the pinned environment (Python 3.12, numpy 2.5.2, scipy 1.18.1, pandas 3.0.5, xarray 2026.7.0, vinecopulas 2.0.3, matplotlib 3.11.1, cartopy 0.25.0) |

## Running it

Requirements: [uv](https://docs.astral.sh/uv/) and Python 3.12 (uv installs it
if needed). All commands run from the repository root.

```sh
uv sync --frozen                      # exact environment from uv.lock
uv run --frozen python scripts/00_check_data.py   # verifies the SHA256 of the input file
```

Then either run `./run_all.sh` (several hours, see the table below) or pick
single steps from it. Every script writes to its own folder under `results/`
and skips nothing silently: each run ends with a `manifest.yaml` that records
the script, the input files with their checksums and the parameters.

Random numbers are seeded. The Monte Carlo test uses a fixed seed per
location, the copula bootstrap uses `numpy.random.SeedSequence(42).spawn(96)`
(one stream per location and period), the dependence tests
`SeedSequence(43).spawn(96)`. Re-running a step therefore reproduces the
reported numbers exactly, not approximately.

## The analysis in order

Two parts, with two event definitions, as explained in Section 2.3 of the
manuscript:

- **Event coincidence analysis (ECA).** Droughts are weeks with SRI < −1,
  floods are weeks with the weekly maximum discharge above the 0.8413 quantile
  of the daily values of the same period (the quantile at the same
  standardised level). A transition is a flood starting in the four weeks after
  the last drought week. Significance is tested analytically under a Poisson
  assumption and by Monte Carlo under a stratified permutation null (10,000
  simulations per location and period).
- **Copula analysis.** Droughts at SRI < −0.5; the transition probability is
  read at the 0.6915 discharge quantile. Marginals by maximum likelihood,
  copula family by AIC among 15 families, 95% intervals by bootstrap
  (2,000 resamples).

| step | script | makes | time |
|---|---|---|---|
| ECA, analytical p (Poisson) at the main definition | `09_sensitivity_grid.py` with `CELL=1.0,0.8413,4` | `results/2026-10-30_eca_poisson_strict/` | 4 min |
| ECA, Monte Carlo p under the stratified null | `37_sensitivity_grid_cprime.py` with `SRI_THRESHOLDS=1.0 FLOOD_QUANTILES=0.8413` | `results/2026-10-30_eca_cprime_strict/` | 4 min |
| Table 3 | `39_table3_eca.py` | `results/2026-10-30_table3_eca_strict/` (table3.md, figure4_categories.csv, summary.md with the pooled ratio 1.07) | seconds |
| Figure 4 | `44_figure4_map.py` | `results/2026-10-30_figure4_map/` | seconds |
| event quantities per location | `27_physical_results_table.py` with `THRESHOLD=1.0` | `results/2026-10-30_physical_table_strict/` | 4 min |
| Table G1 (Appendix G) | `45_physical_table_cprime.py` | `results/2026-10-30_physical_table/` | seconds |
| numbers on the event definition in Sections 2.3 and 2.4.1 | `46_definition_stats.py` with `THRESHOLD=1.0` | `results/2026-10-30_definition_stats/` | 2 min |
| sensitivity grid under the stratified null (Appendix F) | `37_sensitivity_grid_cprime.py` (full grid, 5 × 5) and once more with `FLOOD_QUANTILES=0.8413` for the extra row | `results/2026-10-21_sensitivity_grid_cprime/`, `results/2026-10-30_sensitivity_grid_strict_column/` | 40 + 10 min |
| Figure F1 and Table F1 | `43_sensitivity_cprime_report.py` | `results/2026-10-30_sensitivity_cprime_report/` | seconds |
| Figure F2 (map at SRI −1, flood quantile 0.6915) | `44_figure4_map.py --sri 1.0` | `results/2026-10-30_figure4_map_sri1/` | seconds |
| the milder definition quoted in the text (pooled ratio 1.25, 40 of 48) | `36_run_eca_null_production.py` then `39_table3_eca.py` with its default inputs | `results/2026-10-21_eca_null_production/`, `results/2026-10-27_table3_eca_cprime/` | 4 min |
| copula bootstrap, 101 quantile levels | `22_bootstrap_transition_ci.py` | `results/2026-09-02_copula_bootstrap/` | 3.5 h |
| copula bootstrap with the 0.6915 level in the grid | `22_bootstrap_transition_ci.py` with `EXTRA_Q=0.6915 OUT=results/2026-10-22_copula_bootstrap_6915` | `results/2026-10-22_copula_bootstrap_6915/` | 3.5 h |
| dependence tests per cell (four tests) | `25_dependence_tests.py` | `results/2026-09-02_dependence_tests/` | 2 h |
| copula family per cell and the transition probabilities at 0.6915 | `40_copula_family_and_flood_level.py` | `results/2026-10-22_copula_family_and_flood_level/` | 1 min |
| Figures 5 to 9 | `41_copula_figures.py` | `results/2026-10-22_copula_figures/` | 1 min |
| Table E1 (Appendix E) | `42_appendix_e_copula_table.py` | `results/2026-10-22_appendix_e_copula_table/` | seconds |
| counts of locations where a more severe drought raises the transition probability (Section 3) | `29_increase_criterion_counts.py` | `results/2026-09-04_increase_criterion/` | seconds |
| copula chain under both quantile references (Section 2.3) | `28_copula_quantile_reference.py` | `results/2026-09-04_copula_quantile_reference/` | 5 min |
| copula side at the stricter drought definition (Section 4, limitations) | `27_strict_definition_points.py`, `28_strict_bootstrap_and_tests.py`, `30_strict_post_drought_state.py` | `results/2026-09-04_strict_*` | 10 min + 3.5 h + 2 min |
| Appendix D, all 48 locations | `47_appendix_d_figures.py` | `results/2026-11-02_appendix_d/` | 5 min |
| diagnostics quoted in the text: share of drought weeks per location, selectivity of the thresholds, the quantile reference and its window | `02_sri_diagnostic.py`, `06_threshold_selectivity.py`, `07_reference_grid.py` + `08_reference_grid_report.py` | `results/2026-08-23_sri_diagnostic/`, `results/2026-09-01_threshold_selectivity/`, `results/2026-09-01_reference_grid/` | 1 + 2 + 65 min |

Figures 1 to 3 (study area, data, illustration of the event definition) are
unchanged from R1 and come from the notebook.

Script numbers reflect the order in which the scripts were written, not the
order above; the numbers 27 and 28 occur twice (`27_physical_results_table` and
`27_strict_definition_points`, `28_copula_quantile_reference` and
`28_strict_bootstrap_and_tests`). Scripts written for exploration or for
options that were not adopted are not in this repository.

## Where each reported number comes from

| in the manuscript | file |
|---|---|
| Table 3 | `outputs/tables/table3.md` (from `results/2026-10-30_table3_eca_strict/`) |
| pooled ratio 1.07, 10 of 48 per period | `outputs/tables/table3_summary.md` |
| pooled ratio 1.25, 40 of 48 (milder definition) | `outputs/results/2026-10-27_table3_eca_cprime/summary.md` |
| Figure 4 and which locations it shows | `outputs/figures/fig04_map.png`, `outputs/tables/fig04_symbols.csv` |
| Figures 5 to 9 | `outputs/figures/fig05...fig09` |
| Table E1 | `outputs/tables/table_E1.md` |
| Figure F1, Table F1 | `outputs/figures/figF1_sensitivity_cprime_heatmap.png`, `outputs/tables/table_F1.md` |
| Figure F2 | `outputs/figures/figF2_map_sri1_flood0.6915.png` |
| Table G1 | `outputs/tables/table_G1a_period1.md`, `table_G1b_period2.md` |
| Appendix D | `outputs/figures/appendix_D.pdf` |
| percentages in Sections 2.3 and 2.4.1 (drought weeks, overlap, onset probabilities, lag 1 share) | `outputs/tables/definition_stats_sri1.md` |

## Data

`data/efas_v5_dis06_48_locations_1995_2024.nc` contains the daily values of
the EFAS v5 historical simulation (variable `dis06`, the 12:00 UTC field) at
the 48 grid points nearest to the study locations, 1 January 1995 to
31 December 2024. Source: Copernicus Early Warning Data Store. The file in the
repository is the one the results were computed from; `scripts/00_check_data.py`
verifies its checksum.

## Citing

Please cite the article. The repository state used for R2 is tagged
`r2-2026-11-02`.
