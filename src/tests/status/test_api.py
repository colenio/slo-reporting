from starlette.testclient import TestClient

from config.settings import settings


def test_status_api(client: TestClient) -> None:
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
