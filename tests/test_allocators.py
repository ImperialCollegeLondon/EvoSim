from pytest import raises


def test_random_allocator_too_many_vehicles(rng):
    from evosim.charging_posts import random_charging_posts
    from evosim.fleet import random_fleet
    from evosim.allocators import random_allocator
    from evosim import matchers

    evs = random_fleet(100, seed=rng)
    cps = random_charging_posts(4, seed=rng, capacity=3, occupancy=3)
    matcher = matchers.factory("socket_compatibility")
    with raises(NotImplementedError):
        random_allocator(evs, cps, matcher, seed=rng)


def test_random_allocator_exact_match(rng):
    from evosim.charging_posts import random_charging_posts
    from evosim.fleet import random_fleet
    from evosim.allocators import random_allocator
    from evosim import matchers

    # a set of charging posts with at least one fully occupied post
    cps = random_charging_posts(40, seed=rng, capacity=3, occupancy=3)
    cps.loc[29, "occupancy"] = cps.loc[29, "capacity"]

    matcher = matchers.factory("socket_compatibility")

    # exactly the cars needed to fill the charging posts according ot the chosen
    # matcher
    indices = [
        i for i, row in cps.iterrows() for _ in range(row.occupancy, row.capacity)
    ]
    evs = random_fleet(len(indices), seed=rng)
    rng.shuffle(indices)
    evs["socket"] = cps.socket.loc[indices].reset_index().socket

    result = random_allocator(evs, cps, matcher, seed=rng)

    # all allocations are within the expected range of indices
    assert (result.allocation >= 0).all()
    assert (result.allocation < len(cps)).all()

    # all allocations target available spaces
    available = cps.loc[cps.occupancy < cps.capacity]
    new_assignements = result.groupby("allocation").allocation.count()
    assert (new_assignements.index == available.index).all()
    assert (available.occupancy + new_assignements == available.capacity).all()

    # all allocation do match
    alloc_cps = cps.loc[result.allocation]
    assert matcher(evs, alloc_cps.reset_index(drop=True)).all()


def test_random_allocator_unassigned_cars(rng):
    from evosim.charging_posts import random_charging_posts
    from evosim.fleet import random_fleet
    from evosim.allocators import random_allocator
    from evosim import matchers

    cps = random_charging_posts(40, seed=rng, capacity=3, occupancy=3)
    cps.loc[29, "occupancy"] = cps.loc[29, "capacity"]

    matcher = matchers.factory("socket_compatibility")

    indices = [
        i for i, row in cps.iterrows() for _ in range(row.occupancy, row.capacity)
    ]
    evs = random_fleet(len(indices), seed=rng)
    rng.shuffle(indices)
    evs["socket"] = cps.socket.loc[indices].reset_index().socket
    unassigned = [1, 3, 5, 7, 11]
    evs.loc[unassigned, "socket"] = None  # these EVs can't be matched

    result = random_allocator(evs, cps, matcher, seed=rng)

    # these EVs found no match and are unassigned
    assert (result.loc[unassigned].allocation.isna()).all()
    # all allocations are within the expected range of indices
    assigned = [i for i in result.index if i not in unassigned]
    assert (result.loc[assigned].allocation >= 0).all()
    assert (result.loc[assigned].allocation < len(cps)).all()

    # all allocations target available spaces
    available = cps.loc[cps.occupancy < cps.capacity]
    new_assignements = result.groupby("allocation").allocation.count()
    occupancy = available.occupancy + new_assignements
    assert set(occupancy.index[occupancy.isna()]).isdisjoint(new_assignements.index)
    assert (
        occupancy.loc[~occupancy.isna()] <= available.capacity.loc[~occupancy.isna()]
    ).all()

    # all allocation do match
    alloc_evs = result.loc[~result.allocation.isna()]
    alloc_cps = cps.loc[alloc_evs.allocation]
    assert matcher(
        alloc_evs.reset_index(drop=True), alloc_cps.reset_index(drop=True)
    ).all()
