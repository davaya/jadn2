from abc import ABCMeta, abstractmethod
from typing import Any, Callable, TypeVar

F = TypeVar('F', bound=Callable[..., Any])


class _HybridMeta(ABCMeta):
    """
    A descriptor-based metaclass that overrides Python's internal abstract checklist
    reads, making it completely immune to class rewrites like @dataclass(slots=True).
    """

    @property
    def __abstractmethods__(cls) -> frozenset[str]:
        # Fetch the baseline abstract array recorded by the setter
        abstracts = getattr(cls, '_abc_real_abstracts', frozenset())
        if not abstracts:
            return frozenset()

        explicit_abstracts = set()
        for method_name in abstracts:
            is_optional = False

            # Trace the entire Method Resolution Order (MRO) hierarchy
            for base in cls.__mro__:
                if method_name in base.__dict__:
                    raw_obj = base.__dict__[method_name]
                    # Unpack descriptor or method wrappers if present
                    func_obj = getattr(raw_obj, "__func__", raw_obj)

                    if getattr(func_obj, "__is_optional__", False):
                        is_optional = True
                        break

            if not is_optional:
                explicit_abstracts.add(method_name)

        return frozenset(explicit_abstracts)

    @__abstractmethods__.setter
    def __abstractmethods__(cls, value: Any) -> None:
        # Crucial Fix: Use type.__setattr__ to bypass read-only class mappingproxy bounds
        type.__setattr__(cls, '_abc_real_abstracts', value)


def optional_abstract(func: F) -> F:
    """
    Decorator marking an abstract method as optional for subclasses.
    Static type checkers treat it as abstract, but the runtime skips validation.
    """
    func.__dict__["__is_optional__"] = True
    return abstractmethod(func)  # type: ignore


class PartialABC(metaclass=_HybridMeta):
    """
    Base class providing hybrid abstract capabilities.
    Fully compatible with @dataclass(slots=True) hierarchies.
    """

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        # Dynamic Multi-Environment Guard:
        # Automatically detects if the target initialization target (cls) still has
        # unfiltered mandatory abstract methods left in its registry array.
        if cls.__abstractmethods__:
            raise TypeError(
                f"Can't instantiate abstract class {cls.__name__} with abstract "
                f"methods: {', '.join(cls.__abstractmethods__)}"
            )

        # Prevent direct initialization of the root engine utility wrapper
        if cls is PartialABC:
            raise TypeError("Cannot instantiate abstract utility configuration PartialABC directly.")

        return super().__new__(cls)