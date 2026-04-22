import unittest
import shutil
import os
import subprocess
import sys


class TestCLIRobustness(unittest.TestCase):
    def setUp(self):
        self.test_dir = "/tmp/test_cli_robustness"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        self.repo_dir = os.path.join(self.test_dir, "repo")
        os.makedirs(self.repo_dir)
        # Assuming script paths
        self.tasks_py = os.path.join(os.getcwd(), "tasks.py")
        self.repo_py = os.path.join(os.getcwd(), "repo.py")
        self.check_py = os.path.join(os.getcwd(), "check.py")

        # Init repo
        subprocess.run(["git", "init"], cwd=self.repo_dir, capture_output=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_repo_validation_failure(self):
        """repo commit should fail if validation tools fail or are missing."""
        subprocess.run(
            [sys.executable, self.tasks_py, "init"],
            cwd=self.repo_dir,
            capture_output=True,
        )

        # Copy check.py to temp repo because repo.py calls it
        shutil.copy(self.check_py, self.repo_dir)

        # Configure a tool that is missing from PATH
        subprocess.run(
            [sys.executable, self.tasks_py, "config", "set", "repo.lint", "ruff"],
            cwd=self.repo_dir,
            capture_output=True,
        )

        # Create a change to commit
        with open(os.path.join(self.repo_dir, "change.txt"), "w") as f:
            f.write("change")

        # Run repo commit - should fail because ruff is missing (unless installed)
        subprocess.run(
            [
                sys.executable,
                self.tasks_py,
                "config",
                "set",
                "repo.lint",
                "missing-command",
            ],
            cwd=self.repo_dir,
            capture_output=True,
        )

        result = subprocess.run(
            [sys.executable, self.repo_py, "commit", "test commit"],
            cwd=self.repo_dir,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("failed", result.stdout + result.stderr)

    def test_create_validation_missing_fields(self):
        """Task create should fail if required fields are missing."""
        subprocess.run(
            [sys.executable, self.tasks_py, "init"],
            cwd=self.repo_dir,
            capture_output=True,
        )

        # Test with missing fields
        result = subprocess.run(
            [
                sys.executable,
                self.tasks_py,
                "create",
                "Valid Task Title Here",
            ],
            cwd=self.repo_dir,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("MISSING PARTS", result.stderr)

    def test_create_validation_short_fields(self):
        """Task create should fail if fields are too short."""
        subprocess.run(
            [sys.executable, self.tasks_py, "init"],
            cwd=self.repo_dir,
            capture_output=True,
        )

        # Test with too short fields
        result = subprocess.run(
            [
                sys.executable,
                self.tasks_py,
                "create",
                "Valid Task Title Here",
                "--story",
                "Short",
                "--tech",
                "Short",
                "--criteria",
                "Short",
                "--plan",
                "Short",
            ],
            cwd=self.repo_dir,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("TOO SHORT", result.stderr)


if __name__ == "__main__":
    unittest.main()
