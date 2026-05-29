import argparse
import os
from pathlib import Path

from oq_tsunami_ext.integrate import integrate_epistemic_rates
from oq_tsunami_ext.patcher import apply_patches, patch_status, verify_patches


def _parse_rps(s: str):
    return [float(x.strip()) for x in s.split(",") if x.strip()]


def main(argv=None):
    p = argparse.ArgumentParser(prog="oq-tsunami")
    sub = p.add_subparsers(dest="cmd", required=True)

    patch = sub.add_parser(
        "patch",
        help="Apply and verify the OQ-Tsunami patch set on an oq-engine checkout",
    )
    patch_sub = patch.add_subparsers(dest="patch_cmd", required=True)
    for name in ("status", "apply", "verify"):
        pp = patch_sub.add_parser(name)
        pp.add_argument("--oq-engine", required=True, help="Path to oq-engine checkout")

    ip = sub.add_parser(
        "integrate",
        help="Compute AAL and EP curves for epistemic event-rate samples from an OQ calc",
    )
    ip.add_argument("--calc-id", type=int, required=True)
    ip.add_argument("--event-rates", required=True, help="CSV with eid + sample columns")
    ip.add_argument(
        "--investigation-time",
        type=float,
        default=1.0,
        help="Investigation time T (years) used to convert rates to PoEs",
    )
    ip.add_argument(
        "--return-periods",
        default="10,50,100,250,500",
        help="Comma-separated return periods for EP curve reporting",
    )
    ip.add_argument(
        "--export-dir",
        default=os.environ.get("OQ_EXPORT_DIR", "/tmp"),
        help="Where to write CSV outputs",
    )
    ip.add_argument("--plot", action="store_true", help="Also write PNG plots")
    ip.add_argument(
        "--plot-loss-ratio",
        action="store_true",
        help="Also write PNG plots with losses divided by total exposure value",
    )
    ip.add_argument(
        "--total-exposure-value",
        type=float,
        help="Exposure denominator for loss-ratio plots; inferred when omitted",
    )
    ip.add_argument(
        "--loss-type",
        default="structural",
        help="Loss type used to infer total exposure value",
    )

    args = p.parse_args(argv)

    if args.cmd == "patch":
        oq_engine = Path(args.oq_engine)
        if args.patch_cmd == "status":
            statuses = patch_status(oq_engine)
        elif args.patch_cmd == "apply":
            statuses = apply_patches(oq_engine)
        elif args.patch_cmd == "verify":
            for line in verify_patches(oq_engine):
                print(f"ok: {line}")
            statuses = patch_status(oq_engine)
        for status in statuses:
            mark = "ok" if status.present else "missing"
            print(f"{mark}: {status.name} ({status.detail})")
        return 0

    if args.cmd == "integrate":
        export_dir = Path(args.export_dir)
        export_dir.mkdir(parents=True, exist_ok=True)
        integrate_epistemic_rates(
            calc_id=args.calc_id,
            event_rates_csv=Path(args.event_rates),
            investigation_time=args.investigation_time,
            return_periods=_parse_rps(args.return_periods),
            export_dir=export_dir,
            plot=args.plot or args.plot_loss_ratio,
            plot_loss_ratio=args.plot_loss_ratio,
            total_exposure_value=args.total_exposure_value,
            loss_type=args.loss_type,
        )
        return 0
