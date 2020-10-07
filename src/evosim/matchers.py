from pathlib import Path
from typing import Any, Callable, Mapping, Sequence, Text, Union

import numpy as np

__doc__ = Path(__file__).with_suffix(".rst").read_text()


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
            result &= function(vehicle, charging_post)
        return result

    return match
