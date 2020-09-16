Charging Points
===============

.. testsetup:: *
    
    import pandas as pd
    import numpy as np
    import dask.dataframe as dd
    import evosim

    pd.set_option('precision', 2)
    

Charging points are a list of locations (latitude and longitude) with a socket and
charger type. The simplest way to generate one is to use
:py:func:`evosim.supply.random_charging_points`:

.. doctest::

    >>> result = evosim.supply.random_charging_points(5, seed=1)
    >>> result
       latitude  longitude          socket charger
    0     51.48       0.24             CCS    SLOW
    1     51.68       0.95         CHADEMO    FAST
    2     51.31       0.22             CCS   RAPID
    3     51.68       0.46  DC_COMBO_TYPE2    SLOW
    4     51.39      -0.45         CHADEMO    SLOW

The random ``seed`` is optional. It is provided here so that the code and output above
can be tested reproducibly. By default, the function returns a `pandas.DataFrame`. The
``socket`` and ``charger`` columns take their values from
:py:class:`evosim.supply.Sockets` and :py:class:`evosim.supply.Chargers`:

.. doctest::

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
:py:attr:`~evosim.supply.ChargerType.SLOW` charger.


.. topic:: Creating a charging point of type :py:mod:`dask.dataframe.DataFrame`

    Optionally, :py:func:`evosim.supply.randomly_chargingpoint` can generate
    a :py:mod:`dask` dataframe, simply by supplying it with the requisite arguments from
    :py:func:`dask.dataframe.fom_pandas`.
