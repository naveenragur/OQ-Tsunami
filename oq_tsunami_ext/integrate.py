from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class RatesMatrix:
    eids: np.ndarray  # shape (E,)
    samples: list[str]
    rates: np.ndarray  # shape (E, S)


def read_event_rates_wide_csv(path: Path) -> RatesMatrix:
    df = pd.read_csv(path)
    if "eid" not in df.columns:
        raise ValueError("event rates CSV must contain an 'eid' column")
    samples = [c for c in df.columns if c != "eid"]
    if not samples:
        raise ValueError("event rates CSV must contain at least one sample column")
    eids = df["eid"].to_numpy(dtype=np.int64)
    rates = df[samples].to_numpy(dtype=float)
    return RatesMatrix(eids=eids, samples=samples, rates=rates)


def weighted_aal(losses: np.ndarray, rates: np.ndarray) -> float:
    # losses shape (E,), rates shape (E,)
    return float(np.sum(losses * rates))


def ep_curve_from_losses(
    losses: np.ndarray,
    rates: np.ndarray,
    investigation_time: float,
    loss_levels: np.ndarray,
) -> np.ndarray:
    """Return PoE(loss > x) for each x in loss_levels.

    Uses exceedance rate ν(x)=Σ λ_i I(L_i > x) and PoE=1-exp(-ν T).
    """
    # sort losses once for speed
    order = np.argsort(losses)
    L = losses[order]
    lam = rates[order]
    # cumulative sum of rates from high to low losses
    lam_rev_cum = np.cumsum(lam[::-1])[::-1]

    # for each x, find first index where L > x
    idx = np.searchsorted(L, loss_levels, side="right")
    nu = np.zeros_like(loss_levels, dtype=float)
    mask = idx < len(L)
    nu[mask] = lam_rev_cum[idx[mask]]
    poe = 1.0 - np.exp(-nu * investigation_time)
    return poe


def loss_levels_for_return_periods(losses: np.ndarray, return_periods: Iterable[float]):
    """Pick loss levels based on empirical quantiles of event loss.

    This is a reporting convenience; for true EP curve you want a full curve.
    We map RP -> PoE in 1 year as 1/RP and invert via empirical distribution
    as a starting point.

    NOTE: This is used to generate a finite set of curve points.
    """
    rps = np.array(list(return_periods), dtype=float)
    poes_1y = 1.0 / rps
    # rough mapping: loss quantile = 1 - PoE
    qs = np.clip(1.0 - poes_1y, 0.0, 1.0)
    return np.quantile(losses, qs)


def integrate_epistemic_rates(
    *,
    calc_id: int,
    event_rates_csv: Path,
    investigation_time: float,
    return_periods: list[float],
    export_dir: Path,
):
    from openquake.commonlib import datastore

    ratesm = read_event_rates_wide_csv(event_rates_csv)

    with datastore.read(calc_id) as ds:
        # risk_by_event is indexed by agg_id. We take all agg_ids.
        df = ds.read_df("risk_by_event")

    # Expect columns: agg_id, loss_id, eid, loss (and maybe variance)
    # Normalize loss type
    if "loss" not in df.columns:
        # older versions use 'value' or similar; try a fallback
        for cand in ("value", "losses"):
            if cand in df.columns:
                df = df.rename(columns={cand: "loss"})
                break
        else:
            raise RuntimeError("Cannot find loss column in risk_by_event")

    # map eids to row indices
    eids_loss = df["eid"].to_numpy(dtype=np.int64)
    # build eid->pos map for rates
    eid_to_pos = {eid: i for i, eid in enumerate(ratesm.eids)}
    pos = np.array([eid_to_pos.get(eid, -1) for eid in eids_loss], dtype=int)
    if np.any(pos < 0):
        missing = int(np.sum(pos < 0))
        raise ValueError(
            f"{missing} eids found in risk_by_event are missing from event_rates_file"
        )

    # Create outputs
    aals_rows = []
    ep_rows = []

    # group by aggregation and loss type
    group_cols = ["agg_id", "loss_id"]
    for (agg_id, loss_id), g in df.groupby(group_cols, sort=False):
        losses = g["loss"].to_numpy(dtype=float)
        epos = pos[g.index.to_numpy()]

        # We will compute AAL and EP points for each sample.
        # rates_for_rows shape (Erows, S)
        rates_for_rows = ratesm.rates[epos, :]

        # loss levels for EP reporting: use pooled loss distribution for this group
        loss_levels = loss_levels_for_return_periods(losses, return_periods)

        # compute per-sample AAL vectorized
        # (Erows,S) -> (S,)
        aals = (losses[:, None] * rates_for_rows).sum(axis=0)

        # EP curves per sample: loop over samples (S=1000), but each is fast
        for si, sname in enumerate(ratesm.samples):
            aals_rows.append(
                {
                    "agg_id": int(agg_id),
                    "loss_id": int(loss_id),
                    "sample": sname,
                    "aal": float(aals[si]),
                }
            )
            poe = ep_curve_from_losses(
                losses=losses,
                rates=rates_for_rows[:, si],
                investigation_time=investigation_time,
                loss_levels=loss_levels,
            )
            for rp, ll, p in zip(return_periods, loss_levels, poe):
                ep_rows.append(
                    {
                        "agg_id": int(agg_id),
                        "loss_id": int(loss_id),
                        "sample": sname,
                        "return_period": float(rp),
                        "loss_level": float(ll),
                        "poe": float(p),
                    }
                )

    aals_df = pd.DataFrame(aals_rows)
    ep_df = pd.DataFrame(ep_rows)

    # Stats across samples
    def _stats(df_in: pd.DataFrame, valcol: str, bycols: list[str]):
        g = df_in.groupby(bycols, sort=False)[valcol]
        out = g.agg(
            mean="mean",
            p05=lambda x: np.quantile(x, 0.05),
            p50=lambda x: np.quantile(x, 0.50),
            p95=lambda x: np.quantile(x, 0.95),
        ).reset_index()
        return out

    aals_stats = _stats(aals_df, "aal", ["agg_id", "loss_id"])
    ep_stats = _stats(ep_df, "poe", ["agg_id", "loss_id", "return_period", "loss_level"])

    aals_df.to_csv(export_dir / "aals_epistemic.csv", index=False)
    ep_df.to_csv(export_dir / "epcurves_epistemic.csv", index=False)
    aals_stats.to_csv(export_dir / "aals_stats.csv", index=False)
    ep_stats.to_csv(export_dir / "epcurves_stats.csv", index=False)
