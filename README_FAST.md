# BlueBridge fast simulator upload kit

Based on `tymeee/monte-carlo-retirement-simulation` commit `ffe9409`.
The original `Blue_Bridge_Simulator.py`, calculator pages, market data, logo, and CSS are untouched.
The new entry point is **Fast_Simulator.py**. `requirements.txt` is the one existing file replaced.

## Upload to GitHub

Extract the ZIP first. Upload the extracted files and folders into the root of your existing repository, retaining their relative paths. Uploading the ZIP itself does not install the app. Keep your existing data files and pages.

For an automatic upload using a computer with Git and GitHub CLI installed:

```bash
gh auth login
python upload_to_github.py --create-pr
```

This pushes a new timestamped branch to your existing repository and opens a pull request. It does not change `main` or deploy a server. Review the pull request, then merge it when ready. The script sets a commit identity only in its temporary clone if needed.

## Try the new interface locally

Run these commands from your existing repository after copying in the kit, so the three existing market-data files are present. Use Python **3.12**:

```bash
python -m pip install -r requirements-fast.txt
python -m streamlit run Fast_Simulator.py
```

This works in local/fresh-random mode without a backend. The first run compiles the engine and is slower. Local mode alone does not meet the 30-user target.

On Streamlit Community Cloud, select `Fast_Simulator.py` as the main file. The supplied root `requirements.txt` installs both the new app's requirements and dependencies retained for your original app/pages.

## Dedicated backend: recommended fast mode

Shared-scenario mode computes 1,000 independent Monte Carlo trials for the full 85-year horizon **before readiness**, then reuses those same daily scenarios across requests. It retains daily simulation, covariance, regime switching, fees, contributions, withdrawals, and rebalancing. Repeated portfolios give stable results; this differs from drawing fresh randomness on every click.

It stores about **4.63 GB** of float64 scenario data for both models. Use a server with **16 GB RAM recommended**, and benchmark your actual CPU allocation. Eight compute workers were used for the included local tests; that is a test configuration, not a guarantee for every 8-core server.

```bash
python -m pip install -r requirements-backend.txt
export SIMULATOR_SHARED_SCENARIOS=1
export SIMULATOR_WORKERS=8
export SIMULATOR_MAX_INFLIGHT=64
export SIMULATOR_API_KEY="replace-with-your-own-secret"
python -m uvicorn simulator_api:app --host 0.0.0.0 --port 8000 --workers 1
```

PowerShell users can set an environment variable with `$env:SIMULATOR_SHARED_SCENARIOS="1"`, and similarly for the other settings.

Or use Docker:

```bash
SIMULATOR_WORKERS=8 SIMULATOR_API_KEY="replace-with-your-own-secret" docker compose -f compose.fast.yml up --build -d
```

Docker Compose binds the API to `127.0.0.1:8000`. For remote Streamlit access, put it behind an HTTPS reverse proxy or your hosting service's HTTPS endpoint. If both services are in a container network, use the backend's internal service URL instead. Startup includes scenario generation and compilation; use an always-on service and wait for `/health` to return `ready`. Do not scale this container to zero if warm latency matters.

Use **one Uvicorn process** per backend instance. It owns a bounded compute pool; more Uvicorn processes duplicate the scenario banks and worker pools. This app does not require a database or Redis.

## Connect Streamlit to the backend

Set these in Streamlit's Secrets settings, or in local `.streamlit/secrets.toml`:

```toml
SIMULATOR_API_URL = "https://your-backend.example.com"
SIMULATOR_API_KEY = "the-same-secret-as-the-backend"
```

Do not upload your actual secrets file. An example is included as `secrets-fast.example.toml`.

Results remain in the user's session when inputs change. Only submitting Run triggers computation. PDF generation is a separate button and occurs on the interface host, so it does not occupy a simulation worker.

No browser extension or React rewrite is required. The existing calculator and information pages remain available through Streamlit's normal `pages/` navigation.

## Test performance on your deployed server

```bash
python scripts/load_test_fast.py https://your-backend.example.com --users 30 --rounds 3 --model index --output load-index.json
python scripts/load_test_fast.py https://your-backend.example.com --users 30 --rounds 3 --model funds --output load-funds.json
```

If authentication is enabled, set `SIMULATOR_API_KEY` in the testing shell. These tests use distinct capital values and independent concurrent requests; they do not rely on caching repeated final results. They use all 13 assets, 1,000 trials, age 0, an 85-year horizon, 20 accumulation years, and no withdrawals, so no trial exits early due to bankruptcy.

They exit with status 1 if any request fails or takes more than 6 seconds. Timing includes HTTP transfers and queueing, **not browser chart rendering**. Also verify actual click-to-chart performance from users' devices. Run 40-user bursts and sustained traffic before promising a production service target.

A single command can start and stop a local backend for both 30-user tests:

```bash
python scripts/verify_local_fast.py --workers 8 --users 30 --rounds 3
```

Local verification includes a large startup allocation; do not run it on a small free-tier instance.

## Fresh randomness and reproducibility

- Shared scenarios are opt-in for manual deployment (`SIMULATOR_SHARED_SCENARIOS=1`); the Docker Compose example enables them.
- Shared scenario seed defaults to `20261012`. Change `SIMULATOR_SCENARIO_SEED` and restart to generate another independent bank. Each trial within a bank is independent; different requests intentionally share that bank.
- The UI explicitly labels shared-scenario results. Record both `sampling_mode` and `seed` when reproducing a run.
- With shared scenarios disabled, requests generate fresh trials. An explicit request `seed` makes fresh runs reproducible.
- A shared-scenario API rejects explicit seeds by default to prevent expensive fresh requests competing with fast traffic. Set `SIMULATOR_ALLOW_FRESH=1` only if you accept this additional load, preferably on a separate instance. The load tester's `--fresh` option needs that setting.
- The library function `simulate(request, banks)` can also bypass shared scenarios using an explicit request seed for offline diagnostics.
- `/health` exposes the sampling mode and worker count, not credentials.

## Validation

```bash
python -m pip install pytest
python -m pytest tests -q
```

See `BENCHMARK_RESULTS.md` for measured local results and `MIGRATION.md` for preserved rules and explicit correctness changes. A GitHub Actions workflow runs the tests on Python 3.12 after upload.
