Rename PROGRESSING state to INPROGRESS with backward compatibility for existing .tasks/progressing folders.

## Files to Update

### Core Python Files
1. **tasks_ai/constants.py** (lines 10, 21-30, 64, 68-71, 82):
   - Change `STATE_FOLDERS["PROGRESSING"]` to `STATE_FOLDERS["INPROGRESS"] = "inprogress"`
   - Update `ALLOWED_TRANSITIONS` entries from "PROGRESSING" to "INPROGRESS"
   - Update LIFECYCLE string in comments/docs

2. **tasks_ai/cli.py** (lines 587, 900, 1117, 1240-1241, 1322, 1365, 1381-1382, 1411-1415, 1600):
   - Update all `STATE_FOLDERS["PROGRESSING"]` references to `STATE_FOLDERS["INPROGRESS"]`
   - Update all string comparisons from `== "PROGRESSING"` to `== "INPROGRESS"`
   - Update string literals like `"->PROGRESSING"` to `"->INPROGRESS"`

3. **tasks_ai/help_text.py** (line 11, 27):
   - Update state machine diagram: PROGRESSING -> INPROGRESS
   - Update example commands with INPROGRESS

4. **tasks_ai/tasks.py** (line 108):
   - Update help text example

### Documentation
5. **AGENTS.md** (lines 41, 43, 54, 82):
   - Update activation instructions
   - Update promotion workflow
   - Update multi-step move examples

6. **README.md** (lines 41, 47, 85, 93, 165, 206):
   - Update state machine diagram
   - Update move command examples
   - Update task status display

### Tests
7. **test_tasks.py** (lines 112, 113, 121, 122, 206, 229, 352, 354):
   - Update all "PROGRESSING" references to "INPROGRESS"

8. **test_robustness.py** (lines 107, 109, 117, 136, 154, 177, 239, 318):
   - Update all "PROGRESSING" references to "INPROGRESS"

9. **test_dev_mode.py** (lines 115, 156):
   - Update all "PROGRESSING" references to "INPROGRESS"

### Scripts/Tools
10. **repo.py** (line 323):
    - Update help text

## Backward Compatibility Strategy

**Chosen Approach: Option A + C (Auto-detection with temporary dual support)**

Implement auto-detection in `TasksCLI.__init__` or `find_project_root`:
1. Check if `.tasks/inprogress/` exists - use it if present
2. If `.tasks/inprogress/` missing but `.tasks/progressing/` exists - migrate (rename) on first use
3. Provide deprecation warning for old `.tasks/progressing/` folder until migration complete

Also implement in `tasks doctor`:
- Add `--migrate-progressing` flag for explicit migration
- Auto-upgrade checks on initialization

Migration logic:
```python
# In find_project_root or TasksCLI.__init__
progressing_path = os.path.join(tasks_path, "progressing")
inprogress_path = os.path.join(tasks_path, "inprogress")

if os.path.exists(progressing_path) and not os.path.exists(inprogress_path):
    # Migrate progressing -> inprogress silently on first use
    os.rename(progressing_path, inprogress_path)
```

## Branch Naming
Branch: `70-task-rename-progressing-to-inprogress` (consistent with task Id)

## Risks and Mitigations

1. **Old .tasks worktree**: Auto-migration will handle - no manual intervention needed
2. **Git history**: No impact - folders renamed, commits unchanged
3. **Corrupted tasks**: Migration skips if inprogress folder already exists (failsafe)
4. **Manual edits**: User can run `tasks doctor --migrate-progressing` for explicit migration
5. **Folder rename conflict**: Ensure no naming collision with existing "progressing" folder; datetime prefix prevents conflicts during migration
