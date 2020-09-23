Allocators
==========

Allocators are algorithms that allocate electric vehicles to charging points. They will
generally take as input arguments a dataframe of electric vehicles, a dataframe of
charging points. They may also accept a matcher function from :py:mod:`evosim.matchers`,
as well as an objective function from :py:mod:`evosim.objectives`.
