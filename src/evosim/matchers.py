from pathlib import Path
from typing import (
    Any,
    Callable,
    Iterator,
    Mapping,
    Optional,
    Sequence,
    Text,
    Tuple,
    Union,
)

import numpy as np
import pandas as pd

from evosim.autoconf import AutoConf

__doc__ = Path(__file__).with_suffix(".rst").read_text()

Matcher = Callable[[Any, Any], Any]
"""Signature of all matchers."""

register_matcher = AutoConf("matcher")
"""Registration decorator for matchers."""


@register_matcher
def charging_post_availability(_, charging_post) -> bool:
    """True if the charging post has some spare capacity.

    This matcher checks whether there is any occupancy left. For a single charging
    post, it is either ``True`` or ``False``.  It does not actually depend on the
    vehicles. Hence, the result has not really changed even if both functions are
    applied.

    Example:

        >>> import evosim
        >>> cps = evosim.charging_posts.random_charging_posts(5, seed=1)
        >>> evs = evosim.fleet.random_fleet(10, seed=1)
        >>> evosim.matchers.charging_post_availability(None, cps.loc[0])
        True
        >>> evosim.matchers.charging_post_availability(None, cps)
        post
        0    True
        1    True
        2    True
        3    True
        4    True
        dtype: bool

    This matcher must still conform to the same interface as all other matchers, so that
    it can be used with others via the factory.
    """
    return charging_post.occupancy < charging_post.capacity


@register_matcher
def socket_compatibility(vehicle, charging_post) -> bool:
    """True if vehicle and charging post are compatible."""
    result = np.bitwise_and(vehicle.socket, charging_post.socket)
    if isinstance(result, (np.ndarray, pd.Series)):
        return result.astype(bool)
    return result


@register_matcher
def distance(vehicle, charging_post, max_distance: float = 1) -> bool:
    """Maximum distance between current vehicle location and charging post."""
    from evosim.objectives import distance

    return distance(vehicle, charging_post) < max_distance


@register_matcher
def distance_from_destination(vehicle, charging_post, max_distance: float = 1) -> bool:
    """Maximum distance between vehicle destination and charging post."""
    from evosim.objectives import distance

    return (
        distance(
            vehicle[["dest_lat", "dest_long"]].rename(
                columns=dict(dest_lat="latitude", dest_long="longitude")
            ),
            charging_post,
        )
        < max_distance
    )


@register_matcher
def charger_compatibility(vehicle, charging_post) -> bool:
    """True if vehicle and charging post are compatible."""
    result = np.bitwise_and(vehicle.charger, charging_post.charger)
    if isinstance(result, (np.ndarray, pd.Series)):
        return result.astype(bool)
    return result


def factory(
    settings: Union[Sequence[Union[Text, Mapping]], Union[Text, Mapping]]
) -> Callable[[Any, Any], bool]:
    """Transforms a sequence of strings into a sequence of matchers."""
    if isinstance(settings, (Text, Mapping)):
        return register_matcher.factory(settings)

    functions = [register_matcher.factory(setting) for setting in settings]

    def match(vehicle, charging_post) -> bool:
        result = functions[0](vehicle, charging_post)
        for function in functions[1:]:
            intermediate = function(vehicle, charging_post)
            if isinstance(intermediate, np.ndarray):
                intermediate = intermediate.astype(bool)
            result = np.logical_and(result, intermediate)
        return result

    return match


