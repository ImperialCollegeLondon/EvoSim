from pathlib import Path

import numpy as np

from evosim import constants

__doc__ = Path(__file__).with_suffix(".rst").read_text()


def distance(a, b, radius=constants.EARTH_RADIUS_KM):
    """Great circle distance between two points.

    Computes the distance using a formula derived from the `spherical laws of cosine
    <https://en.wikipedia.org/wiki/Great-circle_distance>`__. It may suffer from large
    rounding errors on single precision floating point architectures, in which case the
    :py:func:`~evosim.objectives.haversine_distance` should be preferred.

    Args:
        a: latitude and longitude of point A in degrees.
        b: latitude and longitude of point B in degrees.
        radius: Radius of the Earth in kilometers. Defaults to
            :py:data:`~evosim.constants.EARTH_RADIUS_KM`.

    Returns:
        distance in kilometers.
    """
    aphi = 2 * np.pi / 360 * a.latitude
    bphi = 2 * np.pi / 360 * b.latitude
    delta_lambda = 2 * np.pi / 360 * (a.longitude - b.longitude)
    return (
        np.arccos(
            np.sin(aphi) * np.sin(bphi)
            + np.cos(aphi) * np.cos(bphi) * np.cos(delta_lambda)
        )
        * radius
    )


def haversine_distance(a, b, radius=constants.EARTH_RADIUS_KM):
    """Great circle distance between two points.

    Implements the `haversine formula for the great circle
    <https://en.wikipedia.org/wiki/Great-circle_distance>`__. It is more computationally
    demanding then :py:func:`evosim.objectives.distance` but is more stable when
    computing small distances with single precision floating points.

    Args:
        a: latitude and longitude of point A in degrees.
        b: latitude and longitude of point B in degrees.
        radius: Radius of the Earth in kilometers. Defaults to
            :py:data:`~evosim.constants.EARTH_RADIUS_KM`.

    Returns:
        distance in kilometers.
    """

    aphi = 2 * np.pi / 360 * a.latitude
    bphi = 2 * np.pi / 360 * b.latitude
    sin_dphi = np.sin((aphi - bphi) / 2)
    cos_dlam = np.sin(np.pi / 360 * (a.longitude - b.longitude))
    return (
        2
        * np.arcsin(
            np.sqrt(
                sin_dphi * sin_dphi + np.cos(aphi) * np.cos(bphi) * cos_dlam * cos_dlam
            )
        )
        * radius
    )
