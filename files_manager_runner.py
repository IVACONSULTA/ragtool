#!/usr/bin/env python3
"""
Files Management Runner

Simple wrapper to run the files management script from the project root.
This avoids Python path issues by running from the correct directory.

Usage:
    python files_manager_runner.py [arguments]

Examples:
    python files_manager_runner.py --list
    python files_manager_runner.py --add data/raw/new.pdf
    python files_manager_runner.py --add data/raw/data.csv
    python files_manager_runner.py --force
    python files_manager_runner.py --supported
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    # Get the project root directory
    project_root = Path(__file__).parent

    # Path to the actual files_manager script
    script_path = project_root / "agents" / "utils" / "files_manager.py"

    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        sys.exit(1)

    # Change to project root directory
    os.chdir(project_root)

    # Check if we're in a virtual environment
    venv_path = project_root / ".venv"
    if venv_path.exists() and "VIRTUAL_ENV" not in os.environ:
        # Activate virtual environment and run
        if os.name == "nt":  # Windows
            python_exe = venv_path / "Scripts" / "python.exe"
        else:  # Unix/Linux
            python_exe = venv_path / "bin" / "python"

        if python_exe.exists():
            cmd = [str(python_exe), str(script_path)] + sys.argv[1:]
        else:
            cmd = [sys.executable, str(script_path)] + sys.argv[1:]
    else:
        # Use current Python interpreter
        cmd = [sys.executable, str(script_path)] + sys.argv[1:]

    try:
        # Run the command and wait for completion
        result = subprocess.run(cmd, cwd=project_root)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running script: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
