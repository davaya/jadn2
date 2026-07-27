from dataclasses import dataclass
from abc import abstractmethod
import pytest
from jadn.abc_extensions import PartialABC, optional_abstract


# ==============================================================================
# 1. SETUP FIXTURES & TEST CLASSES
# ==============================================================================

@dataclass(slots=True)
class MockBaseclass(PartialABC):
    """A realistic base class matching your dataclass hierarchy structure."""
    base_field: str

    @abstractmethod
    def mandatory_method(self) -> str:
        """Subclasses MUST implement this method signature."""
        pass

    @optional_abstract
    def optional_method(self) -> str:
        """Subclasses can completely ignore this without consequences."""
        return "Fallback logic worked"


# ==============================================================================
# 2. THE TEST CASES
# ==============================================================================

def test_valid_subclass_instantiation():
    """
    Verifies that a subclass implementing ONLY the mandatory method instantiates
    and executes correctly, even when decorated with @dataclass(slots=True).
    """
    @dataclass(slots=True)
    class ValidSubclass(MockBaseclass):
        child_field: int

        def mandatory_method(self) -> str:
            return f"Success: {self.base_field} | {self.child_field}"

    # Act
    pkg = ValidSubclass(base_field="Hello", child_field=123)

    # Assert
    assert pkg.mandatory_method() == "Success: Hello | 123"
    assert pkg.optional_method() == "Fallback logic worked"


def test_missing_mandatory_method_raises_error():
    """
    Verifies that if a subclass forgets to override a truly mandatory
    abstractmethod, Python still safely crashes with a TypeError.
    """
    # Act & Assert
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        @dataclass(slots=True)
        class InvalidSubclass(MockBaseclass):
            # Missing 'mandatory_method' implementation
            pass

        # Trying to build the object must fail
        _ = InvalidSubclass(base_field="Broken")


def test_direct_baseclass_instantiation_is_blocked():
    """
    Verifies that developers cannot bypass the system by instantiating
    the abstract Baseclass directly.
    """
    # Act & Assert
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        # We must adjust our PartialABC string guard checks if your base name differs.
        # This checks for 'MockBaseclass' specifically if named as such in __new__.
        _ = MockBaseclass(base_field="Direct Parent")