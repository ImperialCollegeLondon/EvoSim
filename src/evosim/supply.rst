.. _charging-points:

Charging Points
===============

.. testsetup:: charging_points
    
    import pandas as pd
    import numpy as np
    import dask.dataframe as dd
    import evosim

    pd.options.display.precision = 2
    pd.options.display.max_categories = 8
    pd.options.display.max_rows = 20
    pd.options.display.max_columns = 10
    pd.options.display.width = 88

Charging points are represented by a table with columns for the latitude, longitude,
socket type, charger type, current occupancy and maximum capacity. Potentially it can
accept other columns as well. The simplest way to generate one is to use
:py:func:`evosim.supply.random_charging_points`:

.. doctest:: charging_points

    >>> result = evosim.supply.random_charging_points(5, seed=1)
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
from :py:class:`evosim.supply.Sockets` and :py:class:`evosim.supply.Chargers`:

.. doctest:: charging_points

    >>> result.socket
    0               CCS
    1           CHADEMO
    2               CCS
    3    DC_COMBO_TYPE2
    4           CHADEMO
    Name: socket, dtype: category
    Categories (3, object): [CCS, CHADEMO, DC_COMBO_TYPE2]

    >>> result.socket[0]
    <Sockets.CCS: 6>

    >>> result.charger
    0     SLOW
    1     FAST
    2    RAPID
    3     SLOW
    4     SLOW
    Name: charger, dtype: category
    Categories (3, object): [SLOW, FAST, RAPID]

    >>> result.charger[0]
    <Chargers.SLOW: (0, 7)>

Note the range ``(0, 7)``. It indicates the power range of the
:py:attr:`~evosim.supply.Chargers.SLOW` charger.

The range of latitude and longitude, the number of socket and charger types and their
distributions can all be changed in the input. For instance, the following limits the
sockets to two type and heavily favors one rather than the other:

.. doctest:: charging_points

    >>> from evosim.supply import Sockets
    >>> evosim.supply.random_charging_points(
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


.. topic:: Creating a charging point of type :py:class:`dask.dataframe.DataFrame`

    Optionally, :py:func:`~evosim.supply.random_charging_points` can generate a
    :py:class:`dask.dataframe.DataFrame` simply by supplying it with the requisite
    arguments from :py:func:`dask.dataframe.from_pandas`.
