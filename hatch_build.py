# Copyright 2025 The MathWorks, Inc.

import os
import subprocess
from pathlib import Path
from shutil import copytree, which, rmtree, move
from typing import Any, Dict

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


def _ensure_npm_compatibility(npm_path: str) -> None:
    if npm_path is None:
        raise EnvironmentError(
            "npm is not installed or not found in PATH. Please install Node.js and npm to proceed."
        )

    # Verify npm version is v11.3 or newer
    result = subprocess.run(
        [npm_path, "--version"], capture_output=True, text=True, check=True
    )
    version_str = result.stdout.strip()
    version_parts = version_str.lstrip("v").split(".")
    major, minor = int(version_parts[0]), int(version_parts[1])

    if (major, minor) < (11, 3):
        raise EnvironmentError(
            f"npm version {version_str} is not supported. Please upgrade to v11.3 or newer."
        )


def _get_npm() -> Path:
    """Return path to npm executable, raise error if not found."""
    npm_path = which("npm")

    _ensure_npm_compatibility(npm_path)

    return Path(npm_path)


def _initialize_as_python_modules(target_dir: Path) -> None:
    # Create __init__.py files to make directories into Python modules
    (target_dir / "__init__.py").touch(exist_ok=True)
    for root, dirs, _ in os.walk(target_dir):
        for directory in dirs:
            (Path(root) / directory / "__init__.py").touch(exist_ok=True)


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
        src_dir = project_root / "gui"
        target_dir = project_root / "matlab_proxy" / "gui"

        # Install dependencies and build npm project
        try:
            os.chdir(src_dir)

            # "npm install" creates: node_modules, package-lock.json
            subprocess.run(npm_install_cmd, check=True)
            print("npm installation completed successfully.")

            # "npm build" runs "vite build" which writes the results to the target directory
            subprocess.run(npm_build_cmd, check=True)
            _initialize_as_python_modules(target_dir=target_dir)
            print("npm build completed successfully.")
        finally:
            # Clean up build artifacts from npm install
            if not os.environ.get("MWI_DEV", None):
                rmtree(src_dir / "node_modules", ignore_errors=True)
            # Reset working directory
            os.chdir(project_root)

        print("Build hook step completed!")
