from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    Any,
    Callable,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Text,
    Union,
)

__doc__ = Path(__file__).with_suffix(".rst").read_text()


def _strip_docs(docs: Text) -> Text:
    from docstring_parser import parse

    docstring = parse(docs)
    result = docstring.short_description.strip() + "\n"
    if docstring.long_description:
        result += "\n" + docstring.long_description.strip() + "\n\n"
    return result.rstrip()


def _attributes(
    function: Callable, drop: Sequence[Text] = (), docs: Optional[Text] = None
):
    from inspect import signature, Signature
    from docstring_parser import parse
    from omegaconf import MISSING
    from typing import get_type_hints
    import attr
    import typing

    def not_empty(arg, empty=MISSING):
        return arg if arg is not Signature.empty else empty

    if docs is None and function.__doc__:
        docs = function.__doc__

    docparams = {k.arg_name: k for k in parse(docs).params}
    sigs = signature(function).parameters
    thints = get_type_hints(function)

    result = dict()
    for name, param in sigs.items():
        if drop is not None and name in drop:
            continue
        if param.kind != param.POSITIONAL_OR_KEYWORD:
            continue
        default_ = not_empty(param.default)
        if name in docparams and docparams[name].type_name is not None:
            type_ = eval(
                docparams[name].type_name,
                globals(),
                {k: getattr(typing, k) for k in dir(typing) if k[0] != "_"},
            )
        else:
            type_ = not_empty(thints[name], None)

        doc = None
        if name in docparams and docparams[name].description:
            doc = docparams[name].description

        result[name] = attr.ib(default=default_, type=type_, metadata=dict(doc=doc))
    return result


def _create_config(
    function: Callable,
    name: Optional[Text] = None,
    drop: Sequence[Text] = (),
    docs: Optional[Text] = None,
):
    from inspect import signature, Signature
    from omegaconf import MISSING
    from attr import make_class
    from re import split

    if name is None:
        name = function.__name__

    if docs is None and function.__doc__:
        docs = function.__doc__

    def not_empty(arg, empty=MISSING):
        return arg if arg is not Signature.empty else empty

    parameters = signature(function).parameters
    normalized_name = "".join([u.title() for u in split(r"\s|_|-", name)])
    attrs = _attributes(function, drop, docs)
    haskwargs = any(v.kind == v.VAR_KEYWORD for v in parameters.values())
    result = make_class(normalized_name, attrs, bases=(dict if haskwargs else object,))
    if docs:
        result.__doc__ = _strip_docs(docs)
    return result


@dataclass
class AutoConf:
    """Registry of input configurations.

    The goal of this class is to provide a simple way to register objects that can be
    automatically instantiated from YAML files.
    """

    name: Text
    """Name of the factory."""
    factories: MutableMapping[Text, Callable] = field(default_factory=dict)
    """Registry of function factories associated with a given key."""
    configs: MutableMapping[Text, Any] = field(default_factory=dict)
    """Registry of configurations associated with a given key."""

    def __call__(
        self,
        function: Optional[Any] = None,
        name: Optional[Text] = None,
        is_factory: Optional[bool] = None,
        docs: Optional[Text] = None,
    ) -> Callable:
        """Registers a function, a factory function, or a class.

        This function is expected to be used as a decorator. However, if ``function`` is
        ``None``, then it returns a decorator. Presumably, one of the other arguments is
        set in that case.

        Args:
            function: The function to register. If not ``None``, the function and its
                configuration are registered. If ``None``, the call returns a decorator.
            name: name by which to instantiate the function in the registry, defaults to
                ``function.__name__``.
            is_factory: Whether the function is a factory function or not. If
                ``function`` is a class, defaults to ``True``. Otherwise, defaults to
                ``False``.
            docs: Overrides the function's docstring with a docstring specialized for
                the autoconf framework.
        Returns:
            If ``function is None``, returns a decorator. Otherwise, returns
            ``function`` as is.
        """
        from warnings import warn
        from functools import partial
        from inspect import signature, Signature, isclass

        if function is None:
            return partial(self.__call__, name=name, is_factory=is_factory, docs=docs)
        if name is None:
            name = function.__name__
        if name in self.factories:
            warn(f"Overwriting registered function {name}")
        if is_factory is None:
            is_factory = isclass(function)

        def func_factory(**kwargs):
            from omegaconf import KeyValidationError

            if callable(function):
                return partial(function, **kwargs) if kwargs else function
            if kwargs:
                msg = f"{self.name}'s {name} does not accept arguments"
                raise KeyValidationError(msg)
            return function

        self.factories[name] = function if is_factory else func_factory
        drop = None
        if not is_factory:
            params = signature(function).parameters
            drop = [k for k, v in params.items() if v.default is Signature.empty]
        self.configs[name] = _create_config(function, name=name, drop=drop, docs=docs)
        return function

    def factory(self, settings: Union[Text, Mapping]) -> Any:
        """Instantiates a registered object."""
        from omegaconf import (
            OmegaConf,
            KeyValidationError,
            ValidationError,
            MissingMandatoryValue,
        )

        if isinstance(settings, Text):
            settings = dict(name=settings)

        if "name" not in settings:
            raise KeyValidationError(f"Missing `name` key in {self.name} setting.")

        if settings["name"] not in self.configs:
            raise KeyValidationError(f"Unknown {self.name}: {settings['name']}.")

        schema = OmegaConf.structured(self.configs[settings["name"]]())
        config = OmegaConf.create({k: v for k, v in settings.items() if k != "name"})
        factory = self.factories[settings["name"]]
        try:
            config = OmegaConf.merge(schema, config)
            return factory(**config)
        except KeyValidationError as error:
            msg = f"Incorrect key {error.key} in {self.name}, {settings['name']}"
            raise KeyValidationError(msg) from error
        except ValidationError as error:
            msg = (
                f"Incorrect value {error.value!r} for key '{error.key}' in {self.name},"
                f" {settings['name']}"
            )
            raise ValidationError(msg) from error
        except MissingMandatoryValue as error:
            msg = (
                f"Missing mandatory key '{error.key}' in {self.name}, "
                f"{settings['name']}"
            )
            raise MissingMandatoryValue(msg) from error
