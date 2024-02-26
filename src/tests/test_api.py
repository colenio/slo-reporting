import json

from starlette.testclient import TestClient

from models.settings import settings


def test_config(client: TestClient) -> None:
    response = client.get(f"{settings.api_base}/config")
    assert response.status_code == 200
    content = response.json()
    expected = {"Settings": json.loads(settings.model_dump_json(by_alias=True))}
    assert content == expected

# TODO: due to the 'update' call this test is integrative, but fails with a default prom installation aswell as in CI.
#def test_slo_export(client: TestClient) -> None:
#    path = f"{settings.api_base}/slo/export"
#    response = client.get(f"{path}/csv")
#    assert response.status_code == 200
#    assert response.headers["Content-Type"] == "text/csv; charset=utf-8"
#    assert response.headers["Content-Disposition"] == 'attachment; filename="slo-reporting.csv"'
#
#    response = client.get(f"{path}/json")
#    assert response.status_code == 200
#    assert response.headers["Content-Type"] == "application/json"
#
#    response = client.get(f"{path}/xlsx")
#    assert response.status_code == 200
#    assert response.headers["Content-Type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#    assert response.headers["Content-Disposition"] == 'attachment; filename="slo-reporting.xlsx"'

def test_systems_health_success(client: TestClient) -> None:
    with open('alerts.json', 'w') as fp:
        fp.write("[]")

    response = client.get(f"{settings.api_base}/systems-health")
    assert response.status_code == 200

def test_systems_health_failure(client: TestClient) -> None:
    with open('alerts.json', 'w') as fp:
        fp.write('[{"name": "testalert", "description": "", "url":"","startTimestamp": ""}]')

    response = client.get(f"{settings.api_base}/systems-health")
    assert response.status_code == 418
    