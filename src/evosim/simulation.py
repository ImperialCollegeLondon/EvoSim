from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    IO,
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Text,
    Type,
    TypeVar,
    Union,
)

import pandas as pd
from omegaconf import MISSING
from omegaconf.dictconfig import DictConfig
from omegaconf.listconfig import ListConfig

from evosim.autoconf import AutoConf
from evosim.matchers import Matcher

__doc__ = Path(__file__).with_suffix(".rst").read_text()
register_simulation_output = AutoConf("outputs")

INPUT_DEFAULTS: Mapping[Text, Any] = dict(
    fleet=dict(name="from_file", path="${cwd}/fleet.csv"),
    charging_posts=dict(name="from_file", path="${cwd}/charging_posts.csv"),
    objective=dict(name="haversine_distance"),
    allocator=dict(name="greedy"),
    matchers=["socket_compatibility"],
    outputs=[],
    imports=[],
)
"""Default input."""

SimulationVar = TypeVar("SimulationVar", bound="Simulation")
"""Annotation for classes derived from :py:class:`~evosim.simulation.Simulation`."""


@dataclass
class SimulationConfig:
    """Configuration of a simulation for reading with OmegaConf."""

    fleet: Dict = field(default_factory=lambda: DictConfig(MISSING))
    charging_posts: Dict = field(default_factory=lambda: DictConfig(MISSING))
    matchers: List = field(default_factory=lambda: ListConfig(MISSING))
    objective: Dict = field(default_factory=lambda: DictConfig(MISSING))
    allocator: Dict = field(default_factory=lambda: DictConfig(MISSING))
    outputs: List = field(default_factory=lambda: ListConfig(MISSING))
    imports: List = field(default_factory=lambda: ListConfig(MISSING))
    root: Text = field(default_factory=lambda: str(Path.cwd()))
    cwd: Text = field(default_factory=lambda: str(Path.cwd()))


def load_initial_imports(imports: List[Union[Text, Path]]):
    """Load user-declared module to register new functions."""
    from importlib import util as implib

    for path in imports:
        path = Path(path)
        spec = implib.spec_from_file_location(path.stem, path)
        mod = implib.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore


def construct_input(
    settings: Optional[Union[Text, Path, IO, Mapping[Text, Any]]] = None,
    root: Optional[Union[Text, Path]] = None,
    overrides: Optional[DictConfig] = None,
) -> DictConfig:
    """Construct and partially validate an input.

    Args:
        settings (Union[Text, pathlib.Path, dict]): path to a yaml file, or an io
            buffer with yaml content, or a dictionary with the settings already
            prepared.
        root: root custom interpolation when loading omegaconf files. Defaults to
            the directory where the file is located, if the input is a file, or to
            the current working directory.
        overrides(Optional[Mapping]): additional dictionary with which to override the
            underlying inputs.

    Returns:
        Mapping: a fully merged omegaconf input.
    """
    from omegaconf import OmegaConf
    from io import StringIO

    if settings is None:
        settings = dict()
    elif isinstance(settings, (Text, Path)) and root is None:
        root = Path(settings).parent.absolute()
    elif hasattr(settings, "name") and root is None:
        root = Path(getattr(settings, "name")).absolute()
    elif root is None:
        root = Path().absolute()

    if isinstance(settings, (Text, Path, StringIO, IO)) or hasattr(settings, "read"):
        inputs = OmegaConf.load(settings)
    else:
        inputs = OmegaConf.create(settings)
    inputs = OmegaConf.merge(dict(root=str(root), cwd=str(Path().absolute())), inputs)
    if overrides:
        inputs = OmegaConf.merge(inputs, overrides)
    inputs = OmegaConf.merge(OmegaConf.structured(SimulationConfig), inputs)
    for subsection, defaults in INPUT_DEFAULTS.items():
        if OmegaConf.is_missing(inputs, subsection):
            setattr(inputs, subsection, OmegaConf.create(defaults))

    return inputs


def construct_factories(
    inputs: DictConfig, materialize: bool = True
) -> Mapping[Text, Callable]:
    """Constructs factories from pre-constructed inputs.

    Args:
        inputs (Mapping): pre-constructed inputs
        materialize: whether to call the factories (``True``) or return them uncalled.
    """
    from evosim.matchers import factory as matcher_factory
    from evosim.autoconf import evosim_registries

    result = {
        k: v.factory(inputs[k], materialize=materialize)
        for k, v in evosim_registries().items()
        if k not in {"matchers", "outputs"}
    }
    result["matchers"] = matcher_factory(inputs.matchers, materialize)
    result["outputs"] = simulation_output_factory(inputs.outputs, materialize)
    return result


