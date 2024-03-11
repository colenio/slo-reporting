from typing import List

from pydantic import TypeAdapter

from config.settings import settings
from status.config import Monitors
from status.monitors.alertmanager import AlertManagerMonitor
from status.monitors.azure import AzureMonitor
from status.monitors.models import Monitor, Alert
from status.monitors.prometheus import PrometheusMonitor


class AggregateMonitor(Monitor):
    path = settings.status.path

    def __init__(self, monitors: List[Monitor]) -> None:
        super().__init__('aggregate')
        self.monitors = monitors
        self.adapter = TypeAdapter(List[Alert])

    def scrape(self) -> List[Alert]:
        alerts: List[Alert] = []
        for monitor in self.monitors:
            alerts += monitor.scrape()
        self.dump_file(alerts)
        return alerts

    def dump_file(self, alerts: List[Alert]) -> None:
        with open(self.path, mode='wb') as fp:
            fp.write(self.dump_json(alerts))

    def load_file(self) -> List[Alert]:
        with open(self.path, mode='rb') as fp:
            return self.load_json(fp.read())

    def dump_json(self, alerts: List[Alert]) -> bytes:
        return self.adapter.dump_json(alerts)

    def load_json(self, json: bytes) -> List[Alert]:
        return self.adapter.validate_json(json)

    @staticmethod
    def of_monitors(mon: Monitors) -> 'AggregateMonitor':
        monitors: List[Monitor] = [AzureMonitor.of(m) for m in mon.azure]
        monitors += [PrometheusMonitor.of(m) for m in mon.prometheus]
        monitors += [AlertManagerMonitor.of(m) for m in mon.alertmanager]
        return AggregateMonitor(monitors)


