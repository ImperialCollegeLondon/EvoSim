from pytest import mark


def test_charging_point_availability():
    from evosim.matchers import charging_point_availability
    from dataclasses import dataclass

    @dataclass
    class ChargingPoint:
        occupancy: int = 0
        capacity: int = 1

    assert charging_point_availability(None, ChargingPoint(0, 1))
    assert not charging_point_availability(None, ChargingPoint(1, 1))


@mark.parametrize("npartitions", [None, 1, 2])
def test_distance_from_destination(npartitions):
    from evosim.matchers import distance_from_destination, distance
    from evosim.supply import random_charging_points
    from evosim.electric_vehicles import random_electric_vehicles

    cps = random_charging_points(1, seed=1, npartitions=npartitions)
    evs = random_electric_vehicles(10, seed=2, npartitions=npartitions)
    dest = distance_from_destination(evs, cps.loc[0], max_distance=30)
    if hasattr(dest, "compute"):
        dest = dest.compute()
    assert len(dest) == len(evs)

    current = distance(evs, cps.loc[0], max_distance=30)
    if hasattr(current, "compute"):
        current = current.compute()
    assert (dest != current).any()
