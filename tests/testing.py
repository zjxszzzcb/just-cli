"""
Pythonic Testing Framework
==========================

A lightweight, documentation-first testing framework for just-cli.
Implements "tests as documentation" pattern without external dependencies.

Usage Example
-------------

    from testing import describe, it, expect, run_tests

    @describe("Calculator")
    class CalculatorTests:
        '''
        Calculator Module
        =================
        
        The calculator provides basic arithmetic operations.
        '''
        
        @it("adds two numbers correctly")
        def test_addition(self):
            result = 1 + 1
            expect(result).to_equal(2)
        
        @it("handles negative numbers")
        def test_negative():
            expect(-1 + 1).to_equal(0)

    if __name__ == "__main__":
        run_tests()

Design Philosophy
-----------------

1. **Tests as Documentation**: Test descriptions read like specifications
2. **Zero Dependencies**: Uses only Python stdlib
3. **Minimal API**: Just describe/it/expect
4. **Rich Output**: Clear, colorful console output
"""

from __future__ import annotations

import sys
import traceback
import functools
from pathlib import Path
from typing import Any, Callable, TypeVar
from unittest.mock import patch, MagicMock
from contextlib import contextmanager

# Type aliases
T = TypeVar('T')
TestFunc = Callable[[], None]

# Global test registry
_test_suites: list[TestSuite] = []
_current_suite: TestSuite | None = None


# =============================================================================
# Core Classes
# =============================================================================

class TestSuite:
    """A collection of related tests (created by @describe)."""
    
    def __init__(self, name: str, doc: str = ""):
        self.name = name
        self.doc = doc
        self.tests: list[TestCase] = []
        self.setup_fn: Callable | None = None
        self.teardown_fn: Callable | None = None
    
    def add_test(self, test: TestCase):
        self.tests.append(test)


class TestCase:
    """A single test case (created by @it)."""
    
    def __init__(self, description: str, fn: TestFunc):
        self.description = description
        self.fn = fn
        self.passed: bool | None = None
        self.error: Exception | None = None


class ExpectationError(AssertionError):
    """Raised when an expectation fails."""
    pass


class Expectation:
    """Chainable expectation object for fluent assertions."""
    
    def __init__(self, actual: Any):
        self.actual = actual
        self._negated = False
    
    @property
    def not_(self) -> Expectation:
        """Negate the expectation."""
        self._negated = True
        return self
    
    def _check(self, condition: bool, message: str):
        """Check condition and raise if failed."""
        if self._negated:
            condition = not condition
            message = f"NOT {message}"
        
        if not condition:
            raise ExpectationError(message)
    
    def to_equal(self, expected: Any) -> Expectation:
        """Assert that actual equals expected."""
        self._check(
            self.actual == expected,
            f"Expected {self.actual!r} to equal {expected!r}"
        )
        return self
    
    def to_be(self, expected: Any) -> Expectation:
        """Assert that actual is expected (identity check)."""
        self._check(
            self.actual is expected,
            f"Expected {self.actual!r} to be {expected!r}"
        )
        return self
    
    def to_be_true(self) -> Expectation:
        """Assert that actual is truthy."""
        self._check(
            bool(self.actual),
            f"Expected {self.actual!r} to be truthy"
        )
        return self
    
    def to_be_false(self) -> Expectation:
        """Assert that actual is falsy."""
        self._check(
            not bool(self.actual),
            f"Expected {self.actual!r} to be falsy"
        )
        return self
    
    def to_be_none(self) -> Expectation:
        """Assert that actual is None."""
        self._check(
            self.actual is None,
            f"Expected {self.actual!r} to be None"
        )
        return self
    
    def to_contain(self, item: Any) -> Expectation:
        """Assert that actual contains item."""
        self._check(
            item in self.actual,
            f"Expected {self.actual!r} to contain {item!r}"
        )
        return self
    
    def to_have_length(self, length: int) -> Expectation:
        """Assert that actual has expected length."""
        actual_length = len(self.actual)
        self._check(
            actual_length == length,
            f"Expected length {length}, got {actual_length}"
        )
        return self
    
    def to_be_instance_of(self, cls: type) -> Expectation:
        """Assert that actual is an instance of cls."""
        self._check(
            isinstance(self.actual, cls),
            f"Expected {self.actual!r} to be instance of {cls.__name__}"
        )
        return self
    
    def to_be_greater_than(self, value: Any) -> Expectation:
        """Assert that actual > value."""
        self._check(
            self.actual > value,
            f"Expected {self.actual!r} to be greater than {value!r}"
        )
        return self
    
    def to_be_less_than(self, value: Any) -> Expectation:
        """Assert that actual < value."""
        self._check(
            self.actual < value,
            f"Expected {self.actual!r} to be less than {value!r}"
        )
        return self
    
    def to_match(self, pattern: str) -> Expectation:
        """Assert that actual matches regex pattern."""
        import re
        self._check(
            re.search(pattern, str(self.actual)) is not None,
            f"Expected {self.actual!r} to match pattern {pattern!r}"
        )
        return self


