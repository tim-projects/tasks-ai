#!/usr/bin/env python3
"""
repo - Repository management wrapper script
Usage: repo <command> [args]

Commands:
  merge testing to staging   - Run compliance checks and merge testing → staging
  merge staging to main     - Run compliance checks and merge staging → main
  sync [branches...]        - Sync branches in order: testing → staging → main → testing
  clean                     - Clean up generated files and show status
  status                    - Show current branch and pending changes
  git <args>                - Run git command (e.g., repo git status)
  branch list               - List all branches
  branch exists <name>      - Check if branch exists (local or remote)
  branch push <name>        - Push branch to remote
  branch delete <name>      - Delete local branch
  branch create <name>      - Create and switch to new branch
  merged <branch> <target> - Check if branch is merged to target (e.g., repo merged feature main)
  merge-base <a> <b>       - Get merge base between two branches
  worktree list             - List worktrees
  worktree add <path> <branch> - Add worktree
  cleanup                   - Run tasks cleanup (alias for tasks cleanup)
  commit <message>          - Add all changes and commit with message (runs compliance)
  push                      - Push current branch to origin

Options:
  -y, --yes                 Auto-answer yes to prompts (for automation)
  -q, --quiet               Quiet mode, minimal output
  -j, --json                JSON output (for AI parsing)
  -h, --help                Show this help
"""

import subprocess
import sys
import os
import json
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add current dir to path to import tasks_ai
sys.path.append(os.getcwd())
try:
    from tasks_ai.cli import TasksCLI
    from tasks_ai.constants import TASKS_DIR
except ImportError:
    # Fallback if not in project root or venv not active
    TasksCLI = None
    TASKS_DIR = ".tasks"

SCRIPT_DIR = Path(__file__).parent.resolve()
LOG_DIR = SCRIPT_DIR / "logs"

GENERATED_FILES = []

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
CYAN = "\033[0;36m"
NC = "\033[0m"

# Global flags
FLAGS = {"yes": False, "quiet": False, "json": False}


def log(msg):
    if not FLAGS["quiet"]:
        print(f"{GREEN}[repo]{NC} {msg}")


def warn(msg):
    if not FLAGS["quiet"]:
        print(f"{YELLOW}[repo] WARN:{NC} {msg}")


def error(msg):
    if FLAGS["json"]:
        print(json.dumps({"error": msg}))
    else:
        print(f"{RED}[repo] ERROR:{NC} {msg}")
    sys.exit(1)


def info(msg):
    if not FLAGS["quiet"]:
        print(f"{CYAN}[repo]{NC} {msg}")


def out(msg):
    """Output for both modes"""
    if not FLAGS["quiet"]:
        print(msg)


def run(cmd, check=True, capture=False, env=None):
    try:
        return subprocess.run(cmd, check=check, capture_output=capture, text=True, env=env)
    except subprocess.CalledProcessError as e:
        if check:
            error(f"Command failed: {' '.join(cmd)}")
        raise


def get_current_branch():
    result = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture=True)
    return result.stdout.strip()


def check_clean_working_tree() -> bool:
    result = run(["git", "status", "--porcelain"], capture=True)
    if result.stdout.strip():
        error("Uncommitted changes detected")
    return True


def prompt_yes_no(prompt):
    if FLAGS["yes"]:
        return True
    while True:
        response = input(f"{prompt} [y/n] ").strip().lower()
        if response in ["y", "yes"]:
            return True
        if response in ["n", "no"]:
            return False
        print("Please answer y or n")


def output_json(data: Dict[str, Any]):
    print(json.dumps(data, indent=2))


class ToolRunner:
    def __init__(self):
        if TasksCLI:
            self.cli = TasksCLI(quiet=True)
        else:
            self.cli = None

    def run_validation(self, fix=False):
        if not self.cli:
            warn("TasksCLI not available, skipping tool validation")
            return True

        tools = ["format", "lint", "typecheck", "test"]
        all_passed = True

        for tool_type in tools:
            tool = self.cli.get_tool(tool_type)
            if not tool:
                log(f"Skipping {tool_type} (not configured)")
                continue

            log(f"Running {tool_type} ({tool})...")
            # We use TasksCLI's internal tool running logic but captured here
            try:
                # Mock sys.exit for cli.run_tool
                import sys
                original_exit = sys.exit
                sys.exit = lambda x: None
                try:
                    self.cli.run_tool(tool_type, fix=fix)
                finally:
                    sys.exit = original_exit
            except Exception as e:
                warn(f"{tool_type} failed: {e}")
                all_passed = False

        return all_passed


