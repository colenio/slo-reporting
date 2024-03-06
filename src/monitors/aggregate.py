from typing import List

from pydantic import TypeAdapter

from models.settings import settings
from monitors.models import Monitor, Alert


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
        with open(self.path, mode='wb') as fp:
            json = self.adapter.dump_json(alerts)
            fp.write(json)
        return alerts

