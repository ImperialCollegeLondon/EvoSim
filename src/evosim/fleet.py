from enum import Enum, auto
from pathlib import Path
from typing import Callable, Mapping, Optional, Sequence, Text, Tuple, Union

import numpy as np
import pandas as pd

from evosim import constants
from evosim.autoconf import AutoConf
from evosim.charging_posts import Chargers, Sockets, to_chargers, to_sockets

__doc__ = Path(__file__).with_suffix(".rst").read_text()

register_fleet_generator = AutoConf("fleet generation")
"""Registry for functions to read or generate fleets. """


class Models(Enum):
    """All known car models."""

    AUDI_A3_E_TRON = auto()
    BMW_I3 = auto()
    BMW_225XE = auto()
    BMW_330E = auto()
    BMW_530E = auto()
    BMW_X5_40E = auto()
    CITROEN_C_ZERO = auto()
    JAGUAR_I_PACE = auto()
    KIA_NIRO_PHEV = auto()
    HYUNDAI_IONIQ_ELECTRIC = auto()
    HYUNDAI_IONIQ_PLUGIN = auto()
    MERCEDES_BENZ_C350E = auto()
    MERCEDES_BENZ_E350E = auto()
    MINI_COUNTRYMAN_COOPER_SE = auto()
    MITSUBISHI_OUTLANDER_PHEV = auto()
    NISSAN_E_NV200 = auto()
    NISSAN_LEAF = auto()
    PORSCHE_PANAMERA_EHYBRID = auto()
    RENAULT_ZOE = auto()
    SMART_EQ_FORFOUR = auto()
    SMART_EQ_FORTWO = auto()
    TESLA_MODEL_X = auto()
    TESLA_MODEL_S = auto()
    TOYOTA_PRIUS_PLUGIN = auto()
    VOLKSWAGEN_GOLF_GTE = auto()
    VOLKSWAGEN_PASSAT_GTE = auto()
    VOLVO_XC60_TWIN_ENGINE = auto()
    VOLVO_XC90_TWIN_ENGINE = auto()
    VOLVO_V90_TWIN_ENGINE = auto()
    UNKNOWN = auto()

    def __str__(self):
        return self.name


