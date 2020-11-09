Allocators
==========

.. contents:: :depth: 2

Allocators are algorithms that allocate electric vehicles to charging posts. They will
generally take as input arguments a dataframe of electric vehicles and a dataframe of
charging posts. They may also accept a matcher function from :py:mod:`evosim.matchers`,
as well as an objective function from :py:mod:`evosim.objectives`.

For the purpose of exposition, we can generate a random problem as done below:

.. testcode:: random_allocator,greedy_allocator

    rng = np.random.default_rng(1)
    sockets = list(evosim.charging_posts.Sockets)[:2]
    chargers = list(evosim.charging_posts.Chargers)[:2]
    charging_posts = evosim.charging_posts.random_charging_posts(
        100, capacity=3, socket_types=sockets, charger_types=chargers, seed=rng,
    ).sample(10, random_state=2)
    fleet = evosim.fleet.random_fleet(
        400, socket_types=sockets, charger_types=chargers, seed=rng
    ).sample(40, random_state=3)
    matcher = evosim.matchers.factory(["socket_compatibility", "charger_compatibility"])

.. topic:: Indices vs labels

    In the snippet above, we use `sample` to pick a few electric vehicles and few
    charging posts. This is a simple way to ensure that the dataframes indices and
    labels dot not match. It allows us to discover common bugs when working
    with pandas where we (the developer) gets confused between indices and labels. It's
    generally a good thing to do when testing.


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
    vehicle
    376    <NA>
    16       30
    365      13
    82       30
    107    <NA>
    217    <NA>
    396      13
    56       23
    250    <NA>
    40       13
    Name: allocation, dtype: object

The allocator returns a (:py:meth:`shallow <pandas.DataFrame.copy>`) shallow copy of the
electric vehicles table with an extra column, ``allocation``. Each element of the
allocation column is either a label into the charging posts table, or ``pandas.NA``,
indicating that the car could not be allocated to a charging post. We can check that the
allocations do match:

.. doctest:: random_allocator

    >>> alloc_fleet = result.dropna()
    >>> alloc_infra = charging_posts.loc[alloc_fleet.allocation]
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
    post
    83    2
    30    3
    56    2
    24    2
    16    2
    23    2
    2     1
    27    1
    28    2
    13    3
    dtype: int64

    >>> (occupancy <= charging_posts.capacity).all()
    True

The first line above counts the number of occurrences of each allocation. The second
line computes the occupancy including new allocations. If no vehicle where allocated to
a given post, then it would show an occupancy of ``pd.NA``, i.e. a missing data entry as
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


Greedy Allocator
----------------

Using the same random problem as above, we can illustrate the
:py:func:`~evosim.allocators.greedy_allocator`. This allocator tries to match each
vehicle to the nearest compatible post.

.. doctest:: greedy_allocator
    :options: +NORMALIZE_WHITESPACE

    >>> result = evosim.allocators.greedy_allocator(fleet, charging_posts, matcher)
    >>> result.iloc[:5]
             latitude  longitude socket charger  dest_lat  dest_long  \
    vehicle
    376         51.29       1.05  TYPE2    SLOW     51.37       0.91
    16          51.32       1.20  TYPE2    FAST     51.38       0.83
    365         51.42       0.84  TYPE2    SLOW     51.59       0.22
    82          51.46       0.73  TYPE2    FAST     51.53       0.60
    107         51.67      -0.47  TYPE2    SLOW     51.53      -0.16
    <BLANKLINE>
                              model  allocation
    vehicle
    376      HYUNDAI_IONIQ_ELECTRIC          13
    16          MERCEDES_BENZ_E350E          30
    365                      BMW_I3          27
    82                   BMW_X5_40E          23
    107               JAGUAR_I_PACE        <NA>

In the same vein as for :py:func:`~evosim.allocators.random_allocator`, the function
returns a shallow copy of the ``fleet`` with an ``allocation`` column holding the label
of the allocated post in ``charging_posts`` (or ``pd.NA`` if no allocation was
possible). We can check each vehicle is allocated the nearest compatible post, unless
that post is already at capacity.

We can figure out the nearest neighbors using :py:class:`sklearn.neighbors.BallTree`.

