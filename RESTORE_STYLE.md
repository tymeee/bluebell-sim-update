# Restore the original BlueBridge appearance

This patch is for `tymeee/bluebell-sim-update` (inspected at `3179927`).

1. Extract the ZIP.
2. Upload its contents into the root of that repository, preserving `fast_simulator/`, `tests/`, `pages/`, and `.streamlit/` folders. Replace `Fast_Simulator.py` and `tests/test_frontend.py` when prompted. The ZIP itself is not an app file.
3. Keep the existing engine files, requirements, and market-data files.
4. Keep Streamlit's main file set to `Fast_Simulator.py` and reboot after upload. Streamlit Community Cloud will install Chromium from `packages.txt`; a rebuild may take longer than an ordinary rerun.
5. Keep any existing `SIMULATOR_API_URL`/`SIMULATOR_API_KEY` secrets. Local mode still works without a backend.

For an automatic upload from the extracted patch folder (Git and GitHub CLI required):

```bash
gh auth login
python upload_to_github.py --create-pr
```

The uploader defaults to your **new** repository, `tymeee/bluebell-sim-update`, and pushes a separate branch.

## Restored presentation

- Original hero HTML, BlueBridge logo, dark styling, theme configuration, sidebar controls, THB inputs and plus/minus buttons.
- Original asset selectors and Bluebell presets, allocation validation messages, and Run button placement.
- Original percentile line order, colors, titles, hover text and THB-million units, responsive desktop/mobile projection, allocation donut, histogram formatting, and three-column/six-card statistics layout.
- Original PDF page layout and chart styling, generated only when requested. If Chromium/Kaleido is unavailable on a local installation, the existing simplified PDF exporter remains a fallback.
- Original retirement calculator and offered-funds information pages, with their original formatting.
- Your current frontend maximum of 500 trials and default of 250 are retained. The engine/API's existing validation ceiling of 1,000 is untouched.

## Calculation details

The optimized engine, data files, service, and scenario behavior are untouched by this styling patch. Results remain in the session when inputs are edited; the app tells you to Run again before edits take effect.

Monthly chart sampling remains. The annualized metric is labeled **Median Accumulation Annualized Return**, not **Median-Line Annualized Return**, because the optimized engine computes corrected daily per-trial returns and takes their median. Relabeling it as the original percentile-line statistic would be inaccurate. Other existing model corrections are still described in `MIGRATION.md`.

One upstream input helper fix is included: import `dedent` for optional help text and initialize the hidden-label class for collapsed labels. Neither changes the standard visual styling.

## Contribution attribution

The original simulator's financial model, input choices, portfolio rules and UI design are the basis of this implementation. AI assistance was used for refactoring, computation optimization, bug fixes, backend implementation, and restoring the original presentation.

An accurate project description is: "I developed the retirement simulator's original financial model and interface, and used AI assistance to optimize and refactor its implementation."

This source comparison establishes technical provenance; it does not establish legal ownership or the terms of any agreement with Bluebell.

## Verification

All 31 existing calculation/API and updated interface checks passed after restoration. Both supporting pages opened without errors. The original CSS, theme configuration and logo are byte-for-byte copies. PDF generation was tested through the simplified fallback locally; the Chromium-backed original chart export still needs verification on your host. The original on-demand PDF builder and layout are included.
