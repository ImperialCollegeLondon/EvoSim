import numpy as np


def test_distance_from_destination():
    from evosim.matchers import distance_from_destination, distance
    from evosim.charging_posts import random_charging_posts
    from evosim.fleet import random_fleet

    cps = random_charging_posts(1, seed=1)
    evs = random_fleet(10, seed=2)
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
    from evosim.fleet import random_fleet
    from evosim.matchers import socket_compatibility

    cps = random_charging_posts(10, seed=rng, socket_multiplicity=4)
    evs = random_fleet(10, seed=rng, socket_multiplicity=4)
    result = socket_compatibility(cps, evs)
    expected = [bool(a & b) for a, b in zip(evs.socket, cps.socket)]
    assert (result == expected).all()


def test_all_to_all_indices(rng: np.random.Generator):
    from evosim.charging_posts import random_charging_posts
    from evosim.fleet import random_fleet
    from evosim import matchers

    infrastructure = random_charging_posts(40, seed=rng)
    fleet = random_fleet(100, seed=rng)
    matcher = matchers.factory(["socket_compatibility", "charger_compatibility"])

    indices = rng.integers(low=0, high=len(infrastructure), size=(len(fleet), 4))
    result = matchers.match_all_to_all(fleet, infrastructure, matcher, indices=indices)

    for i in range(indices.shape[1]):
        column = matcher(
            fleet, infrastructure.iloc[indices[:, i]].set_index(fleet.index)
        )
        assert (result[:, i] == column).all()


def test_all_to_all_labels(rng: np.random.Generator):
    from evosim.charging_posts import random_charging_posts
    from evosim.fleet import random_fleet
    from evosim import matchers

    infrastructure = random_charging_posts(40, seed=rng)
    fleet = random_fleet(100, seed=rng)
    matcher = matchers.factory(["socket_compatibility", "charger_compatibility"])

    labels = rng.integers(low=0, high=len(infrastructure), size=len(fleet))
    result = matchers.match_all_to_all(fleet, infrastructure, matcher, labels=labels)

    for i in range(len(infrastructure)):
        column = matcher(fleet, infrastructure.loc[labels[i]])
        assert (result[:, i] == column).all()