@dataclass
class Simulation:
    """Simulation input data and runner."""

    fleet: Any
    """pandas.DataFrame: the fleet to allocate"""
    charging_posts: Any
    """pandas.DataFrame: the charging posts to allocate"""
    allocator: Callable
    matchers: Matcher
    outputs: Callable
    objective: Optional[Callable] = None

    def __call__(self) -> pd.DataFrame:
        """Runs the simulation."""
        from inspect import signature

        arguments = dict(fleet=self.fleet, charging_posts=self.charging_posts)
        parameters = signature(self.allocator).parameters
        if "matcher" in parameters:
            arguments["matcher"] = self.matchers
        if "objective" in parameters:
            arguments["objective"] = self.objective

        result = self.allocator(**arguments)

        self.outputs(self, result)

        return result

    @classmethod
    def load(
        cls: Type[SimulationVar],
        settings: Union[Text, Path, IO, Mapping[Text, Any]],
        root: Optional[Union[Text, Path]] = None,
    ) -> SimulationVar:
        """Loads simulation from an input file.

        Args:
            settings (Union[Text, pathlib.Path, dict]): path to a yaml file, or an io
                buffer with yaml content, or a dictionary with the settings already
                prepared.
            root: root custom interpolation when loading omegaconf files. Defaults to
                the directory where the file is located, if the input is a file, or to
                the current working directory.

        Returns:
            :py:data:`~evosim.simulation.SimulationVar`: an instance of a class derived
            from :py:class:`~evosim.simulation.Simulation`.
        """
        inputs = construct_input(settings, root=root)
        load_initial_imports(inputs.imports)
        return cls(**construct_factories(inputs, materialize=True))


def simulation_output_factory(settings, materialize: bool = True) -> Callable:
    """Creates an output function to call all output functions."""
    from evosim.simulation import register_simulation_output

    output_functions = [register_simulation_output.factory(o) for o in settings]
    if len(output_functions) == 0:

        def output(simulation: Simulation, result: pd.DataFrame):
            pass

    elif len(output_functions) == 1:

        output = output_functions[0]

    else:

        def output(simulation: Simulation, result: pd.DataFrame):
            for output in output_functions:
                output(simulation, result)

    if not materialize:

        def output_factory():
            return output

        return output_factory

    return output


def _output_dataframe(
    data_mangler: Callable,
    path: Text,
    overwrite: bool = True,
    fileformat: Optional[Text] = None,
    **kwargs,
):
    if str(path).lower() in ("screen", "stdout", "none", "-"):
        filepath = None
    else:
        filepath = Path(path)
    if filepath is not None and filepath.exists() and filepath.is_dir():
        raise RuntimeError(f"Path {filepath} is a directory, not a file.")

    if filepath is not None and (not overwrite) and filepath.exists():
        raise RuntimeError(f"Path {filepath} already exists and overwrite is False")

    def output(simulation: Simulation, result: pd.DataFrame):
        from evosim.io import output_via_pandas

        data = data_mangler(simulation, result)
        if filepath is None:
            print(data)
        else:
            output_via_pandas(
                data, path=filepath, overwrite=overwrite, fileformat=fileformat
            )

    return output


@register_simulation_output(name="input_fleet", is_factory=True)
def input_fleet_to_file(
    path: Text, overwrite: bool = True, fileformat: Optional[Text] = None, **kwargs
):
    """Writes input fleet to file.

    Args:
        path: path to the output file. If one of "stdout" or "-", then prints to screen.
        overwrite: if ``False``, raises an error rather than overwrite an existing file.
            Defaults to ``True``.
        fileformat: format of the output file. Defaults to guessing from the filename,
            or to csv if there is no good guess.
        **kwargs: any arguments to the underlying :py:mod:`pandas` functions e.g.
            :py:meth:`pandas.DataFrame.to_csv`.
    """
    return _output_dataframe(
        lambda s, r: s.fleet,
        path=path,
        overwrite=overwrite,
        fileformat=fileformat,
        **kwargs,
    )


@register_simulation_output(name="input_charging_posts", is_factory=True)
def input_charging_posts_to_file(
    path: Text, overwrite: bool = True, fileformat: Optional[Text] = None, **kwargs
):
    """Writes input charging posts to file.

    Args:
        path: path to the output file. If one of "stdout" or "-", then prints to screen.
        overwrite: if ``False``, raises an error rather than overwrite an existing file.
            Defaults to ``True``.
        fileformat: format of the output file. Defaults to guessing from the filename,
            or to csv if there is no good guess.
        **kwargs: any arguments to the underlying :py:mod:`pandas` functions e.g.
            :py:meth:`pandas.DataFrame.to_csv`.
    """
    return _output_dataframe(
        lambda s, r: s.charging_posts,
        path=path,
        overwrite=overwrite,
        fileformat=fileformat,
        **kwargs,
    )


