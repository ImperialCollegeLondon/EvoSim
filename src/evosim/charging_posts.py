from enum import Flag, auto
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Sequence, Text, Tuple, Union

import numpy as np
import pandas as pd

from evosim import constants
from evosim.autoconf import AutoConf

__doc__ = Path(__file__).with_suffix(".rst").read_text()

register_charging_posts_generator = AutoConf("charging posts generation")
"""Registry for functions to read or generate charging posts."""


class Sockets(Flag):
    """Charging post socket types."""

    TYPE1 = auto()
    TYPE2 = auto()
    THREE_PIN_SQUARE = auto()
    DC_COMBO_TYPE2 = auto()
    CHADEMO = auto()
    CCS = auto()

    def __str__(self):
        return super().__str__()[8:]


class Chargers(Flag):
    """Charging post charging types."""

    SLOW = auto()
    FAST = auto()
    RAPID = auto()

    def __str__(self):
        return super().__str__()[9:]


MAXIMUM_CHARGER_POWER: Mapping[Chargers, float] = {
    Chargers.SLOW: 4,
    Chargers.FAST: 10,
    Chargers.RAPID: np.inf,
}
""" Maximum power each charger can provide. """


def _to_enum(
    data: Union[Sequence[Text], Text, Any], enumeration, name: Text
) -> Sequence:
    """Transforms text strings to sockets or chargers."""
    if isinstance(data, Text):
        return _to_enum([data], enumeration, name)[0]
    if isinstance(data, enumeration):
        return data

    _locals = {u.name: u for u in enumeration}

    def mapper(item):
        return eval(str(item).upper(), {}, _locals)

    try:
        result = [mapper(k) for k in data]
    except KeyError as e:
        raise ValueError(f"Incorrect {name} name {e}")
    if isinstance(data, np.ndarray):
        return np.array(result)
    elif isinstance(data, pd.Series):
        return pd.Series(result, index=data.index)
    return result


def to_sockets(
    data: Union[Sequence[Union[Sockets, Text]], Text, Sockets]
) -> Sequence[Sockets]:
    """Transforms text strings to sockets.

    Example:

        String to sockets:

        >>> from evosim.charging_posts import to_sockets
        >>> to_sockets("Type1")
        <Sockets.TYPE1: 1>

        Lists of strings to lists sockets:

        >>> to_sockets(["Type1", "type2"])
        [<Sockets.TYPE1: 1>, <Sockets.TYPE2: 2>]

        Numpy arrays of strings to numpy arrays of sockets:

        >>> to_sockets(np.array(["Type1", "type2"]))
        array([<Sockets.TYPE1: 1>, <Sockets.TYPE2: 2>], dtype=object)

        Pandas series to pandas series:

        >>> to_sockets(pd.Series(["Type1", "type2"], index=['a', 'b']))
        a    TYPE1
        b    TYPE2
        dtype: object

        Or sockets to sockets...

        >>> to_sockets(evosim.charging_posts.Sockets.TYPE1)
        <Sockets.TYPE1: 1>
    """
    return _to_enum(data, Sockets, "socket")


def to_chargers(
    data: Union[Sequence[Union[Text, Chargers]], Text, Chargers]
) -> Sequence[Chargers]:
    """Transforms text strings to chargers.
    Example:

        String to chargers:

        >>> from evosim.charging_posts import to_chargers
        >>> to_chargers("slow")
        <Chargers.SLOW: 1>

        Lists of strings to lists chargers:

        >>> to_chargers(["slow", "fast"])
        [<Chargers.SLOW: 1>, <Chargers.FAST: 2>]

        Numpy arrays of strings to numpy arrays of chargers:

        >>> to_chargers(np.array(["slow", "fast"]))
        array([<Chargers.SLOW: 1>, <Chargers.FAST: 2>], dtype=object)

        Pandas series to pandas series:

        >>> to_chargers(pd.Series(["slow", "fast"], index=['a', 'b']))
        a    SLOW
        b    FAST
        dtype: object

        Or chargers to chargers...

        >>> to_chargers(evosim.charging_posts.Chargers.SLOW)
        <Chargers.SLOW: 1>
    """
    return _to_enum(data, Chargers, "charger")


