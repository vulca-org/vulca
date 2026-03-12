"""Test ImageScorer dynamic reference text with fallback."""
from __future__ import annotations
import pytest
from unittest.mock import patch, MagicMock

from app.prototype.agents.image_scorer import (
    ImageScorer,
    _get_references_dynamic,
    _LEGACY_TRADITION_REFERENCES,
)


class TestGetReferencesDynamic:
    def test_legacy_fallback_for_unknown(self):
        with patch("app.prototype.cultural_pipelines.tradition_loader.get_tradition", return_value=None):
            result = _get_references_dynamic("nonexistent")
        assert result == _LEGACY_TRADITION_REFERENCES["default"]

    def test_known_tradition_returns_valid_refs(self):
        result = _get_references_dynamic("chinese_xieyi")
        assert "L1" in result
        assert "L3" in result
        assert "L5" in result

    def test_yaml_tier_when_available(self):
        mock_tc = MagicMock()
        mock_tc.display_name = {"en": "Test Art"}
        terms = []
        for name, levels in [("brush", ["L1", "L3"]), ("ink", ["L1"]), ("philosophy", ["L5"]), ("harmony", ["L3", "L5"])]:
            t = MagicMock()
            t.term = name
            t.l_levels = levels
            terms.append(t)
        mock_tc.terminology = terms

        with patch("app.prototype.cultural_pipelines.tradition_loader.get_tradition", return_value=mock_tc):
            result = _get_references_dynamic("test_tradition")
        assert "L1" in result
        assert "brush" in result["L1"]

    def test_default_always_available(self):
        result = _get_references_dynamic("default")
        assert "L1" in result
        assert "L3" in result
        assert "L5" in result


class TestImageScorerLoadFailed:
    """Test that _load_failed flag prevents repeated model load attempts.

    We mock sentence_transformers at the module level via sys.modules so that
    the ``from sentence_transformers import SentenceTransformer`` inside
    ``_load_model`` picks up our mock — even when the real package is not
    installed (e.g. CI with requirements.render.txt).
    """

    @staticmethod
    def _make_fresh_scorer() -> ImageScorer:
        """Create a fresh ImageScorer instance (not the singleton)."""
        scorer = ImageScorer.__new__(ImageScorer)
        scorer._model = None
        scorer._available = None
        scorer._load_failed = False
        import threading
        scorer._lock = threading.Lock()
        return scorer

    @pytest.fixture(autouse=True)
    def _mock_st_module(self):
        """Inject a fake sentence_transformers module into sys.modules."""
        import sys
        fake_st = MagicMock()
        saved = sys.modules.get("sentence_transformers")
        sys.modules["sentence_transformers"] = fake_st
        self._fake_st = fake_st
        yield
        if saved is None:
            sys.modules.pop("sentence_transformers", None)
        else:
            sys.modules["sentence_transformers"] = saved

    def test_load_failed_flag_set_on_meta_tensor_error(self):
        """When SentenceTransformer raises meta tensor error, _load_failed is set."""
        scorer = self._make_fresh_scorer()
        scorer._available = True

        meta_error = NotImplementedError(
            "Cannot copy out of meta tensor; no data! "
            "Please use torch.nn.Module.to_empty()"
        )
        self._fake_st.SentenceTransformer.side_effect = meta_error
        scorer._load_model()

        assert scorer._load_failed is True
        assert scorer._model is None
        assert scorer.available is False

    def test_load_failed_flag_set_on_runtime_error(self):
        """When SentenceTransformer raises RuntimeError with meta, _load_failed is set."""
        scorer = self._make_fresh_scorer()
        scorer._available = True

        meta_error = RuntimeError(
            "Cannot copy out of meta tensor; no data!"
        )
        self._fake_st.SentenceTransformer.side_effect = meta_error
        scorer._load_model()

        assert scorer._load_failed is True
        assert scorer._model is None

    def test_meta_tensor_error_cpu_fallback_succeeds(self):
        """When initial load fails with meta tensor, CPU fallback is tried."""
        scorer = self._make_fresh_scorer()
        scorer._available = True

        mock_model = MagicMock()
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1 and "device" not in kwargs:
                raise NotImplementedError("Cannot copy out of meta tensor")
            return mock_model

        self._fake_st.SentenceTransformer.side_effect = side_effect
        scorer._load_model()

        assert scorer._load_failed is False
        assert scorer._model is mock_model

    def test_load_failed_prevents_retry(self):
        """Once _load_failed is True, _load_model returns immediately."""
        scorer = self._make_fresh_scorer()
        scorer._load_failed = True

        scorer._load_model()
        assert scorer._model is None

    def test_available_returns_false_when_load_failed(self):
        """available property returns False when _load_failed is True."""
        scorer = self._make_fresh_scorer()
        scorer._load_failed = True
        assert scorer.available is False

    def test_score_image_returns_none_when_load_fails(self, tmp_path):
        """score_image gracefully returns None when model loading fails."""
        scorer = self._make_fresh_scorer()
        scorer._available = True

        img_path = tmp_path / "test.png"
        from app.prototype.agents.draft_provider import _make_placeholder_png
        img_path.write_bytes(_make_placeholder_png(8, 8, 128, 128, 128, 42))

        meta_error = NotImplementedError("Cannot copy out of meta tensor")
        self._fake_st.SentenceTransformer.side_effect = meta_error
        result = scorer.score_image(
            str(img_path), "test subject", "chinese_xieyi"
        )

        assert result is None
        assert scorer._load_failed is True

    def test_unexpected_exception_sets_load_failed(self):
        """Non-meta-tensor exceptions also set _load_failed to prevent retries."""
        scorer = self._make_fresh_scorer()
        scorer._available = True

        self._fake_st.SentenceTransformer.side_effect = OSError("disk full")
        scorer._load_model()

        assert scorer._load_failed is True
        assert scorer._model is None
