import json

import pytest
from starlette.testclient import TestClient

from models.settings import settings


def test_config(client: TestClient) -> None:
    response = client.get(f"{settings.api_base}/config")
    assert response.status_code == 200
    content = response.json()
    expected = {"Settings": json.loads(settings.model_dump_json(by_alias=True))}
    assert content == expected


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


def test_status(client: TestClient) -> None:
    # TODO: test without needing file system
    path = settings.status.path
    with open(path, 'w', encoding='utf-8') as fp:
        fp.write("[]")
    response = client.get(f"{settings.api_base}/status")
    assert response.is_success

    with open(path, 'w', encoding='utf-8') as fp:
        fp.write('[{"name": "testalert", "description": "", "url":"","startTimestamp": ""}]')

    response = client.get(f"{settings.api_base}/status")
    assert response.status_code == settings.status.code
