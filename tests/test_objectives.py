from pytest import approx


def test_distance(rng):
    from evosim.objectives import distance, haversine_distance
    from evosim.supply import random_charging_points

    a = random_charging_points(100, seed=rng)[["latitude", "longitude"]]
    b = random_charging_points(100, seed=rng)[["latitude", "longitude"]]

    assert distance(a, b).to_numpy() == approx(haversine_distance(a, b).to_numpy())
