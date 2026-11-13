from datetime import date, timedelta
from functools import lru_cache

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

from .models import Site

KIND_CODE = {"dining": 0, "restaurant": 1, "event": 2}
KIND_FACTOR = {0: 1.0, 1: 0.8, 2: 1.3}
DOW_FACTOR = np.array([1.0, 1.1, 1.1, 1.0, 0.9, 0.6, 0.5])  # Mon..Sun


@lru_cache(maxsize=1)
def _model() -> GradientBoostingRegressor:
    """Trains on synthetic data. Replace with real dining/event logs when available."""
    rng = np.random.default_rng(42)
    n = 3000
    avg = rng.uniform(10, 120, n)
    kind = rng.integers(0, 3, n)
    dow = rng.integers(0, 7, n)
    event = rng.integers(0, 2, n)
    y = avg * DOW_FACTOR[dow] * np.vectorize(KIND_FACTOR.get)(kind) * (1 + 0.5 * event)
    y += rng.normal(0, 0.08 * avg)
    model = GradientBoostingRegressor(random_state=0)
    return model.fit(np.column_stack([avg, kind, dow, event]), y)


def forecast(sites: list[Site], days: int = 7, start: date | None = None) -> list[dict]:
    start = start or date.today()
    rows, meta = [], []
    for site in sites:
        for i in range(days):
            d = start + timedelta(days=i)
            rows.append([site.avg_lbs, KIND_CODE[site.kind], d.weekday(), 0])
            meta.append((site, d))
    preds = _model().predict(np.array(rows))
    return [
        {"site_id": s.id, "site": s.name, "date": d.isoformat(), "predicted_lbs": round(max(float(p), 0), 1)}
        for (s, d), p in zip(meta, preds)
    ]
