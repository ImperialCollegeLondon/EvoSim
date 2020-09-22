from enum import Enum, auto
from pathlib import Path
from typing import Optional, Sequence, Tuple, Union

import dask.dataframe as dd
import numpy as np
import pandas as pd

from evosim.supply import LONDON_LATITUDE, LONDON_LONGITUDE, Chargers, Sockets

__doc__ = Path(__file__).with_suffix(".rst").read_text()

ElectricVehicles = Union[dd.DataFrame, pd.DataFrame]
""" A data structure representing a charging point. """


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


def random_electric_vehicles(
    n: int,
    latitude: Tuple[float, float] = LONDON_LATITUDE,
    longitude: Tuple[float, float] = LONDON_LONGITUDE,
    socket_types: Sequence[Sockets] = tuple(Sockets),
    socket_distribution: Optional[Sequence[float]] = None,
    charger_types: Sequence[Chargers] = tuple(Chargers),
    charger_distribution: Optional[Sequence[float]] = None,
    model_types: Sequence[Models] = tuple(Models),
    seed: Optional[Union[int, np.random.Generator]] = None,
    **kwargs,
) -> ElectricVehicles:
    """Creates a randomly generated list of charging points.

    Args:
        n: The number of charging points
        latitude: The range over which to create random current locations and
            destinations. Defaults to the london, {LONDON_LATITUDE}.
        longitude: The range over which to create random current locations and
            destinations. Defaults to the london, {LONDON_LATITUDE}.
        socket_types: A list of :py:class:`~evosim.supply.Sockets` from which to
            choose randomly. Defaults to all available socket types.
        socket_distribution: weights when choosing the socket types.
        charger_types: A list of :py:class:`~evosim.supply.Chargers` from which to
            choose randomly. Defaults to all available charger types.
        charger_distribution: weights when choosing the charger types.
        model_types: A list of :py:class:`~evosim.electric_vehicles.Models` from which
            to choose randomly. Defaults to all known models.
        seed: seed for the random number generators. Defaults to ``None``. See
            :py:func:`numpy.random.default_rng`. Alternatively, it can be a
            :py:class:`numpy.random.Generator` instance.
        **kwargs: If keywords are given, then they should be those of
            :py:func:`dask.dataframe.from_pandas`

    Returns:
        Union[dask.dataframe.DataFrame, pandas.DataFrame]: If no keyword arguments are
        givent, then the funtion returns a :py:class:`pandas.DataFrame`. Otherwise, it
        returns a :py:class:`dask.dataframe.DataFrame`.
    """
    from evosim.supply import random_charging_points

    if isinstance(seed, np.random.Generator):
        rng = seed
    else:
        rng = np.random.default_rng(seed=seed)
    result: ElectricVehicles = random_charging_points(
        n,
        latitude,
        longitude,
        socket_types,
        socket_distribution,
        charger_types,
        charger_distribution,
        seed=rng,
    )

    result["dest_lat"] = rng.uniform(
        high=np.max(latitude), low=np.min(latitude), size=n
    )
    result["dest_long"] = rng.uniform(
        high=np.max(longitude), low=np.min(longitude), size=n
    )
    result["model"] = rng.choice(list(model_types), size=n, replace=True)
    result["model"] = result.model.astype("category")

    is_dask = kwargs and any(v is not None for v in kwargs.values())
    return dd.from_pandas(result, **kwargs) if is_dask else result
