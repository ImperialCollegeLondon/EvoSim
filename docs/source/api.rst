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

Functions
---------

.. autofunction:: evosim.charging_posts.random_charging_posts

.. autofunction:: evosim.charging_posts.to_sockets

.. autofunction:: evosim.charging_posts.to_chargers

.. autofunction:: evosim.charging_posts.to_charging_posts

.. autofunction:: evosim.charging_posts.is_charging_posts

Data
----

.. autodata:: evosim.charging_posts.CHARGING_POSTS_SCHEMA


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

.. autofunction:: evosim.matchers.factory

.. autofunction:: evosim.matchers.charging_post_availability

.. autofunction:: evosim.matchers.socket_compatibility

.. autofunction:: evosim.matchers.charger_compatibility

.. autofunction:: evosim.matchers.distance

.. autofunction:: evosim.matchers.match_all_to_all

.. autofunction:: evosim.matchers.classify

.. autofunction:: evosim.matchers.classify_with_fleet

.. autofunction:: evosim.matchers.to_namedtuple


Objectives
==========

.. autofunction:: evosim.objectives.distance

.. autofunction:: evosim.objectives.haversine_distance

Allocators
==========

.. autofunction:: evosim.allocators.random_allocator

.. autofunction:: evosim.allocators.greedy_allocator

Constants
=========

.. autodata:: evosim.constants.LONDON_LATITUDE

.. autodata:: evosim.constants.LONDON_LONGITUDE

.. autodata:: evosim.constants.EARTH_RADIUS_KM
