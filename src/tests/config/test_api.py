import json

from starlette.testclient import TestClient

from config.settings import settings


def test_config_api(client: TestClient) -> None:
    response = client.get(f"{settings.api_base}/config")
    assert response.status_code == 200
    content = response.json()
    expected = {"Settings": json.loads(settings.model_dump_json(by_alias=True))}
    assert content == expected
