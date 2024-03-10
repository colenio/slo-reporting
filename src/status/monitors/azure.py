from datetime import datetime, timezone
from typing import List

from azure.core.credentials import TokenCredential
from azure.identity import DefaultAzureCredential
from azure.mgmt.alertsmanagement import AlertsManagementClient
from azure.mgmt.alertsmanagement.models import Alert as AzAlert, AlertProperties, Essentials
from azure.mgmt.alertsmanagement.models import MonitorCondition
from pydantic import Field

from status.monitors.models import Alert, Monitor, MonitorConfig


class AzureMonitorConfig(MonitorConfig):
    name: str = Field(default="azure")
    subscription_id: str


class AzureMonitor(Monitor):
    client: AlertsManagementClient

    def __init__(self, client: AlertsManagementClient, name: str = '') -> None:
        super().__init__(name)
        self.client = client

    @staticmethod
    def of(config: AzureMonitorConfig) -> 'AzureMonitor':
        credential: TokenCredential = DefaultAzureCredential()  # type: ignore
        client = AlertsManagementClient(credential=credential, subscription_id=config.subscription_id)
        return AzureMonitor(client, config.name)

    def scrape(self) -> List[Alert]:
        response = self.client.alerts.get_all(monitor_condition=MonitorCondition.FIRED, severity='Sev0')
        alerts = [self.alert_of(item) for item in response]
        return alerts

    def alert_of(self, az_alert: AzAlert) -> Alert:
        # @formatter:off
        props = az_alert.properties or AlertProperties()
        essentials = props.essentials or Essentials()
        description = essentials.additional_properties.get('description', '')
        url = essentials.alert_rule or ''
        timestamp = essentials.start_date_time or datetime.now(timezone.utc)
        return Alert(type=self.type, name=az_alert.name, description=description, url=url, timestamp=timestamp)
