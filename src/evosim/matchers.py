from pathlib import Path
from typing import Any, Callable, Iterator, Mapping, Sequence, Text, Tuple, Union

import numpy as np
import pandas as pd

__doc__ = Path(__file__).with_suffix(".rst").read_text()

Matcher = Callable[[Any, Any], Any]


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


def socket_compatibility(vehicle, charging_post) -> bool:
    """True if vehicle and charging post are compatible."""
    return np.bitwise_and(vehicle.socket, charging_post.socket)


def distance(vehicle, charging_post, max_distance: float = 1) -> bool:
    """Maximum distance between current vehicle location and charging post."""
    from evosim.objectives import distance

    return distance(vehicle, charging_post) < max_distance


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


def charger_compatibility(vehicle, charging_post) -> bool:
    """True if vehicle and charging post are compatible."""
    return np.bitwise_and(vehicle.charger, charging_post.charger)


def single_factory(settings: Union[Text, Mapping]) -> Callable[[Any, Any], bool]:
    """Transforms a string into a single matcher."""
    from evosim import matchers
    from functools import partial

    if isinstance(settings, Text):
        return getattr(matchers, settings)
    if "name" not in settings:
        raise ValueError("If a mapping, settings should have a `name` key-value pair.")

    parameters = dict(**settings)
    function = getattr(matchers, parameters.pop("name"))
    if len(parameters) == 0:
        return function
    return partial(function, **parameters)


def factory(
    settings: Union[Sequence[Union[Text, Mapping]], Union[Text, Mapping]]
) -> Callable[[Any, Any], bool]:
    """Transforms a sequence of strings into a sequence of matchers."""
    if isinstance(settings, (Text, Mapping)):
        return single_factory(settings)

    functions = [single_factory(setting) for setting in settings]

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
        data: table to split into classes
        matcher: Method by which to create classes
        revisit: If ``True`` then rows can be part of more than one class.

    Returns:
        Iterator[pd.Series]: a boolean array indicating whether each row of the input
        table ``data`` is part of the class.

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
        socket       True
        charger      True
        capacity     True
        occupancy    True
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

    Using :py:func:`~evosim.matcher.classify`, this function creates matching classes of
    charging posts. It then pairs each with a matching subfleet.

    Returns:
        Iterator[Tuple[pd.Series, pd.Series]]: a named 2-tuple of boolean arrays
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
