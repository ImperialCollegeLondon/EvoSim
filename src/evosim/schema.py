"""Utility functions for dealing with dataframe schemas."""
from typing import Any, Sequence, Text, Type, Union

import numpy as np
import pandas as pd


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


def _dataframe_follows_schema(
    dataframe: pd.DataFrame,
    schema: Type,
    raise_exception: bool = False,
) -> bool:
    missing_cols = set(schema.required) - set(dataframe.columns)
    if missing_cols and raise_exception:
        raise ValueError(f"Missing column(s) {', '.join(missing_cols)}")
    elif missing_cols:
        return False
    for column, dtypes in schema.columns.items():
        if column not in dataframe.columns:
            continue
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
        schema.index_name is not None
        and dataframe.index.name != schema.index_name
        and raise_exception
    ):
        msg = f"Index name is {dataframe.index.name} rather than {schema.index_name}'"
        raise ValueError(msg)
    return schema.index_name is None or dataframe.index.name == schema.index_name


def _transform_to_schema(
    schema: Type,
    data: Union[pd.DataFrame, Any],
    reorder: bool = True,
) -> pd.DataFrame:
    dataframe = data.copy(deep=False)
    for column, dtypes in schema.columns.items():
        if column not in dataframe.columns and column in schema.required:
            raise ValueError(f"Missing column {column}")
        if callable(dtypes):
            dataframe[column] = dtypes(dataframe[column])
            continue
        if not isinstance(dtypes, Sequence):
            dtypes = [dtypes]
        if dataframe[column].dtype not in dtypes:
            dataframe[column] = dataframe[column].astype(dtypes[0])
    if schema.index_name is not None and schema.index_name in dataframe.columns:
        dataframe = dataframe.set_index(schema.index_name)
    else:
        dataframe.index.name = schema.index_name
    if reorder:
        columns = [u for u in schema.columns.keys() if u in dataframe.columns] + [
            u for u in dataframe.columns if u not in schema.columns.keys()
        ]
        dataframe = dataframe[columns]
    return dataframe
