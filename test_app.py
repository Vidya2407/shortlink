import pytest
import app as app_module

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(app_module, "DB", str(tmp_path / "test.db"))
    app_module.init_db()
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"

def test_shorten_valid_url(client):
    r = client.post("/shorten", json={"url": "https://example.com"})
    assert r.status_code == 201
    assert len(r.get_json()["code"]) == 6

def test_shorten_rejects_bad_url(client):
    r = client.post("/shorten", json={"url": "not-a-url"})
    assert r.status_code == 400

def test_redirect_works(client):
    code = client.post("/shorten", json={"url": "https://example.com"}).get_json()["code"]
    r = client.get("/" + code)
    assert r.status_code == 302
    assert r.headers["Location"] == "https://example.com"

def test_unknown_code_returns_404(client):
    assert client.get("/doesnotexist").status_code == 404

def test_click_counter(client):
    code = client.post("/shorten", json={"url": "https://example.com"}).get_json()["code"]
    client.get("/" + code)
    client.get("/" + code)
    assert client.get("/stats/" + code).get_json()["clicks"] == 2