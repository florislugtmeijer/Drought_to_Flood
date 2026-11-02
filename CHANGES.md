# What changed between R1 and R2

For each change: what the submitted version (R1) did, what R2 does, why, and
the effect on the reported numbers. The R1 computation is in `notebooks/`;
every R2 number comes from `scripts/` (see `README.md`). Internal numbering of
the review tasks is omitted here.

## 1. Event detection: the end of one-week events

**R1.** The end-of-event detection required the candidate week to lie strictly
after the start week. For an event of exactly one week the only correct week
was thereby excluded and the end was placed at the next gap further on. One
third of the droughts last one week.

**R2.** The end of an event is the last week of the event, also for one-week
events (`src/dtf/pipeline.py`, `extract_events`). Verified exhaustively over
all 1,024 patterns of ten weeks: 0 deviations in start, end and duration. Two
consequences in the same function: the duration is now a count of weeks (an
event of one week has duration 1, not 0), and the discharge peak after an
event is taken strictly after its last week (four weekly values, not five).

**Why.** The end week is the anchor of the coincidence window. For one-week
droughts the window was (t+1, t+5] instead of (t, t+4], missing the first week
after the drought and taking a fifth week instead.

**Effect.** Drought and flood counts unchanged. Matches +15.5% (4,764 to 5,503
over the 96 location-periods at the R1 null and the milder definition). Under
the R1 null the pooled ratio went from 1.59 to 1.82 in period 1 and from 1.55
to 1.81 in period 2. The copula input changes through the duration and the
peak window (see 4).

## 2. The null hypothesis of the Monte Carlo test

**R1.** Simulated flood onsets were placed uniformly over all weeks of the
period, also within droughts.

**R2.** Stratified permutation null (`scripts/36`, `scripts/37`): simulated
onsets are placed only on weeks where an onset can occur (weeks outside a
drought that are not preceded by a flood week), and the observed number of
onsets that fall within drought weeks is kept. 10,000 simulations per location
and period, fixed seed per location. The analytical Poisson p-value is kept in
Table 3 next to the Monte Carlo p-value; the text explains why they differ.

**Why.** Drought and flood labels come from the same discharge series, so a
flood can hardly start inside a drought by construction. A uniform null expects
too few coincidences and reports this definitional effect as dependence: at
the milder definition a flood starts in one of twenty drought weeks against two
of three non-drought weeks, and 71% of the matches fall in the first week after
a drought.

**Effect.** At the milder definition (SRI −0.5, flood quantile 0.6915) the
pooled ratio of observed to expected coincidences goes from 1.81 to 1.25 and
the number of significant location-periods from 92 to 80 of 96. At the main
definition (see 3) the pooled ratio is 1.26 under the uniform null and 1.07
under the stratified null, with 20 of 96 significant.

## 3. The event definition of the ECA, as described and as computed

**R1.** The methods section described droughts at SRI < −0.5 and floods above
the 69th percentile, while Table 3 had been computed with SRI < −1 and the
84.1st percentile (`docs/reproducibility-check.md`).

**R2.** The ECA uses SRI < −1 with the flood quantile 0.8413, the definition
that was computed, which follows the standard SPI classification of moderate
drought (McKee et al., 1993). The copula analysis keeps SRI < −0.5 with the
0.6915 quantile, as in R1, because it needs more events to estimate a
dependence structure and because at −1 the minor and major categories
coincide. The difference is stated in Section 2.3. The sensitivity of the ECA
result to both thresholds is in Appendix F (`scripts/37`, `scripts/43`).

**Effect.** Table 3 at the main definition: 13 and 17 of 48 locations
significant under the Poisson test, 10 and 10 under the stratified null;
pooled ratio 1.07. Under milder definitions the association is widespread
(pooled ratio 1.2 to 1.3, up to 44 of 48 locations) and for the most extreme
floods it is absent. Figure 4 now shows only the locations significant under
the stratified null.

## 4. The copula side

**R1.** (a) The conditional curve was read at the rank of the post-drought
peak while the unconditional curve was on the discharge-quantile scale; the
marginal CDF of the flood variable, F_Y, was fitted but not applied. (b) The
flood window after a drought included the last drought week (five weekly
values). (c) Mean severity divided by end minus start, one week short. (d) The
drought marginal was empirical while the text described parametric marginals.
(e) No random seed.

**R2.** (a) Curves are read at F_Y(q), so both curves are on the quantile
scale (`src/dtf/copula.py`, `fit_copula`, `axis="quantile"`). (b) Four weeks
strictly after the drought. (c) Duration counted in weeks. (d) Parametric
marginals by maximum likelihood, as described. (e) Seeds per location and
period, `SeedSequence(42).spawn(96)`.

**Why.** (a) to (c) are corrections of the code to what the text describes;
(d) follows the text; (e) makes the draws reproducible.

**Effect.** At the 0.6915 quantile the median transition probability after a
minor drought goes from 0.274 to 0.775; the gap to the unconditional curve
from −0.422 to +0.057; the number of cells where the conditional curve lies
below the unconditional one from 188 to 33 of 192. The comparison of minor
against major droughts is unaffected by (a), since both were already on the
same scale. Four passages in Section 3 that compared the two curves change
sign. The selected copula family changes in about a third of the cells
through (b) and (c).

## 5. New: uncertainty and dependence tests on the copula side

**R2 adds.** 95% bootstrap intervals for every transition curve (2,000
resamples of the drought events, with re-estimation of the marginals and
re-selection of the family in each resample; `scripts/22`), a decomposition of
the difference to the unconditional curve into a marginal and a copula part,
and four dependence tests per cell (Kendall's tau, Hoeffding's D, a permutation
test on the copula fit and one on the copula part at 0.6915; `scripts/25`).
Locations where a more severe drought raises the transition probability are
counted only where at least three of the four tests are significant at 5%
(`scripts/29`). The copula family per cell, the margin of the AIC choice and
the stability of the selection in the bootstrap are in Table E1
(`scripts/40`, `scripts/42`).

## 6. New tables and figures

- Table 4 / Table G1: per location and period, number of droughts, median
  duration, share followed by a flood, the share expected under the stratified
  null, their ratio, the Monte Carlo p-value, median lag and dominant season
  (`scripts/27_physical_results_table`, `scripts/45`).
- Appendix F: the sensitivity grid of the ECA over the drought threshold
  (0.25 to 1.5) and the flood quantile (0.60 to 0.95), under the stratified
  null, plus the map at SRI −1 with the flood quantile unchanged (Figure F2).
- Appendix D regenerated for all 48 locations with the bootstrap bands, one
  page per location with a heading (`scripts/47`).
- Figures 5 to 9 regenerated with the corrected curves and bootstrap bands
  (`scripts/41`); Figure 9 (Vistula, Toruń) is new.

## 7. Text corrections without effect on the numbers

- The data start on 1 January 1995, not 1994.
- The number of Monte Carlo simulations (10,000) and the seeds are now stated.
- Period 2 runs from 2 January 2010 (index 5480) to 31 December 2024, one day
  shorter than period 1; moving the split by one day changes no count and no
  p-value to four decimals, so it was left as computed.
- The quantile reference of the flood threshold is the daily discharge of the
  period itself (daily values, per period), for both parts, as in R1; the
  alternative references were examined (`scripts/07`, `scripts/08`,
  `scripts/28_copula_quantile_reference`) and the choice is now stated in
  Section 2.3.
- Formula (1) and Appendix A now give the coincidence condition as it is
  computed: 0 < t_j^F − t_i^{D,end} ≤ ΔT, with the end of the drought as the
  anchor. Appendix A describes the stratified null and the 10,000 simulations.
