from pipeline import load_and_clean, segment


def test_demo_pipeline_creates_four_segments():
    customers, profiles = segment(load_and_clean(None, demo=True))
    assert len(customers) == 240
    assert customers["Cluster"].nunique() == 4
    assert profiles["Customers"].sum() == len(customers)
