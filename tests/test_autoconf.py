from typing import Text

from pytest import raises


def test_create_config_has_defaults():
    from evosim.autoconf import _create_config
    from omegaconf import MISSING
    import attr

    def function(n: int, kw: Text = "1"):
        """This is a function."""
        pass

    NoDrop = _create_config(function)
    assert NoDrop.__doc__ == function.__doc__
    assert NoDrop.__name__ == function.__name__.title()
    assert NoDrop().n is MISSING
    assert NoDrop().kw == "1"
    assert set([u for u in dir(NoDrop()) if u[0] != "_"]) == {"kw", "n"}

    fields = {k.name: k for k in attr.fields(NoDrop)}
    assert fields["n"].metadata["doc"] is None
    assert fields["kw"].metadata["doc"] is None


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
    import attr

    def function(n: int, kw: Text = "1"):
        """This is a function.

        With a long description.

        Args:
            n (Text): this is a floating point in text format
            kw (int): this is an integer
        """
        pass

    Result = _create_config(function)
    assert Result.__doc__ == "This is a function.\n\nWith a long description."
    structured = OmegaConf.structured(Result)
    with raises(ValidationError):
        structured.kw = "a"
    structured.kw = "1"
    assert structured.kw == 1
    assert not (structured.kw == "1")
    structured.n = 2
    assert structured.n == "2"
    assert not (structured.n == 2)

    fields = {k.name: k for k in attr.fields(Result)}
    assert fields["n"].metadata["doc"] == "this is a floating point in text format"
    assert fields["kw"].metadata["doc"] == "this is an integer"


def test_create_config_kwargs():
    from evosim.autoconf import _create_config
    from omegaconf import OmegaConf
    from omegaconf.errors import ConfigAttributeError

    def no_kw(n: int):
        pass

    def with_kw(n: int, **kwargs):
        pass

    NoKW = _create_config(no_kw)
    with raises(ConfigAttributeError):
        OmegaConf.structured(NoKW).b = 5

    WithKW = _create_config(with_kw)
    OmegaConf.structured(WithKW).b = 5
