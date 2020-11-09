Matchers
========

Creating and using matcher functions
------------------------------------

Matchers are functions that return true or false given charging posts and electric
vehicles: ``matcher(electric_vehicle, charging_post) -> bool``.  If one of the other
are a sequence (e.g. a dataframe), then the matchers are applied element-wise and return
an array. Matchers are stand-alone functions in :py:mod:`evosim.matchers`.  They can be
accessed directly or created via :py:mod:`evosim.matchers.factory`:

.. doctest:: match-one

    >>> matcher = evosim.matchers.factory("socket_compatibility")
    >>> matcher is evosim.matchers.socket_compatibility
    True

    >>> infrastructure = evosim.charging_posts.random_charging_posts(5, seed=1)
    >>> fleet = evosim.fleet.random_fleet(10, seed=1)
    >>> matcher(fleet, infrastructure.loc[0])
    vehicle
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
charging post with the fleet of electric vehicles.

Using the factory becomes interesting when we want to apply a combination of matchers
(using ``and``):

.. doctest:: match-one

    >>> matcher = evosim.matchers.factory(
    ...     ["socket_compatibility", "charger_compatibility"]
    ... )
    >>> matcher(fleet, infrastructure.loc[0])
    vehicle
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


Some matchers, such as :py:func:`evosim.matchers.distance` also accept parameters in the
form of keyword arguments. These parameters can be set from the outset by feeding 
:py:func:`evosim.matchers.factory` a dictionary with a ``name`` and any parameter:

.. doctest:: match-one
    
    >>> dmatcher = evosim.matchers.factory({"name": "distance", "max_distance": 10})
    >>> dmatcher(fleet, infrastructure.loc[1])
    vehicle
    0    False
    1    False
    2    False
    3     True
    4    False
    5    False
    6    False
    7    False
    8    False
    9    False
    dtype: bool

    >>> dmatcher = evosim.matchers.factory({"name": "distance", "max_distance": 30})
    >>> dmatcher(fleet, infrastructure.loc[1])
    vehicle
    0     True
    1    False
    2    False
    3     True
    4    False
    5    False
    6    False
    7    False
    8    False
    9    False
    dtype: bool

Multiple matchers can be combined using a list of dictionaries and strings, e.g.
``[{...}, "...", {...}]``.


Matching multiple electric-vehicles and charging posts
------------------------------------------------------

By default, the matchers operate element-wise when the input fleet and charging posts
are tables: each row of the fleet is matched with the corresponding row of the charging
post. However, `pandas` does not allow comparing two tables (or columns of two tables)
that do not have the same index. This feature helps ensure we are comparing like to
like. And fleet and charging posts generally have different sizes and hence are not
like-to-like.

.. doctest:: match-many

    >>> from pytest import raises
    >>> infrastructure = evosim.charging_posts.random_charging_posts(40, seed=1)
    >>> fleet = evosim.fleet.random_fleet(100, seed=2)
    >>> matcher = evosim.matchers.factory(
    ...     ["socket_compatibility", "charger_compatibility"]
    ... )
    >>> with raises(TypeError):
    ...     matcher(fleet, infrastructure)


However, a subset with the same indices can be compared:

.. doctest:: match-many

    >>> with raises(TypeError):
    ...     matcher(fleet.loc[:10], infrastructure.loc[10:20])
    >>> matcher(fleet.loc[10:20], infrastructure.loc[10:20])
    vehicle
    10    False
    11    False
    12    False
    13    False
    14    False
    15    False
    16    False
    17    False
    18    False
    19     True
    20    False
    dtype: bool

The allocator algorithm often compare fleet and charging posts via an indexing array
from the fleet to the charging posts:

.. doctest:: match-many

    >>> rng = np.random.default_rng(1)
    >>> random_assignation = rng.choice(infrastructure.index, size=len(fleet))
    >>> assigned_posts = infrastructure.loc[random_assignation].set_index(fleet.index)
    >>> matcher(fleet, assigned_posts).sample(5, random_state=29)
    vehicle
    73    False
    8     False
    10    False
    7      True
    19    False
    dtype: bool

Above, we only print a sample of the full matched array.

Another common operation is to match each electric vehicle with each charging post. This
can be achieved with the help of :py:func:`evosim.matchers.match_all_to_all`:

.. doctest:: match-many

    >>> evosim.matchers.match_all_to_all(
    ...     fleet.sample(6, random_state=1),
    ...     infrastructure.sample(4, random_state=82),
    ...     matcher
    ... )
    array([[ True, False, False, False],
           [False, False, False, False],
           [False, False, False, False],
           [False, False,  True,  True],
           [False, False,  True,  True],
           [False, False,  True,  True]])

Each row correspond to a vehicle and each column to a post. The function also allows for
more fanciful indexing into the charging posts, e.g. a different subset of posts for
each vehicle. Please see :py:func:`~evosim.matchers.match_all_to_all` for more
information.
