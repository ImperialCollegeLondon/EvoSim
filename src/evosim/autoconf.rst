Automatic Configuration
=======================

The automatic configuration package provides tools easily link an object (e.g. a
function) in the code and inputs (in a *yaml* file). There three aspects to these links:

#. a means to register a `factory function
   <https://en.wikipedia.org/wiki/Factory_(object-oriented_programming)>`__
#. a means to convert the arguments of the factory function into a `structured
   configuration
   <https://omegaconf.readthedocs.io/en/2.0_branch/structured_config.html>`__ object
   with `OmegConf <https://omegaconf.readthedocs.io/>`__
#. a means to call the factory function given an input to OmegaConf

Usage
-----

We can create a registry with:

.. testcode:: autoconf

    registry = evosim.autoconf.AutoConf("my_registry")

Two kinds of objects can be registered: factory functions (or classes) and
straightforward functions. When instantiated, factory functions will be called with the
arguments read from input and their result returned. Straightforward functions are
returned as is, or wrapped with :py:func:`functools.partial` to take into account input
arguments.

Let's first create a simple, straightforward function without even keyword arguments:

.. testcode:: autoconf

    @registry
    def simple(arg0: int, arg1: int):
        return arg0 + arg1

We can instantiate it as:

.. testcode:: autoconf

    instantiated = registry.factory("simple")
    assert instantiated is simple

The point is that we have used data, ``"simple"``, and converted it to a function. We
could also have fed it a dictionary read from a yaml file:

.. testcode:: autoconf

    from io import StringIO
    from omegaconf import OmegaConf

    yaml = StringIO("name: simple")
    instantiated = registry.factory(OmegaConf.load(yaml))
    assert instantiated is simple

In other words, we have succesfully linked data to code. The name in the input defaults
to the name of the function. But it can also be set by hand:

.. testcode:: autoconf

    @registry(name="not so simple")
    def notthename(a, b):
        return a + b

    assert registry.factory("not so simple") is notthename



A more complicated function with keywords comes with additional goodies: the keyword
arguments can be read and set from the input:

.. testcode:: autoconf

    @registry
    def with_kwargs(arg0: int, arg1: int, operation="sum", factor: float=1):
        if operation == "sum":
            return factor * (arg0 + arg1)
        elif operation == "mul":
            return factor * arg0 * arg1
        else:
            raise RuntimeError(f"Unknown operation {operation}")

    instantiated = registry.factory(dict(name="with_kwargs"))
    assert instantiated(1, 0) == 1
    assert instantiated(0, 1) == 1

    instantiated = registry.factory(dict(name="with_kwargs", factor=2))
    assert instantiated(1, 0) == 2
    assert instantiated(0, 1) == 2

    instantiated = registry.factory(dict(name="with_kwargs", operation="mul"))
    assert instantiated(1, 0) == 0
    assert instantiated(0, 1) == 0
    assert instantiated(1, 2) == 2

As can be seen above, the function ``instantiated`` calls the function ``with_kwargs``,
but with the arguments given by on input (or the default arguments if missing). Better
yet, feeding the registry an argument with the wrong type will result in an error:

.. doctest:: autoconf

    >>> registry.factory(dict(name="with_kwargs", factor="a"))
    Traceback (most recent call last):
        ...
    ValidationError: Incorrect value 'a' for key 'factor' in my_registry, with_kwargs

The type is automatically gathered from the type annotation of the keyword argument, if
it is present. Only those types understood by ``omegaconf`` are supported. Functions
with keywords arguments expecting more complicated types can be wrapped for the registry
into a function with simpler types. Eventually, this limitation is due to `omegaconf`'s
ability to transform text loaded from a yaml file into a python object. Also, see
:ref:`Overriding docstrings and argument types`.

Sometimes we require instantiating more complex functions. This is where factory
functions come in. Factory functions are not returned directly, instead they are called
and the result is passed on to the user:


