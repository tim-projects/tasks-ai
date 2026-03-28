import os
import subprocess
import shutil
import tempfile
import json
import sys
import pytest
from datetime import datetime, timedelta
from pathlib import Path

# Path to the tasks.py script
SCRIPT_PATH = os.path.abspath("tasks.py")


@pytest.fixture
def repo_info():
    """Create a temporary git repository for testing and return (path, branch)."""
    test_dir = tempfile.mkdtemp()
    repo_path = os.path.join(test_dir, "repo")
    os.makedirs(repo_path)

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=repo_path, capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"], cwd=repo_path, check=True
    )

    # Initial commit on main branch
    readme_path = os.path.join(repo_path, "README.md")
    with open(readme_path, "w") as f:
        f.write("# Test Repo")
    subprocess.run(["git", "add", "README.md"], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True)

    # Get branch name
    res = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    branch = res.stdout.strip()

    yield repo_path, branch

    # Cleanup
    shutil.rmtree(test_dir)


def run_cmd(repo_path, args, input_str=None):
    """Run the tasks-ai command and return the JSON output."""
    cmd = [sys.executable, SCRIPT_PATH, "-j"] + args
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.dirname(SCRIPT_PATH)
    result = subprocess.run(
        cmd, cwd=repo_path, input=input_str, capture_output=True, text=True, env=env
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "JSON Decode Error",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
        }


def test_init(repo_info):
    """Test 'init' command."""
    repo_path, _ = repo_info
    res = run_cmd(repo_path, ["init"])
    assert res["success"] is True, res
    assert os.path.exists(os.path.join(repo_path, ".tasks"))
    # Check git logging
    assert any(m.startswith("Git: ") for m in res["messages"]), res["messages"]


def test_create_and_git_logging(repo_info):
    """Test task creation and verify git action logging."""
    repo_path, branch = repo_info
    run_cmd(repo_path, ["init"])
    # Ensure we are on the default branch before creating
    subprocess.run(["git", "checkout", branch], cwd=repo_path, check=True)
    
    res = run_cmd(
        repo_path,
        [
            "create",
            "Test Task Logging",
            "--story",
            "As a tester, I want logging.",
            "--tech",
            "Subprocess capture.",
            "--criteria",
            "Log exists.",
            "--plan",
            "1. Run git.",
        ],
    )
    assert res["success"] is True, res
    # Verify git log messages
    assert any("Git: Committed changes" in m for m in res["messages"]), res["messages"]
    assert any(
        "Git: Created and switched to branch" in m for m in res["messages"]
    ), res["messages"]


def test_rejected_lifecycle(repo_info):
    """Test the new REJECTED status and transitions."""
    repo_path, branch = repo_info
    run_cmd(repo_path, ["init"])
    subprocess.run(["git", "checkout", branch], cwd=repo_path, check=True)
    
    res = run_cmd(
        repo_path,
        [
            "create",
            "Rejectable Task",
            "--story",
            "S" * 10,
            "--tech",
            "T" * 10,
            "--criteria",
            "C" * 10,
            "--plan",
            "P" * 10,
        ],
    )
    task_id = res["data"]["task_id"]

    # Move to TESTING (allowed: BACKLOG->READY->PROGRESSING->TESTING)
    m_res = run_cmd(repo_path, ["move", "1", "READY,PROGRESSING,TESTING"])
    assert m_res["success"] is True, m_res

    # Move to REJECTED (allowed: TESTING->REJECTED)
    res = run_cmd(repo_path, ["move", "1", "REJECTED"])
    assert res["success"] is True, res
    assert res["data"]["status"] == "REJECTED"
    assert os.path.exists(os.path.join(repo_path, ".tasks", "rejected", task_id))

    # Move REJECTED -> PROGRESSING (allowed)
    res = run_cmd(repo_path, ["move", "1", "PROGRESSING"])
    assert res["success"] is True, res
    assert res["data"]["status"] == "PROGRESSING"


def test_backward_moves_complex(repo_info):
    """Test all new backward transitions: REVIEW/ARCHIVED -> PROGRESSING."""
    repo_path, branch = repo_info
    run_cmd(repo_path, ["init"])
    subprocess.run(["git", "checkout", branch], cwd=repo_path, check=True)
    
    res = run_cmd(
        repo_path,
        [
            "create",
            "Backward Task",
            "--story",
            "S" * 10,
            "--tech",
            "T" * 10,
            "--criteria",
            "C" * 10,
            "--plan",
            "P" * 10,
        ],
    )
    task_id = res["data"]["task_id"]

    # 1. REVIEW -> PROGRESSING
    m_res = run_cmd(repo_path, ["move", "1", "READY,PROGRESSING,TESTING,REVIEW"])
    assert m_res["success"] is True, m_res
    res = run_cmd(repo_path, ["move", "1", "PROGRESSING"])
    assert res["success"] is True, res
    assert res["data"]["status"] == "PROGRESSING"

    # 2. ARCHIVED -> PROGRESSING
    # Setup for ARCHIVED: 
    # a) Complete checkboxes
    criteria_path = os.path.join(repo_path, ".tasks", "progressing", task_id, "criteria.md")
    with open(criteria_path, "w") as f:
        f.write("- [x] Done\n")
    
    # b) Promote to STAGING
    run_cmd(repo_path, ["move", "1", "TESTING,REVIEW,STAGING"])
    
    # c) Merge to default branch
    subprocess.run(["git", "checkout", branch], cwd=repo_path, check=True)
    subprocess.run(["git", "merge", "--allow-unrelated-histories", "-m", "Merge for test", task_id], cwd=repo_path, check=True)
    
    # d) Delete branch
    subprocess.run(["git", "branch", "-D", task_id], cwd=repo_path, check=True)

    # e) Move to ARCHIVED
    res = run_cmd(repo_path, ["move", "1", "ARCHIVED", "-y"])
    assert res["success"] is True, res

    res = run_cmd(repo_path, ["move", "1", "PROGRESSING"])
    assert res["success"] is True, res
    assert res["data"]["status"] == "PROGRESSING"


