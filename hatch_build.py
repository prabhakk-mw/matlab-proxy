# Copyright 2025 The MathWorks, Inc.

import os
import subprocess
from pathlib import Path
from shutil import copytree, which, rmtree, move
from typing import Any, Dict

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


def _get_npm() -> Path:
    """Return path to npm executable, raise error if not found."""
    npm_path = which("npm")
    if npm_path is None:
        raise EnvironmentError(
            "npm is not installed or not found in PATH. Please install Node.js and npm to proceed."
        )
    return npm_path


class CustomBuildHook(BuildHookInterface):
    #  Identifier that connects this Python hook class to pyproject.toml configuration
    PLUGIN_NAME = "custom"

    def initialize(self, version: str, build_data: Dict[str, Any]) -> None:
        """Run npm install and build, then copy files to package."""

        npm_path = _get_npm()

        # Adding retries to npm install to avoid transient rate limiting issues
        npm_install_cmd = [npm_path, "install", "--fetch-retries", "10"]
        npm_build_cmd = [npm_path, "run", "build"]

        project_root = Path.cwd()
        src = project_root / "gui"
        dest = project_root / "matlab_proxy" / "gui"

        # Delete old installation
        rmtree(dest, ignore_errors=True)

        # Install dependencies and build npm project
        try:
            os.chdir(src)

            # "npm install" creates: node_modules, package-lock.json
            subprocess.run(npm_install_cmd, check=True)
            print("npm installation completed successfully.")

            # "npm build" creates writes to the "dest" directory as per vite.config.js
            subprocess.run(npm_build_cmd, check=True)
            # Create __init__.py files to make directories into Python modules
            (dest / "__init__.py").touch(exist_ok=True)
            for root, dirs, _ in os.walk(dest):
                for directory in dirs:
                    (Path(root) / directory / "__init__.py").touch(exist_ok=True)

            print("npm build completed successfully.")
        finally:
            # Clean up build artifacts from npm install
            if not os.environ.get("MWI_DEV", None):
                rmtree(src / "node_modules", ignore_errors=True)
            # Reset working directory
            os.chdir(project_root)

        print("Build hook step completed!")
