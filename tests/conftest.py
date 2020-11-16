import pandas as pd
from pytest import fixture


@fixture
def rng(request):
    from numpy.random import default_rng

    return default_rng(getattr(request.config.option, "randomly_seed", None))


@fixture(autouse=True)
def warnings_as_errors(request):
    from warnings import simplefilter
    from platform import system

    pd.set_option("mode.chained_assignment", "raise")
    simplefilter("error", FutureWarning)
    simplefilter("error", PendingDeprecationWarning)
    # sklearn uses deprecated module on windows
    if (
        request.module.__name__ != "test_allocators"
        or not request.node.name.startswith("test_greedy_allocator")
        or system() != "Windows"
    ):
        simplefilter("error", DeprecationWarning)


@fixture(autouse=True)
def save_evosim_registries():
    from copy import copy
    from evosim.autoconf import evosim_registries

    saves = {
        k: (copy(v.configs), copy(v.factories)) for k, v in evosim_registries().items()
    }

    yield

    for name, registry in evosim_registries().items():
        registry.configs = saves[name][0]
        registry.factories = saves[name][1]
