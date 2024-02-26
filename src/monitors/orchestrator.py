import datetime
import json
from typing import Any, List

from models.settings import Monitors
from monitors.azure import AzureMonitor
from monitors.prometheus import PrometheusMonitor
from monitors.models import Monitor, Alert
from monitors.alertmanager import AlertmanagerMonitor


class TimestampEncoder(json.JSONEncoder):
    def default(self,obj: Any) -> Any:
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


class AggregateMonitor:
    def __init__(self, monitor_config: Monitors) -> None:
        azure_monitors = [AzureMonitor.of(m) for m in monitor_config.azure]
        prometheus_monitors = [PrometheusMonitor.of(m) for m in monitor_config.prometheus]
        alertmanager_monitors = [AlertmanagerMonitor.of(m) for m in monitor_config.alertmanager]
        self.monitors: List[Monitor] = azure_monitors + prometheus_monitors + alertmanager_monitors

    def execute(self) -> None:
        alerts: List[Alert] = []
        for monitor in self.monitors:
            alerts += monitor.scrape()
        with open('alerts.json', mode='w', encoding='utf-8') as fp:
            json.dump([a.model_dump() for a in alerts], indent=2, fp=fp,cls=TimestampEncoder)
