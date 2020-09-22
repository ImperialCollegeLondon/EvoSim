from pytest import approx


def test_distance():
    from evosim.objectives import distance, haversine_distance
    from evosim.supply import random_charging_points

    a = random_charging_points(100, seed=2)[["latitude", "longitude"]]
    b = random_charging_points(100, seed=5)[["latitude", "longitude"]]

    assert distance(a, b).to_numpy() == approx(haversine_distance(a, b).to_numpy())
