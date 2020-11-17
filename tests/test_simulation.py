from typing import List

import pandas as pd
from pytest import fixture, mark, raises


@fixture
def chdir_tmp(tmp_path):
    from pathlib import Path
    from os import chdir

    path = Path.cwd()
    chdir(tmp_path)
    yield
    chdir(path)


def test_simplest_load():
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
        allocator:
            name: random
    """
    )
    yaml.seek(0)

    sim = Simulation.load(yaml)
    assert len(sim.fleet) == 5
    assert len(sim.charging_posts) == 5


def test_shortcut_load():
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
        allocator: random
    """
    )
    yaml.seek(0)

    sim = Simulation.load(yaml)
    assert len(sim.fleet) == 5
    assert len(sim.charging_posts) == 5


def test_run():
    from io import StringIO
    from evosim.simulation import Simulation, register_simulation_output

    yaml = StringIO(
        """
        fleet:
            name: random
            n: 5
        charging_posts:
            name: random
            n: 5
        allocator: random
        outputs:
            - my_output
    """
    )
    yaml.seek(0)

    allocated_fleet: List[pd.DataFrame] = []

    @register_simulation_output
    def my_output(simulation, result):
        allocated_fleet.append(result)

    sim = Simulation.load(yaml)
    sim()

    assert len(allocated_fleet) == 1
    assert "allocation" in allocated_fleet[0].columns


def test_defaults_follow_structured_config():
    from evosim.simulation import SimulationConfig, INPUT_DEFAULTS
    from omegaconf import OmegaConf

    schema = OmegaConf.structured(SimulationConfig)
    defaults = OmegaConf.merge(schema, INPUT_DEFAULTS)

    assert set(defaults) == {
        "fleet",
        "charging_posts",
        "allocator",
        "matchers",
        "objective",
        "imports",
        "outputs",
        "root",
        "cwd",
    }


def test_fail_on_missing_output(tmp_path):
    from evosim.simulation import Simulation
    from omegaconf.errors import KeyValidationError

    inputs = dict(
        fleet=dict(name="random", n=5),
        charging_posts=dict(name="random", n=10),
        outputs=["dummy"],
    )
    with raises(KeyValidationError):
        Simulation.load(inputs)


@mark.usefixtures("chdir_tmp")
def test_imports():
    from textwrap import dedent
    from pathlib import Path
    from evosim.simulation import Simulation

    inputs = dict(
        fleet=dict(name="random", n=5),
        charging_posts=dict(name="random", n=10),
        outputs=[dict(name="dummy", path="${root}/output")],
        imports=["${root}/evosim.py"],
    )

    Path("evosim.py").write_text(
        dedent(
            """
            from evosim.simulation import register_simulation_output

            @register_simulation_output
            def dummy(simulation, result, path="output"):
                from pathlib import Path
                Path(path).write_text("hello!")
            """
        )
    )

    simulation = Simulation.load(inputs)

    assert not Path("output").exists()
    simulation()
    assert Path("output").exists()
    assert Path("output").read_text() == "hello!"