@contextmanager
def expect_error(error_type: type[Exception] = Exception):
    """
    Context manager to expect an error.
    
    Usage:
        with expect_error(ValueError):
            raise ValueError("oops")
    """
    try:
        yield
        raise ExpectationError(f"Expected {error_type.__name__} to be raised")
    except error_type:
        pass  # Expected
    except ExpectationError:
        raise
    except Exception as e:
        raise ExpectationError(
            f"Expected {error_type.__name__}, got {type(e).__name__}: {e}"
        )


# =============================================================================
# Decorators
# =============================================================================

def describe(name: str):
    """
    Decorator to define a test suite.
    
    Usage:
        @describe("Feature Name")
        class FeatureTests:
            '''Optional docstring describing the feature.'''
            
            @it("does something")
            def test_something(self):
                ...
    """
    def decorator(cls: type) -> type:
        suite = TestSuite(name, cls.__doc__ or "")
        _test_suites.append(suite)
        
        # Create instance and collect tests
        instance = cls()
        
        # Find @it decorated methods
        for attr_name in dir(instance):
            if attr_name.startswith('_'):
                continue
            attr = getattr(instance, attr_name)
            if hasattr(attr, '_test_description'):
                test = TestCase(attr._test_description, attr)
                suite.add_test(test)
        
        return cls
    
    return decorator


def it(description: str):
    """
    Decorator to define a test case.
    
    Usage:
        @it("should calculate correctly")
        def test_calculation(self):
            expect(1 + 1).to_equal(2)
    """
    def decorator(fn: TestFunc) -> TestFunc:
        fn._test_description = description
        return fn
    
    return decorator


# =============================================================================
# Public API
# =============================================================================

def expect(actual: Any) -> Expectation:
    """
    Create an expectation for fluent assertions.
    
    Usage:
        expect(result).to_equal(42)
        expect(value).not_.to_be_none()
        expect(items).to_contain("apple")
    """
    return Expectation(actual)


@contextmanager
def mock_object(target: str):
    """
    Context manager for mocking objects.
    
    Usage:
        with mock_object('just.system') as mock_sys:
            mock_sys.platform = "linux"
            ...
    """
    with patch(target) as mock:
        yield mock


# =============================================================================
# Test Runner
# =============================================================================

class TestRunner:
    """Runs tests and produces documentation-style output."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.passed = 0
        self.failed = 0
    
    def run_all(self) -> bool:
        """Run all registered test suites."""
        print()
        print("=" * 70)
        print("  TEST DOCUMENTATION")
        print("=" * 70)
        print()
        
        for suite in _test_suites:
            self._run_suite(suite)
        
        self._print_summary()
        return self.failed == 0
    
    def _run_suite(self, suite: TestSuite):
        """Run a single test suite."""
        # Print suite header (documentation style)
        print(f"📚 {suite.name}")
        print("-" * 50)
        
        if suite.doc:
            # Print first paragraph of docstring
            doc_lines = suite.doc.strip().split('\n')
            for line in doc_lines[:3]:  # First 3 lines max
                if line.strip():
                    print(f"   {line.strip()}")
            print()
        
        for test in suite.tests:
            self._run_test(test)
        
        print()
    
    def _run_test(self, test: TestCase):
        """Run a single test case."""
        try:
            test.fn()
            test.passed = True
            self.passed += 1
            print(f"   ✅ {test.description}")
        except Exception as e:
            test.passed = False
            test.error = e
            self.failed += 1
            print(f"   ❌ {test.description}")
            if self.verbose:
                # Print error details indented
                for line in str(e).split('\n'):
                    print(f"      {line}")
    
    def _print_summary(self):
        """Print test summary."""
        print("=" * 70)
        total = self.passed + self.failed
        
        if self.failed == 0:
            print(f"✨ All {total} tests passed!")
        else:
            print(f"Results: {self.passed} passed, {self.failed} failed")
        
        print("=" * 70)


def run_tests(verbose: bool = True) -> bool:
    """
    Run all registered tests.
    
    Returns True if all tests passed, False otherwise.
    """
    runner = TestRunner(verbose=verbose)
    return runner.run_all()


# =============================================================================
# Standalone execution helper
# =============================================================================

def run_module_tests(module_path: str | Path) -> bool:
    """
    Import and run tests from a module file.
    
    Usage:
        run_module_tests(__file__)
    """
    # Clear previous tests
    _test_suites.clear()
    
    # Import the module to trigger @describe decorators
    import importlib.util
    path = Path(module_path)
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules[path.stem] = module
        spec.loader.exec_module(module)
    
    return run_tests()
