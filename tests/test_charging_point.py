import dask.dataframe as dd


def test_random_dask_charging_point(n=6):
    from evosim.supply import random_charging_points

    charging_points = random_charging_points(n, npartitions=1)
    assert isinstance(charging_points, dd.DataFrame)
    assert len(charging_points) == n
    assert set(charging_points.columns).issubset(
        ["latitude", "longitude", "socket", "charger", "occupancy", "capacity"]
    )
    assert charging_points.socket.dtype == "category"
    assert charging_points.charger.dtype == "category"


def test_random_charging_point_with_capacity():
    from evosim.supply import random_charging_points

    charging_points = random_charging_points(50, occupancy=(1, 100), capacity=(1, 5))
    assert (charging_points.occupancy <= charging_points.capacity).all()
