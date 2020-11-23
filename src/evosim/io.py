"""
External Inputs
===============

This module provide some functionality to read from files provided by the industry.
Currently, the objective is to provide a one way bridge to Evosim's data format. Indeed,
some information that is not fully relevant to the simulation is lost.

Usage if fairly straightforward. Some demonstration files are provided in
:py:data:`evosim.io.EXEMPLARS`.


.. doctest:: io
    :options: +NORMALIZE_WHITESPACE

    >>> posts = evosim.io.read_charging_points(
    ...     evosim.io.EXEMPLARS["stations"],
    ...     evosim.io.EXEMPLARS["sockets"],
    ... )
    >>> evosim.charging_posts.is_charging_posts(posts)
    True
    >>> posts[posts.columns[:6]].sample(5, random_state=1)
          latitude  longitude  capacity  occupancy socket charger
    post
    14       51.50      -0.43         1          1  TYPE2    FAST
    21       51.50      -0.43         1          1  TYPE2    SLOW
    18       51.50      -0.43         1          1  TYPE2    FAST
    20       51.53      -0.17         1          1  TYPE2    FAST
    25       51.49       0.03         1          1  TYPE2    FAST
    >>> posts[posts.columns[6:]].sample(5, random_state=1)
          charging_cost  power          state_check
    post
    14              0.0    7.2  2020-01-01 00:00:00
    21              0.0    3.6  2020-01-01 00:00:00
    18              0.1    7.2  2020-01-01 00:00:00
    20              0.0    7.2  2020-01-01 00:00:00
    25              0.0    7.2  2020-01-01 00:00:00
"""
from pathlib import Path
from typing import IO, Mapping, Optional, Text, Union

import numpy as np
import pandas as pd

from evosim.charging_posts import Chargers, register_charging_posts_generator

FileInput = Union[Text, Path, IO[Text]]

EXEMPLARS: Mapping[Text, Path] = {
    "stations": Path(__file__).parent / "data" / "stations.csv",
    "sockets": Path(__file__).parent / "data" / "sockets.csv",
    "examples": Path(__file__).parent / "data" / "examples",
}
"""Exemplar files. """


def read_stations(stations: FileInput = "stations.csv") -> pd.DataFrame:
    """Reads and formats a table of stations.

    .. csv-table:: Stations file
        :file: data/stations.csv
        :width: 80%

    Args:
        stations (Union[pathlib.Path, str, io.StringIO]): Path to a file or a stream to
            be read from.

    Returns:
        pandas.DataFrame: a formatted dataframe with column types and names similar to
        those used in the rest of evosim.
    """
    result = (
        pd.read_csv(stations, index_col="ChargingStationID")
        .rename(
            columns=dict(
                Lat="latitude",
                Long="longitude",
                Availability="available",
                ProviderID="provider",
                Postcode="postcode",
                LastStateCheckTimestamp="state_check",
            )
        )
        .sort_index()
    )
    result.index.name = "charging_station"
    result["provider"] = [int(u.strip("pro-")) for u in result.provider]
    result["available"] = result.available.astype(bool)

    return result


def read_sockets(
    sockets: FileInput = "sockets.csv",
    max_charger_power: Optional[Mapping[Chargers, float]] = None,
) -> pd.DataFrame:
    """Reads and formats a table of sockets.

    .. csv-table:: Sockets file
        :file: data/sockets.csv
        :width: 80%

    Args:
        sockets (Union[pathlib.Path, str, io.StringIO]): Path to a file or a stream to
            be read from.
        max_charger_power: Discriminates between the charger types given their maximum
            power. Defaults to :py:data:`evosim.charging_posts.MAXIMUM_CHARGER_POWER`.

    Returns:
        pandas.DataFrame: a formatted dataframe with column types and names similar to
        those used in the rest of evosim.
    """
    from operator import itemgetter
    from evosim.charging_posts import (
        to_sockets,
        to_chargers,
        MAXIMUM_CHARGER_POWER,
        Status,
    )

    if max_charger_power is None:
        max_charger_power = MAXIMUM_CHARGER_POWER

    result = (
        pd.read_csv(sockets, index_col="SocketID")
        .rename(
            columns=dict(
                SocketType="socket",
                ChargingCost="charging_cost",
                Power="power",
                ChargingStationID="charging_station",
                ProviderID="provider",
                CurrentState="status",
                LastStateCheckTimestamp="state_check",
            )
        )
        .sort_index()
    )
    result.index.name = "socket"
    result["socket"] = to_sockets(
        result.socket.replace(dict(TYPE_1="TYPE1", TYPE_2="TYPE2"))
    )
    result["charger"] = "something went wrong"
    for charger, power in sorted(
        max_charger_power.items(), key=itemgetter(1), reverse=True
    ):
        result.loc[result.power <= power, "charger"] = charger
    result["charger"] = to_chargers(result.charger)
    states = [Status.UNAVAILABLE, Status.AVAILABLE, Status.OUT_OF_SERVICE]
    result["status"] = [states[u] for u in result["status"]]
    return result


