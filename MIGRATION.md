# Model and implementation notes

## Preserved from upstream ffe9409

- Index market-statistics windows: bear 2005-12-01 to 2015-06-01; bull 2015-06-01 to 2025-12-30. Asset order is validated explicitly.
- Index regime transition probabilities: bear to bull 5% daily; bull to bear 2% daily.
- Index heavy tails: df=6 and the original mean-plus-normal sample is multiplied by the chi-square scale. This unusual location scaling was retained rather than silently replacing it with a conventional multivariate t distribution.
- Company model: multivariate t with df=5, its existing daily fee/return offsets, contribution timing, withdrawal comparisons, annual rebalancing, and Rostrum threshold fallback.
- 252 trading days/year, contributions every 21 days during accumulation, horizon ending just before age 85, and the original differences in withdrawal timing between models.
- Index unallocated money is cash; company unallocated money is non-interest-bearing savings. Index savings yield is 1.75% annual.
- The direct-bond amounts in the current upstream index UI are all zero. The new public configuration likewise does not expose direct bonds. Hazard/default/maturity work is skipped when all direct-bond balances are zero; this cannot affect wealth in that case.
- Original pure-cash fallback/reallocation and strict company-model withdrawal comparisons remain as written. This is a performance migration, not a redesign of those modeling rules.
- All three Bluebell presets retain their original allocations.

## Explicit corrections

1. Annualized accumulation returns are collected across all valid trials; the list no longer resets on every trial. The new UI consistently reports their **median** for both models. It does not use the old company model's accidentally last-trial trimmed statistic.
2. Invalid/zero-wealth annualized growth is omitted and displayed as N/A if no valid trials remain. There is no uninitialized `valid_growth` variable.
3. Goal flags initialize to zero, including trials that fail before reaching retirement. Upstream could return an uninitialized `goal_count`.
4. Rostrum's separate univariate t stream consistently uses df=10. Upstream assigned df=10 before the loop, then overwrote df=5 for the multivariate stream inside it, inadvertently changing Rostrum's degrees of freedom after the first trial. The public upstream fund selector did not expose Rostrum; the new custom selector does, with its THB 3 million minimum checked.
5. Requests reject invalid horizons, non-finite or negative allocations, unknown fund names, and totals exceeding 100%.

## Speed and output changes

- Both fresh engines compile the outer trial loop and daily sampling with Numba, release the GIL, reuse covariance factors, and avoid sampling zero-allocation assets. The marginal joint law for active assets is retained, but fixed seeds will not match upstream's random draw sequence.
- Shared-scenario mode samples all assets once before readiness. Banks retain float64 daily multipliers (no monthly-time-step approximation or float32 return conversion). Portfolio balances still advance daily. Multiple requests use common random numbers, so they are **not independent rerolls**; each bank's trials are independent.
- Only monthly portfolio samples, the exact retirement day, the last day, and per-trial summaries survive each trial. Daily path storage is temporary and drawdown uses all daily values. In the company model, path values remain float64 for calculation; the retained chart matrix is float32, matching upstream's full simulation matrix.
- Chart percentiles are computed only at retained days. No interpolation is used to calculate daily drawdown or annualized returns.
- The API returns nominal monthly curves and ending values, target/survival probabilities, median retirement/ending wealth, inflation-adjusted ending wealth, daily maximum drawdown, and median accumulation annualized returns.
- The new interface is a compact separate entry point. It retains the inputs, both models, presets, main percentile projection, histogram, statistics, and PDF export. It does not reproduce every layout element or secondary chart in the original 3,638-line interface.
- PDF generation uses Matplotlib image rendering and ReportLab only on demand, rather than three Kaleido exports during each simulation.

## Operation

- A single API process owns one bounded native-compute thread pool. Admission remains occupied until native work completes, even if a requesting client disconnects.
- A full queue returns HTTP 429; no request is secretly marked complete to meet a latency goal.
- Shared banks cost ~4.63 GB before Python, request buffers, and container overhead. Always-on hosting and a successful readiness response are prerequisites for warm timings.
- Multiple backend instances can scale capacity, but each keeps its own banks. Set the same scenario seed if cross-instance repeatability is needed.
- The frontend and backend do not cache user-specific final results. User data remains request/session-local; market data and shared scenario banks are read-only.
- This package has not been deployed to your company service. GitHub upload alone does not allocate a backend or configure its URL/secrets.