@register_fleet_generator(
    name="random",
    is_factory=True,
    docs="""Generates a random fleet of electric vehicles.

    Args:
        n (int): The number of charging posts
        latitude (Tuple[float, float]): The range over which to create random current
            locations and destinations. Defaults to the :py:data:`London latitudinal
            range <evosim.constants.LONDON_LATITUDE>`.
        longitude (Tuple[float, float]): The range over which to create random current
            locations and destinations. Defaults to the :py:data:`London longitudinal
            range <evosim.constants.LONDON_LONGITUDE>`.
        socket_types (List[Text]): A list of sockets from which to choose randomly.
            Defaults to :py:class:`all available socket types
            <evosim.charging_posts.Sockets>`.
        socket_distribution (Optional[List[float]]): weights when choosing the socket
            types.
        socket_multiplicity (int): number of different types of socket each post can
            accomodate.
        charger_types (List[Text]): A list of chargers from which to choose randomly.
            Defaults to :py:class:`all available charger types
            <evosim.charging_posts.Chargers>` .
        charger_distribution (Optional[List[float]]): weights when choosing the charger
            types.
        charger_multiplicity (int): number of different types of chargers each post can
            accomodate.
        model_types (List[Text]): A list of models from which to choose randomly.
            Defaults to :py:class:`all known models <evosim.fleet.Models>`.
        seed (Optional[int]): optional seed for the random number generators.
    """,
)
def random_fleet(
    n: int,
    latitude: Tuple[float, float] = constants.LONDON_LATITUDE,
    longitude: Tuple[float, float] = constants.LONDON_LONGITUDE,
    socket_types: Sequence[Sockets] = tuple(Sockets),
    socket_distribution: Optional[Sequence[float]] = None,
    socket_multiplicity: int = 1,
    charger_types: Sequence[Chargers] = tuple(Chargers),
    charger_distribution: Optional[Sequence[float]] = None,
    charger_multiplicity: int = 1,
    model_types: Sequence[Models] = tuple(Models),
    seed: Optional[Union[int, np.random.Generator]] = None,
) -> pd.DataFrame:
    """Generates a random table representing a fleet of electric vehicles.

    Args:
        n: The number of charging posts
        latitude: The range over which to create random current locations and
            destinations. Defaults to the :py:data:`London latitudinal range
            <evosim.constants.LONDON_LATITUDE>`.
        longitude: The range over which to create random current locations and
            destinations. Defaults to the :py:data:`London longitudinal range
            <evosim.constants.LONDON_LONGITUDE>`.
        socket_types: A list of :py:class:`~evosim.charging_posts.Sockets` from which to
            choose randomly. Defaults to all available socket types.
        socket_distribution: weights when choosing the socket types.
        socket_multiplicity: number of different types of socket each post can
            accomodate.
        charger_types: A list of :py:class:`~evosim.charging_posts.Chargers` from which
            to choose randomly. Defaults to all available charger types.
        charger_distribution: weights when choosing the charger types.
        charger_multiplicity: number of different types of chargers each post can
            accomodate.
        model_types: A list of :py:class:`~evosim.fleet.Models` from which
            to choose randomly. Defaults to all known models.
        seed (Optional[Union[int, numpy.random.Generator]]): seed for the random number
            generators. Defaults to ``None``. See :py:func:`numpy.random.default_rng`.
            Alternatively, it can be a :py:class:`numpy.random.Generator` instance.

    Returns:
        pandas.DataFrame: A dataframe representing the fleet of electric vehicles.
    """
    from evosim.charging_posts import random_charging_posts

    if isinstance(seed, np.random.Generator):
        rng = seed
    else:
        rng = np.random.default_rng(seed=seed)
    result = random_charging_posts(
        n,
        latitude,
        longitude,
        socket_types,
        socket_distribution,
        socket_multiplicity,
        charger_types,
        charger_distribution,
        charger_multiplicity,
        seed=rng,
    ).drop(columns=["occupancy", "capacity"])

    result["dest_lat"] = rng.uniform(
        high=np.max(latitude), low=np.min(latitude), size=n
    )
    result["dest_long"] = rng.uniform(
        high=np.max(longitude), low=np.min(longitude), size=n
    )
    result["model"] = rng.choice(list(model_types), size=n, replace=True)
    result["model"] = result.model.astype("category")
    result.index.name = "vehicle"

    return to_fleet(result)


def to_models(data: Union[Sequence[Text], Text, Models]) -> Sequence[Models]:
    """Transforms text strings to sockets.

    Example:

        String to models:

        >>> from evosim.fleet import to_models
        >>> to_models("BMW_i3")
        <Models.BMW_I3: 2>

        Lists of strings to lists models:

        >>> to_models(["BMW_i3", "tesla_model_s"])
        [<Models.BMW_I3: 2>, <Models.TESLA_MODEL_S: 23>]

        Numpy arrays of strings to numpy arrays of models:

        >>> to_models(np.array(["BMW_i3", "TESLA_MODEL_S"]))
        array([<Models.BMW_I3: 2>, <Models.TESLA_MODEL_S: 23>], dtype=object)

        Pandas series to pandas series:

        >>> to_models(pd.Series(["bmw_i3", "tesla_model_s"], index=['a', 'b']))
        a           BMW_I3
        b    TESLA_MODEL_S
        dtype: object

        Or models to models...

        >>> to_models(evosim.fleet.Models.BMW_I3)
        <Models.BMW_I3: 2>
    """
    from evosim.charging_posts import _to_enum

    return _to_enum(data, Models, "model")


FLEET_SCHEMA: Mapping[
    Text, Union[np.dtype, Callable[[Sequence], Sequence], Sequence[np.dtype]]
] = dict(
    latitude=(np.dtype(float), np.float16, np.float32, np.float64),
    longitude=(np.dtype(float), np.float16, np.float32, np.float64),
    dest_lat=(np.dtype(float), np.float16, np.float32, np.float64),
    dest_long=(np.dtype(float), np.float16, np.float32, np.float64),
    socket=to_sockets,
    charger=to_chargers,
    model=to_models,
)
"""Schema defining a fleet of electric vehicles

Maps the column to the dtype, a sequence of dtypes, or to an idem-potent callable that
can be used to transform the column. If  a sequence of dtypes is given, then the first
one is the default.All the columns named here are **required**. A charging posts table
can any number of extra columns.
"""


