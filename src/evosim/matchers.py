from pathlib import Path
from typing import Any, Callable, Sequence, Text, Union

import numpy as np

__doc__ = Path(__file__).with_suffix(".rst").read_text()


def charging_point_availability(_, charging_point) -> bool:
    """True if the charging point is available."""
    return charging_point.occupancy <= getattr(charging_point, "capacity", 1)


def socket_compatibility(vehicle, charging_point) -> bool:
    """True if vehicle and charging point are compatible."""
    return np.logical_and(
        vehicle.socket == charging_point.socket,
        vehicle.charger == charging_point.charger,
    )


def single_factory(settings: Text) -> Callable[[Any, Any], bool]:
    """Transforms a string into a single matcher."""
    from evosim import matchers

    return getattr(matchers, settings)


def factory(settings: Union[Sequence[Text], Text]) -> Callable[[Any, Any], bool]:
    """Transforms a sequence of strings into a sequence of matchers."""
    if isinstance(settings, Text):
        return single_factory(settings)

    functions = [single_factory(setting) for setting in settings]

    def match(vehicle, charging_point) -> bool:
        result = functions[0](vehicle, charging_point)
        for function in functions[1:]:
            result &= function(vehicle, charging_point)
        return result

    return match
