from datetime import datetime, timezone

import pytest
import requests_mock
from pydantic import ValidationError

from status.monitors.alertmanager import AlertManagerMonitor, AlertManagerConfig


def test_alertmanager() -> None:
    config = AlertManagerConfig()
    monitor = AlertManagerMonitor.of(config)
    assert monitor.type == 'alertmanager'
    assert monitor.name == 'alertmanager'
    assert monitor.request.method == 'GET'
    url = str(monitor.request.url)
    assert url.startswith('http://localhost:9093/api/v2/alerts?')

    assert config.active is True
    assert 'active=true' in url

    assert config.silenced is False
    assert 'silenced=false' in url

    assert config.inhibited is False
    assert 'inhibited=false' in url

    assert config.unprocessed is False
    assert 'unprocessed=false' in url

    assert config.filters == []
    assert 'filter=' not in url

    assert not config.receiver
    assert 'receiver=' not in url

    config.filters = ['severity=critical']
    config.receiver = '(email|slack|webhook)'
    monitor = AlertManagerMonitor.of(config)
    url = str(monitor.request.url)
    assert 'filter=severity%3Dcritical' in url
    assert 'receiver=%28email%7Cslack%7Cwebhook%29' in url

    with pytest.raises(ValidationError):
        config.model_validate({'receiver': '(invalid regex'})

    timestamp = datetime.now(timezone.utc)
    with requests_mock.Mocker() as m:
        # @formatter:off
        m.get(url, json=[{
            'startsAt': timestamp.isoformat(),
            'labels': {'alertname': 'test'},
            'annotations': {
                'description': 'Alert description',
                'dashboard': 'https://grafana.com/dashboards/123'
            }
        }
        ])
        alerts = monitor.scrape()

    assert len(alerts) == 1
    alert = alerts[0]
    assert alert.name == 'test'
    assert alert.url == 'https://grafana.com/dashboards/123'
    assert alert.description == 'Alert description'
    assert alert.timestamp == timestamp



