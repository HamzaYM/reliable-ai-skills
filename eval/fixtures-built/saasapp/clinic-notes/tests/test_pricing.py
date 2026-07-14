import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]
                       / "backend" / "app" / "ai"))

import pricing


def test_known_models_priced():
    assert pricing.price_completion("summary-standard", 1000, 1000) > 0
    assert pricing.price_completion("summary-pro", 1000, 1000) > 0
