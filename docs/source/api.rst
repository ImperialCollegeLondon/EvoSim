=======================
Developer API catalogue
=======================

Supply
======

Enumerations
------------

.. autoclass:: evosim.supply.Chargers
    :members:
    :undoc-members:

.. autoclass:: evosim.supply.Sockets
    :members:
    :undoc-members:

Functions
---------

.. autofunction:: evosim.supply.random_charging_points

Electric Vehicles
=================

Enumerations
------------

.. autoclass:: evosim.electric_vehicles.Models
    :members:
    :undoc-members:

Functions
---------

.. autofunction:: evosim.electric_vehicles.random_electric_vehicles


Matchers
========

Functions
---------

.. autofunction:: evosim.matchers.factory

.. autofunction:: evosim.matchers.charging_point_availability

.. autofunction:: evosim.matchers.socket_compatibility

.. autofunction:: evosim.matchers.charger_compatibility

.. autofunction:: evosim.matchers.distance

Objectives
==========

Functions
---------

.. autofunction:: evosim.objectives.distance

.. autofunction:: evosim.objectives.haversine_distance

Allocators
==========

Functions
---------

.. autofunction:: evosim.allocators.random_allocator

Constants
=========

.. autodata:: evosim.constants.LONDON_LATITUDE

.. autodata:: evosim.constants.LONDON_LONGITUDE

.. autodata:: evosim.constants.EARTH_RADIUS_KM