CHARGING_POSTS_SCHEMA: Mapping[
    Text, Union[np.dtype, Callable[[Sequence], Sequence], Sequence[np.dtype]]
] = dict(
    latitude=(np.dtype(float), np.float16, np.float32, np.float64),
    longitude=(np.dtype(float), np.float16, np.float32, np.float64),
    capacity=(np.dtype(int), np.int8, np.int16, np.int32, np.int64),
    occupancy=(np.dtype(int), np.int8, np.int16, np.int32, np.int64),
    socket=to_sockets,
    charger=to_chargers,
)
"""Schema defining a charging posts

Maps the column to the dtype, a sequence of dtypes, or to an idem-potent callable that
can be used to transform the column. If  a sequence of dtypes is given, then the first
one is the default. All the columns named here are **required**. A charging posts table
can any number of extra columns.
"""


def _dataframe_follows_schema(
    dataframe: pd.DataFrame,
    schema: Mapping[Text, Any],
    index_name: Optional[Text] = None,
    raise_exception: bool = False,
) -> bool:
    missing_cols = set(schema) - set(dataframe.columns)
    if missing_cols and raise_exception:
        raise ValueError(f"Missing column(s) {', '.join(missing_cols)}")
    elif missing_cols:
        return False
    for column, dtypes in schema.items():
        if callable(dtypes):
            transformed = dtypes(dataframe[column])
            incorrect = (transformed != dataframe[column]).any()
            if incorrect and raise_exception:
                raise ValueError(f"Incorrect values in column {column}")
            elif incorrect:
                return False
        else:
            dtype = dataframe[column].dtype
            is_sequence = isinstance(dtypes, Sequence)
            correct = (dtype in dtypes) if is_sequence else (dtype == dtypes)
            if raise_exception and not correct:
                raise ValueError(f"Incorrect dtypes for {column}: {dtype} vs {dtypes}")
            elif not correct:
                return False
    if (
        index_name is not None
        and dataframe.index.name != index_name
        and raise_exception
    ):
        msg = f"Index name is {dataframe.index.name} rather than {index_name}'"
        raise ValueError(msg)
    return index_name is None or dataframe.index.name == index_name


def is_charging_posts(dataframe: pd.DataFrame, raise_exception: bool = False) -> bool:
    """True if dataframe follows the charging post schema.

    Args:
        dataframe (pandas.DataFrame): putative charging posts
        raise_exception: if ``False`` returns a boolean. If ``True``, will raise an
            exception with some information identifying the difference with
            :py:data:`CHARGING_POSTS_SCHEMA`.

    Usage:

        >>> from pytest import raises
        >>> from evosim.charging_posts import random_charging_posts, is_charging_posts
        >>> posts = random_charging_posts(5)
        >>> is_charging_posts(posts, raise_exception=True)
        True

        >>> is_charging_posts(posts.drop(columns="latitude"))
        False

        >>> wrong_dtype = posts.copy(deep=False)
        >>> wrong_dtype["latitude"] = wrong_dtype.latitude.astype(str)
        >>> is_charging_posts(wrong_dtype)
        False

        >>> wrong_dtype = posts.copy(deep=False)
        >>> wrong_dtype["socket"] = [str(u).lower() for u in wrong_dtype.socket]
        >>> is_charging_posts(wrong_dtype)
        False

        >>> wrong_index_name = posts.copy(deep=False)
        >>> wrong_index_name.index.name = "notpost"
        >>> is_charging_posts(wrong_index_name)
        False
        >>> wrong_index_name.index.name = "POST"
        >>> is_charging_posts(wrong_index_name)
        False

        >>> with raises(ValueError):
        ...     is_charging_posts(posts.drop(columns="latitude"), raise_exception=True)
    """
    from evosim.charging_posts import CHARGING_POSTS_SCHEMA

    return _dataframe_follows_schema(
        dataframe,
        raise_exception=raise_exception,
        schema=CHARGING_POSTS_SCHEMA,
        index_name="post",
    )


