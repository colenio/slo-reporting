import logging
from typing import List

from azure.core.credentials import TokenCredential
from azure.identity import DefaultAzureCredential
from azure.mgmt.alertsmanagement import AlertsManagementClient
from azure.mgmt.alertsmanagement.models import MonitorCondition

from models.settings import AzureMonitorConfig
from monitors import Alert
from monitors.models import Alert, Monitor


class AzureMonitor(Monitor):
    client: AlertsManagementClient

    def __init__(self, name: str, client: AlertsManagementClient) -> None:
        self.name = name
        self.client = client

    @staticmethod
    def of(config: AzureMonitorConfig) -> 'AzureMonitor':
        credential: TokenCredential = DefaultAzureCredential()  # type: ignore
        client = AlertsManagementClient(credential=credential, subscription_id=config.subscription_id)
        return AzureMonitor(config.name, client)

    def scrape(self) -> List[Alert]:
        alerts: List[Alert] = []
        response = self.client.alerts.get_all(
            monitor_condition=MonitorCondition.FIRED,
            severity='Sev0',  #  TODO: This should be configurable
        )
        for item in response:
            alert = Alert(
                type="Azure",
                name=item.name,
                description=item.properties.essentials.additional_properties['description'],
                url=item.properties.essentials.alert_rule,
                timestamp=item.properties.essentials.start_date_time)
            alerts.append(alert)

        logging.debug("Azure-Querier: %s successfully queried", self.name)
        return alerts


