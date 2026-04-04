# AGENTS.md - tests/

## OVERVIEW
Custom test framework using describe()/it()/expect() API (like Jest), NOT pytest. Test runner: run_tests.py (Docker + local).

## WHERE TO LOOK

| Purpose | Location |
|---------|----------|
| Custom test framework | `testing.py` - describe/it/expect decorators, Expectation class |
| Test runner (CLI) | `run_tests.py` - orchestrates Docker + local, --worker mode |
| Test files | `test_*.py` pattern in tests/ root |
| Extension tests | `test_extension/` subdirectory |

## CONVENTIONS

**Test Execution**
- Test files run as standalone scripts via subprocess
- Exit code 0 = pass, non-zero = fail
- `run_tests.py --worker` runs tests directly (no Docker)

**Test File Structure**
- Filename: `test_*.py`
- Can use custom framework OR plain assert-based functions
- Entry point: `if __name__ == "__main__":` block or standalone execution

**Custom Framework API** (testing.py)
```python
from testing import describe, it, expect, run_tests

@describe("Feature")
class FeatureTests:
    @it("does something")
    def test_something(self):
        expect(result).to_equal(42)
```

**Available Matchers**
- `to_equal()`, `to_be()`, `to_be_true()`, `to_be_false()`
- `to_be_none()`, `to_contain()`, `to_have_length()`
- `to_be_instance_of()`, `to_be_greater_than()`, `to_be_less_than()`, `to_match()`
- `not_` negation: `expect(x).not_.to_be_none()`

**Running Tests**
```bash
cd tests && python run_tests.py           # Docker + Local
cd tests && python run_tests.py --worker   # Local only
```

## ANTI-PATTERNS

- Do NOT use pytest or unittest (custom framework only)
- Do NOT expect standard test discovery (files run as scripts)
- Do NOT skip Docker tests on non-Windows (only Windows runs both)
