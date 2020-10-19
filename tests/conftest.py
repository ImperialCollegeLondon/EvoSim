import pandas as pd
from pytest import fixture


@fixture
def rng(request):
    from numpy.random import default_rng

    return default_rng(getattr(request.config.option, "randomly_seed", None))


@fixture(autouse=True)
def warnings_as_errors():
    from warnings import simplefilter

    pd.set_option("mode.chained_assignment", "raise")
    simplefilter("error", FutureWarning)
    simplefilter("error", DeprecationWarning)
    simplefilter("error", PendingDeprecationWarning)
