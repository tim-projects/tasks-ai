# Robustness test plan: 25 scenarios

1. Create task, invalid status move.
2. Create task, valid move to READY, PROGRESSING, TESTING, REVIEW, STAGING, LIVE.
3. Link task, circular dependency attempt.
4. Move to TESTING, then revert to PROGRESSING.
5. Move to STAGING, then move back to PROGRESSING.
6. Create task with short title.
7. Attempt to delete task in LIVE status.
8. Reconcile with non-merged branches.
9. Link non-existent tasks.
10. Attempt multiple checkpoint operations.
11. Run tasks operations while in detached HEAD state.
12. Attempt to move task to illegal state (e.g. READY -> LIVE).
13. Link task to itself.
14. Move task to REJECTED from STAGING.
15. Create issue with same name as existing task.
16. Move task to ARCHIVED without being merged.
17. Attempt to modify task that is ARCHIVED.
18. Move multiple tasks via comma-separated status and check if all succeed.
19. Verify `tasks doctor` detects data inconsistency.
20. Check if `tasks undo` works after a state transition.
21. Run `tasks cleanup` on a task that has been merged.
22. Test `tasks list` with JSON filtering.
23. Run workflow operations with invalid task IDs.
24. Verify file permissions/locked states during operations.
25. Test task creation with extreme character counts in story/tech fields.