@register_simulation_output(name="allocated_fleet", is_factory=True)
def allocated_fleet_to_file(
    path: Text, overwrite: bool = True, fileformat: Optional[Text] = None, **kwargs
):
    """Writes allocated fleet to file.

    Args:
        path: path to the output file. If one of "stdout" or "-", then prints to screen.
        overwrite: if ``False``, raises an error rather than overwrite an existing file.
            Defaults to ``True``.
        fileformat: format of the output file. Defaults to guessing from the filename,
            or to csv if there is no good guess.
        **kwargs: any arguments to the underlying :py:mod:`pandas` functions e.g.
            :py:meth:`pandas.DataFrame.to_csv`.
    """
    return _output_dataframe(
        lambda s, r: r,
        path=path,
        overwrite=overwrite,
        fileformat=fileformat,
        **kwargs,
    )


def distances(fleet: pd.pandas, charging_posts: pd.pandas) -> pd.Series:
    from evosim.objectives import haversine_distance

    vehicles = fleet.loc[
        fleet.allocation.notna(), ["dest_lat", "dest_long", "allocation"]
    ].rename(columns=dict(dest_lat="latitude", dest_long="longitude"))
    posts = charging_posts.loc[
        vehicles.allocation, ["latitude", "longitude"]
    ].set_index(vehicles.index)
    return haversine_distance(vehicles, posts.set_index(vehicles.index))


@register_simulation_output(name="stats")
def allocation_stats(simulation: Simulation, result: pd.DataFrame):
    """Simple standard statistics about the allocation."""
    from textwrap import dedent
    from evosim.objectives import haversine_distance

    vehicles = result.loc[result.allocation.notna()]
    posts = simulation.charging_posts.loc[vehicles.allocation].set_index(vehicles.index)
    final_distances = haversine_distance(
        vehicles[["dest_lat", "dest_long"]].rename(
            columns=dict(dest_lat="latitude", dest_long="longitude")
        ),
        posts,
    )

    print(f"Unallocated vehicles: {result.allocation.isna().sum()}/{len(result)}")
    print(f"Allocated vehicles: {result.allocation.notna().sum()}/{len(result)}")
    print(
        dedent(
            f"""
            Final distances (in kilometers):
                * mean: {final_distances.mean():.2f}
                * stdev: {final_distances.std():.2f}
                * skew: {final_distances.skew():.2f}
                * quantile(25%): {final_distances.quantile(0.25):.2f}
                * quantile(50%): {final_distances.quantile(0.50):.2f}
                * quantile(75%): {final_distances.quantile(0.75):.2f}
                * min: {final_distances.min():.2f}
                * max: {final_distances.max():.2f}
            """
        ).lstrip()
    )


@register_simulation_output(name="sockets", is_factory=True)
def write_sockets(
    path: Text, overwrite: bool = True, fileformat: Optional[Text] = None, **kwargs
):
    """Extract socket information from the charging posts.

    The output may include an extra "VehicleID" column indicating allocating vehicles.
    This output format works best when the input charging posts are read from sockets
    and stations files.

    Args:
        path: path to the output file. If one of "stdout" or "-", then prints to screen.
        overwrite: if ``False``, raises an error rather than overwrite an existing file.
            Defaults to ``True``.
        fileformat: format of the output file. Defaults to guessing from the filename,
            or to csv if there is no good guess.
        **kwargs: any arguments to the underlying :py:mod:`pandas` functions e.g.
            :py:meth:`pandas.DataFrame.to_csv`.
    """

    def create_sockets(
        simulation: Simulation,
        result: pd.DataFrame,
    ):
        from evosim.io import as_sockets

        data = simulation.charging_posts.copy(deep=False)
        if "allocation" in result:
            data["allocation"] = pd.Series(pd.NA, dtype="Int64")
            allocation = result.allocation[result.allocation.notna()]
            data.loc[allocation.to_numpy(), "allocation"] = allocation.index
        return as_sockets(data)

    return _output_dataframe(
        create_sockets,
        path=path,
        overwrite=overwrite,
        fileformat=fileformat,
        **kwargs,
    )


@register_simulation_output(name="stations", is_factory=True)
def write_stations(
    path: Text, overwrite: bool = True, fileformat: Optional[Text] = None, **kwargs
):
    """Extracts station information from the charging posts table.

    This output format works best when the input charging posts are read from sockets
    and stations files.

    Args:
        path: path to the output file. If one of "stdout" or "-", then prints to screen.
        overwrite: if ``False``, raises an error rather than overwrite an existing file.
            Defaults to ``True``.
        fileformat: format of the output file. Defaults to guessing from the filename,
            or to csv if there is no good guess.
        **kwargs: any arguments to the underlying :py:mod:`pandas` functions e.g.
            :py:meth:`pandas.DataFrame.to_csv`.
    """

    def create_stations(
        simulation: Simulation,
        result: pd.DataFrame,
    ):
        from evosim.io import as_stations

        return as_stations(simulation.charging_posts)

    return _output_dataframe(
        create_stations,
        path=path,
        overwrite=overwrite,
        fileformat=fileformat,
        **kwargs,
    )
