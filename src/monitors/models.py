from datetime import datetime
from typing import List, Type, Literal, Optional

from pydantic import BaseModel

from models.settings import MonitorConfig


class Alert(BaseModel):
    type: Literal["Prometheus", "Azure", "Alertmanager"]
    name: str
    timestamp: datetime
    description: Optional[str] = None
    url: Optional[str] = None


class Monitor:
    def scrape(self) -> List[Alert]:
        raise NotImplementedError("Please implement this method in a child-class")

    @staticmethod
    def of(config: Type[MonitorConfig]) -> Type['Monitor']:
        raise NotImplementedError("Please implement this method in a child-class")
