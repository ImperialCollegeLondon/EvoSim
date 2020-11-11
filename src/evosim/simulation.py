from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import IO, Any, Callable, Dict, List, Mapping, Optional, Text, Union

import pandas as pd
from omegaconf import MISSING
from omegaconf.dictconfig import DictConfig
from omegaconf.listconfig import ListConfig

from evosim.autoconf import AutoConf
from evosim.matchers import Matcher

__doc__ = Path(__file__).with_suffix(".rst").read_text()
register_simulation_output = AutoConf("output")


@dataclass
class SimulationConfig:
    """Configuration of a simulation for reading with OmegaConf."""

    fleet: Dict = field(default_factory=lambda: DictConfig(MISSING))
    charging_posts: Dict = field(default_factory=lambda: DictConfig(MISSING))
    matcher: List = field(default_factory=lambda: ListConfig(["socket_compatibility"]))
    objective: Dict = field(
        default_factory=lambda: DictConfig(dict(name="haversine_distance"))
    )
    allocator: Dict = field(default_factory=lambda: DictConfig(dict(name="greedy")))
    outputs: List = field(default_factory=lambda: ListConfig([]))


@dataclass
class Simulation:
    """Simulation input data and runner."""

    fleet: Any
    """pandas.DataFrame: the fleet to allocate"""
    charging_posts: Any
    """pandas.DataFrame: the charging posts to allocate"""
    matcher: Matcher
    allocator: Callable
    output: Callable
    objective: Optional[Callable] = None

    def run(self):
        """Runs the simulation."""
        from inspect import signature

        arguments = dict(fleet=self.fleet, charging_posts=self.charging_posts)
        parameters = signature(self.allocator).parameters
        if "matcher" in parameters:
            arguments["matcher"] = self.matcher
        if "objective" in parameters:
            arguments["objective"] = self.objective

        result = self.allocator(**arguments)

        self.output(self, result)

    @classmethod
    def load(
        cls,
        settings: Union[Text, Path, IO, Mapping[Text, Any]],
        root: Optional[Union[Text, Path]] = None,
    ) -> Simulation:
        """Loads simulation from an input file.

        Args:
            settings (Union[Text, pathlib.Path, dict]): path to a yaml file, or an io
                buffer with yaml content, or a dictionary with the settings already
                prepared.
            root: root custom interpolation when loading omegaconf files. Defaults to
                the directory where the file is located, if the input is a file, or to
                the current working directory.
        """
        from omegaconf import OmegaConf
        from io import StringIO
        from evosim.fleet import register_fleet_generator
        from evosim.matchers import factory as matcher_factory
        from evosim.charging_posts import register_charging_posts_generator
        from evosim.allocators import register_allocator
        from evosim.objectives import register_objective

        if isinstance(settings, (Text, Path)) and root is None:
            root = Path(settings).parent.absolute()
        elif hasattr(settings, "name") and root is None:
            root = Path(getattr(settings, "name")).absolute()
        elif root is None:
            root = Path().absolute()

        if isinstance(settings, (Text, Path, StringIO, IO)):
            inputs = OmegaConf.load(settings)
        else:
            inputs = OmegaConf.create(settings)
        inputs = OmegaConf.merge(OmegaConf.structured(SimulationConfig), inputs)
        inputs = OmegaConf.merge(
            dict(**inputs), dict(root=str(root), cwd=str(Path().absolute()))
        )
        if OmegaConf.is_missing(inputs, "fleet"):
            inputs.fleet = dict(name="from_file", path="${root}/fleet.csv")
        if OmegaConf.is_missing(inputs, "charging_posts"):
            inputs.charging_posts = dict(
                name="from_file", path="${root}/charging_posts.csv"
            )

        fleet = register_fleet_generator.factory(inputs.fleet)
        charging_posts = register_charging_posts_generator.factory(
            inputs.charging_posts
        )
        matcher = matcher_factory(inputs.matcher)
        allocator = register_allocator.factory(inputs.allocator)
        objective = register_objective.factory(inputs.objective)
        output = simulation_output_factory(inputs.outputs)

        return cls(
            matcher=matcher,
            fleet=fleet,
            charging_posts=charging_posts,
            allocator=allocator,
            objective=objective,
            output=output,
        )


