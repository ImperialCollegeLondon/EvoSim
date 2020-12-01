import pandas as pd


def test_as_stations():
    from evosim.io import EXEMPLARS, read_charging_points, as_stations

    charging_posts = read_charging_points(EXEMPLARS["stations"], EXEMPLARS["sockets"])
    stations = as_stations(charging_posts)
    csv = pd.read_csv(EXEMPLARS["stations"], index_col="ChargingStationID")

    assert all(stations.columns == csv.columns)
    assert stations.shape == csv.shape


def test_as_sockets():
    from evosim.io import EXEMPLARS, read_charging_points, as_sockets

    charging_posts = read_charging_points(EXEMPLARS["stations"], EXEMPLARS["sockets"])
    sockets = as_sockets(charging_posts)
    csv = pd.read_csv(EXEMPLARS["sockets"], index_col="SocketID")

    assert all(sockets.columns == csv.columns)
    assert sockets.shape == csv.shape
