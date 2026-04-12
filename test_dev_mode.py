import subprocess
import os
import shutil
import json
import unittest
import sys


class TestDevMode(unittest.TestCase):
    def setUp(self):
        self.dev_dir = "/tmp/.tasks"
        if os.path.exists(self.dev_dir):
            shutil.rmtree(self.dev_dir)

        # Ensure we are in git root
        self.root = (
            subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
            .decode()
            .strip()
        )
        os.chdir(self.root)

    def tearDown(self):
        if os.path.exists(self.dev_dir):
            shutil.rmtree(self.dev_dir)

    def run_tasks(self, args):
        cmd = [sys.executable, "tasks.py", "--dev"] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result

    def test_dev_lifecycle(self):
        # 1. Init
        res = subprocess.run(
            [sys.executable, "tasks.py", "--dev", "init"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        self.assertTrue(os.path.exists(self.dev_dir))
        self.assertTrue(os.path.exists(os.path.join(self.dev_dir, "backlog")))

        # 2. Create
        res = subprocess.run(
            [
                sys.executable,
                "tasks.py",
                "-j",
                "--dev",
                "create",
                "Dev Task Test",
                "--story",
                "As a dev I want to test dev mode",
                "--tech",
                "Using /tmp/.tasks",
                "--criteria",
                "Task exists in /tmp",
                "--plan",
                "1. Run this test",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        task_id = data["data"]["id"]
        self.assertEqual(task_id, 1)

        # Verify it's in /tmp and NOT in project .tasks
        dev_backlog = os.path.join(self.dev_dir, "backlog")
        items = os.listdir(dev_backlog)
        self.assertTrue(any("1-task-dev-task-test" in item for item in items))

        project_tasks = os.path.join(self.root, ".tasks")
        # Ensure no task with that branch name was created in the real project tasks
        for root, dirs, files in os.walk(project_tasks):
            for d in dirs:
                self.assertFalse("1-task-dev-task-test" in d)

        # 3. List
        res = subprocess.run(
            [sys.executable, "tasks.py", "-j", "--dev", "list"],
            capture_output=True,
            text=True,
        )
        data = json.loads(res.stdout)
        self.assertEqual(len(data["data"]["BACKLOG"]), 1)

        # 4. Modify
        res = subprocess.run(
            [
                sys.executable,
                "tasks.py",
                "-j",
                "--dev",
                "modify",
                "1",
                "--progress",
                "Working in dev",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)

        # 5. Move
        res = subprocess.run(
            [
                sys.executable,
                "tasks.py",
                "-j",
                "--dev",
                "move",
                "1",
                "READY,PROGRESSING",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        self.assertTrue(os.path.exists(os.path.join(self.dev_dir, "progressing")))

        # 6. Delete
        res = subprocess.run(
            [sys.executable, "tasks.py", "-j", "--dev", "delete", "1"],
            capture_output=True,
            text=True,
        )
        data = json.loads(res.stdout)
        code = data["data"]["delete_code"]

        res = subprocess.run(
            [
                sys.executable,
                "tasks.py",
                "-j",
                "--dev",
                "delete",
                "1",
                "--confirm",
                code,
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)

        # Verify empty
        res = subprocess.run(
            [sys.executable, "tasks.py", "-j", "--dev", "list"],
            capture_output=True,
            text=True,
        )
        data = json.loads(res.stdout)
        self.assertFalse("BACKLOG" in data["data"])
        self.assertFalse("PROGRESSING" in data["data"])

    def test_config_dev(self):
        # Init
        subprocess.run(
            [sys.executable, "tasks.py", "--dev", "init"], capture_output=True
        )

        # Set a config in dev mode
        res = subprocess.run(
            [
                sys.executable,
                "tasks.py",
                "--dev",
                "config",
                "set",
                "tasks_dir",
                "/tmp/custom",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)

        # Check if it's in /tmp/.tasks/config.yaml
        config_path = os.path.join(self.dev_dir, "config.yaml")
        self.assertTrue(os.path.exists(config_path))
        with open(config_path, "r") as f:
            content = f.read()
            self.assertIn("tasks_dir: /tmp/custom", content)

        # Check that project config is unchanged
        project_config = os.path.join(self.root, ".tasks", "config.yaml")
        if os.path.exists(project_config):
            with open(project_config, "r") as f:
                content = f.read()
                self.assertNotIn("tasks_dir: /tmp/custom", content)


if __name__ == "__main__":
    # Clean up any leftover branch from previous aborted tests
    subprocess.run(["git", "branch", "-D", "1-task-dev-task-test"], capture_output=True)
    unittest.main()
