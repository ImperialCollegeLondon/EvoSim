from enum import Enum, auto
from pathlib import Path
from typing import Optional, Sequence, Tuple, Union

import dask.dataframe as dd
import numpy as np
import pandas as pd

from evosim import constants

__doc__ = Path(__file__).with_suffix(".rst").read_text()


ChargingPoints = Union[dd.DataFrame, pd.DataFrame]
""" A data structure representing a charging point. """


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
    latitude: Tuple[float, float] = constants.LONDON_LATITUDE,
    longitude: Tuple[float, float] = constants.LONDON_LONGITUDE,
    socket_types: Sequence[Sockets] = tuple(Sockets),
    socket_distribution: Optional[Sequence[float]] = None,
    charger_types: Sequence[Chargers] = tuple(Chargers),
    charger_distribution: Optional[Sequence[float]] = None,
    capacity: Optional[Union[Tuple[int, int], int]] = 1,
    occupancy: Optional[Union[Tuple[int, int], int]] = 0,
    seed: Optional[Union[int, np.random.Generator]] = None,
    **kwargs,
) -> ChargingPoints:
    """Creates a randomly generated list of charging points.

    Args:
        n: The number of charging points
        latitude: The range over which to create random current locations and
            destinations. Defaults to the :py:data:`London latitudinal range
            <evosim.constants.LONDON_LATITUDE>`.
        longitude: The range over which to create random current locations and
            destinations. Defaults to the :py:data:`London longitudinal range
            <evosim.constants.LONDON_LONGITUDE>`.
        socket_types: A list of :py:class:`~evosim.supply.Sockets` from which to
            choose randomly. Defaults to all available socket types.
        socket_distribution: weights when choosing the socket types.
        charger_types: A list of :py:class:`~evosim.supply.Chargers` from which to
            choose randomly. Defaults to all available charger types.
        charger_distribution: weights when choosing the charger types.
        capacity: A range from which to choose the maximum capacity for each charging
            point. The range can be given as ``(start, end)``, or as a single number, in
            which case it defaults to ``1, capacity + 1``. Defaults to a capacity of 1
            for each charging point.

            .. note::

                The range given as ``(min, max)`` will allow capacities between ``min``
                included and ``max`` excluded, as per python conventions.

        occupancy: A range from which to choose the current occupancy for each charging
            point. The range can be given as ``(start, end)``, or as a single number, in
            which case it defaults to ``0, occupancy + 1``. Defaults to an occupancy of
            0.  The occupancy is always smaller than the capacity.

            .. warning::

                Owing to the simplicity of the implementation, the distribution of
                occupancies is not quite uniform and may skew towards lower values.

            .. note::

                The range given as ``(min, max)`` will allow capacities between ``min``
                included and ``max`` excluded, as per python conventions.

        seed (Optional[Union[int, numpy.random.Generator]]): seed for the random number
            generators. Defaults to ``None``. See :py:func:`numpy.random.default_rng`.
            Alternatively, it can be a :py:class:`numpy.random.Generator` instance.
        **kwargs: If keywords are given, then they should be those of
            :py:func:`dask.dataframe.from_pandas`

    Returns:
        Union[dask.dataframe.DataFrame, pandas.DataFrame]: If no keyword arguments are
        given, then the funtion returns a :py:class:`pandas.DataFrame`. Otherwise, it
        returns a :py:class:`dask.dataframe.DataFrame`.
    """
    if isinstance(capacity, int):
        capacity = (1, capacity + 1)
    if isinstance(occupancy, int):
        occupancy = (0, occupancy + 1)
    capacity = min(*capacity), max(*capacity)
    if capacity[0] < 1:
        raise ValueError("The minimum capacity must be at least 1.")
    if capacity[1] < 2:
        raise ValueError("The maximum capacity must be at least 2 (excluded).")
    occupancy = min(*occupancy), max(*occupancy)
    if occupancy[0] < 0:
        raise ValueError("The minimum occupancy must be at least 0.")
    if occupancy[1] < 1:
        raise ValueError("The maximum occupancy must be at least 1 (excluded).")
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
    if capacity[0] == capacity[1] + 1 or capacity[0] == capacity[1]:
        capacities = np.ones(n, dtype=int)
    else:
        capacities = rng.integers(low=capacity[0], high=capacity[1], size=n)
    if occupancy[0] == occupancy[1] + 1 or occupancy[0] == occupancy[1]:
        occupancies = np.ones(n, dtype=int)
    else:
        # TODO: random occupancies are not uniform
        # The mod operation will skew the distribution towards lower values. For
        # instance, if the capacity of a particular charging point is 4, but the maximum
        # cpacity as a whole is 5, the occupancies are chosen as one of
        # `[0 % 4, 1 % 4, 2 % 4, 3 % 4, 5 % 4]`, e.g. `[0, 1, 2, 3, 0]`, and `0` is
        # twice as likely as any other value.
        # When fixing, don't forget the **docstring**!
        # labels: bug
        occupancies = (
            rng.integers(low=occupancy[0], high=occupancy[1], size=n) % capacities
        )

    result: ChargingPoints = pd.DataFrame(
        dict(
            latitude=lat,
            longitude=lon,
            socket=socket,
            charger=charger,
            capacity=capacities,
            occupancy=occupancies,
        )
    )
    result["socket"] = result.socket.astype("category")
    result["charger"] = result.charger.astype("category")

    is_dask = kwargs and any(v is not None for v in kwargs.values())
    return dd.from_pandas(result, **kwargs) if is_dask else result
