# Manual Recovery Guide for tasks-ai Race Condition Bug

## The Problem

When multiple tasks are created in quick succession, the race condition in `_get_next_id()` causes:
- Task IDs to be assigned out of order
- Branch names to not match their actual content
- Directories contain correct content but wrong task IDs in metadata

## How to Fix

### Step 1: Identify the Mismatch

For each affected task directory, check what the task actually contains vs what its ID claims:

```bash
# List all backlog tasks
ls -la .tasks/backlog/

# Check the actual story content in each directory
cat .tasks/backlog/<task-dir>/story.md
```

### Step 2: Determine Correct Task IDs

Based on the bug report timeline:
- The first task created had content about "/api/lookup" → ended up in directory 26
- The second task had content about "/api/report" → ended up in directory 27
- The third task had content about "admin endpoints" → ended up in directory 28
- The fourth task had content about "/api/public/sources" → ended up in directory 29 (correct)

Due to the race condition, the actual content was assigned to wrong branch IDs:
- Directory `26-issue-...` actually contains "Deprecate /api/report" → should be ID 27
- Directory `27-issue-...` actually contains "Deprecate admin endpoints" → should be ID 28
- Directory `28-issue-...` actually contains "Remove /api/public/sources" → should be ID 29
- Directory `29-issue-...` is already correct

### Step 3: Rename Directories and Fix Metadata

For each mismatched task, rename the directory to match its ACTUAL content:

```bash
cd .tasks/backlog
# Move content to correct ID based on what it actually contains
mv 26-issue-deprecate--api-lookup---remove 27-issue-deprecate--api-report---remove
mv 27-issue-deprecate--api-report---remove 28-issue-deprecate-admin-endpoints---mo
mv 28-issue-deprecate-admin-endpoints---mo 29-issue-remove--ap
# 29 is already correct
```

Then update the metadata file (meta.json) in each directory to have the correct "Id":
- Edit meta.json in 27-issue-... and set "Id": 27
- Edit meta.json in 28-issue-... and set "Id": 28
- Edit meta.json in 29-issue-... and set "Id": 29

### Step 4: Update Git Branches

```bash
# Rename branches to match the corrected IDs
git branch -m 26-issue-deprecate--api-lookup---remove 27-issue-deprecate--api-report---remove
git branch -m 27-issue-deprecate--api-report---remove 28-issue-deprecate-admin-endpoints---mo
git branch -m 28-issue-deprecate-admin-endpoints---mo 29-issue-remove--ap
```

### Step 5: Commit the Fix

```bash
git add .tasks/backlog/
git commit -m "Fix: Correct task IDs after race condition bug"
```

## Prevention

The bug has been fixed in the codebase by adding `fcntl.flock()` for exclusive locking in `_get_next_id()`. Upgrade to the latest version to prevent future issues.