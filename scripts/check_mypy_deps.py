#!/usr/bin/env python
"""Verify that the mypy hook's additional_dependencies in .pre-commit-config.yaml
includes all runtime dependencies declared in pyproject.toml.

Run directly or via pre-commit (check-mypy-deps hook).
"""

from __future__ import annotations

import sys

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-reuse-def]

import yaml
from packaging.requirements import Requirement


def normalize(name: str) -> str:
    return name.lower().replace("-", "_").replace(".", "_")


def main() -> int:
    with open("pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)

    with open(".pre-commit-config.yaml") as f:
        pre_commit = yaml.safe_load(f)

    project_deps: list[str] = pyproject["project"]["dependencies"]
    project_packages = {normalize(Requirement(dep).name) for dep in project_deps}

    mypy_additional: list[str] | None = None
    for repo in pre_commit["repos"]:
        for hook in repo.get("hooks", []):
            if hook["id"] == "mypy":
                mypy_additional = hook.get("additional_dependencies", [])
                break
        if mypy_additional is not None:
            break

    if mypy_additional is None:
        print("ERROR: mypy hook not found in .pre-commit-config.yaml")
        return 1

    mypy_packages = {normalize(Requirement(dep).name) for dep in mypy_additional}

    missing = project_packages - mypy_packages
    if missing:
        print(
            "ERROR: The following project dependencies are missing from the mypy\n"
            "hook's additional_dependencies in .pre-commit-config.yaml:\n"
        )
        for pkg in sorted(missing):
            print(f"  {pkg}")
        print("\nAdd them to the `additional_dependencies` list of the mypy hook.")
        return 1

    print("OK: mypy additional_dependencies covers all project runtime dependencies.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
