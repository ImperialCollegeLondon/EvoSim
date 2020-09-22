Matchers
========

Matchers are functions that return true of false given charging points and electric
vehicles: ``matcher(electric_vehicle, charging_point) -> bool``.  If one of the other
are a sequence (e.g. a dataframe), then the matchers are applied element-wise and return
an array. Matchers are stand-alone functions in :py:mod:`evosim.matchers`.  They can be
accessed directly or created via :py:mod:`evosim.matchers.factory`:

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
    9     True
    Name: socket, dtype: bool

Here we create a matcher which checks for socket compatibility. We check that it is
indeed just the relevant function from :py:mod:`evosim.matchers`. The we match the first
charging point with the fleet of electric vehicles.

Using the factory becomes interesting when we want to apply a combination of matchers
(using ``and``):

.. doctest:: matchers

    >>> matcher = evosim.matchers.factory(
    ...     ["socket_compatibility", "charger_compatibility"]
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
    Name: socket, dtype: bool
