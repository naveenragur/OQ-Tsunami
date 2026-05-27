"""OQ Tsunami extension package."""

__all__ = ["patch_imt"]


def patch_imt():
    """Register/enable TSU_DEPTH IMT.

    We keep this as a best-effort patch: if OpenQuake already supports custom
    IMTs (or TSU_DEPTH is already known), this is a no-op.

    The implementation uses monkey-patching because OQ does not expose a
    stable plugin API for IMT registration.
    """
    try:
        from openquake.hazardlib import imt as oq_imt
    except Exception:
        return

    # If already works, do nothing
    try:
        oq_imt.from_string("TSU_DEPTH")
        return
    except Exception:
        pass

    # Patch parser to accept TSU_DEPTH as a scalar IMT.
    # We map it to a simple IMT-like object with a string representation.
    # This is enough for risk side, as we are importing GMFs.

    orig_from_string = oq_imt.from_string

    def from_string_patched(s):
        if s == "TSU_DEPTH":
            # create a minimal IMT instance; reuse PGA class if needed but with
            # a different string identifier. The engine mostly uses `.string`.
            pga = orig_from_string("PGA")
            pga.string = "TSU_DEPTH"  # type: ignore[attr-defined]
            return pga
        return orig_from_string(s)

    oq_imt.from_string = from_string_patched
