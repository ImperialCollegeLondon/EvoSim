#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import List, Optional, Text, Union

import click

from evosim import __version__

DEFAULT_FILENAME = "evosim.yml"

EXAMPLES = """
# Examples

The following commands print the final merged inputs rather than run the simulation.
Drop ``-p`` and the simulation should run.

The defaults are given by

> evosim -p

We can override some or all of these inputs by specifying a yaml file to read from. The
file can contain any or all the sections printed above (though we recommend not
overrinding "root" and "cwd").

> evosim -p -i evosim.yml

We can also override some inputs directly on the command-line using omegaconf's dot
syntax:

> evosim -p fleet.name=random fleet.n=5

or

> evosim -p -i evosim.yml fleet.name=random fleet.n=5

In the latter case, the dot-syntax takes priority over the contents of evosim.yml.

The keyword "cwd" refers to the current working directory (from which the command evosim
is started). The keyword "root" refers to the directory where the input file (`-i`)
resides, or to the current working directory if no file is given.
"""


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


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "--input",
    "-i",
    "input_file",
    type=click.Path(exists=False, file_okay=True, dir_okay=True, readable=True),
    help=(
        "Path to an input file or a directory. "
        f"If the latter, a file {DEFAULT_FILENAME} must exiust."
    ),
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
@click.option(
    "--print-interpolated",
    is_flag=True,
    help="Prints input settings to the standard out, including variable interpolation.",
)
@click.option(
    "--help-usage", is_flag=True, help="A few examples showing how to call evosim."
)
@click.option(
    "--help-parameters", help="Print parameter description to screen.", is_flag=True
)
@click.version_option(version=__version__)
@click.argument("inputs", nargs=-1)
def evosim(
    input_file: Optional[Union[Text, Path]],
    inputs: List[Text],
    print_yaml: bool,
    print_interpolated: bool,
    help_usage: bool,
    help_parameters: bool,
):
    """EvoSim simulation.

    Evosim accepts its inputs from three locations with increasing priorities: (i) hard-
    coded defaults, (ii) an optional input file specified on the command-line, (iii) any
    number of modifiers also on the command-line. The latter follow the dot syntax
    implemented by omegaconf. See `--help-usage` and `--help-parameters` for more
    information.
    """
    from io import StringIO
    from omegaconf import OmegaConf
    from yaml import dump
    from evosim.simulation import (
        Simulation,
        construct_input,
        load_initial_imports,
        construct_factories,
    )

    if help_usage:
        click.echo(EXAMPLES)
        return

    if input_file is not None and input_file != "-":
        input_file = Path(input_file)
        if input_file.is_dir():
            input_file /= DEFAULT_FILENAME
        if not input_file.exists():
            click.echo(f"No file {input_file} found, aborting.", err=True)
            return

    if input_file:
        with click.open_file(str(input_file), "r") as fileobj:
            settings = construct_input(fileobj, overrides=OmegaConf.from_cli(inputs))
    else:
        settings = construct_input(overrides=OmegaConf.from_cli(inputs))
    load_initial_imports(settings.imports)
    factories = construct_factories(settings, materialize=False)

    if help_parameters:
        click.echo(get_options())
        return

    if print_interpolated:
        result = OmegaConf.to_container(settings, resolve=True)
        result.pop("cwd")
        result.pop("root")
        click.echo(dump(result))
        return

    if print_yaml:
        stream = StringIO()
        OmegaConf.save(settings, stream)
        stream.seek(0)
        click.echo(stream.read())
        return

    simulation = Simulation(**{k: v() for k, v in factories.items()})
    simulation()
