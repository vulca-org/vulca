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

    def test_sketch_removed_from_create(self):
        """--sketch was dead code (GenerateNode never read sketch_b64). Removed."""
        result = subprocess.run(
            VULCA + ["create", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert "--sketch" not in result.stdout
        # --reference now serves both purposes
        assert "also serves as sketch" in result.stdout

    def test_evaluate_accepts_reference(self):
        result = subprocess.run(
            VULCA + ["evaluate", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert "--reference" in result.stdout
