The current test environment initialization in  fails to properly configure validation tools (, ============================= test session starts ==============================
platform linux -- Python 3.11.2, pytest-7.2.1, pluggy-1.0.0+repack
rootdir: /home/vscode/git/tasks-ai
plugins: mock-3.15.1
collected 68 items / 3 errors

==================================== ERRORS ====================================
___________________ ERROR collecting tests/test_security.py ____________________
ImportError while importing test module '/home/vscode/git/tasks-ai/tests/test_security.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests/test_security.py:5: in <module>
    from tasks_ai.cli import TasksCLI
E   ModuleNotFoundError: No module named 'tasks_ai'
_____________________ ERROR collecting tests/test_tasks.py _____________________
ImportError while importing test module '/home/vscode/git/tasks-ai/tests/test_tasks.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests/test_tasks.py:11: in <module>
    from tasks_ai.file_manager import FM
E   ModuleNotFoundError: No module named 'tasks_ai'
_________________ ERROR collecting tests/test_tasks_modular.py _________________
ImportError while importing test module '/home/vscode/git/tasks-ai/tests/test_tasks_modular.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests/test_tasks_modular.py:7: in <module>
    from tasks_ai.cli import TasksCLI
E   ModuleNotFoundError: No module named 'tasks_ai'
=========================== short test summary info ============================
ERROR tests/test_security.py
ERROR tests/test_tasks.py
ERROR tests/test_tasks_modular.py
!!!!!!!!!!!!!!!!!!! Interrupted: 3 errors during collection !!!!!!!!!!!!!!!!!!!!
============================== 3 errors in 0.10s ===============================, , etc.), leading to false-positive validation failures in temporary repositories. We should symlink or replicate the development environment's toolchain (venv) into the test repositories to ensure consistency.