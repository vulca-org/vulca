import subprocess
import sys

VULCA = [sys.executable, "-m", "vulca.cli"]


class TestCLISync:
    def test_sync_help(self):
        result = subprocess.run(
            VULCA + ["sync", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "sync" in result.stdout.lower()

    def test_sync_without_api_url_fails(self):
        """sync without VULCA_API_URL should print error."""
        import os
        env = os.environ.copy()
        env.pop("VULCA_API_URL", None)
        result = subprocess.run(
            VULCA + ["sync"],
            capture_output=True, text=True, timeout=10,
            env=env,
        )
        assert result.returncode != 0 or "VULCA_API_URL" in result.stderr or "VULCA_API_URL" in result.stdout
