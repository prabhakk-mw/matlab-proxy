# Copyright 2025 The MathWorks, Inc.

import datetime
import os
import subprocess
from pathlib import Path
from shutil import which, rmtree
from typing import Any, Dict

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

__BUILD_MARKER_FILE = "mw_npm_build_marker.log"


def _is_npm_build_required(target_dir: Path) -> bool:
    """Check if there are any git changes (staged, unstaged, or untracked) in the matlab_proxy/gui folder.

    Returns:
        bool: True if there are changes, False otherwise
    """

    # Always rebuild in development mode
    if os.environ.get("MWI_DEV", None):
        return True

    try:
        # Force re-build if build marker file does not exist
        if not (target_dir / __BUILD_MARKER_FILE).exists():
            print("Target directory does not exist, npm build is required.")
            return True

        ## If the marker file exists, proceed with build only if there are git changes
        # Check if git is available
        if not which("git"):
            print("Git not found, assuming GUI changes exist.")
            return True

        # Check for any changes (staged, unstaged, or untracked) in the gui folder
        result = subprocess.run(
            ["git", "status", "--porcelain", "gui/"],
            capture_output=True,
            text=True,
            check=False,
        )

        # If there's any output, there are changes
        if result.stdout.strip():
            print("Detected changes in gui/ directory.")
            return True

        # Check if there are any committed changes that haven't been pushed
        result = subprocess.run(
            ["git", "log", "@{u}..", "--pretty=format:%H", "--", "gui/"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.stdout.strip():
            print("Detected unpushed commits affecting gui/ directory.")
            return True

        print("No changes detected in gui/ directory, skipping npm build.")
        return False
    except Exception as e:
        print(f"Error checking for GUI changes: {e}. Assuming changes exist.")
        return True


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
    return major, minor


def _get_npm() -> tuple[Path, int, int]:
    """Return path to npm executable, raise error if not found."""
    npm_path = which("npm")
    major, minor = _ensure_npm_compatibility(npm_path)
    return (Path(npm_path), major, minor)


def _finalize_target_dir(
    target_dir: Path, npm_major_ver: int, npm_minor_ver: int
) -> None:
    """Prepares target directory to be read as python modules and leaves build marker file."""
    # Create __init__.py files to make directories into Python modules
    (target_dir / "__init__.py").touch(exist_ok=True)
    for root, dirs, _ in os.walk(target_dir):
        for directory in dirs:
            (Path(root) / directory / "__init__.py").touch(exist_ok=True)

    # Get current time in UTC, as a timezone-aware datetime object
    utc_now = datetime.datetime.now(datetime.timezone.utc)

    # Convert the UTC datetime object to a Unix timestamp
    utc_timestamp = utc_now.timestamp()

    # Create build marker file, which can be used to skip future builds if no changes are detected
    marker_file_name = target_dir / __BUILD_MARKER_FILE
    new_content = (
        f"Built date: {utc_timestamp} \nnpm_version: {npm_major_ver}.{npm_minor_ver}\n"
    )

    try:
        # Open the file in 'w' mode.
        # If the file exists, its content will be truncated (erased).
        # If the file does not exist, a new file will be created.
        with open(marker_file_name, "w") as marker_file:
            marker_file.write(new_content)

    except IOError as e:
        print(f"Error writing to file: {e}")
        raise EnvironmentError(
            "Failed to create build marker file, check file permissions."
        )


class CustomBuildHook(BuildHookInterface):
    #  Identifier that connects this Python hook class to pyproject.toml configuration
    PLUGIN_NAME = "custom"

    def initialize(self, version: str, build_data: Dict[str, Any]) -> None:
        """Run npm install and build, then copy files to package."""

        project_root = Path.cwd()
        src_dir = project_root / "gui"
        target_dir = project_root / "matlab_proxy" / "gui"

        # Skip npm build if no GUI changes
        if not _is_npm_build_required(target_dir=target_dir):
            print(
                "Skipping npm build process as no changes requiring a node rebuild were detected."
            )
            return

        npm_path, npm_major_ver, npm_minor_ver = _get_npm()

        # Adding retries to npm install to avoid transient rate limiting issues
        npm_install_cmd = [npm_path, "install", "--fetch-retries", "10"]
        npm_build_cmd = [npm_path, "run", "build"]

        # Install dependencies and build npm project
        try:
            os.chdir(src_dir)

            # "npm install" creates: node_modules, package-lock.json
            subprocess.run(npm_install_cmd, check=True)
            print("npm installation completed successfully.")

            # "npm build" runs "vite build" which writes the results to the target directory
            subprocess.run(npm_build_cmd, check=True)
            _finalize_target_dir(
                target_dir=target_dir,
                npm_major_ver=npm_major_ver,
                npm_minor_ver=npm_minor_ver,
            )
            print("npm build completed successfully.")
        finally:
            # Clean up build artifacts from npm install
            if not os.environ.get("MWI_DEV", None):
                rmtree(src_dir / "node_modules", ignore_errors=True)
            # Reset working directory
            os.chdir(project_root)

        print("Build hook step completed!")
