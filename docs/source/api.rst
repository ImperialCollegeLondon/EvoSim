=======================
Developer API catalogue
=======================

.. contents:: :depth: 3

Charging Posts
==============

Enumerations
------------

.. autoclass:: evosim.charging_posts.Chargers
    :members:
    :undoc-members:

.. autoclass:: evosim.charging_posts.Sockets
    :members:
    :undoc-members:

.. autoclass:: evosim.charging_posts.Status
    :members:
    :undoc-members:

Functions
---------

.. autofunction:: evosim.charging_posts.register_charging_posts_generator

.. autofunction:: evosim.charging_posts.charging_posts_from_file

.. autofunction:: evosim.charging_posts.random_charging_posts

.. autofunction:: evosim.charging_posts.to_sockets

.. autofunction:: evosim.charging_posts.to_chargers

.. autofunction:: evosim.charging_posts.to_status

.. autofunction:: evosim.charging_posts.to_charging_posts

.. autofunction:: evosim.charging_posts.is_charging_posts

Data
----

.. autoclass:: evosim.charging_posts.ChargingPostsSchema
    :members:
    :undoc-members:

.. autodata:: evosim.charging_posts.MAXIMUM_CHARGER_POWER


Electric Vehicles
=================

Enumerations
------------

.. autoclass:: evosim.fleet.Models
    :members:
    :undoc-members:

Functions
---------

.. autofunction:: evosim.fleet.register_fleet_generator

.. autofunction:: evosim.fleet.fleet_from_file

.. autofunction:: evosim.fleet.random_fleet

.. autofunction:: evosim.fleet.to_models

.. autofunction:: evosim.fleet.is_fleet

.. autofunction:: evosim.fleet.to_fleet

Data
----

.. autoclass:: evosim.fleet.FleetSchema
    :members:
    :undoc-members:


Matchers
========

.. autofunction:: evosim.matchers.register_matcher

.. autofunction:: evosim.matchers.factory

.. autofunction:: evosim.matchers.socket_compatibility

.. autofunction:: evosim.matchers.charger_compatibility

.. autofunction:: evosim.matchers.distance

.. autofunction:: evosim.matchers.match_all_to_all

.. autofunction:: evosim.matchers.classify

.. autofunction:: evosim.matchers.classify_with_fleet

.. autofunction:: evosim.matchers.to_namedtuple


Objectives
==========

.. autofunction:: evosim.objectives.register_objective

.. autofunction:: evosim.objectives.distance

.. autofunction:: evosim.objectives.haversine_distance

Allocators
==========

.. autofunction:: evosim.allocators.register_allocator

.. autofunction:: evosim.allocators.random_allocator

.. autofunction:: evosim.allocators.greedy_allocator

Simulation
==========

Classes
-------

.. autoclass:: evosim.simulation.SimulationConfig
    :members:
    :undoc-members:

.. autoclass:: evosim.simulation.Simulation
    :members:
    :undoc-members:

.. autodata:: evosim.simulation.SimulationVar

Functions
---------

.. autofunction:: evosim.simulation.simulation_output_factory

.. autofunction:: evosim.simulation.register_simulation_output

.. autofunction:: evosim.simulation.construct_input

.. autofunction:: evosim.simulation.construct_factories

.. autofunction:: evosim.simulation.load_initial_imports

Data
----

.. autodata:: evosim.simulation.INPUT_DEFAULTS

IO
==

Functions
---------

.. autofunction:: evosim.io.read_stations

.. autofunction:: evosim.io.read_sockets

.. autofunction:: evosim.io.read_charging_points

.. autofunction:: evosim.io.output_via_pandas

.. autofunction:: evosim.io.as_sockets

.. autofunction:: evosim.io.as_stations

Data
----

.. autodata:: evosim.io.EXEMPLARS


AutoConf
========

.. autoclass:: evosim.autoconf.AutoConf
    :members:
    :special-members: __call__

.. autofunction:: evosim.autoconf.evosim_registries

Constants
=========

.. autodata:: evosim.constants.LONDON_LATITUDE

.. autodata:: evosim.constants.LONDON_LONGITUDE

.. autodata:: evosim.constants.EARTH_RADIUS_KM