def _transform_to_schema(
    schema: Mapping[Text, Any],
    data: Optional[Union[pd.DataFrame, Any]],
    index_name: Optional[Text] = None,
    reorder: bool = True,
) -> pd.DataFrame:
    dataframe = data.copy(deep=False)
    for column, dtypes in schema.items():
        if column not in dataframe.columns:
            raise ValueError(f"Missing column {column}")
        if callable(dtypes):
            dataframe[column] = dtypes(dataframe[column])
            continue
        if not isinstance(dtypes, Sequence):
            dtypes = [dtypes]
        if dataframe[column].dtype not in dtypes:
            dataframe[column] = dataframe[column].astype(dtypes[0])
    if index_name is not None and index_name in dataframe.columns:
        dataframe = dataframe.set_index(index_name)
    else:
        dataframe.index.name = index_name
    if reorder:
        columns = list(schema.keys()) + [
            u for u in dataframe.columns if u not in schema.keys()
        ]
        dataframe = dataframe[columns]
    return dataframe


def to_charging_posts(data: pd.DataFrame) -> pd.DataFrame:
    """Tries and transform input data to a charging posts dataframe.

    This function will try and transform the columns of the input dataframe to fit the
    schema defined in :py:data:`evosim.charging_posts.CHARGING_POSTS_SCHEMA`. It also
    sets the "post" column as the index, if it exists. In any-case, it names the
    indices "post". It returns a shallow copy of the input data frame with transformed
    columns as required.

    Args:
        data (pandas.DataFrame): dataframe to transform following the schema.

    Returns:
        pandas.DataFrame: A dataframe conforming to the charging post schema.

    Example:

        >>> from evosim.charging_posts import (
        ...     random_charging_posts,
        ...     to_charging_posts,
        ...     is_charging_posts,
        ...     Sockets,
        ...     Chargers,
        ... )
        >>> dataframe = random_charging_posts(5)
        >>> dataframe["socket"] = [str(u).lower() for u in dataframe.socket]
        >>> dataframe["charger"] = [str(u).lower() for u in dataframe.charger]
        >>> dataframe["capacity"] = dataframe.capacity.astype(float)
        >>> is_charging_posts(dataframe)
        False
        >>> infrastructure = to_charging_posts(dataframe)
        >>> is_charging_posts(infrastructure)
        True
        >>> isinstance(infrastructure.at[0, "socket"], Sockets)
        True
        >>> isinstance(infrastructure.at[0, "charger"], Chargers)
        True
        >>> infrastructure["capacity"].dtype == int
        True
    """
    from evosim.charging_posts import CHARGING_POSTS_SCHEMA

    return _transform_to_schema(CHARGING_POSTS_SCHEMA, data, index_name="post")


