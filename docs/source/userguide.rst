User Guide
==========

.. contents:: table of contents

Usage
-----

EvoSim exposes a command-line script, :command:`evosim`. It can be accessed in one of
two ways:

- as a python module:

    .. code-block:: bash

        python -m evosim --help


- as a standalone script:

    .. code-block:: bash

        evosim --help


The output should look something like:

.. testsetup:: cli,cli_help

    def run_cli(args):
        from click.testing import CliRunner
        from evosim.script import evosim

        runner = CliRunner()
        return runner.invoke(evosim, args)

.. testcode:: cli_help
    :hide:

    runner = run_cli(["--help"])
    assert runner.exit_code == 0
    print(runner.stdout)


.. testoutput:: cli_help
    :options: +NORMALIZE_WHITESPACE

    Usage: evosim [OPTIONS] [INPUTS]...

      EvoSim simulation.

      Evosim accepts its inputs from three locations with increasing priorities:
      (i) hard- coded defaults, (ii) an optional input file specified on the
      command-line, (iii) any number of modifiers also on the command-line. The
      latter follow the dot syntax implemented by omegaconf. See `--help-usage`
      and `--help-parameters` for more information.

    Options:
      -i, --input PATH      Path to an input file or a directory. If the latter, a
                            file evosim.yml must exiust.

      -p, --print-yaml      Prints input settings to the standard out.

                            This option is mainly useful to ensure that the settings
                            are correctly specified, inluding defaults and command-
                            line arguments.

      --print-interpolated  Prints input settings to the standard out, including
                            variable interpolation.

      --help-usage          A few examples showing how to call evosim.
      --help-parameters     Print parameter description to screen.
      --version             Show the version and exit.
      -h, --help            Show this message and exit.


The simulation command-line takes optional arguments as input. Notably, it can spit-out
a few examples showcasing how to call :command:`evosim` (``--help-usage``), as was as all
available parameters (``--help-parameters``). The same information is described in more
details below.

:command:`evosim` can also print out the settings used in a simulation, with the ``-p``
argument (or ``--print-yaml``).  As will be seen in a second, :command:`evosim` merges
inputs from several locations. This argument helps to ensure exactly what
:command:`evosim` will run.

If none of ``--help``, ``--help-usage``, ``--help-parameters``, ``--print-yaml``,
``print-interpolated`` are given, then :command:`evosim` will run the simulation.

:command:`evosim` takes its input from three different locations:

#. In-code, hard-coded defaults
#. An optional input file. It will override the hard-coded defaults.
#. Command-line arguments using `OmegaConf <https://github.com/omry/omegaconf>`__'s
   `dot-syntax
   <https://omegaconf.readthedocs.io/en/2.0_branch/usage.html#from-a-dot-list>`__. It
   will override both the defaults and the content of the optional file.

Using ``-p``, we can take a first look at the inputs, and especially at the hard-coded
defaults:

.. code-block:: bash

    evosim -p

.. testcode:: cli
    :hide:

    print(run_cli(["-p"]).stdout)

.. testoutput:: cli
    :options: +NORMALIZE_WHITESPACE

    fleet:
      name: from_file
      path: ${cwd}/fleet.csv
    charging_posts:
      name: from_file
      path: ${cwd}/charging_posts.csv
    matchers:
    - socket_compatibility
    objective:
      name: haversine_distance
    allocator:
      name: greedy
    outputs: []
    imports: []
    ...
    ...

Generally, the output follows the `YAML <https://yaml.org/>`__ format, including node
and environment variable interpolation, thanks to `omegaconf
<https://omegaconf.readthedocs.io/en/2.0_branch/usage.html#variable-interpolation>`__ It
specifies a simulation which reads an input fleet and table of charging posts from two
CSV files.  These have to be provided by the user for the simulation to run. The other
inputs are include a default matcher that only compare the sockets and an allocator
algorithm which default to the greedy algorithm. The other sections will not be used
here. They are described in the next part of this manual.

