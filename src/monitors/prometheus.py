import datetime
import logging
from typing import List, Dict, Any

from prometheus_api_client import PrometheusConnect
from pydantic import SecretStr

from models.settings import PrometheusMonitorConfig
from monitors.models import Monitor, Alert


class PrometheusMonitor(Monitor):
    def __init__(self, name: str, url: str, user: str, password: SecretStr, ssl_verify: bool, query: str) -> None:
        self.name = name
        self.query = query
        auth = (user, password)
        self.client = PrometheusConnect(url=url, auth=auth, disable_ssl=ssl_verify)

    @staticmethod
    def of(config: PrometheusMonitorConfig) -> 'PrometheusMonitor':
        return PrometheusMonitor(config.name, config.url, config.user, config.password, config.ssl_verify, config.query)

    def scrape(self) -> List[Alert]:
        alerts: List[Alert] = []
        results: List[Dict[str, Any]] = self.client.custom_query(self.query)
        for result in results:
            #  TODO: There's no description nor URL in prom ALERT metric. Those are only present in Alertmanager
            alert = Alert(
                type="Prometheus",
                name=str(result.get('metric', {}).get('alertname', 'Unknown')),
                timestamp=datetime.datetime.utcnow()
            )
            alerts.append(alert)

        logging.debug("Prom-Querier: %s successfully queried", self.name)
        return alerts
