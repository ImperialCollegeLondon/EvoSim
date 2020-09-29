Electric Vehicles
=================

.. testsetup:: EVs
    
    import pandas as pd
    import numpy as np
    import dask.dataframe as dd
    import evosim

    pd.options.display.precision = 2
    pd.options.display.max_categories = 8
    pd.options.display.max_rows = 20
    pd.options.display.max_columns = 10
    pd.options.display.width = 88
    

Electric vehicles are defined in a similar fashion to :ref:`charging-points`.
Indeed, electric vehicles contain the same attributes, e.g.  current latitude and
longitude, socket and charger type, as well as extra attributes, such as the car model.
The simplest way to generate a list of EVs is to use
:py:func:`evosim.electric_vehicles.random_electric_vehicles`:

.. doctest:: EVs
    :options: +NORMALIZE_WHITESPACE

    >>> result = evosim.electric_vehicles.random_electric_vehicles(5, seed=1)
    >>> result
       latitude  longitude          socket charger  dest_lat  dest_long  \
    0     51.48       0.24             CCS    SLOW     51.45   8.13e-01
    1     51.68       0.95         CHADEMO    FAST     51.31  -9.28e-03
    2     51.31       0.22             CCS   RAPID     51.43   3.49e-01
    3     51.68       0.46  DC_COMBO_TYPE2    SLOW     51.34   1.22e+00
    4     51.39      -0.45         CHADEMO    SLOW     51.37   1.18e+00
    <BLANKLINE>
                        model
    0               BMW_225XE
    1           TESLA_MODEL_X
    2           KIA_NIRO_PHEV
    3             NISSAN_LEAF
    4  VOLVO_XC90_TWIN_ENGINE

Much as the chargers and sockets, the models are a categorical array taking their values
from :py:class:`evosim.electric_vehicles.Models`:

.. doctest:: EVs

    >>> result.model
    0                 BMW_225XE
    1             TESLA_MODEL_X
    2             KIA_NIRO_PHEV
    3               NISSAN_LEAF
    4    VOLVO_XC90_TWIN_ENGINE
    Name: model, dtype: category
    Categories (5, object): [BMW_225XE, TESLA_MODEL_X, KIA_NIRO_PHEV, NISSAN_LEAF, VOLVO_XC90_TWIN_ENGINE]

Much as for generating random charging points,
:py:func:`evosim.electric_vehicles.random_electric_vehicles` takes additional parameters
to tailor the geographical location, model distribution, etc.
