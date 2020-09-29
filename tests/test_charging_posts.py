import dask.dataframe as dd


def test_random_dask_charging_post(rng, n=6):
    from evosim.charging_posts import random_charging_posts

    charging_posts = random_charging_posts(n, seed=rng, npartitions=1)
    assert isinstance(charging_posts, dd.DataFrame)
    assert len(charging_posts) == n
    assert set(charging_posts.columns).issubset(
        ["latitude", "longitude", "socket", "charger", "occupancy", "capacity"]
    )
    assert charging_posts.socket.dtype == "category"
    assert charging_posts.charger.dtype == "category"


def test_random_charging_post_with_capacity(rng):
    from evosim.charging_posts import random_charging_posts

    charging_posts = random_charging_posts(
        50, seed=rng, occupancy=(1, 100), capacity=(1, 5)
    )
    assert (charging_posts.occupancy <= charging_posts.capacity).all()
