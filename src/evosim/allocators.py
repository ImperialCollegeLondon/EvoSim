from typing import Any, Callable, Optional, Union

import numpy as np

from evosim.electric_vehicles import ElectricVehicles
from evosim.supply import ChargingPoints


def random_allocator(
    electric_vehicles: ElectricVehicles,
    charging_points: ChargingPoints,
    matcher: Callable[[Any, Any], Any],
    maxiter: Optional[int] = None,
    seed: Optional[Union[int, np.random.Generator]] = None,
) -> ChargingPoints:
    """Randomly assigns EVs to charging points.

    Args:
        electric_vehicles: dataframe of electric vehicles
        charging_points: dataframe of charging_points
        matcher: a callable that takes an electric_vehicle and an charging_point and
            returns true when the two are compatible.
        maxiter: maximum number of iterations before giving up. If negative, zero, or
            None, then defaults to the number of electric vehicles.
        seed (Optional[Union[int, numpy.random.Generator]]): seed for the random number
            generators. Defaults to ``None``. See :py:func:`numpy.random.default_rng`.
            Alternatively, it can be a :py:class:`numpy.random.Generator` instance.

    Returns:
        Union[dask.dataframe.DataFrame, pandas.DataFrame]: A shallow copy of the
        ``electric_vehicles`` dataframe with an extra column, "allocation", giving the
        index into the ``charging_point`` dataframe.

    Example:

        >>> electric_vehicles = evosim.electric_vehicles.random_electric_vehicles(
        ...     20, seed=1
        ... )
        >>> charging_points = evosim.supply.random_charging_points(
        ...     15, seed=2, capacity=4, occupancy = 5
        ... )
        >>> matcher = evosim.matchers.socket_compatibility
        >>> maxiter = 0
        >>> seed = 10
    """
    vacancy_by_number = charging_points.capacity - charging_points.occupancy
    if vacancy_by_number.sum() < len(electric_vehicles):
        # TODO: random allocator cannot deal with len(eVS) > len(vacancies)
        # labels: enhancement
        # The algorithm currently expects that the list of vacancies should be larger
        # that the list of electric vehicles.
        raise NotImplementedError("Cannot deal with overbooking yet")
    if isinstance(seed, np.random.Generator):
        rng = seed
    else:
        rng = np.random.default_rng(seed=seed)
    if maxiter is None or maxiter <= 0:
        maxiter = len(electric_vehicles)

    vacancies = [i for i, n in enumerate(vacancy_by_number) for _ in range(n)]
    rng.shuffle(vacancies)

    assignement = -np.ones(len(electric_vehicles), dtype=int)
    nevs = len(electric_vehicles)
    for _ in range(maxiter):
        is_match = matcher(
            electric_vehicles, charging_points.loc[vacancies[:nevs]].reset_index()
        )
        assignement = np.where(
            np.logical_and(assignement < 0, is_match), vacancies[:nevs], assignement
        )
        if (assignement >= 0).all():
            break
        vacancies = vacancies[1:] + vacancies[:1]
    result = electric_vehicles.copy(deep=False)
    result["allocation"] = assignement
    return result