@register_charging_posts_generator(
    name="random",
    is_factory=True,
    docs="""Generates a random table of charging posts.

    Args:
        n (int): The number of charging posts
        latitude (Tuple[float, float]): The range over which to create random current
            locations and destinations. Defaults to the :py:data:`London latitudinal
            range <evosim.constants.LONDON_LATITUDE>`.
        longitude (Tuple[float, float]): The range over which to create random current
            locations and destinations. Defaults to the :py:data:`London longitudinal
            range <evosim.constants.LONDON_LONGITUDE>`.
        socket_types (List[Text]): A list of sockets from which to choose randomly.
            Defaults to :py:class:`all available socket types
            <evosim.charging_posts.Sockets>`.
        socket_distribution (Optional[List[float]]): weights when choosing the socket
            types.
        socket_multiplicity (int): number of different types of socket each post can
            accomodate.
        charger_types (List[Text]): A list of chargers from which to choose randomly.
            Defaults to :py:class:`all available charger types
            <evosim.charging_posts.Chargers>` .
        charger_distribution (Optional[List[float]]): weights when choosing the charger
            types.
        charger_multiplicity (int): number of different types of chargers each post can
            accomodate.
        capacity (Tuple[int, int]): A range from which to choose the maximum capacity
            for each charging post. The range can be given as ``(start, end)``, or as a
            single number, in which case it defaults to ``1, capacity + 1``. Defaults to
            a capacity of 1 for each charging post.

            .. note::

                The range given as ``(min, max)`` will allow capacities between ``min``
                included and ``max`` excluded, as per python conventions.

        occupancy (Tuple[int, int]): A range from which to choose the current occupancy
            for each charging post. The range can be given as ``(start, end)``, or as a
            single number, in which case it defaults to ``0, occupancy + 1``. Defaults
            to an occupancy of 0. The occupancy is always smaller than the capacity.

            .. warning::

                Owing to the simplicity of the implementation, the distribution of
                occupancies is not quite uniform and may skew towards lower values.

            .. note::

                The range given as ``(min, max)`` will allow capacities between ``min``
                included and ``max`` excluded, as per python conventions.

        seed (Optional[int]): optional seed for the random number generators.
    """,
)
def random_charging_posts(
    n: int,
    latitude: Tuple[float, float] = constants.LONDON_LATITUDE,
    longitude: Tuple[float, float] = constants.LONDON_LONGITUDE,
    socket_types: Sequence[Union[Text, Sockets]] = tuple((str(u) for u in Sockets)),
    socket_distribution: Optional[Sequence[float]] = None,
    socket_multiplicity: int = 1,
    charger_types: Sequence[Union[Text, Chargers]] = tuple((str(u) for u in Chargers)),
    charger_distribution: Optional[Sequence[float]] = None,
    charger_multiplicity: int = 1,
    capacity: Optional[Union[Tuple[int, int], int]] = (1, 2),
    occupancy: Optional[Union[Tuple[int, int], int]] = (0, 1),
    seed: Optional[Union[int, np.random.Generator]] = None,
) -> pd.DataFrame:
    """Generates a random table representing the charging posts infrastructure.

    Args:
        n: The number of charging posts
        latitude: The range over which to create random current locations and
            destinations. Defaults to the :py:data:`London latitudinal range
            <evosim.constants.LONDON_LATITUDE>`.
        longitude: The range over which to create random current locations and
            destinations. Defaults to the :py:data:`London longitudinal range
            <evosim.constants.LONDON_LONGITUDE>`.
        socket_types: A list of :py:class:`~evosim.charging_posts.Sockets` from which to
            choose randomly. Defaults to all available socket types.
        socket_distribution: weights when choosing the socket types.
        socket_multiplicity: number of different types of socket each post can
            accomodate.
        charger_types: A list of :py:class:`~evosim.charging_posts.Chargers` from which
            to choose randomly. Defaults to all available charger types.
        charger_distribution: weights when choosing the charger types.
        charger_multiplicity: number of different types of chargers each post can
            accomodate.
        capacity: A range from which to choose the maximum capacity for each charging
            post. The range can be given as ``(start, end)``, or as a single number, in
            which case it defaults to ``1, capacity + 1``. Defaults to a capacity of 1
            for each charging post.

            .. note::

                The range given as ``(min, max)`` will allow capacities between ``min``
                included and ``max`` excluded, as per python conventions.

        occupancy: A range from which to choose the current occupancy for each charging
            post. The range can be given as ``(start, end)``, or as a single number, in
            which case it defaults to ``0, occupancy + 1``. Defaults to an occupancy of
            0.  The occupancy is always smaller than the capacity.

            .. warning::

                Owing to the simplicity of the implementation, the distribution of
                occupancies is not quite uniform and may skew towards lower values.

            .. note::

                The range given as ``(min, max)`` will allow capacities between ``min``
                included and ``max`` excluded, as per python conventions.

        seed (Optional[Union[int, numpy.random.Generator]]): seed for the random number
            generators. Defaults to ``None``. See :py:func:`numpy.random.default_rng`.
            Alternatively, it can be a :py:class:`numpy.random.Generator` instance.

    Returns:
        pandas.DataFrame: A dataframe representing the charging posts.
    """
    if isinstance(capacity, int):
        capacity = (1, capacity + 1)
    if isinstance(occupancy, int):
        occupancy = (0, occupancy + 1)
    capacity = min(*capacity), max(*capacity)
    if capacity[0] < 1:
        raise ValueError("The minimum capacity must be at least 1.")
    if capacity[1] < 2:
        raise ValueError("The maximum capacity must be at least 2 (excluded).")
    occupancy = min(*occupancy), max(*occupancy)
    if occupancy[0] < 0:
        raise ValueError("The minimum occupancy must be at least 0.")
    if occupancy[1] < 1:
        raise ValueError("The maximum occupancy must be at least 1 (excluded).")
    if isinstance(seed, np.random.Generator):
        rng = seed
    else:
        rng = np.random.default_rng(seed=seed)

    lat = rng.uniform(high=np.max(latitude), low=np.min(latitude), size=n)
    lon = rng.uniform(high=np.max(longitude), low=np.min(longitude), size=n)
    socket = rng.choice(
        list(to_sockets(socket_types)),
        size=(n, socket_multiplicity),
        replace=True,
        p=socket_distribution,
    )
    if socket_multiplicity == 1:
        socket = socket[:, 0]
    else:
        socket = [np.bitwise_or.reduce(u[: rng.integers(1, len(u))]) for u in socket]
    charger = rng.choice(
        list(to_chargers(charger_types)),
        size=(n, charger_multiplicity),
        replace=True,
        p=charger_distribution,
    )
    if charger_multiplicity == 1:
        charger = charger[:, 0]
    else:
        charger = [np.bitwise_or.reduce(u[: rng.integers(1, len(u))]) for u in charger]
    if capacity[0] == capacity[1] + 1 or capacity[0] == capacity[1]:
        capacities = np.ones(n, dtype=int)
    else:
        capacities = rng.integers(low=capacity[0], high=capacity[1], size=n)
    if occupancy[0] == occupancy[1] + 1 or occupancy[0] == occupancy[1]:
        occupancies = np.ones(n, dtype=int)
    else:
        # TODO: random occupancies are not uniform
        # The mod operation will skew the distribution towards lower values. For
        # instance, if the capacity of a particular charging post is 4, but the maximum
        # cpacity as a whole is 5, the occupancies are chosen as one of
        # `[0 % 4, 1 % 4, 2 % 4, 3 % 4, 5 % 4]`, e.g. `[0, 1, 2, 3, 0]`, and `0` is
        # twice as likely as any other value.
        # When fixing, don't forget the **docstring**!
        # labels: bug
        occupancies = (
            rng.integers(low=occupancy[0], high=occupancy[1], size=n) % capacities
        )

    result = pd.DataFrame(
        dict(
            latitude=lat,
            longitude=lon,
            socket=socket,
            charger=charger,
            capacity=capacities,
            occupancy=occupancies,
        )
    )
    result.index.name = "post"
    return to_charging_posts(result)


