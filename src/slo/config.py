from datetime import timedelta, datetime, timezone
from pathlib import Path
from typing import Optional, List

from prometheus_api_client import PrometheusConnect
from pydantic import BaseModel, Field, SecretStr

from config import PROJECT_ROOT


class Prometheus(BaseModel):
    url: str = Field(default="http://localhost:9090", description="URL of the Prometheus server")
    user: str = Field(default="slo-reporting-user", description="Username for the Prometheus server")
    password: SecretStr = Field(default=SecretStr("slo-reporting-password"),
                                description="Password for the Prometheus server")
    ssl_verify: bool = Field(default=False, description="Verify SSL certificate")
    _client: Optional[PrometheusConnect] = None

    @property
    def client(self) -> PrometheusConnect:
        if self._client is None:
            auth = (self.user, self.password.get_secret_value())
            self._client = PrometheusConnect(url=self.url, auth=auth, disable_ssl=self.ssl_verify)
        return self._client


class ServiceLevelObjective(BaseModel):
    name: str = Field(default="prometheus-uptime", description="Name of the SLO")
    goal: float = Field(default=99.9, description="Goal of the SLO")
    query: str = Field(default='100 * avg(avg_over_time(up{job=~"prometheus.*"}[5m]))', description="PromQL query")
    goal_query: Optional[str] = Field(default=None, description="PromQL query for the goal")


class Metrics(BaseModel):
    enabled: bool = True
    prometheus: Prometheus = Prometheus()
    archive: str = Field(default="data/archive.csv", description="Path to the archive (CSV file)")
    window: timedelta = Field(default=timedelta(weeks=1), description="Rolling window")
    step: timedelta = Field(default=timedelta(days=1), description="Step interval")
    objectives: List[ServiceLevelObjective] = Field(default_factory=list, description="List of SLOs")

    @property
    def path(self) -> Path:
        return Path(PROJECT_ROOT / self.archive).resolve().absolute()

    @property
    def now(self) -> datetime:
        # See https://github.com/mediapop/datetime_truncate/blob/master/datetime_truncate/datetime_truncate.py
        dt = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        ts = self.step.total_seconds()
        m = dt.minute % (ts // 60)
        dt -= timedelta(minutes=m)
        h = dt.hour % (ts // 3600)
        dt -= timedelta(hours=h)
        d = dt.day % self.step.days
        dt -= timedelta(days=d)
        return dt
