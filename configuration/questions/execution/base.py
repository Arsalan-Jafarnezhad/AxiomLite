from dataclasses import dataclass, field
from typing import Any

@dataclass
class ExecutionTest:
    test_case_id: int
    test_order: int
    status: str
    passed: bool
    input_snapshot: Any
    expected_output_snapshot: Any
    actual_output: str = ""
    execution_time: float | None = None
    error_type: str = ""
    error_message: str = ""

@dataclass
class ExecutionReport:
    success: bool
    total_tests: int
    passed_tests: int
    failed_tests: int
    tests: list[ExecutionTest] = field(default_factory=list)
    error_type: str = ""
    error_message: str = ""
