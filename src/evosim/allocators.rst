Allocators
==========

Allocators are algorithms that allocate electric vehicles to charging posts. They will
generally take as input arguments a dataframe of electric vehicles and a dataframe of
charging posts. They may also accept a matcher function from :py:mod:`evosim.matchers`,
as well as an objective function from :py:mod:`evosim.objectives`. For the purpose of
exposition, we can generate a random problem as done below:

.. doctest:: random_allocator

    >>> rng = np.random.default_rng(1)
    >>> socket_types = list(evosim.charging_posts.Sockets)[:2]
    >>> charger_types = list(evosim.charging_posts.Chargers)[:2]

    >>> cps = evosim.charging_posts.random_charging_posts(
    ...     10,
    ...     capacity = 3,
    ...     socket_types=socket_types,
    ...     charger_types=charger_types,
    ...     seed=rng,
    ... )
    >>> cps
       latitude  longitude socket charger  capacity  occupancy
    0     51.48       0.82  TYPE1    SLOW         2          0
    1     51.68       0.44  TYPE2    FAST         2          0
    2     51.31       0.08  TYPE1    SLOW         1          0
    3     51.68       0.88  TYPE1    FAST         1          0
    4     51.39       0.03  TYPE1    FAST         2          0
    5     51.44       0.29  TYPE1    SLOW         2          0
    6     51.62      -0.27  TYPE1    FAST         2          0
    7     51.43       0.21  TYPE2    SLOW         3          0
    8     51.50      -0.14  TYPE2    SLOW         2          0
    9     51.26      -0.04  TYPE2    FAST         2          0

    >>> evs = evosim.fleet.random_fleet(
    ...     rng.integers(low=len(cps.capacity), high=cps.capacity.sum()),
    ...     socket_types=socket_types,
    ...     charger_types=charger_types,
    ...     seed=rng,
    ... )
    >>> evs
        latitude  longitude socket charger  dest_lat  dest_long                      model
    0      51.27  -1.65e-01  TYPE2    SLOW     51.62       0.64             CITROEN_C_ZERO
    1      51.49   9.04e-01  TYPE2    SLOW     51.28       0.25                   BMW_330E
    2      51.46  -1.65e-01  TYPE2    FAST     51.62       1.02        MERCEDES_BENZ_C350E
    3      51.28  -3.57e-01  TYPE2    SLOW     51.32       0.61                  BMW_225XE
    4      51.54   9.97e-01  TYPE2    FAST     51.42       0.92        MERCEDES_BENZ_E350E
    5      51.63   1.01e+00  TYPE2    FAST     51.39       0.10  MITSUBISHI_OUTLANDER_PHEV
    6      51.52   1.03e+00  TYPE1    FAST     51.56       0.45           SMART_EQ_FORFOUR
    7      51.37   3.26e-01  TYPE1    SLOW     51.33      -0.16   PORSCHE_PANAMERA_EHYBRID
    8      51.63  -2.04e-02  TYPE1    FAST     51.43       1.24  MINI_COUNTRYMAN_COOPER_SE
    9      51.48  -4.88e-01  TYPE1    SLOW     51.25      -0.07             CITROEN_C_ZERO
    10     51.48   6.30e-01  TYPE2    FAST     51.37      -0.05   PORSCHE_PANAMERA_EHYBRID
    11     51.59   7.60e-01  TYPE2    SLOW     51.44      -0.37  MINI_COUNTRYMAN_COOPER_SE
    12     51.32   9.62e-01  TYPE1    SLOW     51.30      -0.05      VOLKSWAGEN_PASSAT_GTE
    13     51.62  -6.71e-03  TYPE2    FAST     51.53       0.84            SMART_EQ_FORTWO
    14     51.56  -1.23e-01  TYPE2    FAST     51.42       0.72              TESLA_MODEL_X
    15     51.60   6.19e-01  TYPE2    FAST     51.58      -0.27   PORSCHE_PANAMERA_EHYBRID

    >>> matcher = evosim.matchers.factory(
    ...     ["socket_compatibility", "charger_compatibility"]
    ... )


Random Allocation
-----------------

The random allocation algorithm :py:func:`~evosim.allocators.random_allocator` does just
that: it randomly allocates the vehicles to a matching charging post. We can call it as
follows:

.. doctest:: random_allocator
    :options: +NORMALIZE_WHITESPACE

    >>> result = evosim.allocators.random_allocator(evs, cps, matcher, seed=rng)
    >>> result
        latitude  longitude socket charger  dest_lat  dest_long  \
    0      51.27  -1.65e-01  TYPE2    SLOW     51.62       0.64
    1      51.49   9.04e-01  TYPE2    SLOW     51.28       0.25
    2      51.46  -1.65e-01  TYPE2    FAST     51.62       1.02
    3      51.28  -3.57e-01  TYPE2    SLOW     51.32       0.61
    4      51.54   9.97e-01  TYPE2    FAST     51.42       0.92
    5      51.63   1.01e+00  TYPE2    FAST     51.39       0.10
    6      51.52   1.03e+00  TYPE1    FAST     51.56       0.45
    7      51.37   3.26e-01  TYPE1    SLOW     51.33      -0.16
    8      51.63  -2.04e-02  TYPE1    FAST     51.43       1.24
    9      51.48  -4.88e-01  TYPE1    SLOW     51.25      -0.07
    10     51.48   6.30e-01  TYPE2    FAST     51.37      -0.05
    11     51.59   7.60e-01  TYPE2    SLOW     51.44      -0.37
    12     51.32   9.62e-01  TYPE1    SLOW     51.30      -0.05
    13     51.62  -6.71e-03  TYPE2    FAST     51.53       0.84
    14     51.56  -1.23e-01  TYPE2    FAST     51.42       0.72
    15     51.60   6.19e-01  TYPE2    FAST     51.58      -0.27
    <BLANKLINE>
                            model  allocation
    0              CITROEN_C_ZERO           8
    1                    BMW_330E           7
    2         MERCEDES_BENZ_C350E        <NA>
    3                   BMW_225XE           7
    4         MERCEDES_BENZ_E350E        <NA>
    5   MITSUBISHI_OUTLANDER_PHEV           9
    6            SMART_EQ_FORFOUR           3
    7    PORSCHE_PANAMERA_EHYBRID           0
    8   MINI_COUNTRYMAN_COOPER_SE           4
    9              CITROEN_C_ZERO           0
    10   PORSCHE_PANAMERA_EHYBRID           1
    11  MINI_COUNTRYMAN_COOPER_SE           8
    12      VOLKSWAGEN_PASSAT_GTE           5
    13            SMART_EQ_FORTWO           1
    14              TESLA_MODEL_X           9
    15   PORSCHE_PANAMERA_EHYBRID        <NA>

The allocator returns a (:py:meth:`shallow <pandas.DataFrame.copy>`) copy the electric
vehicles table with an extra column, ``allocation``. The column are either indices into
the charging posts table, or ``pandas.NA`` indicating that the cars could not be
allocated to a charging post. We can check that the allocations do match:

.. doctest:: random_allocator

    >>> alloc_evs = result.loc[~result.allocation.isna()]
    >>> alloc_cps = cps.loc[alloc_evs.allocation.to_numpy()]
    >>> matcher(
    ...     alloc_evs.reset_index(drop=True), alloc_cps.reset_index(drop=True)
    ... ).all()
    True

This snippet pares down electric vehicles to those that have been allocated a charging
post. Then it generates a table with such charging posts. Finally, it matches the two
table. In order to do so, the indices of the tables are reset so that they match.
Retaining the meaning of the indices during table manipulation is a :py:mod:`pandas`
feature which has to be done away with in this particular setting.

We can also check that each that the allocation targeted available space only:

.. doctest:: random_allocator

    >>> allocation = result.groupby("allocation").allocation.count()
    >>> occupancy = allocation + cps.occupancy
    >>> occupancy
    0    2.0
    1    2.0
    2    NaN
    3    1.0
    4    1.0
    5    1.0
    6    NaN
    7    2.0
    8    2.0
    9    2.0
    dtype: float64

    >>> np.logical_or(occupancy <= cps.capacity, occupancy.isna()).all()
    True

The first line above groups allocations by the charging post they are targeting and
then counts the number of new assignement. The second line computes the occupancy
including new allocations. However, not all charging posts are targeted. These posts
are not found in ``allocation``, and hence their occupancy is ``np.NaN``. This treatment
of missing data is a feature of :py:mod:`pandas`. The last line shows that allocations
targeted available spaces.


.. testcode:: random_allocator

    spare_evs = result.loc[result.allocation.isna()]
    spare_cps = cps.loc[occupancy.fillna(0) < cps.capacity]
    for _, unallocated in spare_evs.iterrows():
        assert not matcher(unallocated, spare_cps).any()

Here we first figure out the spare (unallocated) vehicles and spare charging posts. We
then check the spare vehicles do not fit with any of the spare charging posts.