def classify(
    data: pd.DataFrame, matcher: Matcher, revisit: bool = False
) -> Iterator[pd.Series]:
    """Partitions a fleet or infrastructure into classes matching the matcher.

    This method breaks up the input ``data`` into classes by figuring which rows match
    each other according to the input ``matcher`` method.

    .. note::

        The result of this method is not necessarily unique. For instance, there can be
        `matcher` function where there exists a row ``i`` in ``matcher(data, data[0])``
        for which ``matcher(data, data[0]) != matcher(data, data[i])``. In  that case,
        if we where to start the classification with `i` it would likely yield a
        different set of classes.

    Args:
        data (pandas.DataFrame): table to split into classes
        matcher: Method by which to create classes
        revisit: If ``True`` then rows can be part of more than one class.

    Returns:
        Iterator[pandas.Series]: a boolean array indicating whether each row of the
        input table ``data`` is part of the class.

    Example:

        This method is actually a generator, meant to be used in a loop. Below, we
        immediately materialize the loop into a list:

        >>> data = evosim.charging_posts.random_charging_posts(
        ...     50, seed=1, socket_multiplicity=3,
        ... )
        >>> matcher = evosim.matchers.factory("socket_compatibility")
        >>> classes = [u for u in evosim.matchers.classify(data, matcher)]

        Each item in ``classes`` is an array of boolean values indicating whether a
        particular row of the input dataframe is part of the class. We can verify that
        the classes have different sizes:

        >>> [u.sum() for u in classes]
        [7, 20, 10, 10, 3]

        Each item also contains an attribute ``template`` which indicates the index of
        the row from which this class was created:

        >>> [u.template for u in classes]
        [0, 1, 2, 3, 18]

        Indeed, each class matches the template row:

        >>> [matcher(data[u], data.loc[u.template]).all() for u in classes]
        [True, True, True, True, True]

        Finally, the concatenation of the classes yields the original data:

        >>> (pd.concat((data[u] for u in classes)).sort_index() == data).all()
        latitude     True
        longitude    True
        capacity     True
        occupancy    True
        socket       True
        charger      True
        dtype: bool

        By default, the classification will only include each row once. However, it is
        possible to create overlapping classes. We can verify that ovelapping classes
        have smaller sizes than non-overlapping classes:

        >>> overlap = [u for u in evosim.matchers.classify(data, matcher, revisit=True)]
        >>> [u.sum() for u in overlap]
        [7, 21, 12, 12, 11]

        >>> [u.sum() <= v.sum() for u, v in zip(classes, overlap)]
        [True, True, True, True, True]

        Furthermore each non-overlapping class is as subset of the relevant overlapping
        class:

        >>> [set(u.index).issubset(v.index) for u, v in zip(classes, overlap)]
        [True, True, True, True, True]

        In fact, the template rows from which the classes derive also match:

        >>> [u.template == v.template for u, v in zip(classes, overlap)]
        [True, True, True, True, True]
    """
    visitless = np.ones(len(data), dtype=bool)
    while visitless.any():
        index = np.argmax(visitless)
        is_match = matcher(data, data.iloc[index])
        yieldee = is_match if revisit else np.logical_and(is_match, visitless)
        yieldee.template = is_match.index[index]
        yield yieldee
        visitless = np.logical_and(~is_match.to_numpy(), visitless)