@register_charging_posts_generator(
    name="from_sockets_and_stations",
    is_factory=True,
    docs="""Reads charging points from sockets and stations.

    Puts together the data from sockets and stations csv files to create a table of
    charging posts.  See :py:func:`~evosim.io.read_stations` and
    :py:func:`~evosim.io.read_sockets` for example files.

    Args:
        stations (str): station input table
        sockets (str): socket input table
        max_charger_power (Optional[Dict[Text, float]]): Maximum charging power for each
            item in charger. Defaults to
            :py:data:`evosim.charging_posts.MAXIMUM_CHARGER_POWER`.
    """,
)
def read_charging_points(
    stations: Union[FileInput, pd.DataFrame] = "stations.csv",
    sockets: Union[FileInput, pd.DataFrame] = "sockets.csv",
    max_charger_power: Optional[Mapping[Chargers, float]] = None,
) -> pd.DataFrame:
    """Reads charging points from sockets and stations.

    Puts together the tables read in :py:func:`~evosim.io.read_stations` and
    :py:func:`~evosim.io.read_sockets` into a charging posts table as understood in the
    rest of evosim.

    Args:
        stations (Union[pathlib.Path, str, io.StringIO, pandas.DataFrame]): station
            input table
        sockets (Union[pathlib.Path, str, io.StringIO, pandas.DataFrame]): socket input
            table
        max_charger_power: Maximum charging power for each item in
            :py:class:`evosim.charging_posts.Chargers`. Defaults to
            :py:data:`evosim.charging_posts.MAXIMUM_CHARGER_POWER`.

    Returns:
        pandas.DataFrame: a table of charging posts following the schema in
        :py:mod:`evosim.charging_posts`.
    """
    from evosim.charging_posts import to_charging_posts

    if not isinstance(stations, pd.DataFrame):
        stations = read_stations(stations)
    if not isinstance(sockets, pd.DataFrame):
        sockets = read_sockets(sockets, max_charger_power)

    merged = pd.concat(
        (
            sockets,
            stations.drop(columns=["provider", "state_check"])
            .loc[sockets.charging_station]
            .set_index(sockets.index),
        ),
        axis="columns",
    )
    merged = merged.loc[
        np.logical_and(merged.current_state >= 0, merged.available)
    ].drop(columns=["available", "postcode"])
    merged.index.name = "socket_id"

    merged["socket"] = merged.socket.astype(str)
    grouped = merged.groupby(["charging_station", "socket", "provider"])
    aggregated = grouped.agg("first")
    aggregated["occupancy"] = grouped.current_state.sum()
    aggregated["capacity"] = grouped.current_state.count()

    aggregated = (
        aggregated.reset_index(level="socket")
        .reset_index(drop=True)
        .drop(columns="current_state")
    )
    return to_charging_posts(aggregated)


def output_via_pandas(
    table,
    path: Union[Text, Path],
    overwrite: bool = True,
    fileformat: Optional[Text] = None,
    **kwargs,
):
    """Writes a table to file, guessing the format from the filename."""
    path = Path(path)
    if path.exists() and path.is_dir():
        raise RuntimeError(f"Path {path} is a directory, not a file.")

    if (not overwrite) and path.exists():
        raise RuntimeError(f"Path {path} already exists and overwrite is False")

    if fileformat is None:
        fileformat = path.suffix
    if fileformat.startswith("."):
        fileformat = fileformat[1:]
    if fileformat == "xlsx":
        table.to_excel(path, **kwargs)
    elif fileformat == "feather":
        table.to_feather(path, **kwargs)
    elif fileformat == "h5":
        table.to_hdf(path, **kwargs)
    elif fileformat == "json":
        table.to_json(path, **kwargs)
    else:
        table.to_csv(path, **kwargs)
