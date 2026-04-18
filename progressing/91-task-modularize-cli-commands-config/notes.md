# Task 91: Modularize CLI commands

## Progress
- Extracted `config`, `doctor`, and validation logic into separate files: `tasks_ai/commands.py` and `tasks_ai/validation.py`.
- Fixed multiple lint/syntax errors across the project.
- Implemented full `doctor` logic.
- Identified that `test_review_diff_generated` failure is due to configuration format mismatch in tests: tests were using nested `repo: {lint: ...}` config instead of flat `repo.lint: ...`.

## Findings
- Test environment uses an outdated configuration schema for `repo.lint/test/type_check/format`.
- Subprocess calls for validation fail because `check.py` expects flat configuration keys, but test setup provides a nested structure.

## Mitigations
- Updated `tests/test_tasks.py` to use the flat configuration schema for task initialization.
- Re-running validation to confirm fix.
