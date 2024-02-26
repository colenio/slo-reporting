from datetime import timedelta, datetime, tzinfo, timezone
from pathlib import Path
from typing import List, Type, Tuple, Any, Dict, Optional

import yaml
from prometheus_api_client import PrometheusConnect
from pydantic import BaseModel, SecretStr, PositiveInt
from pydantic.fields import FieldInfo, Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

PROJECT_ROOT = (Path(__file__).resolve().parent / '..').resolve().absolute()


class YamlConfigSettingsSource(PydanticBaseSettingsSource):
    content: Dict[str, Any] = {}
    content_file: str = f"{PROJECT_ROOT}/config/settings.yaml"
    content_loaded: bool = False

    @property
    def _config(self) -> Dict[str, Any]:
        if not self.content_loaded:
            path = Path(self.content_file)
            if not path.exists():
                raise FileNotFoundError(f"Config file {self.content_file} not found")
            self.content = yaml.safe_load(path.read_text(encoding='utf-8'))
            self.content_loaded = True
        return self.content

    def get_field_value(self, field: FieldInfo, field_name: str) -> Tuple[Any, str, bool]:
        field_value = self._config.get(field_name)
        return field_value, field_name, False

    def prepare_field_value(self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool) -> Any:
        return value

    def __call__(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}

        for field_name, field in self.settings_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(field, field_name)
            field_value = self.prepare_field_value(field_name, field, field_value, value_is_complex)
            if field_value is not None:
                d[field_key] = field_value

        return d


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
    query: str = Field(default='100 * sum(min_over_time(up{job="prometheus"}[15m]))', description="PromQL query")
    goal: float = Field(default=99.9, description="Goal of the SLO")


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


class AzureQuerier(BaseModel):
    name: str = Field(default="azure-querier", description="Name of the Querier")
    subscriptionID: str = Field(description="SubscriptionID of the Azure-Resource to query")


class PrometheusQuerier(BaseModel):
    name: str = Field(default="prometheus-querier", description="Name of the Querier")
    url: str = Field(default="http://localhost:9090", description="URL of the Prometheus server")
    user: str = Field(default="prometheus-user", description="Username for the Prometheus server")
    password: SecretStr = Field(default=SecretStr("password"), description="Password for the Prometheus server")
    ssl_verify: bool = Field(default=False, description="Verify SSL certificate")
    query: str = Field(default="ALERTS{}", description="Query which should be executed")


class Queriers(BaseModel):
    azure: List[AzureQuerier] = Field(default_factory=list, description="List of Azure Queriers")
    prometheus: List[PrometheusQuerier] = Field(default_factory=list, description="List of Prometheus Queriers")


class SystemsHealth(BaseModel):
    enabled: bool = True
    queriers: Queriers = Queriers()
    query_interval: PositiveInt = Field(default=60,description="Interval in which the alert sources should be queried (in Seconds)")

class Settings(BaseSettings):
    api_base: str = "/api"
    project: str = "slo-reporting"
    stage: str = "dev"
    version: str = "0.1.0"
    git_commit: str = "-local-"
    metrics: Metrics = Metrics()
    systems_health: SystemsHealth = SystemsHealth()

    # https://docs.pydantic.dev/latest/concepts/pydantic_settings/#adding-sources
    @classmethod
    def settings_customise_sources(cls, settings_cls: Type[BaseSettings], init_settings: PydanticBaseSettingsSource,
                                   env_settings: PydanticBaseSettingsSource,
                                   dotenv_settings: PydanticBaseSettingsSource,
                                   file_secret_settings: PydanticBaseSettingsSource, ) -> Tuple[
        PydanticBaseSettingsSource, ...]:
        return (init_settings, YamlConfigSettingsSource(settings_cls), env_settings, file_secret_settings,)


settings = Settings()
