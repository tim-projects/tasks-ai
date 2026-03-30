import pytest
import os
import shutil
import sys
import tempfile
import subprocess
from tasks_ai.cli import TasksCLI

@pytest.fixture
def setup_tasks():
    # Setup a temp environment
    sys._called_from_test = True
    test_dir = tempfile.mkdtemp()
    repo_dir = os.path.join(test_dir, "repo")
    os.makedirs(repo_dir)
    
    # Init git
    subprocess.run(["git", "init"], cwd=repo_dir, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_dir)
    
    # Move to repo_dir
    old_cwd = os.getcwd()
    os.chdir(repo_dir)
    
    cli = TasksCLI()
    cli.init()
    
    yield cli
    
    # Cleanup
    os.chdir(old_cwd)
    shutil.rmtree(test_dir)
    del sys._called_from_test

def test_create_and_modify(setup_tasks):
    cli = setup_tasks
    cli.create(
        "Valid Task Title", 
        story="As a user...", 
        tech="Python", 
        criteria=["Pass"], 
        plan=["Step 1"]
    )
    task_id = "1" 
    filepath, state = cli.find_task(task_id)
    assert state == "BACKLOG"
    assert filepath is not None
    
    cli.modify(task_id, title="Updated Valid Task Title")
    filepath, _ = cli.find_task(task_id)
    assert filepath is not None

def test_move_and_delete(setup_tasks):
    cli = setup_tasks
    cli.create("Move Test Task Name", story="S", tech="T", criteria=["C"], plan=["P"])
    task_id = "1"
    
    # Move through states
    cli.move(task_id, "READY")
    _, state = cli.find_task(task_id)
    assert state == "READY"
    
    # Test delete confirmation
    from tasks_ai.file_manager import FM
    path, _ = cli.find_task(task_id)
    
    # First call marks for deletion
    try:
        cli.delete(task_id)
    except SystemExit:
        pass
    
    # Reload to get DeleteCode
    task = FM.load(path)
    assert "DeleteCode" in task.metadata
    
    code = task.metadata["DeleteCode"]
    cli.delete(task_id, confirm=code)
    path, _ = cli.find_task(task_id)
    assert path is None

def test_link_tasks(setup_tasks):
    cli = setup_tasks
    cli.create("Task A Title Long", story="S", tech="T", criteria=["C"], plan=["P"])
    cli.create("Task B Title Long", story="S", tech="T", criteria=["C"], plan=["P"])
    cli.link("1", "2")
    
    from tasks_ai.file_manager import FM
    path, _ = cli.find_task("1")
    task = FM.load(path)
    assert "2" in task.metadata.get("BlockedBy", [])
