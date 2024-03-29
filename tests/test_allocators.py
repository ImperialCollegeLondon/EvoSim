import numpy as np
import pandas as pd


def test_random_allocator_too_many_vehicles(rng):
    from evosim.charging_posts import random_charging_posts
    from evosim.fleet import random_fleet
    from evosim.allocators import random_allocator
    from evosim import matchers

    evs = random_fleet(20, seed=rng)
    cps = random_charging_posts(4, seed=rng, capacity=3, occupancy=3)

    # exactly the cars needed to fill the charging posts according ot the chosen
    # matcher
    cps_indices = [
        i for i, row in cps.iterrows() for _ in range(row.occupancy, row.capacity)
    ]
    rng.shuffle(cps_indices)
    evs_indices = list(evs.index)
    rng.shuffle(evs_indices)
    evs.loc[evs_indices[: len(cps_indices)], "socket"] = cps.socket.loc[
        cps_indices
    ].to_numpy()

    matcher = matchers.factory("socket_compatibility")
    result = random_allocator(evs, cps, matcher, seed=rng)
    new_allocations = result.groupby("allocation").allocation.count()
    assert (new_allocations + cps.occupancy == cps.capacity).all()


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
    new_allocations = result.groupby("allocation").allocation.count()
    assert (new_allocations.index == available.index).all()
    assert (available.occupancy + new_allocations == available.capacity).all()

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
    new_allocations = result.groupby("allocation").allocation.count()
    occupancy = available.occupancy + new_allocations
    assert set(occupancy.index[occupancy.isna()]).isdisjoint(new_allocations.index)
    assert (
        occupancy.loc[occupancy.notna()] <= available.capacity.loc[occupancy.notna()]
    ).all()

    # all allocation do match
    alloc_evs = result.loc[result.allocation.notna()]
    alloc_cps = cps.loc[alloc_evs.allocation]
    assert matcher(
        alloc_evs.reset_index(drop=True), alloc_cps.reset_index(drop=True)
    ).all()


def test_void_overbooking(rng):
    from evosim.charging_posts import random_charging_posts
    from evosim.fleet import random_fleet
    from evosim.allocators import _void_overbooking

    infrastructure = random_charging_posts(20, seed=rng, capacity=5, occupancy=2)
    fleet = random_fleet(100, seed=rng)
    fleet["allocation"] = rng.choice(infrastructure.index, size=len(fleet))
    fleet["allocation"] = fleet.allocation.astype("Int64")
    fleet.loc[fleet.index.isin(rng.choice(fleet.index, size=50)), "allocation"] = pd.NaT

    notoverbooked = _void_overbooking(infrastructure, fleet.allocation)
    assert (notoverbooked == fleet.allocation).dropna().all()
    assert (notoverbooked.dropna().index.isin(fleet.allocation.dropna().index)).all()

    notoverbooking = notoverbooked.value_counts().reindex_like(infrastructure).fillna(0)
    is_overbooked = (
        notoverbooking + infrastructure.occupancy
    ) > infrastructure.capacity
    assert not is_overbooked.any()

    booking = fleet.allocation.value_counts().reindex_like(infrastructure).fillna(0)
    was_overbooked = (booking + infrastructure.occupancy) > infrastructure.capacity
    assert (
        ((notoverbooking + infrastructure.occupancy) == infrastructure.capacity)
        .loc[was_overbooked]
        .all()
    )
    assert (notoverbooking == booking).loc[~was_overbooked].all()
    assert not (notoverbooking == booking).loc[was_overbooked].any()


def test_void_overbooking_single_alloc(rng):
    from evosim.charging_posts import random_charging_posts
    from evosim.fleet import random_fleet
    from evosim.allocators import _void_overbooking

    infrastructure = random_charging_posts(20, seed=rng, capacity=5, occupancy=2)
    fleet = random_fleet(100, seed=rng)
    fleet["allocation"] = 1
    fleet["allocation"] = fleet.allocation.astype("Int64")
    fleet.loc[fleet.index.isin(rng.choice(fleet.index, size=50)), "allocation"] = pd.NaT

    notoverbooked = _void_overbooking(infrastructure, fleet.allocation)
    assert (notoverbooked == fleet.allocation).dropna().all()
    assert (notoverbooked.dropna().index.isin(fleet.allocation.dropna().index)).all()
    assert len(notoverbooked.dropna().unique()) == 1
    assert notoverbooked.dropna().unique()[0] == 1


def test_greedy_allocator(rng):
    from evosim.charging_posts import Sockets, Chargers, random_charging_posts
    from evosim.fleet import random_fleet
    from evosim import matchers
    from evosim.allocators import greedy_allocator

    sockets = list(Sockets)[:2]
    chargers = list(Chargers)[:2]
    charging_posts = random_charging_posts(
        100,
        capacity=3,
        socket_types=sockets,
        charger_types=chargers,
        seed=rng,
    ).sample(50, random_state=2)
    fleet = random_fleet(
        200, socket_types=sockets, charger_types=chargers, seed=rng
    ).sample(100, random_state=3)
    matcher = matchers.factory(["socket_compatibility", "charger_compatibility"])

    result = greedy_allocator(fleet, charging_posts, matcher, nearest_neighbors=-1)

    alloc_fleet = result.dropna()
    alloc_infra = charging_posts.loc[alloc_fleet.allocation]
    assert matcher(alloc_fleet, alloc_infra.set_index(alloc_fleet.index)).all()

    allocation = result.allocation.value_counts().reindex_like(charging_posts)
    occupancy = allocation + charging_posts.occupancy
    assert (occupancy <= charging_posts.capacity).all()

    spare_fleet = result.loc[result.allocation.isna()]
    spare_infra = charging_posts.loc[occupancy.fillna(0) < charging_posts.capacity]
    for _, unallocated in spare_fleet.iterrows():
        assert not matcher(unallocated, spare_infra).any()


def test_greedy_allocator_nearest_neighbor():
    from evosim.charging_posts import Sockets, Chargers, random_charging_posts
    from evosim.fleet import random_fleet
    from evosim import matchers
    from evosim.allocators import greedy_allocator

    rng = np.random.default_rng(1462321313)

    sockets = list(Sockets)[:2]
    chargers = list(Chargers)[:2]
    charging_posts = random_charging_posts(
        100,
        capacity=3,
        socket_types=sockets,
        charger_types=chargers,
        seed=rng,
    ).sample(50, random_state=2)
    fleet = random_fleet(
        200, socket_types=sockets, charger_types=chargers, seed=rng
    ).sample(100, random_state=3)
    matcher = matchers.factory(["socket_compatibility", "charger_compatibility"])

    toosmall = greedy_allocator(fleet, charging_posts, matcher)
    larger = greedy_allocator(fleet, charging_posts, matcher, nearest_neighbors=-1)
    # going to more neighbors happens to be stable
    assert (toosmall.allocation == larger.allocation).all()
    # but some vehicles are newly allocated
    assert toosmall.allocation.notna().sum() != larger.allocation.notna().sum()
