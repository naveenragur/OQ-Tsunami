# OQ-Tsunami extension (plugin)

This repository (branch `tsunami-3.25-epistemic-rates`) is a **thin extension**
package that you install *alongside* a local checkout of **GEM OpenQuake Engine
v3.25.1**.

It adds:

- A tsunami intensity-measure type (IMT) name: `TSU_DEPTH`
- Fast probabilistic integration for **epistemic event rates** *without
  recomputing losses*: given an OpenQuake run that produced `risk_by_event`,
  compute **AAL + EP** for N epistemic rate samples.

This supports your workflow where tsunami hazard is precomputed externally and
provided to OpenQuake as imported GMFs (HDF5).

---

## Install + run with local oq-engine source (recommended)

You said you want to be able to modify OpenQuake code locally. Do this:

### 1) Create env (conda)

```bash
conda create -n oq325 python=3.11 -y
conda activate oq325
python -m pip install -U pip setuptools wheel
```

### 2) Checkout oq-engine v3.25.1 and install editable

```bash
git clone https://github.com/gem/oq-engine.git
cd oq-engine
git checkout v3.25.1

# IMPORTANT: apply the TSU_DEPTH IMT patch (see below)
# then install
pip install -e .
```

### 3) Checkout this extension and install editable

```bash
cd ..
git clone https://github.com/naveenragur/OQ-Tsunami.git oq-tsunami-ext
cd oq-tsunami-ext
git checkout tsunami-3.25-epistemic-rates
pip install -e .
```

You now have:

- `oq` coming from your local `oq-engine` checkout (editable)
- `oq-tsunami` coming from this extension package (editable)

---

## Patch GEM oq-engine (v3.25.1) to add TSU_DEPTH IMT

OpenQuake hazardlib validates IMT names. To use `imt="TSU_DEPTH"` in
vulnerability models and in job configs, you must add a new IMT.

In `oq-engine` repo (tag `v3.25.1`), edit:

- `openquake/hazardlib/imt.py`

Add:

```python
# tsunami IMT

def TSU_DEPTH():
    """Tsunami inundation depth (units as provided by the user, typically cm or m).

    This is intended for imported-GMF risk workflows, not for GMPE-based hazard.
    """
    return IMT('TSU_DEPTH')
```

and ensure it is included in globals (just defining the function is enough).

After patching:

```bash
pip install -e .
```

---

## Workflow

### 1) Run OQ event-based risk from imported GMFs

Your `job.ini` should:

- `calculation_mode = event_based_risk`
- `gmfs_file = tsunami_depth_gmfs.hdf5`
- vulnerability model uses `imt="TSU_DEPTH"`

Then run:

```bash
oq engine --run path/to/job.ini
```

Find calc id:

```bash
oq engine --list-calculations
# or
# oq db find -
```

### 2) Integrate epistemic event rates (AAL + EP)

Prepare a **wide** CSV file with:

- first column: `eid`
- remaining columns: one column per epistemic sample (annual rate in 1/yr)

Example:

```csv
eid,s0,s1,s2
0,0.001,0.002,0.0015
1,0.0001,0.0002,0.00015
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

- `/tmp/aals_epistemic.csv`
- `/tmp/epcurves_epistemic.csv`
- `/tmp/aals_stats.csv` (mean/p05/p50/p95)
- `/tmp/epcurves_stats.csv` (mean/p05/p50/p95)

---

## Notes / assumptions

- The integration uses a Poisson model for exceedance:
  ν(L)=Σ λᵢ I(lossᵢ>L), PoE=1-exp(-νT).
- We only implement AAL + EP in this version. AEP/OEP can be added later.
