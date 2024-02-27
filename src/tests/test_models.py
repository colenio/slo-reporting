import json
from datetime import timedelta, datetime, timezone
from typing import List

from pydantic import TypeAdapter

from models.settings import Settings, AzureMonitorConfig, AlertManagerConfig, PrometheusMonitorConfig
from monitors.models import Alert


def test_settings() -> None:
    settings = Settings()
    assert settings.api_base == "/api"
    assert settings.project == "slo-reporting"
    assert settings.stage == "dev"
    assert settings.version == "0.2.0"
    assert settings.git_commit == "-local-"

    metrics = settings.metrics
    assert metrics.prometheus.url == "http://localhost:9090"
    assert metrics.archive == "./data/slo-reporting.csv"
    assert metrics.window == timedelta(weeks=1)
    assert metrics.step == timedelta(days=1)

    now = metrics.now
    assert now.tzinfo is timezone.utc
    assert metrics.now == datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    assert len(metrics.objectives) > 0
    slo = metrics.objectives[0]
    assert slo.name == "prometheus-uptime"
    assert slo.goal == 99.9


def test_alerts() -> None:
    expected = Alert(type="prometheus", name="prometheus-uptime", timestamp=datetime.now(timezone.utc),
                     description="uptime is low", url="http://localhost:9090")
    alerts = [expected]
    adapter = TypeAdapter(List[Alert])
    output = adapter.dump_json(alerts)
    input = adapter.validate_python(json.loads(output))
    actual = Alert.model_validate(input[0])

    assert actual == expected


def test_monitor_config() -> None:
    am = AlertManagerConfig()
    assert am.name == "alertmanager"
    am = AlertManagerConfig(name="my-name")
    assert am.name == "my-name"

    az = AzureMonitorConfig(subscription_id="id")
    assert az.name == "azure"
    assert az.subscription_id == "id"
    az = AzureMonitorConfig(name="my-name", subscription_id="id")
    assert az.name == "my-name"

    prom = PrometheusMonitorConfig()
    assert prom.name == "prometheus"
    assert prom.url == "http://localhost:9090"
