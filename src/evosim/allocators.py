from pathlib import Path
from typing import Callable, Optional, Union

import numpy as np
import pandas as pd

from evosim.matchers import Matcher

__doc__ = Path(__file__).with_suffix(".rst").read_text()


def random_allocator(
    fleet: pd.DataFrame,
    charging_posts: pd.DataFrame,
    matcher: Matcher,
    maxiter: Optional[int] = None,
    seed: Optional[Union[int, np.random.Generator]] = None,
) -> pd.DataFrame:
    """Randomly assigns EVs to charging posts.

    The implementation tries to make use of numpy's `vectorization
    <https://en.wikipedia.org/wiki/Array_programming>`__ and avoid explicit loops.
    Hence, it runs the matcher elementwise on all unallocated vehicles and charging
    posts at the same time. It proceeds as follows

    #. create a list of available infrastructure and shuffle it. Charging posts with
       more than one availabe spot are duplicated.
    #. run the matcher on the fleet vs the infrastructure list above
    #. remove matched vehicles and posts from the fleet and infrastructure
    #. cycle the infastructure list (remove the first item and put it at the back)
       so that each vehicle can be matched to a different post
    #. rinse and repeat from step 2

    Args:
        fleet (pandas.DataFrame): dataframe of electric vehicles
        charging_posts (pandas.DataFrame): dataframe of charging_posts
        matcher: a callable that takes an electric_vehicle and an charging_post and
            returns true when the two are compatible.
        maxiter: maximum number of iterations before giving up. If negative, zero, or
            None, then defaults to the number of charging post vacancies.
        seed (Optional[Union[int, numpy.random.Generator]]): seed for the random number
            generators. Defaults to ``None``. See :py:func:`numpy.random.default_rng`.
            Alternatively, it can be a :py:class:`numpy.random.Generator` instance.

    Returns:
        pandas.DataFrame: A shallow copy of the ``fleet`` dataframe with an extra
        column, "allocation", giving the index into the ``charging_post`` dataframe.
    """
    from functools import partial

    vacancy_by_number = charging_posts.capacity - charging_posts.occupancy
    if isinstance(seed, np.random.Generator):
        rng = seed
    else:
        rng = np.random.default_rng(seed=seed)
    if vacancy_by_number.sum() < len(fleet):
        return random_overbooking(
            fleet,
            charging_posts,
            seed=rng,
            method=partial(
                random_allocator, maxiter=maxiter, seed=rng, matcher=matcher
            ),
        )

    vacancies = np.array([i for i, n in vacancy_by_number.items() for _ in range(n)])

    if maxiter is None or maxiter <= 0:
        # TODO: tighten random allocator's default maxiter
        # labels: enhancement
        # The default maximum number of iteration is equal to the number of charging
        # post vacancies. But that could be tightened within the loop itself, whenever
        # vacancies are allocated. Not sure how though.
        maxiter = len(vacancies) + 1

    rng.shuffle(vacancies)

    allocation = pd.Series(np.full(len(fleet), pd.NA), dtype="Int64", index=fleet.index)
    unassigned = fleet.copy(deep=False)
    for _ in range(maxiter):
        is_match = matcher(
            unassigned.reset_index(drop=True),
            charging_posts.loc[vacancies[: len(unassigned)]].reset_index(drop=True),
        ).to_numpy()
        if is_match.any():
            allocation.loc[allocation.isna()] = np.where(
                is_match, vacancies[: len(unassigned)], pd.NA
            )
            unassigned = unassigned[~is_match]
            vacancies = vacancies[
                np.concatenate(
                    (~is_match, np.ones(len(vacancies) - len(is_match), dtype=bool))
                )
            ]
            if len(unassigned) == 0:
                break
        vacancies = np.roll(vacancies, shift=-1)
    result = fleet.copy(deep=False)
    result["allocation"] = allocation
    return result


