"""Simple test runner for the Intermediate Code Generation Visualizer."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from optimizer import TACOptimizer, format_tac  # noqa: E402
from parser import CompilerParser  # noqa: E402
from tac_generator import TACGenerator  # noqa: E402


def load_cases(manifest_path: Path) -> list[dict]:
    """Load test case definitions from JSON."""
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def run_pipeline(source_code: str) -> dict[str, str]:
    """Execute the compiler pipeline for test purposes."""
    parser = CompilerParser()
    generator = TACGenerator()
    optimizer = TACOptimizer()

    ast_root = parser.parse(source_code)
    tac_before = generator.generate(ast_root)
    tac_after = optimizer.optimize(tac_before)

    return {
        "tac_before": format_tac(tac_before),
        "tac_after": format_tac(tac_after),
    }


def run_case(case: dict, tests_dir: Path) -> tuple[bool, str]:
    """Run one test case and return pass/fail plus a short message."""
    source_path = tests_dir / case["path"]
    source_code = source_path.read_text(encoding="utf-8")

    try:
        result = run_pipeline(source_code)
    except Exception as error:  # noqa: BLE001
        if case["expected"] != "error":
            return False, f"unexpected error: {error}"

        expected_error = case["error_contains"]
        if expected_error not in str(error):
            return False, f"wrong error: {error}"
        return True, str(error)

    if case["expected"] != "success":
        return False, "expected an error but pipeline succeeded"

    for expected_text in case.get("optimized_tac_contains", []):
        if expected_text not in result["tac_after"]:
            return False, f"optimized TAC missing: {expected_text}"

    return True, "ok"


def main() -> int:
    """Run all test cases and print a compact summary."""
    tests_dir = Path(__file__).resolve().parent
    cases = load_cases(tests_dir / "test_cases.json")

    passed = 0
    total = len(cases)

    print("Compiler Test Suite")
    print("===================")

    for index, case in enumerate(cases, start=1):
        ok, detail = run_case(case, tests_dir)
        status = "PASS" if ok else "FAIL"
        print(f"{index:>2}. [{status}] {case['name']} - {detail}")
        if ok:
            passed += 1

    print("\nSummary")
    print("=======")
    print(f"Passed: {passed}/{total}")

    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
