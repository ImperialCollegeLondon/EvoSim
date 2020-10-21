Allocators
==========

Allocators are algorithms that allocate electric vehicles to charging posts. They will
generally take as input arguments a dataframe of electric vehicles and a dataframe of
charging posts. They may also accept a matcher function from :py:mod:`evosim.matchers`,
as well as an objective function from :py:mod:`evosim.objectives`.

Random Allocator
----------------

The random allocator simply allocates each electriv vehicle to a charging post, as long
as the vehicle and post are compatible according to a matcher function. For the purpose
of exposition, we can generate a random problem as done below:

.. testcode:: random_allocator,greedy_allocator

    rng = np.random.default_rng(1)
    sockets = list(evosim.charging_posts.Sockets)[:2]
    chargers = list(evosim.charging_posts.Chargers)[:2]
    charging_posts = evosim.charging_posts.random_charging_posts(
        100, capacity=3, socket_types=sockets, charger_types=chargers, seed=rng,
    ).sample(10, random_state=2).sort_index()
    fleet = evosim.fleet.random_fleet(
        400, socket_types=sockets, charger_types=chargers, seed=rng
    ).sample(40, random_state=3).sort_index()
    matcher = evosim.matchers.factory(["socket_compatibility", "charger_compatibility"])


Random Allocation
-----------------

The random allocation algorithm :py:func:`~evosim.allocators.random_allocator` does just
that: it randomly allocates the vehicles to a matching charging post. We can call it as
follows:

.. doctest:: random_allocator
    :options: +NORMALIZE_WHITESPACE

    >>> result = evosim.allocators.random_allocator(
    ...     fleet, charging_posts, matcher, seed=rng
    ... )
    >>> (result.loc[:, fleet.columns] == fleet).all()
    latitude     True
    longitude    True
    socket       True
    charger      True
    dest_lat     True
    dest_long    True
    model        True
    dtype: bool

    >>> result.allocation.iloc[:10]
    15    <NA>
    16      23
    24       2
    37      30
    40    <NA>
    56      30
    66    <NA>
    73      24
    82    <NA>
    83      30
    Name: allocation, dtype: object

The allocator returns a (:py:meth:`shallow <pandas.DataFrame.copy>`) shallow copy of the
electric vehicles table with an extra column, ``allocation``. Each element of the
allocation column is either a label into the charging posts table, or ``pandas.NA``,
indicating that the car could not be allocated to a charging post. We can check that the
allocations do match:

.. doctest:: random_allocator

    >>> alloc_fleet = result.dropna()
    >>> alloc_infra = infrastructure.loc[alloc_fleet.allocation]
    >>> matcher(alloc_fleet, alloc_infra.set_index(alloc_fleet.index)).all()
    True

This snippet pares down electric vehicles to those that have been allocated a charging
post. Then it generates a table with such charging posts. Finally, it matches the two
table. In order to do so, the labels of the allocated infrastructure table are set to
match the allocated fleet. This feature of :py:mod:`pandas` ensure we are comparing
like-to-like.

We can also check that each that the allocation targeted available space only:

.. doctest:: random_allocator

    >>> allocation = result.allocation.value_counts().reindex_like(charging_posts)
    >>> occupancy = allocation + charging_posts.occupancy
    >>> occupancy
    2     2
    13    3
    16    2
    23    2
    24    1
    27    1
    28    2
    30    3
    56    2
    83    2
    dtype: int64

    >>> (occupancy <= charging_posts.capacity).all()
    True

The first line above counts the number of occurances of each allocation. The second line
computes the occupancy including new allocations. If no vehicle where allocated to a
given post, then it would show an occupancy of ``pd.NA``, i.e. a missing data entry as
modeled by :py:mod:`pandas`. The last line shows that allocations targeted available
spaces (note that :py:mod:`pandas` automatically dropped the missing value from the
aggregation operation).


.. testcode:: random_allocator

    spare_fleet = result.loc[result.allocation.isna()]
    spare_infra = charging_posts.loc[occupancy.fillna(0) < charging_posts.capacity]
    for _, unallocated in spare_fleet.iterrows():
        assert not matcher(unallocated, spare_infra).any()

Here we first figure out the spare (unallocated) vehicles and spare charging posts. We
then check the spare vehicles do not fit with any of the spare charging posts.
