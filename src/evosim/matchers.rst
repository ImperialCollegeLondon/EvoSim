Matchers
========

.. testsetup:: matchers
    
    import pandas as pd
    import numpy as np
    import dask.dataframe as dd
    import evosim

    pd.options.display.precision = 2
    pd.options.display.max_categories = 8
    pd.options.display.max_rows = 20
    pd.options.display.max_columns = 10
    pd.options.display.width = 88
    
Matchers are functions that return true of false given charging points and electric
vehicles. If one of the other are a sequence (e.g. a dataframe), then the matchers are
applied element-wise. Matchers are stand-alone functions in :py:mod:`evosim.matchers`.
They can be accessed directly or created via :py:mod:`evosim.matchers.factory`:

.. doctest:: matchers

    >>> matcher = evosim.matchers.factory("socket_compatibility")
    >>> matcher is evosim.matchers.socket_compatibility
    True

    >>> cps = evosim.supply.random_charging_points(5, seed=1)
    >>> evs = evosim.electric_vehicles.random_electric_vehicles(10, seed=1)
    >>> matcher(evs, cps.loc[0])
    0    False
    1    False
    2    False
    3    False
    4    False
    5    False
    6    False
    7     True
    8    False
    9    False
    dtype: bool

Here we create a matcher which checks for socket compatibility. We check that it is
indeed just the relevant function from :py:mod:`evosim.matchers`. The we match the first
charging point with the fleet of electric vehicles.

Using the factory becomes interesting when we want to apply a combination of matchers
(using ``and``):

.. doctest:: matchers

    >>> matcher = evosim.matchers.factory(
    ...     ["socket_compatibility", "charging_point_availability"]
    ... )
    >>> matcher(evs, cps.loc[0])
    0    False
    1    False
    2    False
    3    False
    4    False
    5    False
    6    False
    7     True
    8    False
    9    False
    dtype: bool

The matcher :py:mod:`~evosim.matchers.charging_point_availability` checks whether there
is any occupancy left. For a single charging point, it is either ``True`` or ``False``.
It does not actually depend on the vehicles. Hence, the result has not really changed
even if both functions are applied.

 .. doctest:: matchers

    >>> evosim.matchers.charging_point_availability(None, cps.loc[0])
    True
    >>> evosim.matchers.charging_point_availability(None, cps)
    0    True
    1    True
    2    True
    3    True
    4    True
    dtype: bool

Nevertheless, :py:mod:`~evosim.matchers.charging_point_availability` must still conform
to the same interface as all other matchers, so that it can be used with others via the
factory.