.. testcode:: autoconf

    @registry(is_factory=True)
    def factory_function(a: int, b: str):
        msg = f"a={a}, b={b}"


        def callmemaybe(do_raise: bool = True):
            if do_raise:
                raise RuntimeError(msg)
            return msg + ", do_raise=False"

        return callmemaybe


If we instantiate ``"factory_function"`` from the registry, then the inner closure
``callmymaybe`` is returned.


.. doctest:: autoconf

    >>> instantiated = registry.factory(dict(name="factory_function", a=1, b=2.9))
    >>> instantiated(False)
    'a=1, b=2.9, do_raise=False'

    >>> instantiated(True)
    Traceback (most recent call last):
        ...
    RuntimeError: a=1, b=2.9

There are several important differences with the straightforward case described
previously:

- the decorator requires an argument ``is_factory=True``
- the function returned on instantiation is the *inner* function ``callmemaybe`` (or
  indeed, whatever is returned by the factory function)
- the non-keyword arguments of the factory function are now **required** arguments

Let's illustrate that last point:

.. doctest:: autoconf

    >>> instantiated = registry.factory(dict(name="factory_function", a=2))
    Traceback (most recent call last):
        ...
    MissingMandatoryValue: Missing mandatory key 'b' in my_registry, factory_function


Finally, it is also possible to register and instantiate classes. Below, we instantiate
a data-class, but any class will work. In practice, the class' ``__init__`` function is
called as though it were a factory function. And similarly to factory functions, all
non-keyword arguments are required:

.. doctest:: autoconf

    >>> from typing import Text
    >>> from dataclasses import dataclass
    >>> @registry
    ... @dataclass
    ... class MyClass:
    ...     something: Text
    ...     otherthing: int = 4
    >>> registry.factory(dict(name="MyClass", something=3))
    MyClass(something='3', otherthing=4)
    >>> registry.factory(dict(name="MyClass", something="aa", otherthing=5))
    MyClass(something='aa', otherthing=5)
    >>> registry.factory(dict(name="MyClass", otherthing=5))
    Traceback (most recent call last):
        ...
    MissingMandatoryValue: Missing mandatory key 'something' in my_registry, MyClass
    >>> registry.factory(dict(name="MyClass", something=3, otherthing='c'))
    Traceback (most recent call last):
        ...
    ValidationError: Incorrect value 'c' for key 'otherthing' in my_registry, MyClass


Overriding docstrings and argument types
----------------------------------------

``registry`` accepts a docstring argument. If not given, then the docstring is read from
function itself. The types of the arguments will be gathered from there, if provided,
rather than from the function signature. This is useful both to document input arguments
from a user perspective, and to simplify the input types where necessary.

.. testcode:: autoconf_docs

    registry = evosim.autoconf.AutoConf("my_registry")

    @registry(
        docs="""A registered funtion with modified types.

        Generally, this docstring is specialized for users working from input files.

        Args:
            args0 (Text): a description.
        """
    )
    def modified_types(args0: int = 5) :
        """Docstring could also go here. But docs argument takes priority.

        Generally, this docstring is written for developers.
        """
        return args0

    function = registry.factory("modified_types")
    assert function() == "5"
    assert not (function() == 5)


Variational keyword arguments
-----------------------------

The registered functions can be defined with keyword arguments. In that case, it creates
a factory wich takes any number of arguments.

.. testcode:: autoconf_kwargs

    registry = evosim.autoconf.AutoConf("my_registry")


    @registry(
        docs="""A registered funtion with modified types.

        Args:
            args0: a description.
            kwargs: additional keys specified in the input will be passed here.
        """
    )
    def with_kwargs(args0: int = 5, **kwargs):
        return dict(args0=args0, **kwargs)

    function = registry.factory(dict(name="with_kwargs", additional="hello"))
    assert set(function().keys()) == {"args0", "additional"}
    assert function()["args0"] == 5
    assert function()["additional"] == "hello"