def simulation_output_factory(settings) -> Callable:
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

    return output


@register_simulation_output(name="input_fleet", is_factory=True)
def input_fleet_to_file(
    path: Text, overwrite: bool = True, fileformat: Optional[Text] = None, **kwargs
):
    """Writes input fleet to file.

    Args:
        path: path to the output file.
        overwrite: if ``False``, raises an error rather than overwrite an existing file.
            Defaults to ``True``.
        fileformat: format of the output file. Defaults to guessing from the filename,
            or to csv if there is no good guess.
        **kwargs: any arguments to the underlying :py:mod:`pandas` functions e.g.
            :py:meth:`pandas.DataFrame.to_csv`.
    """
    filepath = Path(path)
    if filepath.exists() and filepath.is_dir():
        raise RuntimeError(f"Path {filepath} is a directory, not a file.")

    if (not overwrite) and filepath.exists():
        raise RuntimeError(f"Path {filepath} already exists and overwrite is False")

    def output(simulation: Simulation, result: pd.DataFrame):
        from evosim.io import output_via_pandas

        output_via_pandas(
            simulation.fleet, path=filepath, overwrite=overwrite, fileformat=fileformat
        )

    return output


@register_simulation_output(name="input_charging_posts", is_factory=True)
def input_charging_posts_to_file(
    path: Text, overwrite: bool = True, fileformat: Optional[Text] = None, **kwargs
):
    """Writes input charging posts to file.

    Args:
        path: path to the output file.
        overwrite: if ``False``, raises an error rather than overwrite an existing file.
            Defaults to ``True``.
        fileformat: format of the output file. Defaults to guessing from the filename,
            or to csv if there is no good guess.
        **kwargs: any arguments to the underlying :py:mod:`pandas` functions e.g.
            :py:meth:`pandas.DataFrame.to_csv`.
    """
    filepath = Path(path)
    if filepath.exists() and filepath.is_dir():
        raise RuntimeError(f"Path {filepath} is a directory, not a file.")

    if (not overwrite) and filepath.exists():
        raise RuntimeError(f"Path {filepath} already exists and overwrite is False")

    def output(simulation: Simulation, result: pd.DataFrame):
        from evosim.io import output_via_pandas

        output_via_pandas(
            simulation.charging_posts,
            path=path,
            overwrite=overwrite,
            fileformat=fileformat,
            **kwargs,
        )

    return output


@register_simulation_output(name="allocated_fleet", is_factory=True)
def allocated_fleet_to_file(
    path: Text, overwrite: bool = True, fileformat: Optional[Text] = None, **kwargs
):
    """Writes allocated fleet to file.

    Args:
        path: path to the output file.
        overwrite: if ``False``, raises an error rather than overwrite an existing file.
            Defaults to ``True``.
        fileformat: format of the output file. Defaults to guessing from the filename,
            or to csv if there is no good guess.
        **kwargs: any arguments to the underlying :py:mod:`pandas` functions e.g.
            :py:meth:`pandas.DataFrame.to_csv`.
    """
    filepath = Path(path)
    if filepath.exists() and filepath.is_dir():
        raise RuntimeError(f"Path {filepath} is a directory, not a file.")

    if (not overwrite) and filepath.exists():
        raise RuntimeError(f"Path {filepath} already exists and overwrite is False")

    def output(simulation: Simulation, result: pd.DataFrame):
        from evosim.io import output_via_pandas

        output_via_pandas(
            result, path=filepath, overwrite=overwrite, fileformat=fileformat
        )

    return output


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