There are two additional keywords, ``root`` and ``cwd``. Although they could be
specified on the input file or on the command-line, we recommend leaving them to the
their default values.

    ``cwd``
        points to the current working directory where :command:`evosim` is launched.

    ``root``
        points to the directory where the optional input file is located, if it is
        specified (with ``-i path/to/file.yml``), or to the current working directory.

Both are useful to specify input and output file locations. Nominally, ``cwd`` is not
necessary since :command:`evosim` will default relative path to start from the current
working directory. But it does make it nicely explicit.

Lets specify an :download:`input file <generated/examples/partial_override.yaml>` to
override the fleet and infrastructure generation parts, as well as the outputs:

.. literalinclude:: generated/examples/partial_override.yaml
    :language: yaml

.. warning::

    Paths in :command:`evosim` should be given with ``/`` on unixes and ``\`` on
    windows.

In this example, we tell :command:`evosim` to generate a random fleet with a restricted
number of socket types. We also tell it to generate a random table of charging posts
with the same restricted set of sockets. However, rather than specify the set of sockets
twice (and cut down on copy-paste errors), we refer to the first definition via variable
interpolation. We also use a shortcut in the ``outputs``: ``- stats`` is automatically
translated to ``- name: stats``. The shortcut only works in simple cases where no other
keywords need be specified.

.. note::

    For unix users, ``-i -`` will read from the standard input rather than a file.
    CTRL-D once or twice should terminate the input and start the simulation.

.. testcode:: cli
    :hide:
    
    from evosim.io import EXEMPLARS
    path = EXEMPLARS["examples"] / "partial_override.yaml"
    result = run_cli(["-p", "-i", str(path)])
    assert result.exit_code == 0
    print(result.stdout)

The integrated input looks like this (``evosim -p -i partial_override.yaml``):

.. testoutput:: cli
    :options: +NORMALIZE_WHITESPACE

    fleet:
      name: random
      'n': 10
      socket_types:
      - TYPE1
      - TYPE2
    charging_posts:
      name: random
      'n': 100
      socket_types: ${fleet.socket_types}
    matchers:
    - socket_compatibility
    objective:
      name: haversine_distance
    allocator:
      name: greedy
    outputs:
    - stats
    ...
    ...
    ...


Finally we can also override both the defaults and the optional input file using a `dot`
syntax, as follows:

.. code-block:: bash

    evosim -i partial_override fleet.n=110 fleet.seed=1 charging_posts.seed=2

.. testcode:: cli
    :hide:

    from evosim.io import EXEMPLARS
    path = EXEMPLARS["examples"] / "partial_override.yaml"
    result = run_cli(
       ["-i", str(path), "fleet.n=110", "fleet.seed=1", "charging_posts.seed=2"]
    )
    assert result.exit_code == 0
    print(result.stdout)

.. testoutput:: cli
    :options: +NORMALIZE_WHITESPACE

    Unallocated vehicles: 10/110
    Allocated vehicles: 100/110
    Final distances (in kilometers):
        * mean: 13.86
        * stdev: 15.04
        * skew: 2.35
        * quantile(25%): 4.74
        * quantile(50%): 9.24
        * quantile(75%): 15.30
        * min: 0.52
        * max: 83.15

Above, we ran :command:`evosim` while overriding the size of the fleet. The statistics
printed at the end of the run shows indeed a 110 vehicles were generated. We also added
the optional ``seed`` keywords to the random generation, ensuring that the results are
exactly reproducible.


Input file definition
---------------------

EvoSim's input file uses the `YAML format <https://yaml.org/>`__. Here is a typical
example:

.. literalinclude:: generated/examples/simple.yaml
    :language: yaml


.. testcode:: simple_yaml_smoketest
    :hide:

    from evosim.simulation import Simulation
    from evosim.io import EXEMPLARS

    Simulation.load(EXEMPLARS["examples"] / "simple.yaml")()

