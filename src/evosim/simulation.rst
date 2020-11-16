Simulation and simulation outputs
=================================

The :py:class:`~evosim.simulation.Simulation` is a small wrapper around Evosim's
algorithms to load a simulation from file, run it, and save some outputs. It can be
instantiated quite simply from a yaml file:

.. testcode:: simple_simulation

    from io import StringIO
    from evosim.simulation import Simulation

    yaml = StringIO(
        """
        fleet:
            name: random
            n: 5
        charging_posts:
            name: random
            n: 5
        matcher: socket_compatibility
        allocator:
            name: random
    """
    )
    yaml.seek(0)

    simulation = Simulation.load(yaml)
    assert len(simulation.fleet) == 5
    assert len(simulation.charging_posts) == 5

Above, simulation is instantiated from a yaml in memory. It would work just as well if
provided with a path to a yaml file, or indeed with a dictionary or an OmegaConf object.
The simulation object holds a number of objects, e.g. fleet, charging_posts, allocation
algorithm. All are constructed from input using registered factory functions. The
registries of interest include:

* :py:func:`~evosim.fleet.register_fleet_generator`: reads a fleet from file or creates
  a random one.
* :py:func:`~evosim.charging_posts.register_charging_posts_generator`: reades a charging
  posts from file or creates a random one.
* :py:func:`~evosim.objectives.register_objective`: objective to optimize
  during the allocation algorithm
* :py:func:`~evosim.matchers.register_matcher`: constraints to apply during the
  allocation
* :py:func:`~evosim.allocators.register_allocator`: allocation algorithm to use
* :py:func:`~evosim.simulation.register_simulation_output`: outputs of the algorithm to
  save or print to screen.

We will see an example of registering a simulation output below. But first lets show how
to run the simulation itself.

.. testcode:: simple_simulation

    allocated_fleet = simulation();

That's it! This simulation has no outputs (none were specified) outside of the allocated
fleet returned by the allocator algorithm. So let's try and print something to the
standard out (the screen).  We will use ``stats`` which prints simple statistics and
create function that prints out the unallocated vehicles:


.. testcode:: simulation_with_output

    from io import StringIO
    from evosim.simulation import Simulation, register_simulation_output

    @register_simulation_output
    def unallocated_vehicles(simulation, result, columns=()):
        with pd.option_context(
            "display.precision", 2,
            "display.max_categories", 8,
            "display.max_rows", 100,
            "display.max_columns", 100,
        ):
            unallocated = (
                result.loc[result.allocation.isna()].drop(columns=["allocation"])
            )
            columns = columns or unallocated.columns
            print(unallocated[list(columns)])

The function ``unallocated_vehicles`` above simply prints the unallocated vehicles to
the standard output. Just for show, it also takes a ``columns`` argument, However, it
could also output it to file, or even upload somewhere.  Once it is registered via the
decorator `@register_simulation_output`, it can be accessed from the input file as
follows:

.. testcode:: simulation_with_output

    yaml = StringIO(
        """
        fleet:
            name: random
            n: 100
            seed: 1
        charging_posts:
            name: random
            n: 100
            seed: 2
        matcher: socket_compatibility
        allocator:
            name: random
            seed: 3
        outputs:
            - stats
            - name: unallocated_vehicles
              columns: [model, dest_lat, dest_long]
        """
    )
    yaml.seek(0)

    simulation = Simulation.load(yaml)


The ``stats`` output does not take an argument, so we just name in the list of outputs.
The ``unallocated_vehicles`` output we want to provide with an argument other than the
default. So it is provided in long-form as a dictionary. We are now in a position to run
the simulation:

.. testcode:: simulation_with_output

    simulation()


.. testoutput:: simulation_with_output
    :options: +NORMALIZE_WHITESPACE

    Unallocated vehicles: 19/100
    Allocated vehicles: 81/100
    Final distances (in kilometers):
        * mean: 49.47
        * stdev: 29.69
        * skew: 0.71
        * quantile(25%): 23.68
        * quantile(50%): 44.73
        * quantile(75%): 64.81
        * min: 7.60
        * max: 126.42

                                 model  dest_lat  dest_long
    vehicle
    1              MERCEDES_BENZ_E350E     51.50       1.18
    4                        BMW_225XE     51.44       0.74
    5                       BMW_X5_40E     51.51      -0.12
    11          HYUNDAI_IONIQ_ELECTRIC     51.50      -0.20
    25                   TESLA_MODEL_X     51.28       0.40
    26       MITSUBISHI_OUTLANDER_PHEV     51.54      -0.04
    29                 SMART_EQ_FORTWO     51.29      -0.22
    31                     NISSAN_LEAF     51.51       0.24
    44                      BMW_X5_40E     51.47       0.75
    71           VOLVO_V90_TWIN_ENGINE     51.55      -0.03
    73           VOLVO_V90_TWIN_ENGINE     51.41       0.91
    79             VOLKSWAGEN_GOLF_GTE     51.62       0.30
    80             TOYOTA_PRIUS_PLUGIN     51.41       1.06
    81           VOLVO_V90_TWIN_ENGINE     51.68       0.23
    92       MINI_COUNTRYMAN_COOPER_SE     51.42      -0.14
    96                         UNKNOWN     51.62       1.03
    97                  CITROEN_C_ZERO     51.46      -0.26
    98                 SMART_EQ_FORTWO     51.37       0.89
    99                       BMW_225XE     51.38       0.68