def random_overbooking(
    fleet: pd.DataFrame,
    charging_posts: pd.DataFrame,
    method: Callable[[pd.DataFrame, pd.DataFrame], pd.DataFrame],
    seed: Optional[Union[int, np.random.Generator]] = None,
):
    """Random allocation for overbooked infrastructure.

    The infrastructure is overbooked when there are more electric vehicles than spare
    posts. In that case, we first try and allocate a random subset of vehicles. Then,
    we match left-over vehicles with whatever capacity is still available from the first
    step.

    Args:
        fleet (pandas.DataFrame): dataframe of electric vehicles
        charging_posts (pandas.DataFrame): dataframe of charging_posts
        method: an allocator method taking only two argument, the fleet and the charging
            post infrastructure. It could be something like
            ``functools.partial(random_allocator, matcher=matcher)``.
        seed (Optional[Union[int, numpy.random.Generator]]): seed for the random number
            generators. Defaults to ``None``. See :py:func:`numpy.random.default_rng`.
            Alternatively, it can be a :py:class:`numpy.random.Generator` instance.

    Returns:
        pandas.DataFrame: A shallow copy of the ``fleet`` dataframe with an extra
        column, "allocation", giving the index into the ``charging_post`` dataframe.
    """
    if isinstance(seed, np.random.Generator):
        rng = seed
    else:
        rng = np.random.default_rng(seed=seed)

    vacancy_by_number = charging_posts.capacity - charging_posts.occupancy
    if vacancy_by_number.sum() >= len(fleet):
        return method(fleet, charging_posts)

    # pick a subfleet to service first
    subfleet_filter = np.ones(len(fleet), dtype=bool)
    subfleet_filter[: len(fleet) - vacancy_by_number.sum()] = False
    rng.shuffle(subfleet_filter)

    # create the result table
    result = fleet.copy(deep=False)

    # service the subfleet and copy allocations
    allocated_subfleet = method(fleet.loc[subfleet_filter], charging_posts)
    result["allocation"] = np.full_like(
        allocated_subfleet.allocation, pd.NA, shape=len(result)
    )
    result.loc[subfleet_filter, "allocation"] = allocated_subfleet.allocation

    # check if there is spare capacity to service the leftover fleet
    allocation = charging_posts.occupancy.copy(deep=True)
    new_alloc = allocated_subfleet.groupby("allocation").allocation.count()
    allocation.loc[new_alloc.index] += new_alloc
    infrastructure = charging_posts.copy(deep=False).drop(columns="occupancy")
    infrastructure["occupancy"] = allocation
    spare_cps = infrastructure.loc[infrastructure.occupancy < infrastructure.capacity]
    if len(spare_cps) == 0:
        return result
    # service leftover fleet
    leftover = random_overbooking(
        fleet.loc[~subfleet_filter], spare_cps, method, seed=rng
    )
    result.loc[~subfleet_filter, "allocation"] = leftover.allocation

    return result


def _pick_first(group):
    """Pick only as many as there are vacancies."""
    nvacancies = group.vacancies.iloc[0]
    if len(group) < nvacancies:
        return group.assignment
    return group.assignment.where(np.arange(len(group), dtype=int) < nvacancies, pd.NaT)


def _void_overbooking(
    fleet: pd.DataFrame, charging_posts: pd.DataFrame, assignment: pd.Series
) -> pd.Series:
    """Set overbooked allocations to NaT."""
    vacancies = charging_posts.capacity - charging_posts.occupancy
    assigned = pd.DataFrame(dict(assignment=assignment), index=fleet.index)
    assigned["vacancies"] = (
        vacancies.reindex(assigned.assignment).fillna(0).astype(int).to_numpy()
    )

    x = assigned.groupby("assignment").apply(_pick_first)
    x.index.names = "fleet", "charging_posts"
    assigned = assigned.drop(columns="assignment")
    assigned["assignment"] = x.reset_index("fleet", drop=True)
    return assigned.assignment
