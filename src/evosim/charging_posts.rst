.. _charging-posts:

Charging Posts
==============

Charging posts are represented by a table with columns for the latitude, longitude,
socket type, charger type, current occupancy and maximum capacity. Potentially it can
accept other columns as well. The simplest way to generate one is to use
:py:func:`evosim.charging_posts.random_charging_posts`:

.. doctest:: charging_posts

    >>> result = evosim.charging_posts.random_charging_posts(5, seed=1)
    >>> result
       latitude  longitude          socket charger  capacity  occupancy
    0     51.48       0.24             CCS    SLOW         1          0
    1     51.68       0.95         CHADEMO    FAST         1          0
    2     51.31       0.22             CCS   RAPID         1          0
    3     51.68       0.46  DC_COMBO_TYPE2    SLOW         1          0
    4     51.39      -0.45         CHADEMO    SLOW         1          0

The random ``seed`` is optional. It is provided here so that the code and output above
can be tested reproducibly. By default, the function returns a
:py:class:`pandas.DataFrame`. The ``socket`` and ``charger`` columns take their values
from :py:class:`evosim.charging_posts.Sockets` and :py:class:`evosim.charging_posts.Chargers`:

.. doctest:: charging_posts

    >>> result.socket
    0               CCS
    1           CHADEMO
    2               CCS
    3    DC_COMBO_TYPE2
    4           CHADEMO
    Name: socket, dtype: object

    >>> result.socket[0]
    <Sockets.CCS: 32>

    >>> result.charger
    0     SLOW
    1     FAST
    2    RAPID
    3     SLOW
    4     SLOW
    Name: charger, dtype: object

    >>> result.charger[0]
    <Chargers.SLOW: 1>

The range of latitude and longitude, the number of socket and charger types and their
distributions can all be changed in the input. For instance, the following limits the
sockets to two type and heavily favors one rather than the other:

.. doctest:: charging_posts

    >>> from evosim.charging_posts import Sockets
    >>> evosim.charging_posts.random_charging_posts(
    ...     n=10,
    ...     socket_types=list(Sockets)[:2],
    ...     socket_distribution=[0.2, 0.8],
    ...     capacity=(1, 5),
    ...     seed=1,
    ... )
       latitude  longitude socket charger  capacity  occupancy
    0     51.48       0.82  TYPE2    FAST         4          0
    1     51.68       0.44  TYPE2    FAST         4          0
    2     51.31       0.08  TYPE2    SLOW         2          0
    3     51.68       0.88  TYPE2    SLOW         1          0
    4     51.39       0.03  TYPE2    FAST         3          0
    5     51.44       0.29  TYPE2    FAST         3          0
    6     51.62      -0.27  TYPE2    FAST         4          0
    7     51.43       0.21  TYPE2   RAPID         2          0
    8     51.50      -0.14  TYPE1    FAST         2          0
    9     51.26      -0.04  TYPE2    FAST         1          0

Both chargers and sockets can accept multiple types simultaneously, and they can be
queried accordingly:

.. doctest:: charging_posts
    
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
