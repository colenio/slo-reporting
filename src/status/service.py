from typing import List, Tuple

from config.settings import settings
from status.config import Status
from status.monitors.aggregate import AggregateMonitor
from status.monitors.models import Alert


class StatusService:
    status: Status = settings.status
    monitor: AggregateMonitor = AggregateMonitor.of_monitors(settings.status.monitors)

    def get_status(self) -> Tuple[List[Alert], int]:
        alerts = self.monitor.scrape()
        status_code = self.status.code if alerts else 200
        return alerts, status_code


def get_status_service() -> StatusService:
    return StatusService()
