from __future__ import annotations

from pathlib import Path

from oq_tsunami_ext.native import (
    compute_tsunami_metrics,
    infer_total_exposure_value,
    plot_outputs,
    read_event_rates_wide_csv,
    write_csv_outputs,
)


def integrate_epistemic_rates(
    *,
    calc_id: int,
    event_rates_csv: Path,
    investigation_time: float,
    return_periods: list[float],
    export_dir: Path,
    plot: bool = False,
    plot_loss_ratio: bool = False,
    total_exposure_value: float | None = None,
    loss_type: str = "structural",
):
    from openquake.commonlib import datastore

    ratesm = read_event_rates_wide_csv(event_rates_csv)
    with datastore.read(calc_id) as ds:
        df = ds.read_df("risk_by_event")
        portfolio_agg_id = int(ds["risk_by_event"].attrs.get("K", 0))
        if plot_loss_ratio and total_exposure_value is None:
            total_exposure_value = infer_total_exposure_value(ds, loss_type)

    (aals, aal_stats, curves, curve_stats,
     portfolio_aals, portfolio_aal_stats,
     portfolio_curves, portfolio_curve_stats) = compute_tsunami_metrics(
         df, ratesm, return_periods, investigation_time, portfolio_agg_id)
    write_csv_outputs(
        export_dir, aals, aal_stats, curves, curve_stats,
        portfolio_aals, portfolio_aal_stats,
        portfolio_curves, portfolio_curve_stats)
    if plot:
        if plot_loss_ratio and total_exposure_value is None:
            raise ValueError(
                "Cannot infer total exposure value for loss-ratio plots; "
                "pass --total-exposure-value"
            )
        plot_outputs(
            export_dir, aal_stats, curve_stats,
            portfolio_aal_stats, portfolio_curve_stats,
            loss_ratio_denominator=total_exposure_value if plot_loss_ratio else None)
