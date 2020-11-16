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
    from evosim.autoconf import evosim_registries

    result = ""
    for yaml_name, registry in evosim_registries().items():
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
    from evosim.simulation import Simulation, construct_input, load_initial_imports

    input_file = Path(input_file)
    if input_file.is_dir():
        input_file /= DEFAULT_FILENAME

    if describe_options:
        settings = construct_input(input_file if input_file.exists() else {})
        load_initial_imports(settings.imports)
        click.echo(get_options())
        return

    if not input_file.is_file():
        click.echo(f"Could not read or find input file {input_file}", err=True)
        return

    simulation = Simulation.load(input_file)
    simulation()


if __name__ == "__main__":
    main()
