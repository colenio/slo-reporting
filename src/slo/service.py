from datetime import datetime
from typing import Mapping

import pandas as pd
from pandas import DataFrame
from pydantic import BaseModel

from config.settings import settings
from slo.config import Metrics, ServiceLevelObjective


class SloValue(BaseModel):
    value: float
    goal: float

    @property
    def style(self) -> str:
        if self.value >= self.goal:
            return "success"
        if self.value >= self.goal * 0.80:
            return "warning"
        return "danger"


class SloService:
    metrics: Metrics = settings.metrics

    @property
    def path(self):
        return self.metrics.path

    def get_slo_values(self) -> Mapping[str, SloValue]:
        client = self.metrics.prometheus.client
        result = {}
        for slo in self.metrics.objectives:
            metrics = client.custom_query(query=slo.query)
            goals = client.custom_query(query=slo.goal_query) if slo.goal_query else []
            for i, metric in enumerate(metrics):
                name = metric.get("metric", {}).get(slo.name, slo.name)
                value = metric["value"][1]
                goal = goals[i]["value"][1] if goals else slo.goal
                result[name] = SloValue(value=value, goal=goal)
        return result

    def get_slo_window(self, force: bool = True) -> DataFrame:
        path = self.metrics.path
        need_update = force or not path.exists() or path.stat().st_mtime < self.metrics.now.timestamp()
        df = self._read_archive()
        if not need_update:
            return df
        df_slo = self._read_objectives()
        df = df.combine_first(df_slo)

        df.attrs["updated"] = datetime.now().isoformat()
        df.attrs["file_name"] = path.name

        return df

    def _read_objectives(self) -> DataFrame:
        # https://stackoverflow.com/questions/53645882/pandas-merging-101
        dfs = [self._range_of(slo, self.metrics.now) for slo in self.metrics.objectives]
        df_slo = pd.concat(dfs, axis=1, join="outer")
        return df_slo

    def _range_of(self, slo: ServiceLevelObjective, end: datetime) -> DataFrame:
        start = end - self.metrics.window
        step = str(self.metrics.step.total_seconds())
        client = self.metrics.prometheus.client
        metric_data = client.custom_query_range(query=slo.query, start_time=start, end_time=end, step=step)
        df = DataFrame()
        for metric in metric_data:
            name = metric.get("metric", {}).get(slo.name, slo.name)
            df = df.combine_first(DataFrame(metric["values"], columns=["timestamp", name]))
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        df.set_index("timestamp", inplace=True)
        return df

    def _read_archive(self) -> DataFrame:
        try:
            return pd.read_csv(self.metrics.path, parse_dates=["timestamp"], index_col="timestamp")
        except FileNotFoundError:
            return pd.DataFrame()
