from typing import List

from pydantic import TypeAdapter

from monitors.models import Monitor, Alert


class AggregateMonitor(Monitor):
    def __init__(self, monitors: List[Monitor]) -> None:
        self.monitors = monitors
        self.adapter = TypeAdapter(List[Alert])

    def scrape(self) -> List[Alert]:
        alerts: List[Alert] = []
        for monitor in self.monitors:
            alerts += monitor.scrape()
        with open('alerts.json', mode='wb') as fp:
            json = self.adapter.dump_json(alerts)
            fp.write(json)
        return alerts

