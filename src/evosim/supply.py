from enum import Enum, auto
from pathlib import Path
from typing import Sequence, Tuple, Union

import dask.dataframe as dd
import numpy as np
import pandas as pd

__doc__ = Path(__file__).with_suffix(".rst").read_text()


ChargingPoint = Union[dd.DataFrame, pd.DataFrame]
""" A data structure representing a charging point. """

LONDON_LATITUDE = 51.25, 51.70
LONDON_LONGITUDE = -0.5, 1.25


class SocketTypes(Enum):
    """Charging point socket types."""

    TYPE1 = auto()
    TYPE2 = auto()
    THREE_PIN_SQUARE = auto()
    DC_COMBO_TYPE2 = auto()
    CHADEMO = auto()
    CCS = auto()

    def __str__(self):
        return self.name


class ChargerTypes(Enum):
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
    socket_types: Sequence[SocketTypes] = tuple(SocketTypes),
    charger_types: Sequence[ChargerTypes] = tuple(ChargerTypes),
    seed=None,
    **kwargs,
) -> ChargingPoint:
    """Creates a randomly generated list of charging points.

    Args:
        n: The number of charging points
        latitude: The range over which to create random charging point locations.
            Defaults to the london, {LONDON_LATITUDE}.
        longitude: The range over which to create random charging point locations
            Defaults to the london, {LONDON_LONGITUDE} .
        socket_types: A list of :py:class:`~evosim.supply.SocketTypes` from which to
            choose randomly. Defaults to all available socket types.
        charger_types: A list of :py:class:`~evosim.supply.ChargerTypes` from which to
            choose randomly. Defaults to all available charger types.
        seed: seed for the random number generators. Defaults to ``None``. See
            :py:func:`numpy.random.default_rng`.
        **kwargs: If empty, creates a :py:mod:`pandas` dataframe. If keywords are given,
            then they should be those of :py:mod:`dask.dataframe.from_pandas`.
    """
    rng = np.random.default_rng(seed=seed)
    lat = rng.uniform(high=np.max(latitude), low=np.min(latitude), size=n)
    lon = rng.uniform(high=np.max(longitude), low=np.min(longitude), size=n)
    st = rng.choice(list(socket_types), size=n, replace=True)
    ct = rng.choice(list(charger_types), size=n, replace=True)
    result: ChargingPoint = pd.DataFrame(
        dict(latitude=lat, longitude=lon, socket=st, charger=ct)
    )
    result["socket"] = result.socket.astype("category")
    return dd.from_pandas(result, **kwargs) if kwargs else result


# Ensures sphinx gets the interpolated docstring. Using an f-string does not work.
random_charging_points.__doc__ = random_charging_points.__doc__.format(
    LONDON_LATITUDE=LONDON_LATITUDE, LONDON_LONGITUDE=LONDON_LONGITUDE
)
