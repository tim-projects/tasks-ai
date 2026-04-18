# Task 91: Modularize CLI commands

## Progress
- Extracted `config`, `doctor`, and validation logic into separate files: `tasks_ai/commands.py` and `tasks_ai/validation.py`.
- Fixed multiple lint/syntax errors across the project (`check.py`, `repo.py`, `tests/test_tasks.py`).
- Added `PYTHONPATH` configuration to `check.py` to resolve `ModuleNotFoundError` during tests.
- Implemented full `doctor` logic in `tasks_ai/commands.py`.

## Findings
- `pytest` was failing due to `tasks_ai` not being in `PYTHONPATH`.
- Several files had `E702` (multiple statements on one line) and syntax errors that needed manual fixing.
- `test_review_diff_generated` is failing due to a validation error during the move to `TESTING`.

## Mitigations
- Manually fixed syntax and linting errors to satisfy `check.py all`.
- Updated `check.py` to dynamically set `PYTHONPATH` for sub-processes.
- Investigating `test_review_diff_generated` failure and ensuring proper validation state.
