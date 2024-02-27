from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class Alert(BaseModel):
    model_config = ConfigDict(ser_json_timedelta='iso8601')

    type: str
    name: str
    timestamp: datetime
    description: Optional[str] = None
    url: Optional[str] = None


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
