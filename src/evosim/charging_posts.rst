.. _charging-posts:

Charging Posts
==============

.. contents::
    :depth: 2


Usage
-----

Charging posts are represented by a table with columns for the latitude, longitude,
socket type, charger type, current occupancy and maximum capacity. Potentially it can
accept other columns as well. The simplest way to generate one is to use
:py:func:`evosim.charging_posts.random_charging_posts`:

.. doctest:: charging_posts_usage
    :options: +NORMALIZE_WHITESPACE

    >>> posts = evosim.charging_posts.random_charging_posts(5, seed=1)
    >>> posts
          latitude  longitude  capacity  occupancy          socket charger
    post
    0        51.48       0.24         1          0             CCS    SLOW
    1        51.68       0.95         1          0         CHADEMO    FAST
    2        51.31       0.22         1          0             CCS   RAPID
    3        51.68       0.46         1          0  DC_COMBO_TYPE2    SLOW
    4        51.39      -0.45         1          0         CHADEMO    SLOW

The random ``seed`` is optional. It is provided here so that the code and output above
can be tested reproducibly. By default, the function returns a
:py:class:`pandas.DataFrame`. The ``socket`` and ``charger`` columns take their values
from :py:class:`evosim.charging_posts.Sockets` and :py:class:`evosim.charging_posts.Chargers`:

.. doctest:: charging_posts_usage
    :options: +NORMALIZE_WHITESPACE

    >>> posts.socket
    post
    0               CCS
    1           CHADEMO
    2               CCS
    3    DC_COMBO_TYPE2
    4           CHADEMO
    Name: socket, dtype: object

    >>> posts.socket[0]
    <Sockets.CCS: 32>

    >>> posts.charger
    post
    0     SLOW
    1     FAST
    2    RAPID
    3     SLOW
    4     SLOW
    Name: charger, dtype: object

    >>> posts.charger[0]
    <Chargers.SLOW: 1>

The range of latitude and longitude, the number of socket and charger types and their
distributions can all be changed in the input. For instance, the following limits the
sockets to two type and heavily favors one rather than the other:

.. doctest:: charging_posts_usage
    :options: +NORMALIZE_WHITESPACE

    >>> from evosim.charging_posts import Sockets
    >>> evosim.charging_posts.random_charging_posts(
    ...     n=10,
    ...     socket_types=list(Sockets)[:2],
    ...     socket_distribution=[0.2, 0.8],
    ...     capacity=(1, 5),
    ...     seed=1,
    ... )
          latitude  longitude  capacity  occupancy socket charger
    post
    0        51.48       0.82         4          0  TYPE2    FAST
    1        51.68       0.44         4          0  TYPE2    FAST
    2        51.31       0.08         2          0  TYPE2    SLOW
    3        51.68       0.88         1          0  TYPE2    SLOW
    4        51.39       0.03         3          0  TYPE2    FAST
    5        51.44       0.29         3          0  TYPE2    FAST
    6        51.62      -0.27         4          0  TYPE2    FAST
    7        51.43       0.21         2          0  TYPE2   RAPID
    8        51.50      -0.14         2          0  TYPE1    FAST
    9        51.26      -0.04         1          0  TYPE2    FAST

Both chargers and sockets can accept multiple types simultaneously, and they can be
queried accordingly:

.. doctest:: charging_posts_usage
    
    >>> Sockets.CCS | Sockets.TYPE1
    <Sockets.CCS|TYPE1: 33>
    >>> (Sockets.CCS | Sockets.TYPE1) & Sockets.TYPE1 == Sockets.TYPE1
    True
    >>> (Sockets.CCS | Sockets.TYPE1) & Sockets.TYPE2 == Sockets.TYPE2
    False
    >>> # Alternatively, we can compare to the "null" socket matching nothing
    >>> (Sockets.CCS | Sockets.TYPE1) & Sockets.TYPE2 == Sockets(0)
    True
    >>> # or use bool to convert to boolean
    >>> bool((Sockets.CCS | Sockets.TYPE1) & Sockets.TYPE2)
    False
    >>> # or use numpy's bitwise_and when working with arrays
    >>> np.bitwise_and(
    ...     np.array([Sockets.TYPE2, Sockets.CCS | Sockets.TYPE1]),
    ...     np.array([Sockets.TYPE2, Sockets.TYPE2])
    ... ).astype(bool)
    array([ True, False])


Reading and writing
-------------------

The charging posts can be written and read quite easily using :py:mod:`pandas`
capabilities in that domain. For instance, here we write to a (temporary) csv file, read
the information back and check that it is still the same.

.. testcode:: charging_posts_io

    from io import StringIO
    charging_posts = evosim.charging_posts.random_charging_posts(5, seed=1)

    # write to file ... or to a string buffer
    stream = StringIO()
    charging_posts.to_csv(stream)

    # read from file ... or from a string buffer
    stream.seek(0)
    reread = evosim.charging_posts.to_charging_posts(pd.read_csv(stream))

    assert evosim.charging_posts.is_charging_posts(reread)
    assert (charging_posts.round(4) == reread.round(4)).all().all()

.. note::

    We could just as easily write to a file with ``charging_posts.to_csv("posts.csv")``
    and then read from it with
    ``evosim.charging_posts.to_charging_posts(pd.read_csv("posts.csv"))``.  Instead, we
    read and write to an object in memory that behaves like a file. This is mainly
    because it is not allowed to write to temporary file on the windows machines where
    the code in this manual is tested.

Writing to a csv file, or to any format supported by :py:mod:`pandas` is
straightforward. Reading from a file is also fairly straightforward, but it requires one
extra step: the dataframe read from file is transformed to a charging post via
:py:func:`evosim.charging_posts.to_charging_posts`. This ensures that the required
columns are there and have the correct types. In the penultimate line, we verify with
:py:func:`evosim.charging_posts.is_charging_posts` that the transformed dataframe is
indeed a table of charging posts.


.. topic:: Floating point comparisons

    In the snippet above, we compare the two tables with a finite number of decimal
    points. This is only to ensure the comparison is not influenced by how floating
    points are represented in the csv file written out by pandas. See the option
    `float_format` in :py:meth:`pandas.DataFrame.to_csv` for more details.
