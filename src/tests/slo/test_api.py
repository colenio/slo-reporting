import json

import pytest
from starlette.testclient import TestClient

from config.settings import settings


@pytest.mark.skip("TODO")
def test_slo_export(client: TestClient) -> None:
    path = f"{settings.api_base}/slo/export"
    response = client.get(f"{path}/csv")
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
