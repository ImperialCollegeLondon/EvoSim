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

register_simulation_output = AutoConf("output")


@dataclass
class SimulationConfig:
    fleet: Dict = field(default_factory=lambda: DictConfig(MISSING))
    charging_posts: Dict = field(default_factory=lambda: DictConfig(MISSING))
    matcher: List = field(default_factory=lambda: ListConfig(["socket_compatibility"]))
    objective: Dict = field(default_factory=lambda: DictConfig(dict()))
    allocator: Dict = field(default_factory=lambda: DictConfig(MISSING))
    outputs: List = field(default_factory=lambda: ListConfig([]))


@dataclass
class Simulation:
    fleet: pd.DataFrame
    charging_posts: pd.DataFrame
    matcher: Matcher
    allocator: Callable
    output: Callable
    objective: Optional[Callable] = None

    def run(self):
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
    def load(cls, settings: Union[Text, Path, IO, Mapping[Text, Any]]) -> Simulation:
        from omegaconf import OmegaConf
        from io import StringIO
        from evosim.fleet import register_fleet_generator
        from evosim.matchers import factory as matcher_factory
        from evosim.charging_posts import register_charging_posts_generator
        from evosim.allocators import register_allocator
        from evosim.objectives import register_objective

        if isinstance(settings, (Text, Path, StringIO, IO)):
            inputs = OmegaConf.load(settings)
        else:
            inputs = OmegaConf.create(settings)
        inputs = OmegaConf.merge(OmegaConf.structured(SimulationConfig), inputs)

        fleet = register_fleet_generator.factory(inputs.fleet)
        charging_posts = register_charging_posts_generator.factory(
            inputs.charging_posts
        )
        matcher = matcher_factory(inputs.matcher)
        allocator = register_allocator.factory(inputs.allocator)
        objective = None
        if inputs.objective:
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
