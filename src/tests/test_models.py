from datetime import timedelta, datetime, timezone

from config.settings import Settings
from slo.config import ServiceLevelObjective


def test_settings() -> None:
    settings = Settings()
    assert settings.api_base == "/api"
    assert settings.project == "slo-reporting"
    assert settings.stage == "dev"
    assert settings.build_version == "0.3.0"
    assert settings.build_date <= datetime.now(timezone.utc).isoformat()
    assert settings.git_commit == "-local-"

    metrics = settings.metrics
    assert metrics.prometheus.url == "http://localhost:9090"
    assert metrics.archive == "./data/slo-reporting.csv"
    assert metrics.window == timedelta(days=30)
    assert metrics.step == timedelta(days=1)

    now = metrics.now
    assert now.tzinfo is timezone.utc
    assert metrics.now == datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    assert len(metrics.objectives) > 0
    slo = metrics.objectives[0]
    assert slo.name == "prometheus-uptime"
    assert slo.goal == 99.9


def test_metrics() -> None:
    slo = ServiceLevelObjective(goal_query="100 * pyrra_objective")
    assert slo.goal_query == "100 * pyrra_objective"
    assert slo.goal == 99.9, "default goal"