.. testoutput:: simple_yaml_smoketest

    Unallocated vehicles: ...
    Allocated vehicles: ...
    Final distances (in kilometers):
        * mean: ...
        * stdev: ...
        * skew: ...
        * quantile(25%): ...
        * quantile(50%): ...
        * quantile(75%): ...
        * min: ...
        * max: ...

The file consists of six main sections with indented content each:

    - ``fleet`` defines how to create or read a fleet
    - ``charging_posts`` defines how to create or read a table of charging posts
    - ``allocator`` defines the allocation algorithm to use
    - ``objective`` an optional objective function for allocation algorithms that
      require one (the greedy allocation algorithm does not)
    - ``matchers`` defines a list of constraints that define whether an electric vehicle
      can be assigned to a charging post. The match is positive when all constraints are
      met.
    - ``outputs`` defines a list of outputs to compute and print to screen or save to
      disk
    - ``imports`` defines a list of python files to load prior to generating the
      simulation. Users can drop custom output functions, allocation algorithms,
      matchers, objectives, fleet and charging post generation functions into these
      files and then use them in their models.

The first four consist of a single "thing" each. However the last two define lists of
constraints and outputs. That's why the last two contain items which start with ``-``
(indicating a list in YAML parlance), whereas the first four are sets of keywords and
values separated by ``:`` (indicating a dictionary in YAML parlance).

EvoSim reads a YAML file which can reference itself as well as environment variables, as
shown in `omegaconf's documentation
<https://omegaconf.readthedocs.io/en/latest/usage.html#variable-interpolation>`__.
Additionally, it allows for two extra interpolations:

- ``${root}``: indicates the directory where the YAML file exists. That way, users can
  drop the YAML file defining the simulation as well as files defining the fleet or the
  charging posts in the same directory (or folder) or in a subdirectory. Similarly, the
  location of output files can be specified to sit next to the simulation input in the
  same manner.
- ``${cwd}``: points to the current working directory. Relative paths can also be given
  with the same result.

The inputs are checked for correctness as much as possible and as early as possible.
For instance, inputing a string ``"hello"`` where an integer is expected will likely
result in an immediate error. The descriptions include the expected type of each
keyword.


Fleet Keywords
~~~~~~~~~~~~~~

Defining the fleet section is optional and defaults to reading a "fleet.csv" file in the
directory where the simulation input file is located:

.. include:: generated/yaml/fleet-generation.rst

Charging Posts Keywords
~~~~~~~~~~~~~~~~~~~~~~~

Defining the charging posts section is optional and defaults to reading a
"charging_posts.csv" file in the directory where the simulation input file is located:

.. include:: generated/yaml/charging-posts-generation.rst

Allocator Keywords
~~~~~~~~~~~~~~~~~~

The allocation section is optional and default to using the greedy allocation algorithm.

.. include:: generated/yaml/allocator.rst

Matcher Keywords
~~~~~~~~~~~~~~~~

Defining the matcher is optional and defaults to:

.. include:: generated/yaml/matcher.rst

Objective Keywords
~~~~~~~~~~~~~~~~~~

The objective section is optional and defaults to using the Haversine distance:

.. include:: generated/yaml/objective.rst

Outputs Keywords
~~~~~~~~~~~~~~~~

Defining a list of outputs is optional and defaults to no outputs:

.. include:: generated/yaml/outputs.rst


Imports section
~~~~~~~~~~~~~~~

The ``imports`` section enable users to register their own custom operations with EvoSim
and specify them in the input file (or from the command-line). The custom operations
must be valid python functions with the right signature and decorated with the
corresponding registry. For instance, if a users drops custom operations in a file
`my_ops.py`, then EvoSim must be told about it with:

.. code-block:: YAML

    imports:
    - ${cwd}/my_ops.py

More information about custom operations can be found in :ref:`evosim-simulation`.
