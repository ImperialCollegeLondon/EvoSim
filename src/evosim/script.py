#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import List, Text, Union, Optional

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
    help=f"Path to the input file. Defaults to {DEFAULT_FILENAME} if it exists.",
    default=None,
)
@click.option(
    "--print-yaml",
    "-p",
    is_flag=True,
    help="""Prints input settings to the standard out.

    This option is mainly useful to ensure that the settings are correctly specified,
    inluding defaults and command-line arguments.
    """,
)
@click.argument("inputs", nargs=-1)
def main(
    input_file: Optional[Union[Text, Path]],
    describe_options: bool,
    print_yaml: bool,
    inputs: List[Text],
):
    """EvoSim simulation."""
    from io import StringIO
    from omegaconf import OmegaConf
    from evosim.simulation import Simulation, construct_input, load_initial_imports

    if input_file is not None:
        input_file = Path(input_file)
        if input_file.is_dir():
            input_file /= DEFAULT_FILENAME
    elif Path(DEFAULT_FILENAME).is_file():
        input_file = Path(DEFAULT_FILENAME)

    settings = construct_input(
        input_file if input_file else {}, overrides=OmegaConf.from_cli(inputs)
    )
    load_initial_imports(settings.imports)

    if describe_options:
        click.echo(get_options())
        return

    if print_yaml:
        stream = StringIO()
        OmegaConf.save(settings, stream)
        stream.seek(0)
        click.echo(stream.read())
        return

    simulation = Simulation.load(settings)
    simulation()


if __name__ == "__main__":
    main()
