import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from vulca._vlm import _load_evolved_context


class TestVLMLocalContext:
    def test_reads_local_evolved_context(self):
        with tempfile.TemporaryDirectory() as td:
            ctx = {"traditions": {"chinese_xieyi": {"session_count": 5}}}
            ctx_path = Path(td) / "evolved_context.json"
            ctx_path.write_text(json.dumps(ctx))

            with patch("vulca._vlm._LOCAL_EVOLVED_PATH", ctx_path):
                result = _load_evolved_context()
                assert result is not None
                assert "traditions" in result

    def test_returns_none_when_no_file(self):
        with patch("vulca._vlm._LOCAL_EVOLVED_PATH", Path("/nonexistent/path.json")):
            result = _load_evolved_context()
            assert result is None
