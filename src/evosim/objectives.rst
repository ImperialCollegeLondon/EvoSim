Objectives
==========

Objectives are functions that return a floating point number given charging posts and
electric vehicles: ``objective(electric_vehicle, charging_post) -> float``. If one of
the other are a sequence (e.g. a dataframe), then the objetive is applied element-wise
and return an array. Objectives are stand-alone functions in
:py:mod:`evosim.objectives`. 

There are currently two objectives: 

* :py:func:`~evosim.objectives.distance`: great circle distance in kilometers, adequate
  for double precision floating points.
* :py:func:`~evosim.objectives.haversine_distance`: great circle distance in kilometers
  using a more expensive formula that is accurate for small distances, especially with
  single-precision floating points.

They can be used as follows:

.. doctest:: objectives

    >>> a = evosim.charging_posts.random_charging_posts(5, seed=1)
    >>> b = evosim.charging_posts.random_charging_posts(5, seed=2)
    >>> evosim.objectives.distance(a, b)
    post
    0    41.30
    1    88.79
    2    57.54
    3    57.34
    4    82.12
    dtype: float64
