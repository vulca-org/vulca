import subprocess
import sys

VULCA = [sys.executable, "-m", "vulca.cli"]


class TestCLIReference:
    def test_create_accepts_reference(self):
        result = subprocess.run(
            VULCA + ["create", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert "--reference" in result.stdout
        assert "--ref-type" in result.stdout

    def test_create_accepts_sketch(self):
        result = subprocess.run(
            VULCA + ["create", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert "--sketch" in result.stdout

    def test_evaluate_accepts_reference(self):
        result = subprocess.run(
            VULCA + ["evaluate", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert "--reference" in result.stdout
