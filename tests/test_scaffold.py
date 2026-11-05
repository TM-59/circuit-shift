import subprocess
import sys

from fastapi.testclient import TestClient

from circuit_shift.composition import create_app


def test_REQ_HEALTH_returns_typed_response() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        schema = client.get("/openapi.json").json()
        assert schema["components"]["schemas"]["Health"]["properties"]["status"]["const"] == "ok"


def test_REQ_CORE_imports_without_site_packages() -> None:
    subprocess.run(
        [sys.executable, "-S", "-c", "import circuit_shift.domain, circuit_shift.application"],
        env={"PYTHONPATH": "src"},
        check=True,
        timeout=10,
    )


def test_REQ_HEALTH_scaffold_has_no_game_or_remote_docs_ui() -> None:
    with TestClient(create_app()) as client:
        for path in ("/", "/docs", "/redoc"):
            assert client.get(path).status_code == 404
