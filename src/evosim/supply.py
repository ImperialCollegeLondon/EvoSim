from enum import Enum, auto
from pathlib import Path
from typing import Optional, Sequence, Tuple, Union

import dask.dataframe as dd
import numpy as np
import pandas as pd

__doc__ = Path(__file__).with_suffix(".rst").read_text()


ChargingPoint = Union[dd.DataFrame, pd.DataFrame]
""" A data structure representing a charging point. """

LONDON_LATITUDE = 51.25, 51.70
LONDON_LONGITUDE = -0.5, 1.25


class Sockets(Enum):
    """Charging point socket types."""

    TYPE1 = auto()
    TYPE2 = auto()
    THREE_PIN_SQUARE = auto()
    DC_COMBO_TYPE2 = auto()
    CHADEMO = auto()
    CCS = auto()

    def __str__(self):
        return self.name


class Chargers(Enum):
    """Charging point charging types.

    The values are the power range in kW.
    """

    SLOW: Tuple[float, float] = (0, 7)
    FAST: Tuple[float, float] = (7, 22)
    RAPID: Tuple[float, float] = (43, 150)

    def __str__(self):
        return self.name


def random_charging_points(
    n: int,
    latitude: Tuple[float, float] = LONDON_LATITUDE,
    longitude: Tuple[float, float] = LONDON_LONGITUDE,
    socket_types: Sequence[Sockets] = tuple(Sockets),
    socket_distribution: Optional[Sequence[float]] = None,
    charger_types: Sequence[Chargers] = tuple(Chargers),
    charger_distribution: Optional[Sequence[float]] = None,
    seed: Optional[Union[int, np.random.Generator]] = None,
    **kwargs,
) -> ChargingPoint:
    """Creates a randomly generated list of charging points.

    Args:
        n: The number of charging points
        latitude: The range over which to create random charging point locations.
            Defaults to the london, {LONDON_LATITUDE}.
        longitude: The range over which to create random charging point locations
            Defaults to the london, {LONDON_LONGITUDE} .
        socket_types: A list of :py:class:`~evosim.supply.Sockets` from which to
            choose randomly. Defaults to all available socket types.
        socket_distribution: weights when choosing the socket types.
        charger_types: A list of :py:class:`~evosim.supply.Chargers` from which to
            choose randomly. Defaults to all available charger types.
        charger_distribution: weights when choosing the charger types.
        seed: seed for the random number generators. Defaults to ``None``. See
            :py:func:`numpy.random.default_rng`. Alternatively, it can be a
            :py:class:`numpy.random.Generator` instance.
        **kwargs: If keywords are given, then they should be those of
            :py:func:`dask.dataframe.from_pandas`

    Returns:
        Union[dask.dataframe.DataFrame, pandas.DataFrame]: If no keyword arguments are
        given, then the funtion returns a :py:class:`pandas.DataFrame`. Otherwise, it
        returns a :py:class:`dask.dataframe.DataFrame`.
    """
    if isinstance(seed, np.random.Generator):
        rng = seed
    else:
        rng = np.random.default_rng(seed=seed)

    lat = rng.uniform(high=np.max(latitude), low=np.min(latitude), size=n)
    lon = rng.uniform(high=np.max(longitude), low=np.min(longitude), size=n)
    socket = rng.choice(list(socket_types), size=n, replace=True, p=socket_distribution)
    charger = rng.choice(
        list(charger_types), size=n, replace=True, p=charger_distribution
    )
    result: ChargingPoint = pd.DataFrame(
        dict(latitude=lat, longitude=lon, socket=socket, charger=charger)
    )
    result["socket"] = result.socket.astype("category")
    result["charger"] = result.charger.astype("category")
    return dd.from_pandas(result, **kwargs) if kwargs else result


# Ensures sphinx gets the interpolated docstring. Using an f-string does not work.
random_charging_points.__doc__ = random_charging_points.__doc__.format(
    LONDON_LATITUDE=LONDON_LATITUDE, LONDON_LONGITUDE=LONDON_LONGITUDE
)
