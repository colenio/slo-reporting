from datetime import datetime

import requests_mock

from models.settings import PrometheusMonitorConfig
from monitors.prometheus import PrometheusMonitor


def test_prometheus_monitor() -> None:
    config = PrometheusMonitorConfig()
    monitor = PrometheusMonitor.of(config)
    assert monitor.type == 'prometheus'

    timestamp = datetime.utcnow()
    with requests_mock.Mocker() as m:
        m.get(
            url=f'{config.url}/api/v1/query?query={config.query}',
            # @formatter:off
            json={
                "status": "success",
                "data": {
                    "result": [{
                        "metric": {
                            "__name__": config.query,
                            "alertname": "test",
                            "severity": "critical"
                        },
                        "value": [timestamp.timestamp(), 0]
                    }]
                }
            }
        )
        alerts = monitor.scrape()
    assert len(alerts) == 1
    alert = alerts[0]
    assert alert.name == 'test'
    assert alert.timestamp == timestamp
