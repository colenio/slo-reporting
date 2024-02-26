import datetime
from typing import List

import requests

from monitors.models import Alert, Monitor
from models.settings import AlertmanagerMonitorConfig


class AlertmanagerMonitor(Monitor):
    requestUrl: str 

    def __init__(self, name: str,url: str,filters: List[str],active: bool, silenced: bool, inhibited: bool, unprocessed: bool):
        self.name = name 
        filter = ""

        if len(filters) > 0:
            filter: str = "filter=" + "&".join(filters)
        self.requestUrl = f"{url}/api/v2/alerts?{filter}&active={str(active).lower()}&silenced={str(silenced).lower()}&inhibited={str(inhibited).lower()}&unprocessed={str(unprocessed).lower()}"

    @staticmethod
    def of(config: AlertmanagerMonitorConfig) -> 'AlertmanagerMonitor':
        return AlertmanagerMonitor(config.name,config.url,config.filters,config.active,config.silenced,config.inhibited,config.unprocessed)

    def scrape(self) -> List[Alert]:
        alerts: List[Alert] = []

        results = requests.get(self.requestUrl).json()
        for result in results:
            alert = Alert(
                type="Alertmanager",
                name = str(result.get('labels',{}).get('alertname', 'Unknown')),
                description = str(result.get('annotations', {}).get('description', '')),
                # TODO: get timestamp and parse it to datetime 
                timestamp=datetime.datetime.utcnow(),
                url = str(result.get('annotations',{}).get('dashboard','')),
            )
            alerts.append(alert)
           
        return alerts
                   
