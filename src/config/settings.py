from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Tuple, Type

import yaml
from pydantic.fields import FieldInfo
from pydantic_settings import PydanticBaseSettingsSource, BaseSettings

from config import PROJECT_ROOT
from slo.config import Metrics
from status.config import Status
from ui.config import UIConfig


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


class Settings(BaseSettings):
    api_base: str = "/api"
    project: str = "slo-reporting"
    stage: str = "dev"
    build_version: str = "0.3.0"
    build_date: str = datetime.now(timezone.utc).isoformat()
    git_commit: str = "-local-"
    metrics: Metrics = Metrics()
    status: Status = Status()
    ui: UIConfig = UIConfig()

    # https://docs.pydantic.dev/latest/concepts/pydantic_settings/#adding-sources
    @classmethod
    # @formatter:off
    def settings_customise_sources(cls, settings_cls: Type[BaseSettings],
       init_settings: PydanticBaseSettingsSource,
       env_settings: PydanticBaseSettingsSource,
       dotenv_settings: PydanticBaseSettingsSource,
       file_secret_settings: PydanticBaseSettingsSource
   ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return init_settings, YamlConfigSettingsSource(settings_cls), env_settings, file_secret_settings,


settings = Settings()