def _from_file(path: Union[Text, Path], validator: Callable, **kwargs):
    """Reads a atble from file, guessing the format from the filename.

    Defaults to the csv file format.
    """
    from omegaconf import ValidationError

    path = Path(path)
    if path.is_dir():
        path = path / "fleet.csv"

    if not path.exists():
        raise ValidationError(f"Path {path} does not point to a file.")

    if path.suffix == ".xlsx":
        reader = pd.read_excel
    elif path.suffix == ".feather":
        reader = pd.read_feather
    elif path.suffix == ".h5":
        reader = pd.read_hdf
    elif path.suffix == ".json":
        reader = pd.read_json
    else:
        reader = pd.read_csv
    return validator(reader(path, **kwargs))


@register_charging_posts_generator(
    name="from_file",
    is_factory=True,
    docs="""Reads charging posts from a variety of files.
    Args:
        path (Text): path to a file, either excel, csv, json, feather, or hdf5.
        kwargs: Additional arguments are passed on to the underlying :py:mod:pandas`
            function, e.g. :py:func:`pandas.read_csv`.
    """,
)
def charging_posts_from_file(path: Union[Text, Path], **kwargs):
    """Reads charging posts from file, guessing the format from the filename.

    Defaults to the csv file format.
    """
    return _from_file(path, to_charging_posts, **kwargs)
