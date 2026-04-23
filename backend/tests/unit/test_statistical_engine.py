from datetime import date, timedelta

from app.services.statistical_engine import StatisticalDecisionEngine


def test_pipeline_reaches_polynomial_stage_with_enough_data():
    engine = StatisticalDecisionEngine()
    start = date(2026, 1, 1)
    records = []
    for i in range(50):
        records.append(
            {
                "log_date": (start + timedelta(days=i)).isoformat(),
                "calories": 2200 + i,
                "sleep_hours": 7 + (i % 3) * 0.1,
                "steps": 9000 + i * 5,
                "diet_type": "balanced" if i % 2 == 0 else "low-carb",
                "stress_level": 4,
                "weight_kg": 80 - i * 0.05,
            }
        )

    result = engine.run_pipeline(records)
    assert result["stage"] == "polynomial"
    assert "regression" in result
    assert "polynomial" in result
    assert isinstance(result["insights"], list)
