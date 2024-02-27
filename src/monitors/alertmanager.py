from datetime import datetime
from typing import List, Dict, Any

from requests import Request, PreparedRequest, Session

from models.settings import AlertManagerConfig
from monitors.models import Alert, Monitor


class AlertManagerMonitor(Monitor):
    request: PreparedRequest

    def __init__(self, request: PreparedRequest, name: str):
        super().__init__(name)
        self.request = request

    @staticmethod
    def of(config: AlertManagerConfig) -> 'AlertManagerMonitor':
        params = config.to_params()
        request = Request(method='GET', url=config.url, params=params).prepare()
        return AlertManagerMonitor(request, config.name)

    def scrape(self) -> List[Alert]:
        results = Session().send(self.request).json()
        alerts = [self.alert_of(result) for result in results]
        return alerts

    def alert_of(self, result: Dict[str, Any]) -> Alert:
        timestamp = datetime.fromisoformat(result.get('startsAt', datetime.utcnow().isoformat()))

        labels: Dict[str, str] = result.get('labels', {})
        name = labels.get('alertname', 'Unknown')

        annotations: Dict[str, str] = result.get('annotations', {})
        description = annotations.get('description', '')
        url = annotations.get('dashboard', annotations.get('runbook_url', ''))

        return Alert(type=self.type, name=name, timestamp=timestamp, description=description, url=url)
