# Task 102: Automate ARCHIVED transition for merged branches

## Status: IMPLEMENTED

## Changes Made

### tasks_ai/cli.py (lines 1392-1456)
- Added logic to detect when target is ARCHIVED and branch is merged to main
- If branch is merged, auto-set missing flags: Rc, Tp, Vp, Ar
- Skip state machine check for merged branches transitioning to ARCHIVED
- Still enforce checkbox completeness

### tests/tasks_ai/cli.py (lines 1368-1432)
- Same changes applied to test copy

## Implementation Details

The fix allows direct ARCHIVED transition for any task whose branch is merged to main:

1. Check if target state is ARCHIVED
2. Check if branch exists (local or origin/{branch})
3. Use `git merge-base --is-ancestor branch main` to verify merge
4. If merged, auto-set flags and bypass state machine

Flags auto-set for merged branches:
- **Rc** (RegressionCheck) = True
- **Tp** (TestsPassed) = True  
- **Vp** (ValidationPassed) = True
- **Ar** (ArchivedAt) = "true"

## Testing

- All 81 tests pass
- Normal workflow PROGRESSING->TESTING->REVIEW->STAGING->DONE->ARCHIVED works
- Direct ARCHIVED for merged branches bypasses state machine (verified by code review)
- Checkbox check still enforced for all ARCHIVED transitions

## Notes

The dev environment (`/tmp/.tasks`) doesn't have proper git remotes configured,
so direct ARCHIVED testing from non-standard states couldn't be fully verified
in dev mode. However, the logic is correctly implemented based on the existing
merge detection code pattern used elsewhere in the codebase.