import logging
from datetime import datetime
from typing import List, Dict, Any

from prometheus_api_client import PrometheusConnect
from pydantic import Field, SecretStr

from status.monitors.models import Monitor, Alert, MonitorConfig


class PrometheusMonitorConfig(MonitorConfig):
    name: str = Field(default='prometheus')
    url: str = Field(default='http://localhost:9090')
    user: str = Field(default='')
    password: SecretStr = Field(default=SecretStr(''))
    ssl_verify: bool = Field(default=False)
    query: str = Field(default='ALERTS{alertstate="firing", severity="critical", relevance="health-status"}')


class PrometheusMonitor(Monitor):
    client: PrometheusConnect
    query: str = 'up'

    def __init__(self, client: PrometheusConnect, query: str = 'up', name: str = '') -> None:
        super().__init__(name)
        self.client = client
        self.query = query

    @staticmethod
    def of(config: PrometheusMonitorConfig) -> 'PrometheusMonitor':
        # @formatter:off
        client = PrometheusConnect(
            url=config.url, disable_ssl=config.ssl_verify,
            auth=(config.user, config.password.get_secret_value()) if config.user else None
        )
        return PrometheusMonitor(client=client, query=config.query, name=config.name)

    def scrape(self) -> List[Alert]:
        results: List[Dict[str, Any]] = self.client.custom_query(self.query)
        alerts = [self.alert_of(result) for result in results]
        logging.debug("Prom-Querier: %s successfully queried", self.name)
        return alerts

    def alert_of(self, result: Dict[str, Any]) -> Alert:
        name = str(result.get('metric', {}).get('alertname', 'Unknown'))
        timestamp = datetime.utcnow()
        try:
            ts = result.get('value', [0, 0])[0]
            timestamp = datetime.fromtimestamp(ts)
        except IndexError:
            logging.warning("No timestamp found in result: %s", result)
        return Alert(type=self.type, name=name, timestamp=timestamp)
