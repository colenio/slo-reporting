from datetime import datetime, timezone

from pytest_mock import MockFixture
from starlette.testclient import TestClient

from config.settings import settings
from status.monitors.models import Alert
from status.service import get_status_service
from tests.utils import patch_of


def test_status_api(client: TestClient, mocker: MockFixture) -> None:
    p = patch_of(mocker, get_status_service().get_status)  # type: ignore
    p.return_value = [], 200
    response = client.get(f"{settings.api_base}/status")
    assert response.is_success

    alert = Alert(type="alertmanager", name="test", timestamp=datetime.now(timezone.utc))
    p.return_value = [alert], settings.status.code
    response = client.get(f"{settings.api_base}/status")
    assert response.status_code == settings.status.code
