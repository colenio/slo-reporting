from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MonitorConfig(BaseModel):
    pass


# @formatter:off
ALERT_STYLES = {
    'critical': 'danger',
    'error': 'danger',
    'fatal': 'danger',
    'warning': 'warning'
}


class Alert(BaseModel):
    model_config = ConfigDict(ser_json_timedelta='iso8601')

    type: str
    name: str
    timestamp: datetime
    severity: str = Field(default='critical')
    description: Optional[str] = None
    url: Optional[str] = None

    @property
    def style(self) -> str:
        return ALERT_STYLES.get(self.severity.lower(), 'info')


class Monitor:
    _name: str = ''

    def __init__(self, name: str = '') -> None:
        self._name = name or self.type

    @property
    def name(self) -> str:
        return self._name or self.type

    @property
    def type(self) -> str:
        return self.__class__.__name__.removesuffix("Monitor").lower()

    def scrape(self) -> List[Alert]:
        raise NotImplementedError("Please implement this method in a child-class")
