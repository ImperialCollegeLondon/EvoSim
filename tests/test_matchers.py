from pytest import mark


def test_charging_post_availability():
    from evosim.matchers import charging_post_availability
    from dataclasses import dataclass

    @dataclass
    class ChargingPost:
        occupancy: int = 0
        capacity: int = 1

    assert charging_post_availability(None, ChargingPost(0, 1))
    assert not charging_post_availability(None, ChargingPost(1, 1))


@mark.parametrize("npartitions", [None, 1, 2])
def test_distance_from_destination(npartitions):
    from evosim.matchers import distance_from_destination, distance
    from evosim.charging_posts import random_charging_posts
    from evosim.electric_vehicles import random_electric_vehicles

    cps = random_charging_posts(1, seed=1, npartitions=npartitions)
    evs = random_electric_vehicles(10, seed=2, npartitions=npartitions)
    dest = distance_from_destination(evs, cps.loc[0], max_distance=30)
    if hasattr(dest, "compute"):
        dest = dest.compute()
    assert len(dest) == len(evs)

    current = distance(evs, cps.loc[0], max_distance=30)
    if hasattr(current, "compute"):
        current = current.compute()
    assert (dest != current).any()


def test_socket_compatibility(rng):
    from evosim.charging_posts import random_charging_posts
    from evosim.electric_vehicles import random_electric_vehicles
    from evosim.matchers import socket_compatibility

    cps = random_charging_posts(10, seed=rng, socket_multiplicity=4)
    evs = random_electric_vehicles(10, seed=rng, socket_multiplicity=4)
    result = socket_compatibility(cps, evs)
    expected = [bool(a & b) for a, b in zip(evs.socket, cps.socket)]
    assert (result == expected).all()
