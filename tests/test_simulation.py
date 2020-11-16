from typing import List

import pandas as pd


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
    sim.run()

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
        "matcher",
        "objective",
    }