.. testcode:: greedy_allocator

    from sklearn.neighbors import BallTree
    post_locations = np.concatenate(
        (
            charging_posts["latitude"].to_numpy()[:, None],
            charging_posts["longitude"].to_numpy()[:, None]
        ),
        axis=1,
    ) * np.pi / 180
    tree = BallTree(post_locations, metric="haversine")

The tree is a special structure which once constructed makes querying for neighbors a
computationally efficient operation. Given a set of locations, it returns for each the
distances and indices of the ``k`` nearest neighbors:

.. doctest:: greedy_allocator

    >>> evs_locations = np.concatenate(
    ...     (
    ...         fleet["dest_lat"].to_numpy()[:, None],
    ...         fleet["dest_long"].to_numpy()[:, None]
    ...     ),
    ...     axis=1,
    ... ) * np.pi / 180
    >>> distances, indices = tree.query(evs_locations, k=len(charging_posts))
    >>> indices[:5, :]
    array([[6, 0, 9, 4, 3, 1, 8, 5, 7, 2],
           [6, 0, 9, 4, 3, 1, 8, 5, 7, 2],
           [3, 5, 1, 2, 4, 8, 7, 9, 6, 0],
           [9, 3, 5, 6, 1, 0, 4, 8, 2, 7],
           [2, 1, 7, 8, 5, 4, 3, 9, 6, 0]]...)

The first row of the matrix above corresponds to the first electric vehicle. It gives
the indices (as in :py:meth:`pandas.DataFrame.iloc`, not the labels of
:py:meth:`pandas.DataFrame.loc`) of the posts, left to right from nearest to furthest.
The distance matrix follows the same structure.


.. topic:: Distances on the surface of the Eartch

    The distances are computed using
    :py:func:`sklearn.metrics.pairwise.haversine_distances` on the unit ball. We can
    easily convert them to kilometers on the surface of the Earth:

    .. doctest:: greedy_allocator

        >>> (distances[:5] * evosim.constants.EARTH_RADIUS_KM).round(2)
        array([[10.64, 13.29, 27.58, 55.58, 58.24, 64.32, 67.21, 67.47, 77.23, 84.69],
               [15.48, 18.86, 26.77, 50.02, 53.75, 58.73, 61.61, 62.68, 71.57, 79.36],
               [12.1 , 13.3 , 17.57, 28.8 , 33.  , 35.21, 36.47, 45.21, 66.92, 69.63],
               [18.86, 29.05, 38.58, 39.84, 41.08, 41.61, 41.9 , 50.95, 57.77, 57.87],
               [12.74, 15.79, 17.91, 26.5 , 28.9 , 34.31, 36.99, 72.97, 89.51, 93.25]])

We can also compute the match between each and every vehicle and post:

.. doctest:: greedy_allocator

    >>> match = evosim.matchers.match_all_to_all(fleet, charging_posts, matcher)
    >>> match[:5, :5]
    array([[False, False, False, False, False],
           [False,  True, False, False, False],
           [False, False, False, False, False],
           [False,  True, False, False, False],
           [False, False, False, False, False]])

:py:func:`evosim.matchers.match_all_to_all` returns an matrix of boolean values where
each row corresponds to a vehicle and each column to a charging post. With nearest
neighbors and match in hand, we can now verify that each vehicle is allocated to the
first empty matching post:

.. testcode:: greedy_allocator

    vacancies = (
        charging_posts.capacity
        - charging_posts.occupancy
        - result.allocation.value_counts().reindex_like(charging_posts).fillna(0)
    )

    iterator = enumerate(result.itertuples(index=False))
    for i, vehicle in iterator:

        post_labels = charging_posts.iloc[indices[i, match[i, indices[i]]]].index

        # post_labels ought all to be compatible with the vehicle
        assert matcher(vehicle, charging_posts.loc[post_labels]).all()

        # if allocated, allocation must be from matching posts
        assert vehicle.allocation is pd.NA or vehicle.allocation in post_labels

        if vehicle.allocation is not pd.NA:
            # list of posts nearer than the allocated one must all be full
            fully_occupied = post_labels[:list(post_labels).index(vehicle.allocation)]
        else:
            # all matching posts must be full
            fully_occupied = post_labels 

        assert (vacancies.loc[fully_occupied] == 0).all()