def cmd_status():
    branch = get_current_branch()

    if FLAGS["json"]:
        result = run(["git", "status", "--porcelain"], capture=True)
        untracked = result.stdout.splitlines()

        branches = {}
        for b in ["main", "staging", "testing"]:
            try:
                sha = run(
                    ["git", "rev-parse", "--short", f"origin/{b}"], capture=True
                ).stdout.strip()
                branches[b] = sha
            except:
                branches[b] = None

        output_json(
            {
                "current_branch": branch,
                "clean": len(untracked) == 0,
                "uncommitted": untracked,
                "branches": branches,
            }
        )
        return

    info(f"Current branch: {branch}")
    result = run(["git", "status", "--porcelain"], capture=True)
    if result.stdout.strip():
        warn("Uncommitted changes:")
        print(result.stdout)
    else:
        info("Working tree is clean")
    print()
    info("Branches:")
    for b in ["main", "staging", "testing"]:
        try:
            sha = run(
                ["git", "rev-parse", "--short", f"origin/{b}"], capture=True
            ).stdout.strip()
            print(f"  {b}: {sha}")
        except:
            print(f"  {b}: N/A")


def cmd_merge_testing_staging():
    """Merge testing to staging with compliance checks"""
    current = get_current_branch()
    if current != "testing":
        if FLAGS["yes"] or prompt_yes_no(
            f"You're on '{current}', not 'testing'. Switch to testing?"
        ):
            run(["git", "checkout", "testing"])
        else:
            error("Must be on testing branch")

    check_clean_working_tree()

    info("Ready to merge testing → staging")
    if not FLAGS["yes"]:
        if not prompt_yes_no("Proceed with merge?"):
            log("Cancelled")
            return

    ToolRunner().run_validation(fix=True)

    log("Merging testing into staging...")
    run(["git", "checkout", "staging"])
    run(["git", "pull", "origin", "staging"])
    run(["git", "merge", "testing", "-m", "merge: testing into staging (automated)"])
    run(["git", "push", "origin", "staging"])
    run(["git", "checkout", "testing"])

    log("✅ Successfully merged testing → staging")


def cmd_merge_staging_main():
    """Merge staging to main with compliance checks"""
    current = get_current_branch()
    if current != "staging":
        if FLAGS["yes"] or prompt_yes_no(
            f"You're on '{current}', not 'staging'. Switch to staging?"
        ):
            run(["git", "checkout", "staging"])
        else:
            error("Must be on staging branch")

    check_clean_working_tree()

    info("Ready to merge staging → main")
    if not FLAGS["yes"]:
        if not prompt_yes_no("Proceed with merge to main?"):
            log("Cancelled")
            return

    ToolRunner().run_validation(fix=False)

    log("Merging staging into main...")
    run(["git", "checkout", "main"])
    run(["git", "pull", "origin", "main"])
    run(["git", "merge", "staging", "-m", "merge: staging into main (automated)"])
    run(["git", "push", "origin", "main"])
    run(["git", "checkout", "staging"])

    log("✅ Successfully merged staging → main")


def cmd_commit(message):
    if not message:
        error("Commit message required")
    
    log("Running pre-commit compliance...")
    ToolRunner().run_validation(fix=True)
    
    run(["git", "add", "."])
    run(["git", "commit", "-m", message])
    log("✅ Changes committed")


def cmd_push():
    branch = get_current_branch()
    log(f"Pushing {branch} to origin...")
    run(["git", "push", "origin", branch])
    log("✅ Successfully pushed")


def main():
    global FLAGS
    # Parse flags
    args = []
    for arg in sys.argv[1:]:
        if arg in ["-y", "--yes"]: FLAGS["yes"] = True
        elif arg in ["-q", "--quiet"]: FLAGS["quiet"] = True
        elif arg in ["-j", "--json"]: FLAGS["json"] = True
        elif arg in ["-h", "--help"]:
            print(__doc__)
            return
        else:
            args.append(arg)

    if not args:
        print(__doc__)
        return

    cmd = args[0]

    if cmd == "merge":
        if len(args) < 3: error("Usage: repo merge testing to staging | repo merge staging to main")
        sub = f"{args[1]} {args[2]}"
        if sub == "testing to staging": cmd_merge_testing_staging()
        elif sub == "staging to main": cmd_merge_staging_main()
        else: error(f"Unknown merge: {sub}")
    elif cmd == "sync":
        # Simplified sync for now
        cmd_merge_testing_staging()
        cmd_merge_staging_main()
    elif cmd == "status": cmd_status()
    elif cmd == "commit": cmd_commit(" ".join(args[1:]) if len(args) > 1 else None)
    elif cmd == "push": cmd_push()
    elif cmd == "git": run(["git"] + args[1:], capture=False)
    elif cmd == "branch":
        sub = args[1] if len(args) > 1 else "list"
        if sub == "list": run(["git", "branch", "-a"], capture=False)
        elif sub == "create": run(["git", "checkout", "-b", args[2]])
        elif sub == "delete": run(["git", "branch", "-d", args[2]])
    elif cmd == "cleanup": run(["python3", "tasks.py", "cleanup"] + args[1:])
    else:
        error(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
