def test_random_charging_post_with_capacity(rng):
    from evosim.charging_posts import random_charging_posts

    charging_posts = random_charging_posts(
        50, seed=rng, occupancy=(1, 100), capacity=(1, 5)
    )
    assert (charging_posts.occupancy <= charging_posts.capacity).all()
