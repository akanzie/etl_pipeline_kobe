#!/usr/bin/env python3
"""Validate Airflow DAG files for common anti-patterns.

Checks for top-level code that may cause scheduler performance issues.
Airflow best practice: Top-level code should only define DAGs, operators, and imports.
It should NOT make DB connections, API calls, or heavy computations.

Usage:
    python validate_dag_integrity.py <path_to_python_file_or_directory>
"""

import ast
import sys
from pathlib import Path

from loguru import logger


def check_file(filepath: Path) -> bool:
    """Parse a Python file and check for top-level code anti-patterns.

    Args:
        filepath: Path to the Python file to validate.

    Returns:
        True if no issues found, False otherwise.
    """
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as e:
        logger.error("Syntax error in {}: {}", filepath, e)
        return False

    issues: list[str] = []

    for node in tree.body:
        # Allow imports
        if isinstance(node, ast.Import | ast.ImportFrom):
            continue

        # Allow assignments (constants, DAG definitions)
        if isinstance(node, ast.Assign):
            continue

        # Allow function and class definitions
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            continue

        # Allow simple expressions (docstrings are Expr with Constant value)
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue

        # Allow 'with DAG(...) as dag:' context managers (common Airflow pattern)
        if isinstance(node, ast.With):
            continue

        # Flag top-level expressions that may perform I/O
        if isinstance(node, ast.Expr):
            issues.append(
                f"Line {node.lineno}: Top-level expression found. "
                "Ensure this doesn't perform I/O."
            )

        # Flag control flow and calls that shouldn't be at module level
        if isinstance(node, ast.Call | ast.For | ast.While | ast.Try):
            issues.append(
                f"Line {node.lineno}: Top-level {type(node).__name__} found. "
                "Verify this is safe for the Scheduler."
            )

    if issues:
        logger.warning("Potential issues in {}:", filepath.name)
        for issue in issues:
            logger.warning("  - {}", issue)
        logger.info(
            "Airflow best practice: Avoid top-level code that connects to DBs or APIs"
        )
        return False

    logger.success("{} - no obvious top-level side effects", filepath.name)
    return True


def main() -> int:
    """Entry point for the DAG validation script.

    Returns:
        Exit code: 0 if all files pass, 1 otherwise.
    """
    if len(sys.argv) < 2:
        logger.error(
            "Usage: validate_dag_integrity.py <path_to_python_file_or_directory>"
        )
        return 1

    target = Path(sys.argv[1])
    all_passed = True

    if target.is_file():
        all_passed = check_file(target)
    elif target.is_dir():
        python_files = list(target.rglob("*.py"))
        if not python_files:
            logger.warning("No Python files found in {}", target)
            return 0

        for py_file in python_files:
            if not check_file(py_file):
                all_passed = False
    else:
        logger.error("Path not found: {}", target)
        return 1

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
