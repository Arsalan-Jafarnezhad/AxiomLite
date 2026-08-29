import base64
import subprocess
import time
import uuid

from django.conf import settings

from questions.constants import TestResultStatus
from questions.execution.base import ExecutionReport, ExecutionTest
from questions.execution.registry import register
from questions.utils import compare_outputs


@register("auto")
@register("python_stdio")
class PythonDockerExecutor:
    image = getattr(
        settings,
        "QUESTIONS_PYTHON_IMAGE",
        "questions-python:3.14-sandbox",
    )

    def execute(self, submission, tests):
        # A `docker run` (container create + start + network namespace setup
        # + teardown) has real, multi-second overhead on Docker Desktop /
        # WSL2 -- independent of what the submitted code actually does (a
        # submission that fails with an instant SyntaxError still pays this
        # cost). Paying that cost once per *test case* is what was causing
        # entire submissions to blow past their timeout budget even for
        # trivially fast/failing code.
        #
        # Instead: start ONE long-lived container per submission (its
        # entrypoint just decodes the code and then `sleep infinity`s), and
        # run each test case via `docker exec` against that same container.
        # `docker exec` does not pay container-creation overhead, so this
        # amortizes the expensive part across all test cases instead of
        # repeating it per test.
        container_name = f"submission-{submission.pk}-{uuid.uuid4().hex[:12]}"

        if not self._start_container(submission.code, container_name):
            return ExecutionReport(
                False,
                len(tests),
                0,
                len(tests),
                [],
                error_type="setup_error",
                error_message="Failed to start the sandbox container.",
            )

        try:
            results = [self._run_test(container_name, test) for test in tests]
        finally:
            self._stop_container(container_name)

        passed = sum(result.passed for result in results)

        return ExecutionReport(
            True,
            len(results),
            passed,
            len(results) - passed,
            results,
        )

    def _start_container(self, code, container_name):
        code_b64 = base64.b64encode(code.encode("utf-8")).decode("ascii")

        cmd = [
            "docker",
            "run",
            "--rm",
            "-d",
            "--name",
            container_name,
            "--network",
            "none",
            "--read-only",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,nodev,size=16m",
            "--cpus",
            str(getattr(settings, "QUESTIONS_MAX_EXECUTION_CPU", 1)),
            "--memory",
            str(getattr(settings, "QUESTIONS_MAX_EXECUTION_MEMORY", "128m")),
            "--pids-limit",
            str(getattr(settings, "QUESTIONS_MAX_PROCESSES", 32)),
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--user",
            "65534:65534",
            "-e",
            f"SUBMISSION_CODE_B64={code_b64}",
            self.image,
        ]

        container_startup_timeout = float(
            getattr(settings, "QUESTIONS_CONTAINER_STARTUP_TIMEOUT_SECONDS", 15.0)
        )

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=container_startup_timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            self._stop_container(container_name)
            return False

        return proc.returncode == 0

    def _stop_container(self, container_name):
        # Best-effort cleanup. `--rm` should already remove the container
        # once it stops, but don't let a hung/unresponsive daemon block the
        # worker: give this a short timeout of its own.
        try:
            subprocess.run(
                ["docker", "rm", "-f", container_name],
                capture_output=True,
                check=False,
                timeout=5,
            )
        except subprocess.TimeoutExpired:
            pass

    def _run_test(self, container_name, test):
        started = time.monotonic()

        input_text = "\n".join(str(value) for value in test.inputs)

        timeout = float(test.timeout)

        # `docker exec` still has a little overhead of its own (much less
        # than `docker run`, but not zero), so keep a small buffer between
        # the inner `timeout Xs` and the outer subprocess timeout.
        exec_overhead = float(
            getattr(settings, "QUESTIONS_DOCKER_EXEC_OVERHEAD_SECONDS", 2.0)
        )
        subprocess_timeout = timeout + exec_overhead

        output_limit = int(getattr(settings, "QUESTIONS_MAX_OUTPUT_SIZE", 64 * 1024))

        cmd = [
            "docker",
            "exec",
            "-i",
            container_name,
            "timeout",
            f"{timeout}s",
            "python",
            "/tmp/submission.py",
        ]

        try:
            proc = subprocess.run(
                cmd,
                input=input_text,
                text=True,
                capture_output=True,
                timeout=subprocess_timeout,
                check=False,
            )

        except subprocess.TimeoutExpired:
            # The in-container `timeout Xs` should be what fires here. If we
            # get here, `docker exec` itself is stuck (daemon/WSL2 issue),
            # not the submitted code. The container itself gets torn down
            # by execute()'s `finally` block once all tests finish/error.
            return ExecutionTest(
                test.pk,
                test.order,
                TestResultStatus.TIMEOUT,
                False,
                test.inputs,
                test.expected_outputs,
                execution_time=time.monotonic() - started,
                error_type="timeout",
                error_message="Execution timed out.",
            )

        actual = proc.stdout

        if len(actual.encode("utf-8")) > output_limit:
            return ExecutionTest(
                test.pk,
                test.order,
                TestResultStatus.OUTPUT_LIMIT_EXCEEDED,
                False,
                test.inputs,
                test.expected_outputs,
                actual[:output_limit],
                time.monotonic() - started,
                "output_limit_exceeded",
                "Output limit exceeded.",
            )

        if proc.returncode != 0:
            error_message = proc.stderr.strip() or "Program exited with an error."

            return ExecutionTest(
                test.pk,
                test.order,
                TestResultStatus.ERROR,
                False,
                test.inputs,
                test.expected_outputs,
                actual,
                time.monotonic() - started,
                "runtime_error",
                error_message,
            )

        actual_lines = actual.splitlines()

        passed = compare_outputs(
            test.expected_outputs,
            actual_lines,
            test.comparison_mode,
        )

        return ExecutionTest(
            test.pk,
            test.order,
            (TestResultStatus.PASSED if passed else TestResultStatus.FAILED),
            passed,
            test.inputs,
            test.expected_outputs,
            actual,
            time.monotonic() - started,
        )
