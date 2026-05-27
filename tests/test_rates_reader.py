from oq_tsunami_ext.integrate import read_event_rates_wide_csv


def test_read_event_rates_wide_csv(tmp_path):
    p = tmp_path / "rates.csv"
    p.write_text("eid,s0,s1\n1,0.1,0.2\n2,0.0,0.3\n")
    rm = read_event_rates_wide_csv(p)
    assert rm.eids.tolist() == [1, 2]
    assert rm.samples == ["s0", "s1"]
    assert rm.rates.shape == (2, 2)