def test_cleanup_workflow(repo_info):
    """Test the cleanup command (reconcile --all)."""
    repo_path, branch = repo_info
    run_cmd(repo_path, ["init"])
    subprocess.run(["git", "checkout", branch], cwd=repo_path, check=True)
    
    res = run_cmd(
        repo_path,
        [
            "create",
            "Merged Task",
            "--story",
            "S" * 10,
            "--tech",
            "T" * 10,
            "--criteria",
            "C" * 10,
            "--plan",
            "P" * 10,
        ],
    )
    task_id = res["data"]["task_id"]

    # Complete checkboxes
    criteria_path = os.path.join(repo_path, ".tasks", "backlog", task_id, "criteria.md")
    with open(criteria_path, "w") as f:
        f.write("- [x] Done\n")

    # Move to REVIEW
    run_cmd(repo_path, ["move", "1", "READY,PROGRESSING,TESTING,REVIEW"])

    # Merge to default branch
    subprocess.run(["git", "checkout", branch], cwd=repo_path, check=True)
    subprocess.run(["git", "merge", "--allow-unrelated-histories", "-m", "Merge for cleanup", task_id], cwd=repo_path, check=True)

    # Reconcile (dry run scan)
    res = run_cmd(repo_path, ["reconcile"])
    assert res["success"] is True, res
    assert len(res["data"]["cleaned"]) >= 1
    assert any(task_id == c for c in res["data"]["cleaned"])

    # Reconcile --all (performs cleanup)
    res = run_cmd(repo_path, ["reconcile", "--all"])
    assert res["success"] is True, res
    assert any(task_id == c for c in res["data"]["cleaned"])

    # Verify branch deleted and task archived
    branches = subprocess.run(
        ["git", "branch"], cwd=repo_path, capture_output=True, text=True
    ).stdout
    assert task_id not in branches
    assert os.path.exists(os.path.join(repo_path, ".tasks", "archived", task_id))


def test_config_and_tools(repo_info):
    """Test configuration detection and tool execution."""
    repo_path, _ = repo_info
    run_cmd(repo_path, ["init"])

    # Create dummy pytest config to be detected
    with open(os.path.join(repo_path, "pyproject.toml"), "w") as f:
        f.write('[tool.pytest.ini_options]\ntestpaths = ["."]')

    # Detect
    res = run_cmd(repo_path, ["config", "detect"])
    assert res["success"] is True, res
    assert res["data"]["detected"]["test"] == "pytest"

    # Save detection
    res = run_cmd(repo_path, ["config", "detect", "--save"])
    assert res["success"] is True, res

    # Verify saved
    res = run_cmd(repo_path, ["config", "list"])
    assert res["data"]["repo.test"] == "pytest"


def test_link_and_block_lifecycle(repo_info):
    """Test blocking logic with new transitions."""
    repo_path, branch = repo_info
    run_cmd(repo_path, ["init"])
    subprocess.run(["git", "checkout", branch], cwd=repo_path, check=True)
    
    res1 = run_cmd(
        repo_path,
        [
            "create",
            "Blocker Task",
            "--story",
            "S" * 10,
            "--tech",
            "T" * 10,
            "--criteria",
            "C" * 10,
            "--plan",
            "P" * 10,
        ],
    )
    res2 = run_cmd(
        repo_path,
        [
            "create",
            "Blocked Task",
            "--story",
            "S" * 10,
            "--tech",
            "T" * 10,
            "--criteria",
            "C" * 10,
            "--plan",
            "P" * 10,
        ],
    )
    task_id1 = res1["data"]["task_id"]

    # Complete checkboxes for blocker
    cp = os.path.join(repo_path, ".tasks", "backlog", task_id1, "criteria.md")
    with open(cp, "w") as f:
        f.write("- [x] Done\n")

    # Link 2 to 1
    run_cmd(repo_path, ["link", "2", "1"])

    # Attempt to move Blocked to PROGRESSING (should fail)
    res = run_cmd(repo_path, ["move", "2", "PROGRESSING"])
    assert res["success"] is False
    assert "Blocked by" in res["error"]

    # Archive Blocker
    run_cmd(repo_path, ["move", "1", "READY,PROGRESSING,TESTING,REVIEW,STAGING"])
    # Mock merge for archive
    subprocess.run(["git", "checkout", branch], cwd=repo_path, check=True)
    subprocess.run(["git", "merge", "--allow-unrelated-histories", "-m", "Merge blocker", task_id1], cwd=repo_path, check=True)
    subprocess.run(["git", "branch", "-D", task_id1], cwd=repo_path, check=True)
    run_cmd(repo_path, ["move", "1", "ARCHIVED", "-y"])

    # Now attempt Blocked to PROGRESSING (should succeed)
    res = run_cmd(repo_path, ["move", "2", "PROGRESSING"])
    assert res["success"] is True, res
