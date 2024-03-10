import json
from datetime import datetime, timezone
from typing import List

from pydantic import TypeAdapter

from status.monitors.alertmanager import AlertManagerConfig
from status.monitors.azure import AzureMonitorConfig
from status.monitors.models import Alert
from status.monitors.prometheus import PrometheusMonitorConfig


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
