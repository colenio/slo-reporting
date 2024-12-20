from pandas import DataFrame
from pytest_mock import MockFixture
from starlette.testclient import TestClient

from config.settings import settings
from slo.service import get_slo_service
from tests.utils import patch_of

def test_slo_export(client: TestClient, mocker: MockFixture) -> None:
    p = patch_of(mocker, get_slo_service().get_slo_window)  # type: ignore
    df = DataFrame()
    p.return_value = df

    path = f"{settings.api_base}/slo/export"
    response = client.get(f"{path}/csv?update=true")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/csv; charset=utf-8"
    assert response.headers["Content-Disposition"] == 'attachment; filename="slo-reporting.csv"'

    response = client.get(f"{path}/json")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"

    response = client.get(f"{path}/xlsx")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert response.headers["Content-Disposition"] == 'attachment; filename="slo-reporting.xlsx"'
