import argparse
import os
from pathlib import Path

from oq_tsunami_ext import patch_imt
from oq_tsunami_ext.integrate import integrate_epistemic_rates


def _parse_rps(s: str):
    return [float(x.strip()) for x in s.split(",") if x.strip()]


def main(argv=None):
    patch_imt()

    p = argparse.ArgumentParser(prog="oq-tsunami")
    sub = p.add_subparsers(dest="cmd", required=True)

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

    args = p.parse_args(argv)

    if args.cmd == "integrate":
        export_dir = Path(args.export_dir)
        export_dir.mkdir(parents=True, exist_ok=True)
        integrate_epistemic_rates(
            calc_id=args.calc_id,
            event_rates_csv=Path(args.event_rates),
            investigation_time=args.investigation_time,
            return_periods=_parse_rps(args.return_periods),
            export_dir=export_dir,
        )
