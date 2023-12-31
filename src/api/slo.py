from datetime import datetime

import pandas as pd
from fastapi import APIRouter
from fastapi_restful.cbv import cbv
from pandas import DataFrame
from starlette.responses import FileResponse

from models.settings import settings, ServiceLevelObjective, Metrics

router = APIRouter()


@cbv(router)
class SloController:
    metrics: Metrics = settings.metrics

    @router.post("/_update")
    def update(self, force: bool = True) -> None:
        df = self._update(force)
        df.to_csv(self.metrics.path)

    @router.get("/export/csv")
    def export_csv(self) -> FileResponse:
        self.update(False)
        path = self.metrics.path
        return FileResponse(path, media_type="text/csv", filename=path.name)

    @router.get("/export/json")
    def export_json(self) -> str:
        df = self._update(False)
        content = df.to_json(orient="records")
        return content

    @router.get("/export/xlsx")
    def export_xlsx(self) -> FileResponse:
        df = self._update(False)
        file_name = self.metrics.path.with_suffix(".xlsx")
        df.to_excel(file_name)
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
        return FileResponse(file_name, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            filename=file_name.name)

    def _update(self, force: bool = True) -> DataFrame:
        path = self.metrics.path
        need_update = force or not path.exists() or path.stat().st_mtime < self.metrics.now.timestamp()
        df = self._read_archive()
        if not need_update:
            return df
        df_slo = self._read_slos()
        df = df.combine_first(df_slo)
        return df

    def _read_slos(self) -> DataFrame:
        # https://stackoverflow.com/questions/53645882/pandas-merging-101
        dfs = [self._range_of(slo, self.metrics.now) for slo in self.metrics.objectives]
        df_slo = pd.concat(dfs, axis=1, join="outer")
        return df_slo

    def _range_of(self, slo: ServiceLevelObjective, end: datetime) -> DataFrame:
        start = end - self.metrics.window
        step = str(self.metrics.step.total_seconds())
        client = self.metrics.prometheus.client
        metric_data = client.custom_query_range(query=slo.query, start_time=start, end_time=end, step=step)
        df = DataFrame(metric_data[0]["values"], columns=["timestamp", slo.name])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        df[slo.name] = pd.to_numeric(df[slo.name], errors="coerce")
        df.set_index("timestamp", inplace=True)
        return df

    def _read_archive(self) -> DataFrame:
        try:
            return pd.read_csv(self.metrics.path, parse_dates=["timestamp"], index_col="timestamp")
        except FileNotFoundError:
            return pd.DataFrame()
