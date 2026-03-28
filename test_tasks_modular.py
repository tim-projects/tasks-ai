import pytest
import os
import shutil
import sys
from tasks_ai.cli import TasksCLI

# Helper to run CLI
def run_cli(args):
    # We can mock the CLI or just run it directly. 
    # For a thorough test, we'll instantiate the class and call methods.
    # We need to simulate the environment.
    pass

@pytest.fixture
def setup_tasks():
    # Setup a temp environment
    sys._called_from_test = True
    os.makedirs(".tasks", exist_ok=True)
    # Mocking init
    cli = TasksCLI()
    cli.init()
    yield cli
    # Cleanup
    del sys._called_from_test
    if os.path.exists(".tasks"):
        shutil.rmtree(".tasks")
    if os.path.exists("tasks"):
        shutil.rmtree("tasks")

def test_create_and_modify(setup_tasks):
    cli = setup_tasks
    cli.create(
        "Valid Task Title", 
        story="As a user...", 
        tech="Python", 
        criteria=["Pass"], 
        plan=["Step 1"]
    )
    task_id = "task_valid-task-title"
    filepath, state = cli.find_task(task_id)
    assert state == "BACKLOG"
    
    cli.modify(task_id, title="Updated Valid Task Title")
    filepath, _ = cli.find_task(task_id) # The filename shouldn't change when title changes
    assert filepath is not None

def test_move_and_delete(setup_tasks):
    cli = setup_tasks
    cli.create("Move Test Task Name", story="S", tech="T", criteria=["C"], plan=["P"])
    task_id = "task_move-test-task-name"
    
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
    cli.link("task_task-a-title-long", "task_task-b-title-long")
    
    from tasks_ai.file_manager import FM
    path, _ = cli.find_task("task_task-a-title-long")
    task = FM.load(path)
    assert "task_task-b-title-long" in task["Bl"]

def test_reconcile(setup_tasks):
    # This is complex due to git dependency.
    # We can test the reconcile logic partially.
    pass
