from datetime import datetime, timezone
from unittest.mock import create_autospec

import requests_mock
from azure.core.credentials import TokenCredential
from azure.mgmt.alertsmanagement import AlertsManagementClient

from status.monitors.azure import AzureMonitor


def test_azure_monitor() -> None:
    credential = create_autospec(TokenCredential)
    azure_client = AlertsManagementClient(credential=credential, subscription_id='123')

    monitor = AzureMonitor(azure_client)
    assert monitor.type == 'azure'

    # az_alert = AzAlert(name='test', properties=None)
    # alerts_client.get_all.return_value = [az_alert]
    timestamp = datetime.now(timezone.utc)
    with requests_mock.Mocker() as m:
        # Example response: https://learn.microsoft.com/en-us/rest/api/monitor/alertsmanagement/alerts/get-all
        # @formatter:off
        m.get(
            url='https://management.azure.com/subscriptions/123/providers/Microsoft.AlertsManagement/alerts?monitorCondition=Fired&severity=Sev0',
            json={"value": [{
                "name": "cpu alert",
                "properties": {
                    "essentials": {
                        "alertRule": "https://contoso.com/alerts/123",
                        "monitorCondition": "Fired",
                        "severity": "Sev0",
                        "signalType": "Metric",
                        "startDateTime": timestamp.isoformat(),
                    }
                }
            }]}
        )

        alerts = monitor.scrape()
        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.name == 'cpu alert'
        assert alert.url == 'https://contoso.com/alerts/123'
        assert alert.timestamp == timestamp