def classify_with_fleet(
    charging_posts: pd.DataFrame, matcher: Matcher, fleet: pd.DataFrame, revisit=False
) -> Iterator[Tuple[pd.Series, pd.Series]]:
    """Creates classes of matching charging_posts and subfleets.

    Using :py:func:`~evosim.matchers.classify`, this function creates matching classes
    of charging posts. It then pairs each with a matching subfleet.

    Args:
        charging_posts (pandas.DataFrame): the table of charging posts.
        matcher: a function to compare charging posts and electric vehicles.
        fleet (pandas.DataFrame): the table of electric vehicles.
        revisit: if `True`, then the classes can overlap.

    Returns:
        Iterator[Tuple[pandas.Series, pandas.Series]]: a named 2-tuple of boolean arrays
        indicating whether each row of the input table ``charging_posts`` and ``fleet``
        is part of the class.

    Example:

        This method is actually a generator, meant to be used in a loop. Below, we
        immediately materialize the loop into a list:

        >>> infrastructure = evosim.charging_posts.random_charging_posts(
        ...     50, seed=1, socket_multiplicity=3,
        ... )
        >>> fleet = evosim.fleet.random_fleet(500, seed=1)
        >>> matcher = evosim.matchers.factory("socket_compatibility")
        >>> classes = [
        ...     u for u in evosim.matchers.classify_with_fleet(
        ...         infrastructure, matcher, fleet
        ...     )
        ... ]

        Each item is composed of a (named) tuple of two boolean arrays indicating the
        rows of the charging posts and infrastructure:

        >>> [(u.charging_posts.sum(), u.fleet.sum()) for u in classes]
        [(7, 97), (20, 166), (10, 79), (10, 85), (3, 73)]

        We can check that the charging posts and subfleet do match the template:

        >>> [
        ...     matcher(
        ...         infrastructure.loc[u.charging_posts],
        ...         infrastructure.loc[u.charging_posts.template]
        ...     ).all()
        ...     for u in classes
        ... ]
        [True, True, True, True, True]

        >>> [
        ...     matcher(
        ...         fleet.loc[u.fleet], infrastructure.loc[u.charging_posts.template]
        ...     ).all()
        ...     for u in classes
        ... ]
        [True, True, True, True, True]
    """
    from collections import namedtuple

    ChargingPostsAndFleet = namedtuple(
        "ChargingPostsAndFleet", ("charging_posts", "fleet")
    )

    visitless = np.ones(len(fleet), dtype=bool)
    for infrastructure in classify(charging_posts, matcher, revisit=revisit):
        is_match = matcher(fleet, charging_posts.loc[infrastructure.template])
        yieldee = is_match if revisit else np.logical_and(is_match, visitless)
        yield ChargingPostsAndFleet(infrastructure, yieldee)
        visitless = np.logical_and(~is_match.to_numpy(), visitless)


def to_namedtuple(data: pd.DataFrame, transform: Optional[Callable] = None):
    """Convert dataframe to namedtuple and apply transformation to each column.

    The main use case is to perform a matrix-wise match between a fleet and charging
    posts, as per :py:func:`~evosim.matchers.match_all_to_all`.

    Args:
        data (pandas.DataFrame): a dataframe to transform to a named tuple.
        transform: an optional operation applied to each column.
    """
    from collections import namedtuple

    if transform is None:
        transform = pd.Series.to_numpy

    DataTuple = namedtuple("DataTuple", [str(u) for u in data.columns])  # type: ignore
    args = {str(k): transform(data[k]) for k in data.columns}
    return DataTuple(**args)  # type: ignore


def match_all_to_all(
    fleet: pd.DataFrame,
    charging_posts: pd.DataFrame,
    matcher: Matcher,
    labels: Optional[Sequence] = None,
    indices: Optional[Sequence[int]] = None,
) -> np.ndarray:
    """Match a fleet with each charging post (or a subset therein).

    Essentially, this is an outer product between the fleet and the charging posts where
    the product is the matcher.

    Args:
        fleet (pandas.DataFrame): fleet of electric vehicles
        charging_posts (pandas.DataFrame): infrastructure against which to match each
            vehicle of the fleet.
        matcher: matching function to apply between each vehicle and charging posts.
        labels: if present, this is an array of labels (i.e.
            :py:meth:`pandas.DataFrame.loc`) into the chargin_posts. It cannot be used
            in conjunction with `indices`.
        indices: if present, this should a matrix of indices (i.e.
            :py:meth:`pandas.DataFrame.iloc`) into the charging posts. It cannot be use
            in conjunction with `labels`.

    Returns:
        A boolean numpy matrix (fleet vs charing posts) indicating each match.
    """
    fleet_nt = to_namedtuple(fleet, lambda x: x.to_numpy()[:, None])
    if indices is None and labels is None:
        infrastructure_nt = to_namedtuple(charging_posts, lambda x: x.to_numpy()[None])
    elif indices is not None and labels is None:
        infrastructure_nt = to_namedtuple(
            charging_posts, lambda x: x.to_numpy()[indices]
        )
    elif indices is None and labels is not None:
        infrastructure_nt = to_namedtuple(
            charging_posts.loc[labels], lambda x: x.to_numpy()[None]
        )
    else:
        msg = "`indices` and `labels` cannot both be given at the same time."
        raise ValueError(msg)
    return matcher(fleet_nt, infrastructure_nt)
