import dask.dataframe as dd


def test_random_dask_charging_point(n=6):
    from evosim.supply import random_charging_points

    charging_points = random_charging_points(n, npartitions=1)
    assert isinstance(charging_points, dd.DataFrame)
    assert len(charging_points) == n
    assert set(charging_points.columns).issubset(
        ["latitude", "longitude", "socket", "charger"]
    )
    assert charging_points.socket.dtype == "category"
    assert charging_points.charger.dtype == "category"
