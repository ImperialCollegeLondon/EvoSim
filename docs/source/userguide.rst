User Guide
==========

.. contents:: table of contents


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

    Simulation.load(EXEMPLARS["examples"] / "simple.yaml").run()

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
    - ``matcher`` defines a list of constraints that define whether an electric vehicle
      can be assigned to a charging post
    - ``outputs`` defines a list of outputs to compute and print to screen or save to
      disk

The first four consist of a single "thing" each. However the last two define lists of
constraints and ouputs. That's why the last two contain items which start with ``-``
(indicating a list in YAML parlance), whereas the first four are sets of keywords and
values separated by ``:`` (indicating a dictionary in YAML parlance).

EvoSim reads a YAML file which can reference itself as well as environment variables, as
shown in `omegaconf's documentation
<https://omegaconf.readthedocs.io/en/latest/usage.html#variable-interpolation>`__.
Additionally, it allows for two extra interpolations:

- ``${root}``: indicates the directory where the YAML file exists. That way, users can
  drop the yaml file defining the simulation as well as files defining the fleet or the
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
--------------

Defining the fleet section is optional and defaults to reading a "fleet.csv" file in the
directory where the simulation input file is located:

.. include:: generated/yaml/fleet-generation.rst

Charging Posts Keywords
-----------------------

Defining the charging posts section is optional and defaults to reading a
"charging_posts.csv" file in the directory where the simulation input file is located:

.. include:: generated/yaml/charging-posts-generation.rst

Allocator Keywords
------------------

The allocation section is optional and default to using the greedy allocation algorithm.

.. include:: generated/yaml/allocator.rst

Matcher Keywords
----------------

Defining the matcher is optional and defaults to:

.. include:: generated/yaml/matcher.rst

Objective Keywords
------------------

The objective section is optional and defaults to using the haversine distance:

.. include:: generated/yaml/objective.rst

Outputs Keywords
----------------

Defining a list of outputs is optional and defaults to no outputs:

.. include:: generated/yaml/output.rst
