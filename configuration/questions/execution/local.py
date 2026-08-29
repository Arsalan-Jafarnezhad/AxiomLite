import subprocess, tempfile, time
from pathlib import Path
from questions.execution.base import ExecutionReport, ExecutionTest
from questions.execution.registry import register
from questions.constants import TestResultStatus
from questions.utils import compare_outputs

@register("python_stdio_local")
class LocalPythonExecutor:
    def execute(self, submission, tests):
        results=[]
        for test in tests:
            started=time.monotonic()
            with tempfile.TemporaryDirectory(prefix="questions-local-") as td:
                path=Path(td)/"submission.py"
                path.write_text(submission.code, encoding="utf-8")
                try:
                    p=subprocess.run(["python",str(path)],input="\n".join(map(str,test.inputs)),text=True,capture_output=True,timeout=float(test.timeout))
                except subprocess.TimeoutExpired:
                    results.append(ExecutionTest(test.pk,test.order,TestResultStatus.TIMEOUT,False,test.inputs,test.expected_outputs,execution_time=time.monotonic()-started,error_type="timeout",error_message="Execution timed out."))
                    continue
                if p.returncode:
                    results.append(ExecutionTest(test.pk,test.order,TestResultStatus.ERROR,False,test.inputs,test.expected_outputs,p.stdout,time.monotonic()-started,"runtime_error","Program exited with an error."))
                    continue
                passed=compare_outputs(test.expected_outputs,p.stdout.splitlines(),test.comparison_mode)
                results.append(ExecutionTest(test.pk,test.order,TestResultStatus.PASSED if passed else TestResultStatus.FAILED,passed,test.inputs,test.expected_outputs,p.stdout,time.monotonic()-started))
        passed=sum(x.passed for x in results)
        return ExecutionReport(True,len(results),passed,len(results)-passed,results)
