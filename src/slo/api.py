from typing import Mapping

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi_restful.cbv import cbv
from starlette.responses import Response, FileResponse, JSONResponse

from slo import deps
from slo.service import SloService, SloValue

router = APIRouter()


@cbv(router)
class SloController:
    service: SloService = Depends(deps.get_slo_service)

    @router.get("/")
    def get_slo(self) -> Mapping[str, SloValue]:
        return self.service.get_slo_values()

    @router.post("/_update")
    def update(self, force: bool = True) -> Response:
        df = self.service.get_slo_window(force)
        df.to_csv(self.service.path)
        return Response(status_code=204)

    @router.get("/export/csv")
    def export_csv(self) -> FileResponse:
        self.update(False)
        path = self.service.path
        return FileResponse(path, media_type="text/csv", filename=path.name)

    @router.get("/export/json")
    def export_json(self) -> JSONResponse:
        df = self.service.get_slo_window(False)
        content = jsonable_encoder(df.to_dict())
        return JSONResponse(content=content)

    @router.get("/export/xlsx")
    def export_xlsx(self) -> FileResponse:
        df = self.service.get_slo_window(False)
        file_name = self.service.path.with_suffix(".xlsx")
        df.to_excel(file_name)
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
        return FileResponse(file_name, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            filename=file_name.name)
