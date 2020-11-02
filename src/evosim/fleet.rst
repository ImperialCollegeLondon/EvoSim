Electric Vehicles
=================

.. contents::
    :depth: 2

Usage
-----

A fleet of electric vehicles are defined in a similar fashion to :ref:`charging-posts`.
Indeed, the fleet contains the same attributes, e.g. current latitude and longitude,
socket and charger type, as well as extra attributes, such as the car model.  The
simplest way to generate a fleet is to use :py:func:`evosim.fleet.random_fleet`:

.. doctest:: EVs
    :options: +NORMALIZE_WHITESPACE

    >>> result = evosim.fleet.random_fleet(5, seed=1)
    >>> result
             latitude  longitude          socket charger  dest_lat  dest_long  \
    vehicle
    0           51.48       0.24             CCS    SLOW     51.45   8.13e-01
    1           51.68       0.95         CHADEMO    FAST     51.31  -9.28e-03
    2           51.31       0.22             CCS   RAPID     51.43   3.49e-01
    3           51.68       0.46  DC_COMBO_TYPE2    SLOW     51.34   1.22e+00
    4           51.39      -0.45         CHADEMO    SLOW     51.37   1.18e+00
    <BLANKLINE>
                              model
    vehicle
    0                     BMW_225XE
    1                 TESLA_MODEL_X
    2                 KIA_NIRO_PHEV
    3                   NISSAN_LEAF
    4        VOLVO_XC90_TWIN_ENGINE

Much as the chargers and sockets, the models are a categorical array taking their values
from :py:class:`evosim.fleet.Models`:

.. doctest:: EVs

    >>> result.model
    vehicle
    0                 BMW_225XE
    1             TESLA_MODEL_X
    2             KIA_NIRO_PHEV
    3               NISSAN_LEAF
    4    VOLVO_XC90_TWIN_ENGINE
    Name: model, dtype: category
    Categories (5, object): [BMW_225XE, TESLA_MODEL_X, KIA_NIRO_PHEV, NISSAN_LEAF, VOLVO_XC90_TWIN_ENGINE]

Much as for generating random charging posts, :py:func:`evosim.fleet.random_fleet` takes
additional parameters to tailor the geographical location, model distribution, etc. For
instance, we can create electric vehicles accepting multiple types of sockets:

.. doctest:: EVs
    :options: +NORMALIZE_WHITESPACE

    >>> evosim.fleet.random_fleet(5, socket_multiplicity=3, seed=1)
             latitude  longitude                  socket charger  dest_lat  dest_long  \
    vehicle
    0           51.48       0.24                     CCS    SLOW     51.69      -0.22
    1           51.68       0.95  CHADEMO|DC_COMBO_TYPE2   RAPID     51.68       1.20
    2           51.31       0.22        THREE_PIN_SQUARE    SLOW     51.58       0.40
    3           51.68       0.46             TYPE2|TYPE1    SLOW     51.49      -0.30
    4           51.39      -0.45                     CCS    FAST     51.37       0.59
    <BLANKLINE>
                                 model
    vehicle
    0        MITSUBISHI_OUTLANDER_PHEV
    1        MINI_COUNTRYMAN_COOPER_SE
    2              TOYOTA_PRIUS_PLUGIN
    3             HYUNDAI_IONIQ_PLUGIN
    4                      RENAULT_ZOE


Reading and writing fleets
--------------------------

The fleets can be written and read quite easily using :py:mod:`pandas` capabilities in
that domain. For instance, here we write to a (temporary) csv file, read the information
back and check that it is still the same.

.. testcode:: fleet_io

    from io import StringIO
    fleet = evosim.fleet.random_fleet(5, seed=1)

    # write to file ... or to a string buffer
    stream = StringIO()
    fleet.to_csv(stream)

    # read from file ... or from a string buffer
    stream.seek(0)
    reread = evosim.fleet.to_fleet(pd.read_csv(stream))

    assert evosim.fleet.is_fleet(reread)
    assert (fleet.round(4) == reread.round(4)).all().all()

.. note::

    We could just as easily write to a file with ``fleet.to_csv("fleet.csv")`` and then
    read from it with ``evosim.fleet.to_fleet(pd.read_csv("fleet.csv"))``.  Instead, we
    read and write to an object in memory that behaves like a file. This is mainly
    because it is not allowed to write to temporary file on the windows machines where
    the code in this manual is tested.

Writing to a csv file, or to any format supported by :py:mod:`pandas` is
straightforward. Reading from a file is also fairly straightforward, but it requires one
extra step: the dataframe read from file is transformed to a charging post via
:py:func:`evosim.fleet.to_fleet`. This ensures that the required columns are there and
have the correct types. In the penultimate line, we verify with
:py:func:`evosim.fleet.is_fleet` that the transformed dataframe is indeed a fleet.

.. topic:: Floating point comparisons

    In the snippet above, we compare the two tables with a finite number of decimal
    points. This is only to ensure the comparison is not influenced by how floating
    points are represented in the csv file written out by pandas. See the option
    `float_format` in :py:meth:`pandas.DataFrame.to_csv` for more details.
