from pathlib import Path
from typing import Any, Callable, Optional, Union

import numpy as np
import pandas as pd

from evosim.electric_vehicles import ElectricVehicles
from evosim.supply import ChargingPoints

__doc__ = Path(__file__).with_suffix(".rst").read_text()


def random_allocator(
    electric_vehicles: ElectricVehicles,
    charging_points: ChargingPoints,
    matcher: Callable[[Any, Any], Any],
    maxiter: Optional[int] = None,
    seed: Optional[Union[int, np.random.Generator]] = None,
) -> ChargingPoints:
    """Randomly assigns EVs to charging points.

    Args:
        electric_vehicles (Union[dask.dataframe.DataFrame, pandas.DataFrame]): dataframe
            of electric vehicles
        charging_points (Union[dask.dataframe.DataFrame, pandas.DataFrame]): dataframe
            of charging_points
        matcher (Union[dask.dataframe.DataFrame, pandas.DataFrame]): a callable that
            takes an electric_vehicle and an charging_point and returns true when the
            two are compatible.
        maxiter: maximum number of iterations before giving up. If negative, zero, or
            None, then defaults to the number of charging point vacancies.
        seed (Optional[Union[int, numpy.random.Generator]]): seed for the random number
            generators. Defaults to ``None``. See :py:func:`numpy.random.default_rng`.
            Alternatively, it can be a :py:class:`numpy.random.Generator` instance.

    Returns:
        Union[dask.dataframe.DataFrame, pandas.DataFrame]: A shallow copy of the
        ``electric_vehicles`` dataframe with an extra column, "allocation", giving the
        index into the ``charging_point`` dataframe.
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

    vacancies = np.array([i for i, n in enumerate(vacancy_by_number) for _ in range(n)])

    if maxiter is None or maxiter <= 0:
        # TODO: tighten random allocator's default maxiter
        # labels: enhancement
        # The default maximum number of iteration is equal to the number of charging
        # point vacancies. But that could be tightened within the loop itself, whenever
        # vacancies are allocated. Not sure how though.
        maxiter = len(vacancies)

    rng.shuffle(vacancies)

    assignement = -np.ones(len(electric_vehicles), dtype=int)

    unassigned = electric_vehicles.copy(deep=False)
    for _ in range(maxiter):
        is_match = matcher(
            unassigned.reset_index(drop=True),
            charging_points.loc[vacancies[: len(unassigned)]].reset_index(drop=True),
        ).to_numpy()
        assignement[assignement < 0] = np.where(
            is_match, vacancies[: len(unassigned)], -1
        )
        unassigned = unassigned[~is_match]
        vacancies = vacancies[
            np.concatenate(
                (~is_match, np.ones(len(vacancies) - len(is_match), dtype=bool))
            )
        ]
        if len(unassigned) == 0:
            break
        vacancies = np.roll(vacancies, shift=1)
    result = electric_vehicles.copy(deep=False)
    result["allocation"] = pd.Series(
        np.where(assignement < 0, pd.NA, assignement), dtype="Int64"
    )
    return result
