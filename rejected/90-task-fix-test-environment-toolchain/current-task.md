# Current Task: Fix test environment toolchain initialization

## Investigation
- **Problem**: Temporary test repositories (`/tmp/tmp*`) lack the necessary toolchain (`ruff`, `pytest`, `pyright`) and configuration to pass `check.py` validation. 
- **Current Approach**: Attempted copying/symlinking `check.py`, `repo.py`, `venv`, and a mocked `config.yaml` to the temporary repo during `TestTasksAI.setUp()`. 
- **Issues**: Symlinking `venv` into the temp directory is problematic due to absolute paths in generated executables. Simply pointing to the host's tool binaries in `.tasks/config.yaml` is the most viable path forward for consistency.

## Plan
1. **Toolchain Configuration**: Update `TestTasksAI.setUp` to detect local paths of `ruff`, `pytest`, `pyright` and write a correct `config.yaml` using these absolute paths.
2. **Resource Injection**: Ensure `check.py` and `repo.py` are properly available in the test environment.
3. **Verification**: Validate that pipeline transitions (e.g., `move to TESTING`) succeed without validation bypasses.
