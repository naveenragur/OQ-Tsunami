# OQ-Tsunami extension (plugin)

This branch turns this repository into a **thin extension package** that works
with **GEM OpenQuake Engine v3.25.1** installed from PyPI (pip/uv).

It adds:

- A tsunami intensity-measure type (IMT) name: `TSU_DEPTH`
- Fast probabilistic integration for **epistemic event rates** *without
  recomputing losses*: given an OpenQuake run that produced `risk_by_event`,
  compute AAL + EP curves for N epistemic rate samples.

## Install (uv)

```bash
uv venv
source .venv/bin/activate
uv pip install -U pip
uv pip install "openquake.engine==3.25.1"
uv pip install -e .
```

## Workflow

### 1) Run an OQ event-based risk calculation from imported GMFs

Your `job.ini` should:

- use `calculation_mode = event_based_risk`
- reference your GMF HDF5 via `gmfs_file = ...hdf5`
- use vulnerability with `imt="TSU_DEPTH"`

Then run:

```bash
oq engine --run path/to/job.ini
```

Find the calc id:

```bash
oq db find - | tail
# or
oq engine --list-calculations
```

### 2) Integrate epistemic rates into probabilistic outputs (AAL + EP)

Prepare a **wide** CSV file with:

- first column: `eid`
- remaining columns: one column per epistemic sample (annual rates in 1/yr)

Example header:

```csv
eid,s0,s1,s2
```

Run integration:

```bash
oq-tsunami integrate \
  --calc-id <CALC_ID> \
  --event-rates path/to/event_rates.csv \
  --investigation-time 1.0 \
  --return-periods 10,50,100,250,500 \
  --export-dir /tmp
```

Outputs:

- `/tmp/aals_epistemic.csv` (AAL by loss_type, aggregation, sample)
- `/tmp/epcurves_epistemic.csv` (EP/PoE by return period, sample)
- `/tmp/aals_stats.csv` and `/tmp/epcurves_stats.csv` (mean/p05/p50/p95)

## Notes

- This package **does not** duplicate the OpenQuake engine source code.
- It operates as post-processing: it reuses the `risk_by_event` dataset
  produced by the OQ calculation.
