from pathlib import Path
from typing import Any, Callable, Sequence, Text, Union

__doc__ = Path(__file__).with_suffix(".rst").read_text()


def charging_point_availability(_, charging_point) -> bool:
    """True if the charging point has some spare capacity.

    This matcher checks whether there is any occupancy left. For a single charging
    point, it is either ``True`` or ``False``.  It does not actually depend on the
    vehicles. Hence, the result has not really changed even if both functions are
    applied.

    Example:

        >>> import evosim
        >>> cps = evosim.supply.random_charging_points(5, seed=1)
        >>> evs = evosim.electric_vehicles.random_electric_vehicles(10, seed=1)
        >>> evosim.matchers.charging_point_availability(None, cps.loc[0])
        True
        >>> evosim.matchers.charging_point_availability(None, cps)
        0    True
        1    True
        2    True
        3    True
        4    True
        dtype: bool

    This matcher must still conform to the same interface as all other matchers, so that
    it can be used with others via the factory.
    """
    return charging_point.occupancy < charging_point.capacity


def socket_compatibility(vehicle, charging_point) -> bool:
    """True if vehicle and charging point are compatible."""
    return vehicle.socket == charging_point.socket


def charger_compatibility(vehicle, charging_point) -> bool:
    """True if vehicle and charging point are compatible."""
    return vehicle.charger == charging_point.charger


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
