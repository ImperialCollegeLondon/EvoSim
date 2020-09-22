def test_charging_point_availability():
    from evosim.matchers import charging_point_availability
    from dataclasses import dataclass

    @dataclass
    class ChargingPoint:
        occupancy: int = 0
        capacity: int = 1

    assert charging_point_availability(None, ChargingPoint(0, 1))
    assert not charging_point_availability(None, ChargingPoint(1, 1))
