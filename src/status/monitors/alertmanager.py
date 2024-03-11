import re
from datetime import datetime, timezone
from typing import List, Dict, Any

from pydantic import Field, field_validator
from pydantic_core.core_schema import ValidationInfo
from requests import Request, PreparedRequest, Session

from status.monitors.models import Alert, Monitor, MonitorConfig


class AlertManagerConfig(MonitorConfig):
    name: str = Field(default="alertmanager")
    # https://github.com/prometheus/alertmanager/blob/main/api/v2/openapi.yaml
    url: str = Field(default="http://localhost:9093/api/v2/alerts", description="URL of the AlertManager server")
    filters: List[str] = Field(default_factory=list, description="A list of matchers to filter alerts by")
    active: bool = Field(default=True, description="Show active alerts")
    silenced: bool = Field(default=False, description="Show silenced alerts")
    inhibited: bool = Field(default=False, description="Show inhibited alerts")
    unprocessed: bool = Field(default=False, description="Show unprocessed alerts")
    receiver: str = Field(default='', description="A regex matching receivers to filter alerts by")

    def to_params(self) -> Dict[str, Any]:
        # https://github.com/prometheus/alertmanager/blob/efa801faf7e1c176b797e30379b840b6521973ed/api/v2/openapi.yaml#L142
        # @formatter:off
        dct = {
            'active': str(self.active).lower(),
            'inhibited': str(self.inhibited).lower(),
            'silenced': str(self.silenced).lower(),
            'unprocessed': str(self.unprocessed).lower(),
        }
        if self.filters:
            dct['filter'] = self.filters  # type: ignore
        if self.receiver:
            dct['receiver'] = self.receiver
        return dct

    @field_validator('receiver')
    @classmethod
    def check_regex(cls, v: str, info: ValidationInfo) -> str:
        try:
            re.compile(v)
            return v
        except re.error as exc:
            raise ValueError(f'{info.field_name} must be a valid regex') from exc


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
        timestamp = datetime.fromisoformat(result.get('startsAt', datetime.now(timezone.utc).isoformat()))

        labels: Dict[str, str] = result.get('labels', {})
        name = labels.get('alertname', 'Unknown')
        severity = labels.get('severity', 'info')

        annotations: Dict[str, str] = result.get('annotations', {})
        description = annotations.get('description', '')
        url = annotations.get('dashboard', annotations.get('runbook_url', ''))

        return Alert(
            type=self.type, name=name, timestamp=timestamp,
            severity=severity, description=description, url=url
        )
