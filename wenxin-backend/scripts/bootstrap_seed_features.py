"""Manual bootstrap: backfill cultural features + sync feedback + run evolution."""
import sys
import json
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.prototype.digestion.feature_extractor import backfill_missing_features
from app.prototype.feedback.feedback_store import FeedbackStore
from app.prototype.digestion.context_evolver import ContextEvolver


def main():
    print("=== Bootstrap Seed Features ===")

    # Step 1: Backfill missing cultural features
    count = backfill_missing_features()
    print(f"Backfilled {count} sessions with cultural_features")

    # Step 2: Sync inline feedback
    store = FeedbackStore.get()
    synced = store.sync_from_sessions()
    print(f"Synced {synced} feedback entries from sessions")

    # Step 3: Run evolution
    evolver = ContextEvolver()
    evolver.evolve()
    print("Evolution complete")

    # Step 4: Verify
    data_dir = Path(__file__).resolve().parent.parent / "app" / "prototype" / "data"
    ctx_path = data_dir / "evolved_context.json"
    if ctx_path.exists():
        ctx = json.loads(ctx_path.read_text())
        print(f"\nevolved_context.json:")
        print(f"  evolutions: {ctx.get('evolutions', 0)}")
        print(f"  traditions: {list(ctx.get('tradition_weights', {}).keys())}")
        print(f"  cultures: {len(ctx.get('cultures', []))}")
        print(f"  prompt_contexts: {len(ctx.get('prompt_contexts', {}))}")
    else:
        print("WARNING: evolved_context.json not found")


if __name__ == "__main__":
    main()
