from typing import Text

from pytest import raises


def test_create_config_has_defaults():
    from evosim.autoconf import _create_config
    from omegaconf import MISSING

    def function(n: int, kw: Text = "1"):
        """This is a function."""
        pass

    NoDrop = _create_config(function)
    assert NoDrop.__doc__ == function.__doc__
    assert NoDrop.__name__ == function.__name__.title()
    assert NoDrop().n is MISSING
    assert NoDrop().kw == "1"
    assert set([u for u in dir(NoDrop()) if u[0] != "_"]) == {"kw", "n"}


def test_create_config_has_types():
    from evosim.autoconf import _create_config
    from omegaconf import OmegaConf, ValidationError

    def function(n: int, kw: Text = "1"):
        """This is a function."""
        pass

    Result = _create_config(function)
    structured = OmegaConf.structured(Result)
    with raises(ValidationError):
        structured.n = "a"
    structured.n = "1"
    assert structured.n == 1
    assert not (structured.n == "1")
    structured.kw = 2
    assert structured.kw == "2"
    assert not (structured.kw == 2)


def test_create_config_drop_behaviour():
    from evosim.autoconf import _create_config

    def function(n: int, kw: Text = "1"):
        """This is a function."""
        pass

    NoDrop = _create_config(function)
    assert set([u for u in dir(NoDrop()) if u[0] != "_"]) == {"kw", "n"}

    DropN = _create_config(function, drop=["n"])
    assert set([u for u in dir(DropN()) if u[0] != "_"]) == {"kw"}

    DropKW = _create_config(function, drop=["kw"])
    assert set([u for u in dir(DropKW()) if u[0] != "_"]) == {"n"}

    DropAll = _create_config(function, drop=["kw", "n"])
    assert len([u for u in dir(DropAll()) if u[0] != "_"]) == 0


def test_create_config_types_from_docs():
    from evosim.autoconf import _create_config
    from omegaconf import ValidationError, OmegaConf

    def function(n: int, kw: Text = "1"):
        """This is a function.

        Args:
            n (Text): this is a floating point in text format
            kw (int): this is an integer
        """
        pass

    Result = _create_config(function)
    structured = OmegaConf.structured(Result)
    with raises(ValidationError):
        structured.kw = "a"
    structured.kw = "1"
    assert structured.kw == 1
    assert not (structured.kw == "1")
    structured.n = 2
    assert structured.n == "2"
    assert not (structured.n == 2)
