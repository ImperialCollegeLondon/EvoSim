=======================
Developer API catalogue
=======================

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

Functions
---------

.. autofunction:: evosim.charging_posts.random_charging_posts

Electric Vehicles
=================

Enumerations
------------

.. autoclass:: evosim.fleet.Models
    :members:
    :undoc-members:

Functions
---------

.. autofunction:: evosim.fleet.random_fleet


Matchers
========

Functions
---------

.. autofunction:: evosim.matchers.factory

.. autofunction:: evosim.matchers.charging_post_availability

.. autofunction:: evosim.matchers.socket_compatibility

.. autofunction:: evosim.matchers.charger_compatibility

.. autofunction:: evosim.matchers.distance

.. autofunction:: evosim.matchers.classify

.. autofunction:: evosim.matchers.classify_with_fleet

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

