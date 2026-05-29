# OQ-Tsunami Patch Tool

`OQ-tsunami` is a lightweight patch/apply tool for running tsunami workflows
through a native editable OpenQuake Engine checkout. It is not a separate risk
engine: OpenQuake still runs `event_based_risk`, writes `risk_by_event`, and
then calls a native `postrisk_func`.

The current scope is imported-GMF tsunami risk with one tsunami IMT,
`FLOWDEPTH`, plus AAL and EP metrics from epistemic annual event-rate samples.

## Install

Install OpenQuake from an editable source checkout, then install this package in
the same Python environment:

```bash
cd /path/to/oq-engine
pip install -e .

cd /path/to/oq-tsunami-ext
pip install -e .
```

## Patch Native OpenQuake

Apply the OQ-Tsunami patch set on top of the editable OpenQuake checkout:

```bash
oq-tsunami patch status --oq-engine /path/to/oq-engine
oq-tsunami patch apply --oq-engine /path/to/oq-engine
oq-tsunami patch verify --oq-engine /path/to/oq-engine
```

`apply` is idempotent and only adds missing changes. `verify` compiles the
touched OpenQuake files and confirms that `FLOWDEPTH` and
`openquake.calculators.postrisk.tsunami.main` are importable.

The patch set is intentionally small and fork-friendly:

- `openquake/hazardlib/imt.py`: add `FLOWDEPTH()`.
- `openquake/commonlib/oqvalidation.py`: allow `FLOWDEPTH` as a primary IMT for
  imported-GMF risk functions.
- `openquake/calculators/base.py`: for imported GMFs, log and continue when
  exposure assets fall outside the hazard site collection.
- `openquake/baselib/workerpool.py`: wait up to 60 seconds for Slurm
  `jobs.pik` visibility and use `sys.executable`.
- `openquake/calculators/postrisk/tsunami.py`: expose `tsunami.main`.
- `openquake/calculators/postrisk/__init__.py`: import the tsunami postrisk
  module.

Do not use `secondary_perils = tsunami`, `multi_peril_file`, or a fake
secondary-peril class for this workflow.

## Native OpenQuake Workflow

Use imported tsunami GMFs and the native OpenQuake postrisk hook:

```ini
[general]
calculation_mode = event_based_risk

[hazard sites]
gmfs_file = tsunami_hazard.hdf5

[risk_calculation]
aggregate_by = Construction
return_periods = 10 50 100 250 500
postrisk_func = tsunami.main
postrisk_args = {
  'event_rates_file': 'event_rates.csv',
  'plot': True,
  'plot_loss_ratio': True
  }
```

The vulnerability model should use `imt="FLOWDEPTH"`. The event-rates CSV must
be wide format with `eid` as the first column and one annual-rate column per
epistemic sample:

```csv
eid,s0,s1,s2
0,0.001,0.002,0.0015
1,0.0001,0.0002,0.00015
```

`tsunami.main(dstore, event_rates_file, plot=True, export_dir=None)` reads
native OQ `risk_by_event`, computes metrics using annual event rates, stores
them in the datastore, and exports CSV/PNG outputs.

Datastore outputs:

- `tsunami_aal_sample`
- `tsunami_aal_stats`
- `tsunami_aggcurves_sample`
- `tsunami_aggcurves_stats`

CSV outputs:

- `tsunami_aal_sample.csv`
- `tsunami_aal_stats.csv`
- `tsunami_aggcurves_sample.csv`
- `tsunami_aggcurves_stats.csv`

PNG outputs when `plot=true`:

- `tsunami_aal_by_aggregation.png`
- `tsunami_ep_loss_by_return_period.png`
- `tsunami_aal_loss_ratio_by_aggregation.png` when `plot_loss_ratio=true`
- `tsunami_ep_loss_ratio_by_return_period.png` when `plot_loss_ratio=true`

## Legacy Manual Integration

The original manual post-processing command remains available:

```bash
oq-tsunami integrate \
  --calc-id <CALC_ID> \
  --event-rates path/to/event_rates.csv \
  --investigation-time 1.0 \
  --return-periods 10,50,100,250,500 \
  --export-dir /tmp \
  --plot \
  --plot-loss-ratio
```

This reads `risk_by_event` from an existing calculation and writes the same CSV
and optional PNG products outside the OpenQuake postrisk flow.

## Notes

- Event-rate columns are annual rates.
- AAL is computed as `sum(loss * annual_rate)` for each epistemic sample.
- Stats tables report `mean`, `p05`, `p16`, `p50`, `p84`, and `p95`
  across epistemic samples.
- Loss-ratio plots divide loss by total exposure value. The native postrisk path
  infers this from `agg_values` when possible; pass `total_exposure_value` in
  `postrisk_args` or `--total-exposure-value` in the CLI to override it.
- EP losses are derived from weighted exceedance-rate tables and reported at the
  configured return periods.
- The postrisk implementation is based on `risk_by_event`, not tsunami hazard
  files, so it can later support coupled shaking and tsunami losses from a
  single event-based run.
