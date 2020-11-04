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


def _create_config(
    function: Callable, name: Optional[Text] = None, drop: Sequence[Text] = ()
):
    from inspect import signature, Signature
    from omegaconf import MISSING
    from attr import make_class, ib
    from re import split

    if name is None:
        name = function.__name__

    def not_empty(arg, empty=MISSING):
        return arg if arg is not Signature.empty else empty

    parameters = signature(function).parameters
    normalized_name = "".join([u.title() for u in split(r"\s|_|-", name)])
    attrs = {
        k: ib(not_empty(v.default), type=not_empty(v.annotation, None))
        for k, v in parameters.items()
        if drop is None or k not in drop
    }
    return make_class(normalized_name, attrs)


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
        Returns:
            If ``function is None``, returns a decorator. Otherwise, returns
            ``function`` as is.
        """
        from warnings import warn
        from functools import partial
        from inspect import signature, Signature, isclass

        if function is None:
            return partial(self.__call__, name=name, is_factory=is_factory)
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
        self.configs[name] = _create_config(function, name=name, drop=drop)
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
