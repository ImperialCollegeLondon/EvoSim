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
    27       51.46      -0.43         1          0  TYPE2    FAST
    3        51.61      -0.07         1          0  TYPE2    FAST
    22       51.53      -0.17         1          0  TYPE2    FAST
    18       51.57      -0.50         1          0  TYPE2    FAST
    23       51.53      -0.17         1          0  TYPE2    FAST
    >>> posts[posts.columns[6:11]].sample(5, random_state=1)
             status  socket_id  charging_cost  power  charging_station_id
    post
    27    AVAILABLE        138            0.1    7.2                   14
    3     AVAILABLE        114            0.0    7.2                    2
    22    AVAILABLE        133            0.0    7.2                   12
    18    AVAILABLE        129            0.0    7.2                   10
    23    AVAILABLE        134            0.0    7.2                   12
    >>> posts[posts.columns[11:]].sample(5, random_state=1)
          provider_id          state_check station_state_check postcode
    post
    27              2  2020-01-01 00:00:00  2020-01-0100:00:00  TW149QS
    3               2  2020-01-01 00:00:00  2020-01-0100:00:00   N170TX
    22              1  2020-01-01 00:00:00  2020-01-0100:00:00   NW89SG
    18              1  2020-01-01 00:00:00  2020-01-0100:00:00   UB94HD
    23              2  2020-01-01 00:00:00  2020-01-0100:00:00   NW89SG

Tables corresponding to "sockets" and "stations" files can be extracted from a charging
posts table using :py:func:`~evosim.io.as_sockets` and
:py:func:`~evosim.io.as_stations`. However, this only makes sense if the charging posts
table was originally read from such files in the first place.
"""
from pathlib import Path
from typing import IO, Mapping, Optional, Text, Union

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
                ProviderID="provider_id",
                Postcode="postcode",
                LastStateCheckTimestamp="state_check",
            )
        )
        .sort_index()
    )
    result.index.name = "charging_station"
    result["provider_id"] = [int(u.strip("pro-")) for u in result.provider_id]
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
                ChargingStationID="charging_station_id",
                ProviderID="provider_id",
                CurrentState="status",
                LastStateCheckTimestamp="state_check",
            )
        )
        .sort_index()
    )
    result.index.name = "socket_id"
    result["socket"] = to_sockets(
        result.socket.replace(dict(TYPE_1="TYPE1", TYPE_2="TYPE2"))
    )
    result["charger"] = "something went wrong"
    for charger, power in sorted(
        max_charger_power.items(), key=itemgetter(1), reverse=True
    ):
        result.loc[result.power <= power, "charger"] = charger
    result["charger"] = to_chargers(result.charger)
    result["capacity"] = [(1, 1, 0)[u] for u in result["status"]]
    result["occupancy"] = [(1, 0, 0)[u] for u in result["status"]]
    states = (Status.UNAVAILABLE, Status.AVAILABLE, Status.OUT_OF_SERVICE)
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
    from evosim.charging_posts import to_charging_posts, Status

    if not isinstance(stations, pd.DataFrame):
        stations = read_stations(stations)
    if not isinstance(sockets, pd.DataFrame):
        sockets = read_sockets(sockets, max_charger_power)

    if "state_check" in stations.columns:
        stations = stations.rename(columns=dict(state_check="station_state_check"))

    merged = pd.concat(
        (
            sockets,
            stations.drop(columns="provider_id")
            .loc[sockets.charging_station_id]
            .set_index(sockets.index),
        ),
        axis="columns",
    )
    merged.loc[~merged.available, "status"] = Status.UNAVAILABLE
    merged = merged.drop(columns="available")
    merged.index.name = "socket_id"
    merged = merged.reset_index("socket_id")
    merged.index.name = "post"
    return to_charging_posts(merged)


def output_via_pandas(
    table,
    path: Union[Text, Path, IO],
    overwrite: bool = True,
    fileformat: Optional[Text] = None,
    **kwargs,
):
    """Writes a table to file, guessing the format from the filename.

    Args:
        path (Union[Text, pathlib.Path, io.StringIO]): path to an output file or output
            stream.
        overwrite: If ``True``, then will overwrite any existing file.
        fileformat: One of "csv", "xlsx", "feather", "h5", "json". Defaults to the file
            suffix or "csv".
    """
    if isinstance(path, (Text, Path)):
        path = Path(path)
        if path.exists() and path.is_dir():
            raise RuntimeError(f"Path {path} is a directory, not a file.")
        if (not overwrite) and path.exists():
            raise RuntimeError(f"Path {path} already exists and overwrite is False")

    if fileformat is None:
        fileformat = getattr(path, "suffix", "csv")
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


def as_stations(charging_posts: pd.DataFrame) -> pd.DataFrame:
    """Extracts from a charging posts table the station information.

    Args:
        charging_posts (pandas.DataFrame): charging posts table originally read from
            "sockets" and "stations" file.

    Returns:
        pandas.DataFrame: A table with information similar to that contained in a
        "stations" file.
    """
    charging_posts = charging_posts.copy(deep=False)
    if "charging_station_id" not in charging_posts:
        charging_posts["charging_station_id"] = range(1, len(charging_posts) + 1)
    if "availability" not in charging_posts.columns:
        charging_posts["availability"] = charging_posts.capacity != 0
    columns = dict(
        charging_station_id="ChargingStationID",
        latitude="Lat",
        longitude="Long",
        availability="Availability",
        station_state_check="LastStateCheckTimestamp",
        provider_id="ProviderID",
        postcode="Postcode",
    )
    data = (
        charging_posts[[u for u in columns if u in charging_posts.columns]]
        .rename(columns=columns)
        .drop_duplicates("ChargingStationID")
        .set_index("ChargingStationID")
    )
    if "ProviderID" in data.columns:
        data["ProviderID"] = [f"pro-{i}" for i in data["ProviderID"]]
    data["Availability"] = data["Availability"].astype(int)

    return data


def as_sockets(charging_posts: pd.DataFrame) -> pd.DataFrame:
    """Extracts a "sockets" table from a charging posts table.

    Args:
        charging_posts (pandas.DataFrame): charging posts table originally read from
            "sockets" and "stations" file.

    Returns:
        pandas.DataFrame: A table with information similar to that contained in a
        "sockets" file.
    """
    if (charging_posts.capacity > 1).any():
        raise ValueError("Expected capacities to all be equal to 1.")
    if "charging_station_id" not in charging_posts:
        charging_posts["charging_station_id"] = range(1, len(charging_posts) + 1)
    if "socket_id" not in charging_posts:
        charging_posts["socket_id"] = range(1, len(charging_posts) + 1)

    columns = dict(
        socket_id="SocketID",
        socket="SocketType",
        charging_cost="ChargingCost",
        power="Power",
        charging_station_id="ChargingStationID",
        provider_id="ProviderID",
        status="CurrentState",
        state_check="LastStateCheckTimestamp",
        allocation="VehicleID",
    )
    data = (
        charging_posts[[u for u in columns if u in charging_posts.columns]]
        .rename(columns=columns)
        .set_index("SocketID")
    )
    if "CurrentState" in data:
        data["CurrentState"] = [
            dict(AVAILABLE=1, OUT_OF_SERVICE=-1).get(str(u).upper(), 0)
            for u in data["CurrentState"]
        ]
    data["SocketType"] = (
        data["SocketType"].astype(str).replace(dict(TYPE1="TYPE_1", TYPE2="TYPE_2"))
    )
    return data
