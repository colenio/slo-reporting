import typing

from fastapi.testclient import TestClient
from pytest_mock import MockFixture


@typing.no_type_check
def test_home(client: TestClient) -> None:
    # See https://www.starlette.io/templates/#testing-template-responses
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.next_request.url.path == "/slo"


@typing.no_type_check
def test_about(client: TestClient) -> None:
    response = client.get("/about")
    assert response.status_code == 200
    assert response.template.name == 'about.html'
    assert "settings" in response.context
