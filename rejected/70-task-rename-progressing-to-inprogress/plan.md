1. Investigate all PROGRESSING references using grep
2. Create branch 70-task-rename-progressing-to-inprogress
3. Update constants.py: STATE_FOLDERS, ALLOWED_TRANSITIONS, LIFECYCLE docs
4. Update cli.py: all PROGRESSING references
5. Update help_text.py: state machine and examples
6. Update tasks.py: help text
7. Update AGENTS.md: activation and workflow instructions
8. Update README.md: state machine diagram and examples
9. Update repo.py: help text
10. Update test_tasks.py: all PROGRESSING references
11. Update test_robustness.py: all PROGRESSING references
12. Update test_dev_mode.py: all PROGRESSING references
13. Rename .tasks/progressing to .tasks/inprogress in local worktree
14. Implement auto-migration in TasksCLI.__init__ or find_project_root
15. Add tasks doctor --migrate-progressing command
16. Verify backward compatibility
17. Run all validation (lint, typecheck, tests)
