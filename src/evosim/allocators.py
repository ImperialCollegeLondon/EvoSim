from pathlib import Path
from typing import Callable, Optional, Text, Union

import numpy as np
import pandas as pd

from evosim.matchers import Matcher

__doc__ = Path(__file__).with_suffix(".rst").read_text()


class AllocationWarning(UserWarning):
    """Warning raised in allocation algorithms."""


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


def greedy_allocator(
    fleet: pd.DataFrame,
    charging_posts: pd.DataFrame,
    matcher: Matcher,
    distance: Text = "haversine",
    nearest_neighbors: Optional[int] = 10,
    leaf_size: int = 40,
    maxiter: Optional[int] = None,
) -> pd.DataFrame:
    """Greedy allocation algorithm.

    The greedy allocation tries and match the nearest compatible post to each vehicle.
    If a given post is the nearest neighbor to more vehicles than it can accomodate,
    then the vehicles higher in the ``fleet`` table will receive preferential treatment.
    Hence shuffling the fleet may well yield different results.

    Args:
        fleet (pandas.DataFrame): table defining the fleet of vehicles
        charging_posts (pandas.DataFrame): table defining the charging infrastructure
        matcher: defines the compatibility between an electric vehicle and a charging
            post
        distance: the distance metric used to compute the nearest neighbors. See
            :py:class:`sklearn.neighbors.BallTree`.
        leaf_size: parameter of :py:class:`sklearn.neighbors.BallTree`
        maxiter: maximum number of iterations before bailing out. Defaults to the number
            of vacancies.

            .. note::

                Earch turn of the loop, the iteration counter is increased by the number
                of filled vacancies, rather than by 1 as in more standard algorithms.

    Returns:
        pandas.DataFrame: a shallow copy the fleet with an extra column, "allocation",
        indicating the label of the allocated post into the ``charging_posts`` table. Or
        ``pd.NA`` if the vehicle is not allocated.
    """
    from sklearn.neighbors import BallTree
    from evosim.matchers import match_all_to_all
    from warnings import warn

    if nearest_neighbors is None or nearest_neighbors <= 0:
        nearest_neighbors = len(charging_posts)
    if maxiter is None or maxiter <= 0:
        maxiter = (charging_posts.capacity - charging_posts.occupancy).sum() + 1

    def locations(data: pd.DataFrame, is_current=True) -> np.ndarray:
        names = ("latitude", "longitude") if is_current else ("dest_lat", "dest_long")
        return (
            np.concatenate(
                (
                    data[names[0]].to_numpy()[:, None],
                    data[names[1]].to_numpy()[:, None],
                ),
                axis=1,
            )
            * np.pi
            / 180
        )

    sfleet = fleet.copy(deep=False).drop("allocation", errors="ignore")
    allocation = pd.Series(
        np.full(len(sfleet), fill_value=pd.NA), dtype="Int64", index=sfleet.index,
    )

    # copy of charging posts where we can modify the occupancy
    infrastructure = charging_posts.drop(columns="occupancy")
    infrastructure["occupancy"] = charging_posts.occupancy.copy(deep=True)

    iteration = 0
    while iteration < maxiter:
        if (infrastructure.capacity - infrastructure.occupancy).sum() == 0:
            break
        if len(allocation) - allocation.count() == 0:
            break

        has_vacancies = infrastructure.capacity > infrastructure.occupancy
        available_posts = infrastructure.loc[has_vacancies]
        available_fleet = sfleet.loc[allocation.isna()]
        tree = BallTree(
            locations(available_posts), metric=distance, leaf_size=leaf_size
        )
        k = min(nearest_neighbors, len(available_posts))
        _, indices = tree.query(locations(available_fleet, is_current=False), k=k)

        # boolean matrix evs by nearest posts, where True if ev and post match
        nearest_matches = match_all_to_all(
            available_fleet, available_posts, matcher, indices=indices
        )
        # retain index of the nearest matching post only, if any
        nearest_matching = pd.Series(
            available_posts.index[
                indices[
                    np.where(nearest_matches, nearest_matches.cumsum(axis=1), 0) == 1
                ]
            ],
            index=available_fleet.index[nearest_matches.any(axis=1)],
            dtype="Int64",
        )
        newly_assigned = _void_overbooking(sfleet, available_posts, nearest_matching)
        allocation.where(
            allocation.notna(), newly_assigned, inplace=True,
        )

        iteration += max(newly_assigned.count(), 1)
        if newly_assigned.isna().all():
            if k < len(available_posts):
                msg = (
                    "Could not allocate all vehicles: "
                    "increasing ``nearest_neighbors`` might be beneficial"
                )
                warn(msg, AllocationWarning)
            break
        infrastructure.occupancy += (
            newly_assigned.value_counts(dropna=True)
            .reindex(infrastructure.index)
            .fillna(0)
        )

    result = sfleet.copy(deep=False)
    result["allocation"] = allocation
    return result


def _pick_first(group):
    """Pick only as many as there are vacancies."""
    nvacancies = group.vacancies.iloc[0]
    if len(group) < nvacancies:
        return group.allocation
    return group.allocation.where(np.arange(len(group), dtype=int) < nvacancies, pd.NaT)


def _void_overbooking(
    fleet: pd.DataFrame, charging_posts: pd.DataFrame, allocation: pd.Series
) -> pd.Series:
    """Set overbooked allocations to NaT."""
    nonan_alloc = allocation.dropna()
    if len(nonan_alloc) == 0:
        return allocation

    def pick_first(group):
        label = group.iloc[0]
        nvacs = charging_posts.capacity.at[label] - charging_posts.occupancy.at[label]
        return group.where(np.arange(group.shape[0]) < nvacs)

    return (
        nonan_alloc.groupby(by=nonan_alloc)
        .transform(pick_first)
        .reindex_like(allocation)
    )