def is_fleet(dataframe: pd.DataFrame, raise_exception: bool = False) -> bool:
    """True if dataframe follows the fleet schema.

    Args:
        dataframe (pandas.DataFrame): putative fleet of electric vehicles
        raise_exception: if ``False`` returns a boolean. If ``True``, will raise an
            exception with some information identifying the difference with
            :py:data:`FLEET_SCHEMA`.

    Usage:

        >>> from pytest import raises
        >>> from evosim.fleet import random_fleet, is_fleet
        >>> fleet = random_fleet(5)
        >>> is_fleet(fleet)
        True

        >>> is_fleet(fleet.drop(columns="latitude"))
        False

        >>> wrong_dtype = fleet.copy(deep=False)
        >>> wrong_dtype["latitude"] = wrong_dtype.latitude.astype(str)
        >>> is_fleet(wrong_dtype)
        False

        >>> wrong_dtype = fleet.copy(deep=False)
        >>> wrong_dtype["socket"] = [str(u).lower() for u in wrong_dtype.socket]
        >>> is_fleet(wrong_dtype)
        False

        >>> wrong_index_name = fleet.copy(deep=False)
        >>> wrong_index_name.index.name = "notvehicle"
        >>> is_fleet(wrong_index_name)
        False
        >>> wrong_index_name.index.name = "VEHICLE"
        >>> is_fleet(wrong_index_name)
        False

        >>> with raises(ValueError):
        ...     is_fleet(fleet.drop(columns="latitude"), raise_exception=True)
    """
    from evosim.charging_posts import _dataframe_follows_schema
    from evosim.fleet import FLEET_SCHEMA

    return _dataframe_follows_schema(
        dataframe,
        raise_exception=raise_exception,
        schema=FLEET_SCHEMA,
        index_name="vehicle",
    )


def to_fleet(data: pd.DataFrame) -> pd.DataFrame:
    """Tries and transform input data to a fleet dataframe.

    This function will try and transform the columns of the input dataframe to fit the
    schema defined in :py:data:`evosim.fleet.FLEET_SCHEMA`. It also sets the "vehicle"
    column as the index, if it exists. In any-case, it names the indices "vehicle". It
    returns a shallow copy of the input data frame with transformed columns as required.

    Args:
        data (pandas.DataFrame): dataframe to transform following the schema.

    Returns:
        pandas.DataFrame: A dataframe conforming to the fleet schema.

    Example:

        >>> from evosim.fleet import random_fleet, to_fleet, is_fleet
        >>> from evosim.charging_posts import Sockets, Chargers
        >>> dataframe = random_fleet(5)
        >>> dataframe["socket"] = [str(u).lower() for u in dataframe.socket]
        >>> dataframe["charger"] = [str(u).lower() for u in dataframe.charger]
        >>> is_fleet(dataframe)
        False
        >>> fleet = to_fleet(dataframe)
        >>> is_fleet(fleet)
        True
        >>> isinstance(fleet.at[0, "socket"], Sockets)
        True
        >>> isinstance(fleet.at[0, "charger"], Chargers)
        True
    """
    from evosim.charging_posts import _transform_to_schema
    from evosim.fleet import FLEET_SCHEMA

    return _transform_to_schema(FLEET_SCHEMA, data, index_name="vehicle")


@register_fleet_generator(
    name="from_file",
    is_factory=True,
    docs="""Reads a fleet from a variety of files.
    Args:
        path (Text): path to a file, either excel, csv, json, feather, or hdf5.
        kwargs: Additional arguments are passed on to the underlying :py:mod:pandas`
            function, e.g. :py:func:`pandas.read_csv`.
    """,
)
def fleet_from_file(path: Union[Text, Path], **kwargs):
    """Reads a fleet from file, guessing the format from the filename.

    Defaults to the csv file format.
    """
    from evosim.charging_posts import _from_file

    return _from_file(path, to_fleet, **kwargs)
