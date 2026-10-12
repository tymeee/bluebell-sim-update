# Measured verification results

Date: 2026-10-12. Source repository commit: `ffe9409`.

## Final warm HTTP burst tests

One local Uvicorn process, eight native-compute workers, shared scenarios enabled. The container reported an 8-vCPU quota and 8 GiB memory limit. These are measurements in this environment, not promises for every server with the same advertised specs.

Each burst submits **30 simultaneous distinct requests**: 1,000 trials, age 0, 85-year horizon, 20 years of accumulation, all 13 regular assets allocated equally, distinct initial amounts, and no withdrawals (so paths cannot exit early due to withdrawal bankruptcy). The funds benchmark does not allocate to optional Rostrum. Three bursts were run for each model, sequentially across models.

| Model | Burst 1 maximum | Burst 2 maximum | Burst 3 maximum | Requests | Errors |
| --- | --- | --- | --- | --- | --- |
| Index | 3.545 s | 3.114 s | 2.997 s | 90 | 0 |
| Funds | 3.158 s | 3.182 s | 2.977 s | 90 | 0 |

All 180 final HTTP requests passed the six-second threshold. Backend startup/readiness took approximately **48.7 seconds** in this run. Startup is excluded from warm request latency.

HTTP timing includes waiting for a compute worker, server calculation, JSON serialization, and localhost transfer. It **does not include browser rendering, a public internet connection, remote Streamlit request handling, or PDF generation**. The original Streamlit deployment was not measured under the same hardware/load, so no full-app before/after speedup ratio is claimed.

The exact records are in `verification/load-index-30.json` and `verification/load-funds-30.json`. Re-run the supplied load tester against your deployed HTTPS service and measure real click-to-chart times before offering a service guarantee.

## Intermediate findings

- Fresh randomness with all 13 assets and the longest 1,000-trial workload took approximately **21 seconds** per request here. Fresh mode is retained for diagnostics and does not meet the target.
- An earlier shared-scenario index implementation reached **7.3–8.4 seconds** at 30 simultaneous requests. Replacing daily array views and temporary vector allocations with scalar updates reduced the final burst maxima to those above.
- Shared scenarios remove repeated shock generation, not daily portfolio mechanics. They intentionally reuse randomness across requests. Repeating the same portfolio yields the same paths for the same bank, trial count, and model settings.

## Calculation and interface checks

**31 tests passed** after the final engine change:

- Original-vs-new daily portfolio-rule regressions for both models, including contribution, withdrawal, rebalance, and bankruptcy cases, in both fresh and shared-scenario kernels.
- Student-t sample location/covariance, covariance-factor validity, input validation, seeded thread concurrency, scenario capacity checks, and all-trial annualized statistics.
- API readiness, authentication, invalid input rejection, bounded admission, interface submissions for both models, persistent last-run results, and separate PDF export.
- Python compilation of all new modules and scripts.

The statistical check does not prove every distributional or financial modeling assumption. See `MIGRATION.md` for the explicit corrections and rules retained from upstream. No production deployment or Docker image build was performed in this environment.
