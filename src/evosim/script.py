#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Text, Union

import click

DEFAULT_FILENAME = "evosim.yml"


def get_default_yaml(name):
    from evosim.simulation import INPUT_DEFAULTS
    from omegaconf import OmegaConf
    from io import StringIO

    stream = StringIO()
    OmegaConf.save({str(name): INPUT_DEFAULTS[name]}, stream)
    stream.seek(0)
    return stream.read()


def get_options():
    import evosim

    registries = dict(
        fleet=evosim.fleet.register_fleet_generator,
        charging_posts=evosim.charging_posts.register_charging_posts_generator,
        matcher=evosim.matchers.register_matcher,
        objective=evosim.objectives.register_objective,
        allocator=evosim.allocators.register_allocator,
        outputs=evosim.simulation.register_simulation_output,
    )
    result = ""
    for yaml_name, registry in registries.items():
        name = registry.name.title()
        result += name + "\n" + "-" * len(name) + "\n\n"
        result += "Defaults to:\n\n~~~yaml\n"
        result += get_default_yaml(yaml_name).strip()
        result += "\n~~~\n\n"
        result += registry.parameter_docs.rstrip() + "\n\n"
    return result.rstrip()


@click.command()
@click.option(
    "--describe-options", help="Print option description to screen", is_flag=True
)
@click.option(
    "--input",
    "-i",
    "input_file",
    type=click.Path(exists=False, file_okay=True, dir_okay=True, readable=True),
    help=f"Path to the input file. Defaults to {DEFAULT_FILENAME}",
    default=DEFAULT_FILENAME,
)
def main(input_file: Union[Text, Path], describe_options: bool):
    """EvoSim simulation."""
    from evosim.simulation import Simulation

    if describe_options:
        click.echo(get_options())
        return

    input_file = Path(input_file)
    if input_file.is_dir():
        input_file /= DEFAULT_FILENAME
    if not input_file.is_file():
        click.echo(f"Could not read or find input file {input_file}", err=True)
        return

    simulation = Simulation.load(input_file)
    simulation.run()


if __name__ == "__main__":
    main()
